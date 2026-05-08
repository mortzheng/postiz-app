"""
PreToolUse hook — blocks Edit/Write unless the declared current change is in-progress.

Reads `.harness/current-change` for the declared change name and verifies that
the corresponding spec has `status: in-progress`. The marker file is required —
without it, all edits are blocked.

Exempts writes to doc/changes/ and .harness/current-change paths — those are
bootstrapping writes that must succeed before the gate can be satisfied.

Claude Code runs this before every Edit or Write tool call.
Exit 0  → allow the tool call through.
Exit 2  → block the tool call and surface the stderr message to the user.

Usage (registered in .claude/settings.json):
    python3 .harness/tools/check_active_spec.py
"""
import json
import os
import re
import sys
from pathlib import Path

_DEFAULT_CHANGES_DIR = Path(__file__).parent.parent.parent / "doc" / "changes"
_CHANGES_DIR = (
    Path(os.environ["HARNESS_CHANGES_DIR"])
    if "HARNESS_CHANGES_DIR" in os.environ
    else _DEFAULT_CHANGES_DIR
)

_DEFAULT_HARNESS_DIR = Path(__file__).parent.parent
_HARNESS_DIR = (
    Path(os.environ["HARNESS_HARNESS_DIR"])
    if "HARNESS_HARNESS_DIR" in os.environ
    else _DEFAULT_HARNESS_DIR
)

_DEFAULT_REPO_ROOT = Path(__file__).parent.parent.parent
_REPO_ROOT = (
    Path(os.environ["HARNESS_REPO_ROOT"])
    if "HARNESS_REPO_ROOT" in os.environ
    else _DEFAULT_REPO_ROOT
)

_CHANGES_PATH_PATTERN = re.compile(r"doc/changes/")
_CURRENT_CHANGE_PATH_PATTERN = re.compile(r"\.harness/current-change")


def is_exempt_path(file_path: str) -> bool:
    """Return True if the file path is exempt from the gate check."""
    normalized = file_path.replace("\\", "/")
    return bool(
        _CHANGES_PATH_PATTERN.search(normalized)
        or _CURRENT_CHANGE_PATH_PATTERN.search(normalized)
    )


def _spec_is_in_progress(spec_path: Path) -> bool:
    """Return True if the spec file exists and has status: in-progress."""
    if not spec_path.exists():
        return False
    for line in spec_path.read_text().splitlines():
        if line.strip().startswith("status:") and "in-progress" in line:
            return True
    return False


def check_declared_change() -> tuple[bool, str]:
    """Check the declared current-change marker.

    Returns (passed, message):
      - (True, "") if the declared change is in-progress
      - (False, reason) if the marker is missing, empty, or the change is invalid
    """
    marker_path = _HARNESS_DIR / "current-change"
    if not marker_path.exists():
        return False, (
            "[SDD GATE] No .harness/current-change marker found.\n"
            "\nBefore editing any file, declare which change you are working on:\n"
            "  1. ls doc/changes/ | sort -V | tail -1   # find next NNN\n"
            "  2. mkdir doc/changes/NNN-name\n"
            "  3. Create doc/changes/NNN-name/00-spec.md with status: in-progress\n"
            "  4. echo 'NNN-name' > .harness/current-change\n"
            "\nSee CLAUDE.md § Spec-Driven Workflow for full instructions.\n"
        )

    change_name = marker_path.read_text().strip()
    if not change_name:
        return False, (
            "[SDD GATE] .harness/current-change is empty.\n"
            "\nWrite the change name to the marker file:\n"
            "  echo 'NNN-name' > .harness/current-change\n"
        )

    spec_path = _CHANGES_DIR / change_name / "00-spec.md"
    if not spec_path.exists():
        return False, (
            f"[SDD GATE] Declared change '{change_name}' not found.\n"
            f"\nExpected: {_CHANGES_DIR / change_name}/00-spec.md\n"
            f"\nEither create the spec or update .harness/current-change.\n"
        )

    if _spec_is_in_progress(spec_path):
        return True, ""

    return False, (
        f"[SDD GATE] Declared change '{change_name}' is not in-progress.\n"
        f"\nThe spec at {spec_path} does not have status: in-progress.\n"
        f"Transition it to in-progress or update .harness/current-change.\n"
    )


def _is_multi_agent_enabled() -> bool:
    """Check if multi-agent mode is enabled in harness.toml."""
    toml_path = _HARNESS_DIR / "harness.toml"
    if not toml_path.exists():
        return False
    try:
        content = toml_path.read_text(encoding="utf-8")
        # Simple TOML parsing — look for multi_agent = "true"
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("multi_agent") and "=" in stripped:
                value = stripped.split("=", 1)[1].strip().strip('"').strip("'")
                return value.lower() == "true"
    except OSError:
        pass
    return False


def _get_current_role() -> str | None:
    """Read the current role from `.harness/current-role`."""
    marker_path = _HARNESS_DIR / "current-role"
    if not marker_path.exists():
        return None
    role = marker_path.read_text().strip().lower()
    return role if role else None


def check_sprint_contract() -> tuple[bool, str]:
    """Check that a sprint contract exists (multi-agent builder only).

    Returns (passed, message):
      - (True, "") if check passes or is not applicable
      - (False, reason) if builder has no sprint contract
    """
    if not _is_multi_agent_enabled():
        return True, ""

    role = _get_current_role()
    if role != "builder":
        return True, ""

    contract_path = _REPO_ROOT / "doc" / "multi-agent" / "sprint-contract.md"
    if contract_path.exists():
        return True, ""

    return False, (
        "[SDD GATE] No sprint contract found.\n"
        "\nIn multi-agent mode, the Builder cannot write source code without a sprint contract.\n"
        "The Planner must create doc/multi-agent/sprint-contract.md first.\n"
    )


def main() -> None:
    # Read file_path from stdin payload (same JSON format as other hooks)
    raw = sys.stdin.read().strip()
    if raw:
        try:
            data = json.loads(raw)
            file_path = data.get("tool_input", {}).get("file_path", "")
            if is_exempt_path(file_path):
                sys.exit(0)
        except (json.JSONDecodeError, KeyError):
            pass

    # Check declared current-change marker (required)
    passed, msg = check_declared_change()
    if passed:
        # SDD gate passed — also check sprint contract (multi-agent builder only)
        contract_ok, contract_msg = check_sprint_contract()
        if not contract_ok:
            print(f"\n{contract_msg}", file=sys.stderr)
            sys.exit(2)
        sys.exit(0)

    print(f"\n{msg}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
