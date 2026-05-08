"""
PreToolUse hook — enforces multi-agent role boundaries on Edit/Write.

Reads `.harness/current-role` for the declared role (planner, builder, evaluator)
and restricts file edits based on the role's permission allowlist.

When no `.harness/current-role` file exists (the default for non-multi-agent
projects), the hook exits 0 immediately — zero impact on single-agent workflows.

Claude Code runs this before every Edit or Write tool call.
Exit 0  → allow the tool call through.
Exit 2  → block the tool call and surface the stderr message to the user.

Usage (registered in .claude/settings.json):
    python3 .harness/tools/check_role_gate.py
"""
import json
import os
import re
import sys
from pathlib import Path

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

VALID_ROLES = {"planner", "builder", "evaluator"}

# ---------------------------------------------------------------------------
# Role permission patterns (allowlists)
# ---------------------------------------------------------------------------
# Each role has a list of regex patterns matching paths they ARE allowed to edit.
# Paths not matching any pattern are BLOCKED.

PLANNER_ALLOW = [
    r"doc/spec/",
    r"doc/changes/",
    r"doc/multi-agent/plan\.md",
    r"doc/multi-agent/sprint-contract",
    r"(agent|claude)-progress\.txt",
    r"\.harness/current-change",
    r"\.harness/current-role",
]

BUILDER_ALLOW = [
    r"doc/changes/",
    r"(agent|claude)-progress\.txt",
    r"\.harness/current-change",
    r"\.harness/current-role",
    # Source and test files — everything except doc/multi-agent/evaluation-* and doc/evals/
    # We use a broad allow + explicit deny pattern (see BUILDER_DENY)
]

BUILDER_DENY = [
    r"doc/multi-agent/evaluation-",
    r"doc/evals/",
    r"doc/spec/",
    r"doc/multi-agent/plan\.md",
    r"doc/multi-agent/sprint-contract",
]

EVALUATOR_ALLOW = [
    r"doc/multi-agent/evaluation-",
    r"doc/evals/",
    r"(agent|claude)-progress\.txt",
    r"\.harness/current-role",
]

_COMPILED_PLANNER_ALLOW = [re.compile(p) for p in PLANNER_ALLOW]
_COMPILED_BUILDER_ALLOW = [re.compile(p) for p in BUILDER_ALLOW]
_COMPILED_BUILDER_DENY = [re.compile(p) for p in BUILDER_DENY]
_COMPILED_EVALUATOR_ALLOW = [re.compile(p) for p in EVALUATOR_ALLOW]


def get_current_role() -> str | None:
    """Read the current role from `.harness/current-role`, or None if absent/empty."""
    marker_path = _HARNESS_DIR / "current-role"
    if not marker_path.exists():
        return None
    role = marker_path.read_text().strip().lower()
    return role if role else None


def normalize_path(file_path: str) -> str:
    """Normalize a file path to be relative to the repo root."""
    normalized = file_path.replace("\\", "/")
    # Try to make it relative to repo root
    try:
        rel = str(Path(normalized).relative_to(_REPO_ROOT))
    except ValueError:
        rel = normalized
    return rel.replace("\\", "/")


def is_allowed(role: str, file_path: str) -> tuple[bool, str]:
    """Check if the role is allowed to edit the given file path.

    Returns (allowed, reason).
    """
    rel = normalize_path(file_path)

    if role == "planner":
        for pattern in _COMPILED_PLANNER_ALLOW:
            if pattern.search(rel):
                return True, ""
        return False, (
            f"[ROLE GATE] Planner cannot edit '{rel}'.\n"
            f"\nPlanners can only edit doc/spec/, doc/changes/, doc/multi-agent/plan.md, "
            f"doc/multi-agent/sprint-contract*.md, and agent-progress.txt.\n"
            f"\nSource code edits are reserved for the Builder role.\n"
        )

    if role == "builder":
        # Check deny list first
        for pattern in _COMPILED_BUILDER_DENY:
            if pattern.search(rel):
                return False, (
                    f"[ROLE GATE] Builder cannot edit '{rel}'.\n"
                    f"\nBuilders cannot edit evaluation files, specs, or planning documents.\n"
                    f"Use agent-progress.txt to communicate issues back to the Planner.\n"
                )
        # Builder can edit everything not in deny list
        return True, ""

    if role == "evaluator":
        for pattern in _COMPILED_EVALUATOR_ALLOW:
            if pattern.search(rel):
                return True, ""
        return False, (
            f"[ROLE GATE] Evaluator cannot edit '{rel}'.\n"
            f"\nEvaluators can only edit doc/multi-agent/evaluation-*.md, "
            f"doc/evals/, and agent-progress.txt.\n"
            f"\nSource code edits are reserved for the Builder role.\n"
        )

    # Unknown role — block with guidance
    return False, (
        f"[ROLE GATE] Unknown role '{role}'.\n"
        f"\nValid roles: planner, builder, evaluator.\n"
        f"Update .harness/current-role with a valid role.\n"
    )


def main() -> None:
    # Read file_path from stdin payload
    raw = sys.stdin.read().strip()
    if not raw:
        sys.exit(0)

    try:
        data = json.loads(raw)
        file_path = data.get("tool_input", {}).get("file_path", "")
    except (json.JSONDecodeError, KeyError):
        sys.exit(0)

    if not file_path:
        sys.exit(0)

    role = get_current_role()
    if role is None:
        # No role marker — non-multi-agent project, allow everything
        sys.exit(0)

    allowed, reason = is_allowed(role, file_path)
    if allowed:
        sys.exit(0)

    print(f"\n{reason}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
