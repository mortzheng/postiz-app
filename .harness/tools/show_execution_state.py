#!/usr/bin/env python3
"""Read execution.jsonl and print a summary of task states for a change.

Usage:
    python show_execution_state.py --change NNN-name

Environment:
    HARNESS_CHANGES_DIR — override the default changes/ directory (used in tests)

Prints a table:
    TASK | LAST EVENT | TIMESTAMP

Incomplete tasks (those without a 'done' event) are prefixed with [!].
Corrupt (non-JSON) lines are skipped with a warning to stderr.
"""

import argparse
import json
import os
import sys
from pathlib import Path

DONE_EVENT = "done"


def _changes_dir() -> Path:
    """Return the changes/ directory, respecting HARNESS_CHANGES_DIR env override."""
    override = os.environ.get("HARNESS_CHANGES_DIR")
    if override:
        return Path(override)
    return Path.cwd() / "doc" / "changes"


def _read_state(jsonl_path: Path) -> tuple[list[tuple[str, str, str]], int]:
    """Parse execution.jsonl and return (ordered task states, corrupt line count).

    Returns a list of (task, last_event, last_ts) tuples in insertion order of
    first appearance per task, along with a count of skipped corrupt lines.
    """
    # task -> (event, ts) — overwritten on each new event (last-wins)
    state: dict[str, tuple[str, str]] = {}
    order: list[str] = []  # preserves first-seen order for display
    corrupt_count = 0

    for raw_line in jsonl_path.read_text().splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            entry = json.loads(raw_line)
        except json.JSONDecodeError:
            corrupt_count += 1
            print(f"Warning: skipping corrupt line: {raw_line!r}", file=sys.stderr)
            continue

        task = entry.get("task", "")
        event = entry.get("event", "")
        ts = entry.get("ts", "")

        if task not in state:
            order.append(task)
        state[task] = (event, ts)

    result = [(task, state[task][0], state[task][1]) for task in order]
    return result, corrupt_count


def _print_table(rows: list[tuple[str, str, str]]) -> None:
    """Print a formatted table of task states."""
    if not rows:
        print("(no tasks recorded)")
        return

    # Column widths
    task_w = max(len("TASK"), max(len(r[0]) for r in rows))
    event_w = max(len("LAST EVENT"), max(len(r[1]) for r in rows))
    ts_w = max(len("TIMESTAMP"), max(len(r[2]) for r in rows))

    header = f"{'TASK':<{task_w}}  {'LAST EVENT':<{event_w}}  {'TIMESTAMP':<{ts_w}}"
    separator = "-" * len(header)
    print(header)
    print(separator)

    for task, event, ts in rows:
        prefix = "    " if event == DONE_EVENT else "[!] "
        print(f"{prefix}{task:<{task_w}}  {event:<{event_w}}  {ts:<{ts_w}}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Show execution state for a change.")
    parser.add_argument("--change", required=True, help="Change directory name (e.g. 049-execution-jsonl-state)")
    args = parser.parse_args()

    changes_root = _changes_dir()
    jsonl_path = changes_root / args.change / "execution.jsonl"

    if not jsonl_path.exists():
        print(f"No execution.jsonl found for change '{args.change}' (path: {jsonl_path})")
        sys.exit(0)

    rows, corrupt_count = _read_state(jsonl_path)

    if not rows:
        print(f"Empty execution.jsonl for change '{args.change}'")
        sys.exit(0)

    _print_table(rows)

    incomplete = [task for task, event, _ in rows if event != DONE_EVENT]
    if incomplete:
        print(f"\n[!] {len(incomplete)} incomplete task(s):")
        for t in incomplete:
            print(f"    - {t}")

    if corrupt_count:
        print(f"\nWarning: {corrupt_count} corrupt line(s) skipped.", file=sys.stderr)


if __name__ == "__main__":
    main()
