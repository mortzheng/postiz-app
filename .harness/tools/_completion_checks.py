"""
Shared completion-gate logic used by check_completion.py (hook) and
verify_completion.py (CLI).

Not a user-facing tool — prefixed _ to signal it is an internal helper.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path


# ---------------------------------------------------------------------------
# Lang / test-command helpers
# ---------------------------------------------------------------------------

def read_langs(root: Path) -> list[str]:
    """Read langs from .harness/harness.toml, or [] if absent/unreadable.

    Supports both new ``langs = [...]`` and legacy ``lang = "..."`` formats.
    """
    toml_path = root / ".harness" / "harness.toml"
    if not toml_path.exists():
        return []
    content = toml_path.read_text(encoding="utf-8")
    # New format: langs = ["python", "typescript"]
    langs_match = re.search(r'langs\s*=\s*\[([^\]]*)\]', content)
    if langs_match:
        raw = langs_match.group(1)
        return [m.group(1) for m in re.finditer(r'"([^"]+)"', raw)]
    # Legacy format: lang = "python"
    m = re.search(r'lang\s*=\s*"([^"]+)"', content)
    return [m.group(1)] if m else []


def read_lang(root: Path) -> str | None:
    """Read primary lang from .harness/harness.toml, or None if absent."""
    langs = read_langs(root)
    return langs[0] if langs else None


def test_command_for_lang(lang: str | None, root: Path) -> list[str] | None:
    """Return the test command list for *lang*, or None if no runner is found.

    None means "skip tests" — not a failure.

    python     → ["uv", "run", "pytest"]
    typescript → ["npx", "vitest", "run", "--passWithNoTests"]  if vitest.config.* exists
                 ["npx", "jest", "--passWithNoTests"]            elif jest.config.* exists
                 None                                            otherwise
    java       → ["./mvnw", "test", "-q"]  if pom.xml exists
                 ["./gradlew", "test"]      elif build.gradle* exists
                 None                       otherwise
    """
    if lang is None or lang == "python":
        return ["uv", "run", "pytest"]

    if lang == "typescript":
        if list(root.glob("vitest.config.*")):
            return ["npx", "vitest", "run", "--passWithNoTests"]
        if list(root.glob("jest.config.*")):
            return ["npx", "jest", "--passWithNoTests"]
        return None

    if lang == "java":
        if (root / "pom.xml").exists():
            return ["./mvnw", "test", "-q"]
        if list(root.glob("build.gradle*")):
            return ["./gradlew", "test"]
        return None

    # Unknown lang — fall back to pytest (safe default for harness-scaffold itself)
    return ["uv", "run", "pytest"]


def run_tests(root: Path) -> list[str]:
    """Run the project's test suite(s) and return a failure list.

    For multi-lang projects, runs test commands for each configured language.
    Returns [] on pass or when no test runner is configured (skip).
    Returns a list with error summaries on failure.

    Allowed exit codes: 0 (pass), 5 (pytest: no tests collected).
    """
    langs = read_langs(root)
    if not langs:
        # Fall back to single-lang behaviour
        langs = [None]  # type: ignore[list-item]

    failures: list[str] = []
    for lang in langs:
        cmd = test_command_for_lang(lang, root)
        if cmd is None:
            continue  # No test runner configured for this lang — skip

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        if result.returncode not in (0, 5):
            lines = (result.stdout + result.stderr).strip().splitlines()
            summary = lines[-1] if lines else "(no output)"
            lang_label = lang or "default"
            failures.append(f"[tests failed ({lang_label})] exit={result.returncode}: {summary}")

    return failures


# ---------------------------------------------------------------------------
# Integration / E2E test support
# ---------------------------------------------------------------------------

# Per-language conventional directories for integration/e2e tests
_E2E_TEST_DIRS: dict[str, list[str]] = {
    "python": ["tests/integration", "tests/e2e"],
    "typescript": ["tests/integration", "tests/e2e", "e2e"],
    "java": ["src/test/java/**/integration", "src/test/java/**/e2e"],
    "react-native": ["e2e"],
    "kotlin": ["src/test/java/**/integration", "src/test/java/**/e2e"],
}

# Per-language test file glob patterns
_E2E_TEST_PATTERNS: dict[str, list[str]] = {
    "python": ["test_*.py", "*_test.py"],
    "typescript": ["*.test.ts", "*.test.tsx", "*.spec.ts", "*.spec.tsx"],
    "java": ["*Test.java", "*IT.java"],
    "react-native": ["*.test.ts", "*.test.tsx", "*.spec.ts", "*.spec.tsx"],
    "kotlin": ["*Test.java", "*Test.kt", "*IT.java", "*IT.kt"],
}

# E2E runner config files — checked in priority order
_E2E_CONFIG_FILES = [
    ("playwright.config.ts", ["npx", "playwright", "test"]),
    ("playwright.config.js", ["npx", "playwright", "test"]),
    ("cypress.config.ts", ["npx", "cypress", "run"]),
    ("cypress.config.js", ["npx", "cypress", "run"]),
    (".detoxrc.js", ["npx", "detox", "test"]),
]


def e2e_test_dirs_for_lang(lang: str) -> list[str]:
    """Return conventional integration/e2e test directory patterns for *lang*."""
    return list(_E2E_TEST_DIRS.get(lang, []))


def has_e2e_test_files(directory: Path, lang: str) -> bool:
    """Return True if *directory* contains test files matching *lang*'s patterns.

    Returns False if directory doesn't exist or contains no matching files.
    """
    if not directory.exists() or not directory.is_dir():
        return False
    patterns = _E2E_TEST_PATTERNS.get(lang, _E2E_TEST_PATTERNS.get("python", []))
    for pattern in patterns:
        if list(directory.rglob(pattern)):
            return True
    return False


def e2e_test_command(root: Path, lang: str) -> list[str] | str | None:
    """Detect the e2e test runner command from config files.

    Returns the command list, the string "pytest" for Python fallback,
    or None if no e2e runner is configured.
    """
    # Check for config-file-based runners
    for config_file, cmd in _E2E_CONFIG_FILES:
        if (root / config_file).exists():
            return cmd

    # Check for detox in package.json
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            pkg_text = pkg_json.read_text(encoding="utf-8").lower()
            if '"detox"' in pkg_text:
                return ["npx", "detox", "test"]
        except OSError:
            pass

    # Python fallback: pytest with e2e dirs
    if lang in ("python",):
        return "pytest"

    return None


def _resolve_e2e_dirs(root: Path, lang: str) -> list[Path]:
    """Resolve e2e test dir patterns to actual directories that exist."""
    dirs: list[Path] = []
    for pattern in e2e_test_dirs_for_lang(lang):
        if "**" in pattern:
            # Glob pattern — find matching dirs
            for d in root.glob(pattern):
                if d.is_dir():
                    dirs.append(d)
        else:
            candidate = root / pattern
            if candidate.exists() and candidate.is_dir():
                dirs.append(candidate)
    return dirs


def run_integration_tests(root: Path) -> list[str]:
    """Run integration/e2e tests if test files exist in conventional dirs.

    Returns [] if:
      - No integration/e2e test dirs exist
      - Dirs exist but contain no test files
      - Tests pass

    Returns failure list if tests exist and fail.
    """
    langs = read_langs(root)
    if not langs:
        return []

    # Collect all e2e dirs with test files across all langs
    test_dirs_with_files: list[tuple[str, list[Path]]] = []
    for lang in langs:
        resolved = _resolve_e2e_dirs(root, lang)
        dirs_with_tests = [d for d in resolved if has_e2e_test_files(d, lang)]
        if dirs_with_tests:
            test_dirs_with_files.append((lang, dirs_with_tests))

    if not test_dirs_with_files:
        return []

    failures: list[str] = []

    for lang, dirs in test_dirs_with_files:
        cmd = e2e_test_command(root, lang)
        if cmd is None:
            continue

        if cmd == "pytest":
            # Python: run pytest on the specific dirs
            dir_args = [str(d.relative_to(root)) for d in dirs]
            full_cmd = ["uv", "run", "pytest"] + dir_args
        else:
            full_cmd = list(cmd)

        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        if result.returncode not in (0, 5):
            lines = (result.stdout + result.stderr).strip().splitlines()
            summary = lines[-1] if lines else "(no output)"
            failures.append(
                f"[integration/e2e tests failed ({lang})] exit={result.returncode}: {summary}"
            )

    return failures


# ---------------------------------------------------------------------------
# Checkbox / spec parsing
# ---------------------------------------------------------------------------

def _parse_sections(text: str) -> dict[str, str]:
    """Split a markdown document into {section_heading: section_body} pairs."""
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        heading_match = re.match(r"^#{1,6}\s+(.+)", line)
        if heading_match:
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines)
            current_heading = heading_match.group(1).strip()
            current_lines = []
        else:
            if current_heading is not None:
                current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines)

    return sections


def open_checkboxes(content: str) -> list[str]:
    """Return all unchecked checkbox lines in *content*."""
    return [
        line.strip()
        for line in content.splitlines()
        if re.match(r"^-\s+\[\s\]", line.strip())
    ]


def open_acs(spec_content: str) -> list[str]:
    """Return unchecked AC lines from the Acceptance Criteria section only."""
    sections = _parse_sections(spec_content)
    ac_text = sections.get("Acceptance Criteria", "")
    return [
        line.strip()
        for line in ac_text.splitlines()
        if re.match(r"^-\s+\[\s\]", line.strip())
    ]


def open_tasks_in_tasks_file(spec_file_path: str) -> list[str]:
    """Return open task checkboxes from 02-tasks.md, or [] if absent."""
    tasks_file = Path(spec_file_path).parent / "02-tasks.md"
    if not tasks_file.exists():
        return []
    return open_checkboxes(tasks_file.read_text(encoding="utf-8"))


def parse_checked_specs_to_update(content: str) -> list[str]:
    """Return spec file paths that are checked off in 'Specs to Update'."""
    in_section = False
    paths: list[str] = []

    for line in content.splitlines():
        if re.match(r"^##\s+Specs to Update", line):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            break
        if in_section:
            m = re.search(r"-\s+\[x\]\s+`([^`]+)`", line)
            if m:
                paths.append(m.group(1))

    return paths


def hash_file(path: Path) -> str:
    """Return SHA-256 hex digest of file, or 'missing' if absent."""
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "missing"


def stale_specs(spec_file_path: str, content: str, root: Path) -> list[str]:
    """Return spec paths that are checked in 'Specs to Update' but have no
    uncommitted changes relative to git HEAD.

    Uses ``git diff`` instead of hash snapshots — immune to hook timing races.
    Returns [] gracefully when git is unavailable or the project is not a repo.
    """
    checked = parse_checked_specs_to_update(content)
    if not checked:
        return []

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--"] + checked,
            capture_output=True,
            text=True,
            cwd=str(root),
        )
    except FileNotFoundError:
        # git not installed
        return []

    if result.returncode != 0:
        # Not a git repo or other git error — degrade gracefully
        return []

    changed_files = set(result.stdout.strip().splitlines())
    return [rel for rel in checked if rel not in changed_files]


# ---------------------------------------------------------------------------
# Spec-driven integration boundaries (Change 053)
# ---------------------------------------------------------------------------

# Patterns that indicate an environment failure (not a test logic failure)
_ENV_FAILURE_PATTERNS = [
    r"ConnectionRefusedError",
    r"ECONNREFUSED",
    r"Connection refused",
    r"TimeoutError",
    r"ETIMEDOUT",
    r"command not found",
    r"ENOTFOUND",
    r"getaddrinfo",
]


def parse_integration_boundaries(spec_text: str) -> list[tuple[str, str, str]]:
    """Parse the ``## Integration Boundaries`` markdown table from a spec.

    Returns a list of (boundary, test_suite, status) tuples.
    Returns [] if the section doesn't exist, the table is empty, or rows
    contain only HTML comment placeholders.
    """
    sections = _parse_sections(spec_text)
    ib_text = sections.get("Integration Boundaries", "")
    if not ib_text:
        return []

    rows: list[tuple[str, str, str]] = []
    header_seen = False
    separator_seen = False

    for line in ib_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 3:
            continue

        # Skip header row
        if not header_seen:
            header_seen = True
            continue
        # Skip separator row (|---|---|---|)
        if not separator_seen and all(re.match(r"^-+$", c) for c in cells):
            separator_seen = True
            continue

        boundary, test_suite, status = cells[0], cells[1], cells[2]

        # Skip HTML comment placeholder rows
        if "<!--" in boundary:
            continue

        rows.append((boundary, test_suite, status))

    return rows


def classify_env_failure(output: str) -> bool:
    """Return True if *output* indicates an environment failure (not test logic).

    Matches common infrastructure error patterns like connection refused,
    timeout, DNS resolution failure, missing commands. Defaults to False
    (fail-safe: treat ambiguous failures as test failures).
    """
    for pattern in _ENV_FAILURE_PATTERNS:
        if re.search(pattern, output):
            return True
    return False


def _update_spec_env_failure(spec_path: Path, test_suite: str, boundary: str) -> None:
    """Update spec file: mark boundary as skipped (env) and append Completion Notes."""
    content = spec_path.read_text(encoding="utf-8")

    # Update the status in the Integration Boundaries table row
    # Match the row containing this test suite and replace "exists" with "skipped (env)"
    lines = content.splitlines()
    updated_lines = []
    for line in lines:
        if test_suite in line and "| exists |" in line:
            line = line.replace("| exists |", "| skipped (env) |")
        updated_lines.append(line)
    content = "\n".join(updated_lines)
    # Preserve trailing newline if original had one
    if not content.endswith("\n"):
        content += "\n"

    # Append to or create Completion Notes section
    suite_basename = Path(test_suite).name
    warning = f"- Skipped integration suite `{suite_basename}` ({boundary}): environment unavailable. Human review required before merge."

    if "## Completion Notes" in content:
        # Append to existing section
        content = content.rstrip("\n") + "\n" + warning + "\n"
    else:
        # Create the section at the end
        content = content.rstrip("\n") + "\n\n## Completion Notes\n\n" + warning + "\n"

    spec_path.write_text(content, encoding="utf-8")


def run_declared_integration_tests(change_dir: Path, root: Path) -> list[str]:
    """Run integration test suites declared in the spec's Integration Boundaries.

    Reads 00-spec.md from *change_dir*, parses the Integration Boundaries
    table, and for each boundary with status ``exists``:
      - Runs the test suite
      - If it passes: continues
      - If it fails with an env failure: updates spec to ``skipped (env)``,
        appends a Completion Notes warning, continues
      - If it fails with test logic: adds to failures list

    Returns [] when spec has no boundaries, all are absent/skipped, or all pass.
    Returns a failure list for test-logic failures (blocks completion).
    """
    spec_path = change_dir / "00-spec.md"
    if not spec_path.exists():
        return []

    spec_text = spec_path.read_text(encoding="utf-8")
    boundaries = parse_integration_boundaries(spec_text)
    if not boundaries:
        return []

    failures: list[str] = []

    for boundary, test_suite, status in boundaries:
        if status != "exists":
            continue

        # Resolve test suite path relative to project root
        suite_path = root / test_suite
        if not suite_path.exists():
            # Declared as exists but file not found — treat as failure
            failures.append(
                f"[integration boundary: {boundary}] test suite not found: {test_suite}"
            )
            continue

        # Run the test suite
        result = subprocess.run(
            ["uv", "run", "pytest", str(suite_path)],
            capture_output=True,
            text=True,
            cwd=str(root),
        )

        if result.returncode in (0, 5):
            continue  # Pass or no tests collected

        combined_output = result.stdout + result.stderr

        if classify_env_failure(combined_output):
            # Environment failure — update spec and continue
            _update_spec_env_failure(spec_path, test_suite, boundary)
        else:
            # Test logic failure — block completion
            out_lines = combined_output.strip().splitlines()
            summary = out_lines[-1] if out_lines else "(no output)"
            failures.append(
                f"[integration boundary: {boundary}] {test_suite} failed: {summary}"
            )

    return failures
