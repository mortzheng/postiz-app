#!/usr/bin/env python3
"""Append a task event to execution.jsonl for a given change directory.

Usage:
    python record_task_event.py --change NNN-name --task "<text>" --event started|done|failed|skipped

Environment:
    HARNESS_CHANGES_DIR — override the default changes/ directory (used in tests)

Called by agents during SDD implementation to track task-level progress.
If the last recorded event for the given task is already 'done', the call is a no-op
(idempotent) to avoid duplicate completions after a crash-resume cycle.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_EVENTS = {"started", "done", "failed", "skipped"}


def _changes_dir() -> Path:
    """Return the changes/ directory, respecting HARNESS_CHANGES_DIR env override."""
    override = os.environ.get("HARNESS_CHANGES_DIR")
    if override:
        return Path(override)
    # Default: current working directory / doc/changes
    return Path.cwd() / "doc" / "changes"


def _last_event_for_task(jsonl_path: Path, task: str) -> str | None:
    """Return the last recorded event string for *task*, or None if not found."""
    if not jsonl_path.exists():
        return None
    last = None
    for raw_line in jsonl_path.read_text().splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            entry = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if entry.get("task") == task:
            last = entry.get("event")
    return last


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a task event in execution.jsonl.")
    parser.add_argument("--change", required=True, help="Change directory name (e.g. 049-execution-jsonl-state)")
    parser.add_argument("--task", required=True, help="Exact task description string")
    parser.add_argument("--event", required=True, choices=list(VALID_EVENTS), help="Event type")
    args = parser.parse_args()

    changes_root = _changes_dir()
    change_dir = changes_root / args.change
    change_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = change_dir / "execution.jsonl"

    # Idempotency: skip if last event for this task is already 'done'
    if args.event == "done" and _last_event_for_task(jsonl_path, args.task) == "done":
        print(f"Skipped (already done): {args.task}")
        sys.exit(0)

    entry = {
        "ts": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task": args.task,
        "event": args.event,
    }
    with jsonl_path.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Recorded [{args.event}]: {args.task}")


if __name__ == "__main__":
    main()
