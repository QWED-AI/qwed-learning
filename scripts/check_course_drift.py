"""Course-vs-code drift check for qwed-learning (issue #19).

Fails loudly when the course text drifts from the implementations it teaches:

  1. Stale pins   — every ``pip install qwed...==/>=X.Y.Z`` pin in
     ``module-*/README.md`` and ``capstone-project/README.md`` must satisfy
     ``X.Y.Z <= <latest release on PyPI>``.
  2. Dead tags    — every ``QWED-AI/<repo>@vX.Y.Z`` reference must resolve
     to a real tag.
  3. Banned vocab — ``INVALID`` / ``APPROVED`` / ``QUARANTINED`` may appear in
     course markdown only on lines that also mention workflow/disposition.
  4. Dead imports — every ``from qwed... import <name>`` in fenced Python
     blocks must resolve against the installed packages.

Stdlib only. Run locally with ``python scripts/check_course_drift.py`` after
``pip install qwed qwed-a2a qwed-infra``; CI installs latest releases so new
API removals are caught. Documented exceptions live in
``scripts/course_drift_exceptions.json`` and are reviewed like code.
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

ROOT = Path(__file__).resolve().parent.parent
EXCEPTIONS_FILE = Path(__file__).resolve().parent / "course_drift_exceptions.json"

# qwed-a2a refuses to import without a deployment ID; the check needs imports
# to resolve, not a real deployment, so default it when unset.
os.environ.setdefault("QWED_A2A_DEPLOYMENT_ID", "course-drift-check")

PIN_SCOPE = sorted(ROOT.glob("module-*/README.md")) + [ROOT / "capstone-project" / "README.md"]
IMPORT_SCOPE = list(PIN_SCOPE)

EXCLUDE_DIRS = {".git", ".github", "node_modules", ".venv", "test_venv", "__pycache__"}

PIN_COMMAND_RE = re.compile(r"pip install\s+((?:\"[^\"]*\"|'[^']*'|\S+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\S+))*)")
PIN_SPEC_RE = re.compile(
    r"(qwed[a-z0-9_-]*)(?:\[[^\]]*\])?\s*(==|>=)\s*"
    r"([0-9][0-9A-Za-z.\-]*)"
)
TAG_RE = re.compile(r"(QWED-AI/[A-Za-z0-9_.\-]+)@(v\d+\.\d+\.\d+[^\s\"'`]*)")
VOCAB_RE = re.compile(r"\b(INVALID|APPROVED|QUARANTINED)\b")
VOCAB_CONTEXT_RE = re.compile(r"workflow|disposition", re.IGNORECASE)
FROM_IMPORT_RE = re.compile(r"from\s+(qwed[a-z0-9_.]*)\s+import\s+([^\n#]+)")
FENCE_RE = re.compile(r"```python(.*?)```", re.DOTALL)


# PEP 440 pre/post-release ranking so suffixed versions order sanely
# (dev < alpha < beta < rc < final < post) instead of crashing comparison.
_SUFFIX_ORDER = {"dev": 0, "a": 1, "alpha": 1, "b": 2, "beta": 2, "rc": 3, "post": 5}
_FINAL_RANK = 4


def _suffix_key(suffix: str) -> tuple:
    text = suffix.strip().lstrip("-_.")
    if not text:
        return (_FINAL_RANK,)
    match = re.match(r"([a-zA-Z]+)([0-9.]*)", text)
    if not match:
        return (_FINAL_RANK, text)
    word, nums = match.group(1).lower(), match.group(2)
    rank = _SUFFIX_ORDER.get(word, _FINAL_RANK)
    num_tuple = tuple(int(piece) for piece in nums.split(".") if piece.isdigit()) or (0,)
    return (rank, num_tuple, text)


def _version_key(version: str) -> tuple:
    """Crash-free comparable key for release version strings.

    Compares numeric release segments first, then PEP 440 suffix rank, so
    valid-but-unusual metadata can never raise TypeError inside the check.
    """
    match = re.match(r"^[vV]?([0-9]+(?:\.[0-9]+)*)(.*)$", version.strip())
    if not match:
        return ((), (_FINAL_RANK, version.strip()))
    numbers = tuple(int(piece) for piece in match.group(1).split("."))
    return (numbers, _suffix_key(match.group(2)))


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

    Scans the whole install command so later packages in multi-package
    installs (e.g. ``pip install qwed==7.2.0 qwed-a2a==0.3.0``) are checked
    too — matching only the first package would let a stale later pin pass.
    """
    specs = []
    for command in PIN_COMMAND_RE.finditer(text):
        for spec in PIN_SPEC_RE.finditer(command.group(1)):
            specs.append((spec.group(1), spec.group(2), spec.group(3)))
    return specs


def check_pins(failures: list[str]) -> None:
    for readme in PIN_SCOPE:
        if not readme.is_file():
            failures.append(f"pins: expected course file missing: {readme.relative_to(ROOT)}")
            continue
        text = readme.read_text(encoding="utf-8")
        for package, operator, pinned in _pin_specs(text):
            try:
                latest = _pypi_latest(package)
            except RuntimeError as exc:
                failures.append(f"pins: {exc}")
                continue
            # Exact pins must track the current release; minimum-version
            # (>=) pins must name a version that exists (i.e. <= latest).
            # An exact pin older than latest is stale course, not safety.
            if operator == "==":
                if _version_key(pinned) != _version_key(latest):
                    failures.append(
                        f"pins: {readme.relative_to(ROOT)} pins {package}=={pinned} "
                        f"but latest release is {latest}"
                    )
            elif _version_key(pinned) > _version_key(latest):
                failures.append(
                    f"pins: {readme.relative_to(ROOT)} requires {package}>={pinned} "
                    f"but latest release is {latest}"
                )


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
            repo, ref = match.group(1), match.group(2)
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
    ``from <module> import UnknownSymbol`` through unnoticed.
    """
    try:
        return importlib.import_module(module)
    except Exception:
        uncovered = [
            name for name in names
            if name != "*" and (rel, f"{module}.{name}") not in import_allowlist
        ]
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


def _from_import_targets(block: str) -> list[tuple[str, list[str]]]:
    """Yield (module, [names]) for course-relevant from-imports in a block.

    AST first; on SyntaxError fall back to regex extraction so one sketch
    error cannot smuggle drifted imports past the gate.
    """
    try:
        tree = ast.parse(block)
    except SyntaxError:
        return [
            (match.group(1), _split_import_names(match.group(2)))
            for match in FROM_IMPORT_RE.finditer(block)
            if match.group(1).startswith("qwed")
        ]
    targets = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        module = node.module or ""
        if module.startswith("qwed"):
            targets.append((module, [alias.name for alias in node.names]))
    return targets


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
    imports = {(entry["file"], entry["symbol"]) for entry in payload.get("imports", [])}
    return vocab, imports


def main() -> int:
    vocab_exceptions, import_allowlist = load_exceptions()
    failures: list[str] = []
    check_pins(failures)
    check_tags(failures)
    check_vocab(failures, vocab_exceptions)
    check_imports(failures, import_allowlist)
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
