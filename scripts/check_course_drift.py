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
import subprocess
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

PIN_RE = re.compile(
    r"pip install\s+[\"']?(qwed[a-z0-9_-]*)(?:\[[^\]]*\])?\s*(==|>=)\s*"
    r"([0-9][0-9A-Za-z.\-]*)\s*[\"']?"
)
TAG_RE = re.compile(r"(QWED-AI/[A-Za-z0-9_.\-]+)@(v\d+\.\d+\.\d+[^ \s\"'`]*)")
VOCAB_RE = re.compile(r"\b(INVALID|APPROVED|QUARANTINED)\b")
VOCAB_CONTEXT_RE = re.compile(r"workflow|disposition", re.IGNORECASE)
FROM_IMPORT_RE = re.compile(r"from\s+(qwed[a-z0-9_.]*)\s+import\s+([^\n#]+)")
FENCE_RE = re.compile(r"```python(.*?)```", re.DOTALL)


def _version_tuple(version: str) -> tuple:
    parts = []
    for piece in re.split(r"[.\-]", version):
        parts.append(int(piece) if piece.isdigit() else piece)
    return tuple(parts)


def _pypi_latest(package: str) -> str:
    url = f"https://pypi.org/pypi/{package}/json"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.load(response)
    except Exception as exc:
        raise RuntimeError(f"could not fetch PyPI metadata for {package}: {exc}") from exc
    return str(payload["info"]["version"])


def check_pins(failures: list[str]) -> None:
    for readme in PIN_SCOPE:
        if not readme.is_file():
            failures.append(f"pins: expected course file missing: {readme.relative_to(ROOT)}")
            continue
        text = readme.read_text(encoding="utf-8")
        for match in PIN_RE.finditer(text):
            package, operator, pinned = match.group(1), match.group(2), match.group(3)
            _ = operator  # == and >= both assert "course tracks a released version"
            try:
                latest = _pypi_latest(package)
            except RuntimeError as exc:
                failures.append(f"pins: {exc}")
                continue
            if _version_tuple(pinned) > _version_tuple(latest):
                failures.append(
                    f"pins: {readme.relative_to(ROOT)} pins {package}=={pinned} "
                    f"but latest release is {latest}"
                )


def check_tags(failures: list[str]) -> None:
    for readme in PIN_SCOPE:
        if not readme.is_file():
            continue
        text = readme.read_text(encoding="utf-8")
        for match in TAG_RE.finditer(text):
            repo, ref = match.group(1), match.group(2)
            url = f"https://github.com/{repo}.git"
            try:
                completed = subprocess.run(
                    ["git", "ls-remote", "--tags", url, ref],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=False,
                )
            except Exception as exc:
                failures.append(f"tags: could not list tags for {repo}: {exc}")
                continue
            if completed.returncode != 0 or ref not in completed.stdout:
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


def check_vocab(failures: list[str], vocab_exceptions: set[tuple[str, str]]) -> None:
    for path in _iter_markdown():
        rel = path.relative_to(ROOT).as_posix()
        for line in path.read_text(encoding="utf-8").splitlines():
            for token in VOCAB_RE.findall(line):
                if (rel, token) in vocab_exceptions:
                    continue
                if not VOCAB_CONTEXT_RE.search(line):
                    failures.append(
                        f"vocab: {rel} uses banned term {token!r} without "
                        f"workflow/disposition context: {line.strip()[:120]}"
                    )


def _fenced_blocks(text: str) -> list[str]:
    return FENCE_RE.findall(text)


def check_imports(failures: list[str], import_allowlist: set[tuple[str, str]]) -> None:
    for readme in IMPORT_SCOPE:
        if not readme.is_file():
            continue
        rel = readme.relative_to(ROOT).as_posix()
        text = readme.read_text(encoding="utf-8")
        for block in _fenced_blocks(text):
            try:
                tree = ast.parse(block)
            except SyntaxError:
                continue  # illustrative sketches, not runnable blocks
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom):
                    continue
                module = node.module or ""
                if not module.startswith("qwed"):
                    continue
                # The module itself must be importable ...
                try:
                    imported = importlib.import_module(module)
                except Exception:
                    if (rel, module) not in import_allowlist:
                        failures.append(
                            f"imports: {rel} imports from unresolvable module {module!r}"
                        )
                    continue
                # ... and so must every imported name.
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    if (rel, f"{module}.{alias.name}") in import_allowlist:
                        continue
                    if not hasattr(imported, alias.name):
                        failures.append(
                            f"imports: {rel} imports {alias.name!r} from {module!r} "
                            f"but the installed package has no such symbol"
                        )


def load_exceptions() -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    try:
        payload = json.loads(EXCEPTIONS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return set(), set()
    vocab = {(entry["file"], entry["token"]) for entry in payload.get("vocabulary", [])}
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
