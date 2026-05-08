"""
Claude Code SessionStart hook — injects the harness-index orientation skill
plus current-change state at session start, clear, and compact.

Reads the installed skill body from ``.claude/commands/harness-index.md``
(Claude install) or ``.agents/skills/harness-index/SKILL.md`` (Codex install).
Falls back to a one-line context if neither is present so the session never
hard-fails on missing files.

Output JSON shape:
    {"hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "<skill body>\\n\\n## Current State\\n\\n<state>"}}

Exit 0 always — SessionStart hooks cannot block the session, only inject context.
"""
import json
import os
import sys
from pathlib import Path

_DEFAULT_REPO_ROOT = Path(__file__).parent.parent.parent
_REPO_ROOT = (
    Path(os.environ["HARNESS_REPO_ROOT"])
    if "HARNESS_REPO_ROOT" in os.environ
    else _DEFAULT_REPO_ROOT
)

_DEFAULT_HARNESS_DIR = Path(__file__).parent.parent
_HARNESS_DIR = (
    Path(os.environ["HARNESS_HARNESS_DIR"])
    if "HARNESS_HARNESS_DIR" in os.environ
    else _DEFAULT_HARNESS_DIR
)

_DEFAULT_CHANGES_DIR = _REPO_ROOT / "doc" / "changes"
_CHANGES_DIR = (
    Path(os.environ["HARNESS_CHANGES_DIR"])
    if "HARNESS_CHANGES_DIR" in os.environ
    else _DEFAULT_CHANGES_DIR
)


def _read_skill_body() -> str:
    """Locate and read the harness-index skill body. Returns a fallback string
    if no installed copy is found."""
    candidates = [
        _REPO_ROOT / ".claude" / "commands" / "harness-index.md",
        _REPO_ROOT / ".agents" / "skills" / "harness-index" / "SKILL.md",
    ]
    for path in candidates:
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
    return (
        "Use `/harness-sdd-workflow` before any source-code edit. "
        "If `.harness/current-change` is set to an in-progress change, resume it."
    )


def _check_current_change() -> str:
    """One-line summary of `.harness/current-change` state."""
    marker_path = _HARNESS_DIR / "current-change"
    if not marker_path.exists():
        return (
            "No active change. Before writing source code, create "
            "`doc/changes/NNN-name/00-spec.md` and write its name to "
            "`.harness/current-change`."
        )

    change_name = marker_path.read_text().strip()
    if not change_name:
        return "Warning: `.harness/current-change` is empty. Declare the active change."

    spec_path = _CHANGES_DIR / change_name / "00-spec.md"
    if not spec_path.exists():
        return f"Warning: Change `{change_name}` declared but no spec at `{spec_path}`."

    for line in spec_path.read_text().splitlines():
        if line.strip().startswith("status:") and "in-progress" in line:
            return f"Active change: `{change_name}` (in-progress) — resume rather than open a new one."

    return f"Warning: Change `{change_name}` exists but is not in-progress."


def main() -> None:
    body = _read_skill_body()
    state = _check_current_change()

    additional_context = f"{body}\n\n## Current State\n\n{state}"

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context,
        },
    }

    json.dump(output, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
