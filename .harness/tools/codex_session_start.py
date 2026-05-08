"""
Codex SessionStart hook — injects SDD workflow context at session start.

This hook runs when a Codex CLI session begins (startup or resume). It outputs
JSON with ``additionalContext`` containing the SDD workflow summary so the agent
always has the harness engineering protocol in context.

Unlike Claude Code's PreToolUse hooks, Codex SessionStart cannot block operations.
It only provides context. Enforcement relies on the agent following the injected
instructions plus the AGENTS.md guidance.

Codex runs this via .codex/hooks.json SessionStart entry.
Exit 0  with JSON → context injected.
Exit 0  with no output → no-op.
"""
import json
import os
import re
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


def _check_current_change() -> str:
    """Build a status message about the current change state."""
    marker_path = _HARNESS_DIR / "current-change"
    if not marker_path.exists():
        return (
            "No active change declared. Before writing any source code:\n"
            "  1. Find next change number: ls doc/changes/ | sort -V | tail -1\n"
            "  2. Create doc/changes/NNN-name/00-spec.md from template\n"
            "  3. Set status: in-progress\n"
            "  4. echo 'NNN-name' > .harness/current-change"
        )

    change_name = marker_path.read_text().strip()
    if not change_name:
        return "Warning: .harness/current-change is empty. Declare the active change name."

    spec_path = _CHANGES_DIR / change_name / "00-spec.md"
    if not spec_path.exists():
        return f"Warning: Change '{change_name}' declared but no spec found at {spec_path}."

    # Check status
    for line in spec_path.read_text().splitlines():
        if line.strip().startswith("status:") and "in-progress" in line:
            return f"Active change: {change_name} (in-progress)"

    return f"Warning: Change '{change_name}' exists but is not in-progress."


def main() -> None:
    context_parts = [
        "## Harness SDD Workflow (auto-injected at session start)",
        "",
        "This project uses spec-driven development. You MUST follow this protocol:",
        "",
        "1. **Read specs first** — check doc/spec/product/ and doc/spec/tech/ for the area you're changing",
        "2. **Create a change spec BEFORE writing source code** — doc/changes/NNN-name/00-spec.md",
        "3. **Declare the active change** — echo 'NNN-name' > .harness/current-change",
        "4. **Implement against acceptance criteria** — check off ACs as you complete them",
        "5. **Run completion gate** — python .harness/tools/verify_completion.py --change NNN",
        "",
        "Use `$harness-sdd-workflow` for full protocol details.",
        "",
        f"Current state: {_check_current_change()}",
    ]

    output = {
        "hookSpecificOutput": {
            "additionalContext": "\n".join(context_parts),
        },
    }

    json.dump(output, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
