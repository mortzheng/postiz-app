---
title: Change Lifecycle
status: active
created: 2026-03-10
updated: 2026-03-18
---

# Change Lifecycle

Every change in `doc/changes/NNN-name/` follows this lifecycle. The current state is tracked in the `status` field of `00-spec.md` frontmatter.

## Change Types

| Type | When to use | Required docs |
|------|-------------|---------------|
| **feature** | New behaviour, refactor, or multi-step work | `00-spec.md`, `01-design.md`, `02-tasks.md` |
| **patch** | Bug fix or small single-file tweak | `00-spec.md` only |

Patch changes use a condensed `00-spec.md` format — see `.harness/specs/templates/00-patch-spec.md`.

### Classification Decision Tree

Use this numbered if/else sequence to classify any change. Work through each question in order and stop at the first match.

1. **Does the change touch more than one source file?**
   Yes → **feature**

2. **Does the change add new observable behaviour?**
   (New endpoint, new CLI tool, new scheduled job, new Slack command, new agent, new memory structure)
   Yes → **feature**

3. **Does the change alter a public API or data schema?**
   (Function signature visible to other modules, JSONL field, YAML config key, tool stdout contract)
   Yes → **feature**

4. **Is it purely fixing broken behaviour in a single file, with no API surface changes?**
   Yes → **patch**

5. **Default — when uncertain, pick feature.**
   More documentation is always safer than less. The cost of three docs is low; the cost of a misclassified patch (missing design rationale, missing task tracking) is high.

### Patch Examples

Real changes classified as patch:

| Change | Why patch |
|--------|-----------|
| `043-scheduler-in-progress-leak` | Bug fix in `scheduler.py` + `agent_runner.py` — both files touched but both are fixing one broken invariant; no new behaviour added, no API changed |
| `044-session-reset-stale-summary-fix` | Single logic bug in `needs_session_reset()` — one function, one file, no public API or schema change |
| `013-fix-track-b-ack-ordering` | Ordering bug in `agent_runner.py` — moved side-effect into coroutine; no new behaviour, single file |

### Feature Examples

Real changes classified as feature:

| Change | Why feature |
|--------|-------------|
| `046-watches-persistent-target-intelligence` | New subsystem (`WatchStore`, four scanner modules, two CLI tools, scheduler job, `ContextBuilder` injection) — adds new observable behaviour across many files |
| `045-memory-upgrade-phase1` | New `KnowledgeStore` class, new `search_memory.py` tool, `ContextBuilder` changes, wiring in `main.py` — multi-file, new behaviour |
| `042-agent-team-phase1` | New `SubAgentRunner`, `AgentOrchestrator`, agent YAML configs, new log tooling — entirely new capability, multi-file |

### Edge Case Table

Borderline scenarios with explicit rulings:

| Scenario | Ruling | Reason |
|----------|--------|--------|
| Single-file refactor that renames a public function used by other modules | **feature** | Alters public API — other callers must update; needs design rationale |
| Two-line config default change in one file | **patch** | No new behaviour, no API change; isolated tweak |
| Adding a new field to a JSONL schema (even in one file) | **feature** | Data schema change; downstream readers and writers are affected |
| Updating only a markdown doc or spec file (no source code) | **patch** | Documentation fix; no runtime behaviour change |
| A bug fix that also improves error handling in the same function | **patch** | The improvement is incidental to fixing the bug; if the improvement adds new external-facing behaviour, re-evaluate |
| A refactor that splits one large module into two files | **feature** | Multi-file by definition; public import paths change |

## States

```
draft → approved → in-progress → done
             ↓
         cancelled
```

| State         | Description                                                       | Required Docs     |
|---------------|-------------------------------------------------------------------|-------------------|
| `draft`       | Initial authoring. Spec is incomplete or not ready to implement.  | `00-spec.md` (partial) |
| `approved`    | Spec accepted. Ready to implement.                                | `00-spec.md` |
| `in-progress` | Implementation underway. Tasks being checked off.                 | feature: all three docs; patch: `00-spec.md`; optional: `execution.jsonl` |
| `done`        | All ACs checked, all tasks complete, updated specs confirmed.     | same as `in-progress` |
| `cancelled`   | Change abandoned. Reason noted in `00-spec.md` summary.           | `00-spec.md` |

### Recovery Artefact: `execution.jsonl`

During `in-progress`, agents may optionally write an `execution.jsonl` file to the change directory. This file is an append-only JSONL log of task-level events (`started`, `done`, `failed`, `skipped`). It is a recovery artefact — if an agent crashes or the session is interrupted, calling `show_execution_state.py --change NNN` identifies completed vs incomplete tasks so the agent can resume from where it left off.

`execution.jsonl` is **not required** for a change to be valid. Agents are encouraged (but not mandated) to write it for multi-task features. See CLAUDE.md "Step 3 — Implement" for the record/resume pattern.

## Transition Rules

| From          | To            | Condition                                                          |
|---------------|---------------|--------------------------------------------------------------------|
| `draft`       | `approved`    | `00-spec.md` has all required sections and is ready to act on     |
| `draft`       | `cancelled`   | Decision to not proceed                                            |
| `approved`    | `in-progress` | feature: `01-design.md` and `02-tasks.md` created; patch: work begun |
| `approved`    | `cancelled`   | Decision to not proceed                                            |
| `in-progress` | `done`        | **All `- [ ]` ACs in `00-spec.md` changed to `- [x]`**; feature: all task checkboxes checked; updated specs confirmed; `verify_completion.py --change NNN` exits 0 |
| `in-progress` | `cancelled`   | Decision to abandon mid-implementation                             |

## On Completion (`done`)

Before transitioning any change to `done`, **run the completion gate tool** and confirm it exits 0:

```bash
python .harness/tools/verify_completion.py --change NNN
```

The tool machine-checks all conditions below. Do not mark `done` if it exits non-zero.

1. Every `- [ ]` in `00-spec.md` **Acceptance Criteria** must be changed to `- [x]`
2. feature only: every `- [ ]` in `02-tasks.md` must be changed to `- [x]`
3. Every spec listed in **Specs to Update** must have been edited; confirm by adding `- [x]` next to each entry
4. `uv run pytest` must pass with no failures
5. Update the `updated` date in frontmatter

## Numbering

Changes are numbered sequentially as 3-digit zero-padded integers: `001`, `002`, `003`, etc. The directory name follows the pattern `NNN-short-name` (e.g., `002-slack-adapter`). The `id` field in frontmatter stores the numeric value (e.g., `2`).
