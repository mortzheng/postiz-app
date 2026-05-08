Use when starting any session in a harness-scaffold project — names the entry-point skill, the current-change state, and the `/harness-*` catalog.

## The rule

Before any source-code edit, invoke `/harness-sdd-workflow`. If `.harness/current-change` is set to an in-progress change, **resume it — don't open a new one**.

If a skill might apply to your task — even at 1% confidence — invoke it via the `Skill` tool.

## Skill catalog

| Skill | Trigger |
|---|---|
| `/harness-sdd-workflow` | Any code change — feature, bug fix, refactor (mandatory entry point) |
| `/harness-tdd-workflow` | Implementing or fixing behaviour, before writing code |
| `/harness-brainstorming` | Vague, multi-pronged, or "build a thing that does X" requests |
| `/harness-design-critique` | Proposing a new artifact, schema, gate, hook, or persistence layer |
| `/harness-test-advisor` | Deciding integration / e2e coverage for a change |
| `/harness-retrospective` | After a change reaches `status: done` |
| `/harness-sync-specs` | When `doc/spec/` may be drifting from the codebase |
| `/harness-import-spec` | Bringing external docs into `doc/spec/` |
| `/harness-gc` | Auditing the codebase for rule violations |

For multi-agent work: `/harness-planner` → `/harness-builder` → `/harness-evaluator`.
