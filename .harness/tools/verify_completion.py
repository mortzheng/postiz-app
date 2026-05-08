#!/usr/bin/env python3
"""Verify all completion-gate conditions for a change before transitioning to `done`.

Usage:
    python verify_completion.py --change NNN [--root /path/to/project]

Exit codes:
    0 — all checks passed
    1 — one or more gate conditions failed (list printed to stdout)
    2 — usage error or change directory not found

Called by the agent before setting any change status to `done`.
Test execution is lang-aware: reads lang from .harness/harness.toml and
dispatches to pytest (Python), vitest/jest (TypeScript), or mvnw/gradlew (Java).
"""
import sys
from pathlib import Path as _ToolsPath
sys.path.insert(0, str(_ToolsPath(__file__).parent))

from pathlib import Path

from _completion_checks import (
    open_acs,
    open_checkboxes,
    open_tasks_in_tasks_file,
    parse_checked_specs_to_update,
    run_declared_integration_tests,
    run_integration_tests,
    run_tests,
)


def find_change_dir(change_num: int, root: Path) -> Path | None:
    """Return the `changes/NNN-*` directory for *change_num*, or None if not found."""
    changes_root = root / "doc" / "changes"
    if not changes_root.exists():
        return None
    matches = sorted(changes_root.glob(f"{change_num:03d}-*"))
    return matches[0] if matches else None


def check_open_acs(change_dir: Path) -> list[str]:
    spec_path = change_dir / "00-spec.md"
    if not spec_path.exists():
        return [f"00-spec.md not found in {change_dir}"]
    text = spec_path.read_text(encoding="utf-8")
    return [f"[open AC] {line}" for line in open_acs(text)]


def check_open_tasks(change_dir: Path) -> list[str]:
    tasks_path = change_dir / "02-tasks.md"
    if not tasks_path.exists():
        return []
    return [f"[open task] {line}" for line in open_checkboxes(tasks_path.read_text(encoding="utf-8"))]


def check_unconfirmed_specs(change_dir: Path) -> list[str]:
    spec_path = change_dir / "00-spec.md"
    if not spec_path.exists():
        return []
    text = spec_path.read_text(encoding="utf-8")
    # Unconfirmed = unchecked entries in "Specs to Update"
    import re
    in_section = False
    failures: list[str] = []
    for line in text.splitlines():
        if re.match(r"^##\s+Specs to Update", line):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            break
        if in_section:
            stripped = line.strip()
            if re.match(r"^-\s+\[\s\]", stripped):
                failures.append(f"[unconfirmed spec] {stripped}")
    return failures


def run(change_num: int, root: Path) -> tuple[int, str]:
    """Run all completion-gate checks. Returns (exit_code, output_text)."""
    change_dir = find_change_dir(change_num, root)
    if change_dir is None:
        return 2, f"Error: no doc/changes/{change_num:03d}-* directory found under {root}"

    failures: list[str] = []
    failures.extend(check_open_acs(change_dir))
    failures.extend(check_open_tasks(change_dir))
    failures.extend(check_unconfirmed_specs(change_dir))
    failures.extend(run_tests(root))
    failures.extend(run_integration_tests(root))
    failures.extend(run_declared_integration_tests(change_dir, root))

    if failures:
        lines = [f"Completion gate FAILED for change {change_num:03d}:", ""]
        lines.extend(f"  {f}" for f in failures)
        return 1, "\n".join(lines)

    # All gates passed — regenerate spec index so it's fresh for next session
    _regenerate_spec_index(root)

    return 0, f"All checks passed for change {change_num:03d}. Ready to transition to done."


def _regenerate_spec_index(root: Path) -> None:
    """Regenerate the CLAUDE.md spec index (best-effort, never fails the gate)."""
    try:
        from generate_spec_index import main as gen_index
        gen_index(root)
    except Exception:
        pass  # Non-critical — index can be regenerated manually


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify all completion-gate conditions before transitioning a change to done."
    )
    parser.add_argument("--change", type=int, required=True, help="Change number (e.g. 47)")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root (default: current working directory)",
    )
    args = parser.parse_args()

    exit_code, output = run(args.change, args.root)
    print(output)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
