"""
PreToolUse hook — blocks writing `status: done` to a change spec unless all
completion-gate conditions pass.

Gate conditions (delegated to _completion_checks):
  1. All acceptance criteria checkboxes are checked (`- [x]`)
  2. All task checkboxes in 02-tasks.md are checked (feature changes only)
  3. All checked specs in "Specs to Update" have changed since their snapshots
  4. Project test suite passes (lang-aware: Python/TypeScript/Java)
  5. Integration/E2E tests pass (if test files exist in conventional dirs)

Only fires when the target file matches doc/changes/*/00-spec.md AND the
incoming content contains `status: done`.

Claude Code sends tool input as JSON on stdin:
  Write → {"tool_name": "Write", "tool_input": {"file_path": "...", "content": "..."}}
  Edit  → {"tool_name": "Edit",  "tool_input": {"file_path": "...", "old_string": "...", "new_string": "..."}}

Exit 0 → allow.
Exit 2 → block with instructions.
"""
import sys
from pathlib import Path as _ToolsPath
sys.path.insert(0, str(_ToolsPath(__file__).parent))

import json
import os
import re
from pathlib import Path

from _completion_checks import (
    open_acs,
    open_tasks_in_tasks_file,
    run_declared_integration_tests,
    run_integration_tests,
    run_tests,
    stale_specs,
)

_DEFAULT_REPO_ROOT = Path(__file__).parent.parent.parent
_REPO_ROOT = (
    Path(os.environ["HARNESS_REPO_ROOT"])
    if "HARNESS_REPO_ROOT" in os.environ
    else _DEFAULT_REPO_ROOT
)
_SPEC_PATTERN = re.compile(r"doc/changes/[^/]+/00-spec\.md$")


def is_spec_file(file_path: str) -> bool:
    return bool(_SPEC_PATTERN.search(file_path.replace("\\", "/")))


def has_status_done(content: str) -> bool:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("status:") and "done" in stripped:
            return True
    return False


def final_content(tool_name: str, tool_input: dict) -> str:
    """Produce the text the file will contain after this tool call."""
    file_path = tool_input.get("file_path", "")

    if tool_name == "Write":
        return tool_input.get("content", "")

    if tool_name == "Edit":
        try:
            existing = Path(file_path).read_text(encoding="utf-8")
        except OSError:
            existing = ""
        old = tool_input.get("old_string", "")
        new = tool_input.get("new_string", "")
        return existing.replace(old, new, 1)

    return ""


def main() -> None:
    raw = sys.stdin.read().strip()
    if not raw:
        sys.exit(0)

    try:
        data = json.loads(raw)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
    except (json.JSONDecodeError, KeyError):
        sys.exit(0)

    if not is_spec_file(file_path):
        sys.exit(0)

    content = final_content(tool_name, tool_input)

    if not has_status_done(content):
        sys.exit(0)

    # Gate 1: all ACs must be checked
    unchecked_acs = open_acs(content)
    if unchecked_acs:
        items = "\n".join(f"  {ac}" for ac in unchecked_acs)
        print(
            f"\n[COMPLETION GATE] Cannot mark done — {len(unchecked_acs)} AC(s) still open:\n"
            f"{items}\n"
            f"\nCheck off all acceptance criteria before setting status: done.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # Gate 2: all tasks in 02-tasks.md must be checked (feature changes only)
    unchecked_tasks = open_tasks_in_tasks_file(file_path)
    if unchecked_tasks:
        items = "\n".join(f"  {t}" for t in unchecked_tasks)
        print(
            f"\n[COMPLETION GATE] Cannot mark done — {len(unchecked_tasks)} task(s) still open in 02-tasks.md:\n"
            f"{items}\n"
            f"\nCheck off all tasks before setting status: done.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # Gate 3: all checked specs in "Specs to Update" must have changed since snapshot
    unchanged = stale_specs(file_path, content, _REPO_ROOT)
    if unchanged:
        items = "\n".join(f"  {p}" for p in unchanged)
        print(
            f"\n[COMPLETION GATE] Cannot mark done — {len(unchanged)} spec(s) listed in "
            f"'Specs to Update' appear unchanged since in-progress snapshot:\n"
            f"{items}\n"
            f"\nUpdate each listed spec to reflect the changes introduced before setting status: done.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # Gate 4: tests must pass (lang-aware)
    failures = run_tests(_REPO_ROOT)
    if failures:
        print(
            f"\n[COMPLETION GATE] Cannot mark done — tests failed:\n\n"
            f"{failures[0]}\n"
            f"\nFix all test failures before setting status: done.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # Gate 5: integration/e2e tests must pass (if test files exist)
    e2e_failures = run_integration_tests(_REPO_ROOT)
    if e2e_failures:
        items = "\n".join(f"  {f}" for f in e2e_failures)
        print(
            f"\n[COMPLETION GATE] Cannot mark done — integration/e2e tests failed:\n"
            f"{items}\n"
            f"\nFix all integration/e2e test failures before setting status: done.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # Gate 6: spec-declared integration boundary tests must pass
    change_dir = Path(file_path).parent
    boundary_failures = run_declared_integration_tests(change_dir, _REPO_ROOT)
    if boundary_failures:
        items = "\n".join(f"  {f}" for f in boundary_failures)
        print(
            f"\n[COMPLETION GATE] Cannot mark done — declared integration boundary tests failed:\n"
            f"{items}\n"
            f"\nFix all integration boundary test failures before setting status: done.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # All gates passed — regenerate spec index so it's fresh for next session
    try:
        from generate_spec_index import main as gen_index
        gen_index(_REPO_ROOT)
    except Exception:
        pass  # Non-critical — index can be regenerated manually

    sys.exit(0)


if __name__ == "__main__":
    main()
