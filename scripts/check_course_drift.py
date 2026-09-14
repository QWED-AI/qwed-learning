"""Course-vs-code drift check for qwed-learning (issue #19).

Fails loudly when the course text drifts from the implementations it teaches:

  1. Stale pins   — every ``pip install qwed...==X.Y.Z`` pin in
     ``module-*/README.md`` and ``capstone-project/README.md`` must equal
     the latest release on PyPI (``>=`` minimums must name an existing
     version). Comparisons use real PEP 440 ordering.
  2. Dead tags    — every ``QWED-AI/<repo>@vX.Y.Z`` reference must resolve
     to a real tag.
  3. Banned vocab — ``INVALID`` / ``APPROVED`` / ``QUARANTINED`` may appear in
     course markdown only on lines that also mention workflow/disposition.
  4. Dead imports — every ``from qwed... import <name>`` in fenced Python
     blocks must resolve against the installed packages.
  5. Workflow sync — the drift workflow must install exactly what the
     course pins (no missing packages, no skew, no below-minimum).

Run locally with ``python scripts/check_course_drift.py`` after
``pip install qwed qwed-a2a qwed-infra``; CI installs the pinned releases.
Documented exceptions live in
``scripts/course_drift_exceptions.json`` and are reviewed like code.

Needs ``packaging`` (ships with pip/setuptools — present in every Python
that can install the course packages) for PEP 440 comparison; everything
else is stdlib.
"""

from __future__ import annotations

import ast
import importlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

try:
    from packaging.version import InvalidVersion, Version
except ImportError as exc:
    raise RuntimeError(
        "check_course_drift needs the 'packaging' module (ships with pip)"
    ) from exc

ROOT = Path(__file__).resolve().parent.parent
EXCEPTIONS_FILE = Path(__file__).resolve().parent / "course_drift_exceptions.json"

# qwed-a2a refuses to import without a deployment ID; the check needs imports
# to resolve, not a real deployment, so default it when unset.
os.environ.setdefault("QWED_A2A_DEPLOYMENT_ID", "course-drift-check")

PIN_SCOPE = sorted(ROOT.glob("module-*/README.md")) + [ROOT / "capstone-project" / "README.md"]
IMPORT_SCOPE = list(PIN_SCOPE)

EXCLUDE_DIRS = {".git", ".github", "node_modules", ".venv", "test_venv", "__pycache__"}
WORKFLOW_FILE = ROOT / ".github" / "workflows" / "course-drift.yml"

PIN_SPEC_RE = re.compile(
    r"(qwed[a-z0-9_-]*)(?:\[[^\]]*\])?\s*(==|>=)\s*"
    r"([\d][\dA-Za-z.\-]*)",
    re.IGNORECASE,
)
TAG_RE = re.compile(r"(QWED-AI/[A-Za-z0-9_.\-]+)@(v\d+\.\d+\.\d+[^\s\"'`]*)")


def _clean_tag_ref(ref: str) -> str:
    """Strip trailing Markdown punctuation (``.``/``,``/``)``) from a tag."""
    return ref.rstrip(".,;:)]}")
VOCAB_RE = re.compile(r"\b(INVALID|APPROVED|QUARANTINED)\b")
VOCAB_CONTEXT_RE = re.compile(r"workflow|disposition", re.IGNORECASE)
FROM_IMPORT_RE = re.compile(r"from\s+(qwed[a-z0-9_.]*)\s+import\s+([^\n#]+)")
PLAIN_IMPORT_RE = re.compile(
    r"^\s*import\s+([a-z0-9_.]+(?:\s+as\s+[a-z0-9_]+)?"
    r"(?:\s*,\s*[a-z0-9_.]+(?:\s+as\s+[a-z0-9_]+)?)*)",
    re.MULTILINE,
)
FENCE_RE = re.compile(r"```python(.*?)```", re.DOTALL)


# Version comparison uses packaging.version.Version (real PEP 440:
# zero-padding, pre/post/dev ordering, c/rc aliases) — hand-rolled
# comparators kept disagreeing with the standard, so they were deleted.
def _parse_version(raw: str, location: str, failures: list[str]):
    """Parse a version string, recording loud drift on unparsable input."""
    try:
        return Version(raw)
    except InvalidVersion:
        failures.append(f"pins: {location} has unparsable version {raw!r}")
        return None


def _pypi_latest(package: str) -> str:
    url = f"https://pypi.org/pypi/{package}/json"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except Exception as exc:
        raise RuntimeError(f"could not fetch PyPI metadata for {package}: {exc}") from exc
    return str(payload["info"]["version"])


def _pin_specs(text: str) -> list[tuple[str, str, str]]:
    """Yield (package, operator, version) for every qwed spec in pip commands.

    Matches are bounded to a single logical shell command (backslash
    continuations joined, everything else line-local), so later Markdown
    prose can never be swallowed into a command match.
    """
    specs = []
    continued = ""
    for raw_line in text.splitlines():
        line = (continued + " " + raw_line.strip()) if continued else raw_line
        continued = ""
        if line.rstrip().endswith("\\"):
            continued = line.rstrip()[:-1]
            continue
        marker = line.find("pip install")
        if marker < 0:
            continue
        for spec in PIN_SPEC_RE.finditer(line[marker:]):
            # PyPI names are case-insensitive; normalize so QWED==... and
            # qwed==... check the same distribution.
            specs.append((spec.group(1).lower(), spec.group(2), spec.group(3)))
    return specs


def _check_pin(location: str, package: str, operator: str, pinned: str,
               failures: list[str]) -> None:
    """Exact pins must equal latest; >= pins must name an existing version."""
    try:
        latest = _pypi_latest(package)
    except RuntimeError as exc:
        failures.append(f"pins: {exc}")
        return
    wanted = _parse_version(pinned, location, failures)
    current = _parse_version(latest, f"PyPI {package}", failures)
    if wanted is None or current is None:
        return
    # An exact pin older than latest is stale course, not safety.
    if operator == "==":
        if wanted != current:
            failures.append(
                f"pins: {location} pins {package}=={pinned} "
                f"but latest release is {latest}"
            )
    elif wanted > current:
        failures.append(
            f"pins: {location} requires {package}>={pinned} "
            f"but latest release is {latest}"
        )


def check_pins(failures: list[str]) -> None:
    for readme in PIN_SCOPE:
        if not readme.is_file():
            failures.append(f"pins: expected course file missing: {readme.relative_to(ROOT)}")
            continue
        text = readme.read_text(encoding="utf-8")
        location = readme.relative_to(ROOT).as_posix()
        for package, operator, pinned in _pin_specs(text):
            _check_pin(location, package, operator, pinned, failures)


def _github_tag_exists(repo: str, ref: str) -> bool:
    """True when ``ref`` is a real tag on a public GitHub repo.

    Uses the public git matching-refs API (no auth, no subprocess) so the
    check stays dependency-free and out of the local git state.
    """
    url = f"https://api.github.com/repos/{repo}/git/matching-refs/tags/{ref}"
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except Exception as exc:
        raise RuntimeError(f"could not list tags for {repo}: {exc}") from exc
    return any(entry.get("ref") == f"refs/tags/{ref}" for entry in payload)


def check_tags(failures: list[str]) -> None:
    for readme in PIN_SCOPE:
        if not readme.is_file():
            continue
        text = readme.read_text(encoding="utf-8")
        for match in TAG_RE.finditer(text):
            repo, ref = match.group(1), _clean_tag_ref(match.group(2))
            try:
                exists = _github_tag_exists(repo, ref)
            except RuntimeError as exc:
                failures.append(f"tags: {exc}")
                continue
            if not exists:
                failures.append(
                    f"tags: {readme.relative_to(ROOT)} references {repo}@{ref} "
                    f"which resolves to no real tag"
                )


def _iter_markdown() -> list[Path]:
    found = []
    for path in sorted(ROOT.rglob("*.md")):
        if any(part in EXCLUDE_DIRS for part in path.relative_to(ROOT).parts):
            continue
        found.append(path)
    return found


def check_vocab(failures: list[str], vocab_exceptions: set[tuple[str, str, str]]) -> None:
    for path in _iter_markdown():
        rel = path.relative_to(ROOT).as_posix()
        for line in path.read_text(encoding="utf-8").splitlines():
            for token in VOCAB_RE.findall(line):
                # Exceptions are scoped to one occurrence: file + token +
                # a substring of that exact line, so a later unrelated use
                # of the same token still fails.
                if any(
                    rel == exc_file and token == exc_token and exc_text in line
                    for exc_file, exc_token, exc_text in vocab_exceptions
                ):
                    continue
                if not VOCAB_CONTEXT_RE.search(line):
                    failures.append(
                        f"vocab: {rel} uses banned term {token!r} without "
                        f"workflow/disposition context: {line.strip()[:120]}"
                    )


def _fenced_blocks(text: str) -> list[str]:
    return FENCE_RE.findall(text)


def _resolve_course_module(rel: str, module: str, names: list[str], failures: list[str],
                            import_allowlist: set[tuple[str, str]]):
    """Import a course-referenced module, or record drift (None on failure).

    An unresolvable module is only excused when every imported name carries
    its own module.symbol exception — a module-level pass would let a future
    ``from <module> import UnknownSymbol`` through unnoticed. Wildcards need
    an explicit ``module.*`` exception; they never pass silently. A plain
    ``import <module>`` names no symbols, so the module itself is the claim
    and needs its own exception entry.
    """
    try:
        return importlib.import_module(module)
    except Exception:
        uncovered = []
        for name in names or ["<module>"]:
            key = module if name == "<module>" else f"{module}.{name}"
            if (rel, key) not in import_allowlist:
                uncovered.append(name)
        if uncovered:
            failures.append(
                f"imports: {rel} imports from unresolvable module {module!r} "
                f"(no exception covers: {', '.join(uncovered)})"
            )
        return None


def _check_imported_symbols(rel: str, module: str, imported, names: list[str],
                            failures: list[str],
                            import_allowlist: set[tuple[str, str]]) -> None:
    """Every name a course block imports must exist on the installed module."""
    for name in names:
        if name == "*":
            continue
        if (rel, f"{module}.{name}") in import_allowlist:
            continue
        if not hasattr(imported, name):
            failures.append(
                f"imports: {rel} imports {name!r} from {module!r} "
                f"but the installed package has no such symbol"
            )


def _split_import_names(raw: str) -> list[str]:
    """Split a from-import name list, dropping ``as`` aliases and parens."""
    names = []
    for piece in raw.replace("(", " ").replace(")", " ").split(","):
        piece = piece.strip()
        if not piece:
            continue
        names.append(piece.split()[0])
    return names


def _ast_import_targets(tree: ast.AST) -> list[tuple[str, list[str]]]:
    """Yield (module, [names]) for course-relevant imports in a syntax tree."""
    targets = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.startswith("qwed"):
                targets.append((module, [alias.name for alias in node.names]))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("qwed"):
                    targets.append((alias.name, []))
    return targets


def _strip_code_comments(block: str) -> str:
    """Remove `#` comments line-wise so commented-out imports never validate.

    Import lines cannot contain a bare `#` inside a string (module paths
    and imported names have no `#`), so splitting at the first `#` per
    line is exact here — unlike a general Python comment stripper.
    """
    return "\n".join(line.split("#", 1)[0] for line in block.splitlines())


def _fallback_import_targets(block: str) -> list[tuple[str, list[str]]]:
    """Regex-extract imports from a syntax-broken block (same shape as AST)."""
    code = _strip_code_comments(block)
    targets = [
        (match.group(1), _split_import_names(match.group(2)))
        for match in FROM_IMPORT_RE.finditer(code)
        if match.group(1).startswith("qwed")
    ]
    for match in PLAIN_IMPORT_RE.finditer(code):
        for name in _split_import_names(match.group(1)):
            if name.startswith("qwed"):
                targets.append((name, []))
    return targets


def _from_import_targets(block: str) -> list[tuple[str, list[str]]]:
    """Yield (module, [names]) for course-relevant imports in a block.

    Covers ``from X import ...`` and plain ``import X`` (empty names means
    "the module itself is the claim"). AST first; on SyntaxError fall back
    to regex extraction so one sketch error cannot smuggle drifted imports
    past the gate.
    """
    try:
        return _ast_import_targets(ast.parse(block))
    except SyntaxError:
        return _fallback_import_targets(block)


def check_imports(failures: list[str], import_allowlist: set[tuple[str, str]]) -> None:
    for readme in IMPORT_SCOPE:
        if not readme.is_file():
            continue
        rel = readme.relative_to(ROOT).as_posix()
        text = readme.read_text(encoding="utf-8")
        for block in _fenced_blocks(text):
            for module, names in _from_import_targets(block):
                imported = _resolve_course_module(rel, module, names, failures,
                                                  import_allowlist)
                if imported is None:
                    continue
                _check_imported_symbols(rel, module, imported, names, failures,
                                        import_allowlist)


def load_exceptions() -> tuple[set[tuple[str, str, str]], set[tuple[str, str]]]:
    """Load reviewed exceptions; validates shape so a typo fails loudly."""
    try:
        payload = json.loads(EXCEPTIONS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return set(), set()
    if not isinstance(payload, dict):
        raise RuntimeError(f"{EXCEPTIONS_FILE.name} must be a JSON object")
    vocab = set()
    for entry in payload.get("vocabulary", []):
        try:
            vocab.add((entry["file"], entry["token"], entry["contains"]))
        except (KeyError, TypeError) as exc:
            raise RuntimeError(
                f"{EXCEPTIONS_FILE.name}: vocabulary entries need "
                f"file/token/contains: {exc}"
            ) from exc
    imports = set()
    raw_imports = payload.get("imports", [])
    if not isinstance(raw_imports, list):
        raise RuntimeError(
            f"{EXCEPTIONS_FILE.name}: 'imports' must be a list"
        )
    for entry in raw_imports:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("file"), str)
            or not isinstance(entry.get("symbol"), str)
        ):
            raise RuntimeError(
                f"{EXCEPTIONS_FILE.name}: imports entries need "
                f"string file/symbol fields, got {entry!r}"
            )
        imports.add((entry["file"], entry["symbol"]))
    return vocab, imports


def _collect_course_versions(failures: list[str]) -> tuple[dict[str, set], dict[str, object]]:
    """Map each course-pinned package to its exact versions and top minimum.

    Versions are parsed (canonical PEP 440); unparsable entries fail loudly
    here so every later comparison is between real versions.
    """
    exact: dict[str, set] = {}
    minimums: dict[str, object] = {}
    for readme in PIN_SCOPE:
        if not readme.is_file():
            continue
        location = readme.relative_to(ROOT).as_posix()
        for package, operator, pinned in _pin_specs(readme.read_text(encoding="utf-8")):
            parsed = _parse_version(pinned, location, failures)
            if parsed is None:
                continue
            if operator == "==":
                exact.setdefault(package, set()).add(parsed)
            else:
                current = minimums.get(package)
                if current is None or parsed > current:
                    minimums[package] = parsed
    return exact, minimums


def _check_package_sync(package: str, versions: set, workflow_versions: dict,
                         minimums: dict, failures: list[str]) -> None:
    """One package: uniform course pins, installed in workflow, above minimum."""
    if len(versions) > 1:
        failures.append(
            f"workflow: course pins disagree on {package}: "
            f"{sorted(str(v) for v in versions)}"
        )
        return
    course_version = min(versions)
    if package not in workflow_versions:
        failures.append(
            f"workflow: course pins {package}=={course_version} "
            f"but the workflow does not install it"
        )
        return
    if workflow_versions[package] != course_version:
        failures.append(
            f"workflow: installs {package}=={workflow_versions[package]} "
            f"but the course pins {package}=={course_version}"
        )
    minimum = minimums.get(package)
    if minimum is not None and workflow_versions[package] < minimum:
        failures.append(
            f"workflow: installs {package}=={workflow_versions[package]} "
            f"below the documented minimum {package}>={minimum}"
        )


def check_workflow_sync(failures: list[str]) -> None:
    """The workflow must install exactly what the course pins.

    Otherwise the import gate validates against a different version than
    the docs teach: bumping a README pin without the workflow (or vice
    versa) passes one gate while the other checks stale code.
    """
    try:
        workflow_text = WORKFLOW_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        failures.append(f"workflow: expected workflow missing: {WORKFLOW_FILE.relative_to(ROOT)}")
        return
    workflow_versions = {}
    location = WORKFLOW_FILE.relative_to(ROOT).as_posix()
    for package, operator, pinned in _pin_specs(workflow_text):
        if operator == "==":
            parsed = _parse_version(pinned, location, failures)
            if parsed is not None:
                workflow_versions[package] = parsed
    course_versions, minimums = _collect_course_versions(failures)
    for package in sorted(course_versions):
        _check_package_sync(package, course_versions[package], workflow_versions,
                             minimums, failures)


def main() -> int:
    vocab_exceptions, import_allowlist = load_exceptions()
    failures: list[str] = []
    check_pins(failures)
    check_tags(failures)
    check_vocab(failures, vocab_exceptions)
    check_imports(failures, import_allowlist)
    check_workflow_sync(failures)
    if failures:
        print("COURSE DRIFT DETECTED — the course no longer matches the code:")
        for failure in failures:
            print(f"  - {failure}")
        print(f"\n{len(failures)} drift item(s). Fix the course or update "
              f"{EXCEPTIONS_FILE.relative_to(ROOT)} with a reason.")
        return 1
    print("drift check passed: pins, tags, vocabulary, and imports match the code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
