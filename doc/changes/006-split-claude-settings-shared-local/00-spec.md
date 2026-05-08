---
id: 6
title: "Split .claude/settings.json into project policy (hooks) and personal allowlist (permissions)"
status: done
created: 2026-05-08
updated: 2026-05-08
---

## Problem

`.claude/settings.json` is committed to the repo and currently mixes two kinds of configuration with very different sharing semantics:

1. **Hooks** (the `hooks` block) — wire up `.harness/tools/check_active_spec.py`, `check_completion.py`, and `claude_session_start.py`. These scripts live in the repo and every contributor working here must run them for the SDD gate to function. This is genuine team-wide project policy. Sharing is the point.

2. **Permissions** (the `permissions.allow` list) — accumulated from Claude Code "approve once" clicks across many sessions. Today the list contains 45+ entries. The naive split (move only obviously machine-local entries to `.local`) leaves ~26 "portable" entries in the shared file. That split is wrong:
   - **Permission policy is personal, not project policy.** A wildcard like `Bash(docker compose *)` grants Claude broad rights — different contributors have different risk tolerances, and committing one person's "approve once" decision imposes it on everyone.
   - **Claude Code's docs put permissions on the personal side.** `settings.json` is for team-wide *config* (hooks, sub-agents, env vars). `settings.local.json` is documented as "personal preferences not checked into source control." Permissions fit the personal bucket.
   - **Shared permission lists grow forever via auto-approve clicks.** Every "approve once" during any contributor's session would update a tracked file. Mid-session evidence: two `Bash(python3 .harness/tools/verify_completion.py --change 005)` and `--change 006` entries were auto-added during this very change — already stale (next change is 007).
   - **Most "portable" entries aren't broadly useful anyway.** `Bash(open -a Docker)` is macOS-only, `Bash(command -v nvm/fnm/volta/asdf)` only matches one user's choice, `Bash(verify_completion.py --change NNN)` is bound to a specific change number.

The repo also has no `.claude/settings.local.json` and no `.gitignore` entry for it — the file is currently only ignored by the developer's user-level `~/.config/git/ignore`, which other contributors don't have.

## Fix

- `.claude/settings.json` keeps only the `hooks` block (team-wide project policy). All `permissions.allow` entries are removed from it. The hooks block is preserved verbatim.
- `.claude/settings.local.json` holds the entire `permissions.allow` list (everyone's personal allowlist). Each contributor curates their own.
- `.gitignore` ignores `.claude/settings.local.json` so personal allowlists never leak into commits.
- Verify both files parse as valid JSON, the local file is gitignored, and the shared file remains tracked.

The split follows Rule 4 (R02-golden-principles.md): scaffold-managed shared files should not carry contributor-specific noise. It also matches Claude Code's documented split between team config (`settings.json`) and personal preferences (`settings.local.json`).

## Acceptance Criteria

- [x] `.claude/settings.json` exists, parses as valid JSON, and its top-level keys are exactly `{"hooks"}` (no `permissions` key remains).
- [x] `.claude/settings.json` `hooks` block matches the pre-change content verbatim — the three `python3 .harness/tools/…` hook commands and their matchers are preserved.
- [x] `.claude/settings.local.json` exists, parses as valid JSON, and its `permissions.allow` array contains every entry that was in the original `.claude/settings.json` `permissions.allow` (no permissions are lost in the move).
- [x] `.gitignore` contains a line that ignores `.claude/settings.local.json` (verified by `git check-ignore .claude/settings.local.json` printing the matching repo `.gitignore` rule, not the user-global `~/.config/git/ignore`).
- [x] `git ls-files .claude/settings.local.json` produces no output (the local file is not tracked).
- [x] `git ls-files .claude/settings.json` still lists the shared file (it remains tracked).
