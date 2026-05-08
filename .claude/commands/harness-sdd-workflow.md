Use when starting any code change — new feature, bug fix, refactor, or multi-file work — before opening any source file.

**MANDATORY PROTOCOL — follow every step in order. Do not skip steps. Do not write source code before Step 2 is complete.**

## Session start (run these three before anything else)

1. `git log --oneline -20` — what changed since you last looked.
2. `uv run pytest -q` (or the project's equivalent: `npx vitest run`, `./mvnw test`) — establish a green baseline. If red, fix existing breakage as a separate patch change before starting new work; do not pile new failing tests on top of a broken baseline.
3. `cat .harness/current-change` if present — name of an in-flight change to resume instead of opening a new one. The named change directory under `doc/changes/` carries the structured progress (open ACs, open tasks).

## Step 0 — Pre-spec gates

Before opening a spec, run these three gates in order. Each can be skipped when its triggers don't apply.

### Step 0a — Brainstorm if ambiguous

If the request is vague ("build a feature for X", "improve Y"), bundles 2+ independent subsystems, or has multiple viable approaches with no obvious winner, invoke `/harness-brainstorming` first. The brainstorm refines purpose, constraints, and approach into a one-sentence problem + 2–3 draft ACs before any spec is written.

Skip for: clear bug fixes, single-file refactors, mechanical cleanup, or specific feature requests with crisp scope.

### Step 0b — Critique if non-trivial

For non-trivial proposals (new artifact, schema, gate, hook, persistence layer, or anything that feels "obviously good"), invoke `/harness-design-critique` to stress-test the proposal against the duplication / customer / evidence-bar checklist. Skip for bug fixes, single-file refactors, and mechanical cleanup.

### Step 0c — Triage: single-agent or multi-agent?

Classify this change. Count how many of the following **complexity signals** apply:

1. **Multiple subsystems** — the change touches 3+ modules or layers (e.g., API + DB + UI)
2. **Architectural decision required** — there are 2+ viable approaches and you need to evaluate trade-offs
3. **Ambiguous requirements** — you cannot write all acceptance criteria without first exploring or clarifying scope
4. **Cross-cutting concern** — the change affects a shared concern like auth, logging, error handling, or platform support across multiple features

**Decision rule:**
- **0–1 signals → Single-agent SDD.** Proceed with the steps below.
- **2+ signals → Multi-agent.** Stop here. Tell the user: *"This change has [N] complexity signals: [list them]. Recommend multi-agent mode."* Then invoke `/harness-planner` to begin the Planner → Builder → Evaluator pipeline.

**You must output your triage decision before proceeding:**

> **Triage: single-agent** — [1-sentence reason, e.g., "patch fixing one function in one file, no architectural decisions"]

or

> **Triage: multi-agent** — signals: [list]. Switching to `/harness-planner`.

The user may override your classification. If they say "just do it single-agent" or "use multi-agent for this", follow their direction.

---

### Reference files (read before doing any work)

- `.harness/specs/meta/change-lifecycle.md` — lifecycle states, transition rules, completion gate
- `.harness/specs/meta/spec-schemas.md` — required document sections and field definitions
- `doc/spec/tech/R02-golden-principles.md` — golden principles and agent retrospective rules for this project
- `doc/spec/tech/R00-system-architecture.md` — layer boundaries, key constraints, security guidelines, architecture decisions
- `doc/spec/product/00-overview.md` — project purpose, mental model, and out-of-scope boundaries
- `.harness/specs/templates/` — copy the right template, never write from scratch

### Directory structure

- **`doc/spec/product/`** — Behaviour specs. Always reflects what the system does.
- **`doc/spec/tech/`** — Architecture specs. Always reflects how the system is built.
- **`doc/changes/`** — Append-only change history. Never delete or renumber directories.
- **`.harness/specs/meta/`** — Lifecycle rules, document schemas, and templates (managed by harness-scaffold).
- **`.harness/tools/`** — Completion gate and task tracking tools (managed by harness-scaffold).

### Step 1 — Read before touching anything

Before writing any code or making any file edits, read:
1. The relevant `doc/spec/product/` and `doc/spec/tech/` files for the area you are changing
2. Related `doc/changes/` entries — see below

#### Mining change history

`doc/spec/` records *what the system does*. `doc/changes/` records *why it became that way* — motivation, rejected alternatives, and lessons learned. Read history before relying solely on the current specs.

**When to mine history:**
- You are touching a module or subsystem that has been changed before
- Something in a spec seems counterintuitive or over-engineered — the reason is usually in a past Problem section
- You are about to make an architectural choice — check for rejected alternatives first
- A test is failing in a surprising way — past changes often document similar failures

**How to find relevant entries:**
```bash
grep -rl "keyword_or_module_name" doc/changes/ | sort
```

**What to read in each hit:**
- `00-spec.md` → **Problem** and **Fix** sections — understand what was broken and why
- `01-design.md` (feature changes) → rejected alternatives and the reasoning behind the chosen approach

You don't need to read all of history. Read the 2–3 entries most relevant to the area you're touching.

### Step 2 — Create the change spec (BEFORE writing any source code)

Determine the next sequential change number:
```bash
ls doc/changes/ | sort -V | tail -1   # find the highest existing NNN
```

Choose the change type:
- **Patch** — bug fix or isolated single-file tweak → one doc only (`00-spec.md`)
- **Feature** — new behaviour, refactor, multi-file work → three docs (`00-spec.md` + `01-design.md` + `02-tasks.md`)

Create `doc/changes/NNN-name/00-spec.md` from the appropriate template:
- Patch: `.harness/specs/templates/00-patch-spec.md`
- Feature: `.harness/specs/templates/00-change-spec.md`

Set `status: approved` immediately (no spec-review gate — this is a single-agent project).

For feature changes, also create `01-design.md` and `02-tasks.md` from their templates.

**Populate Integration Boundaries:** If this change affects cross-module contracts (e.g., database schemas, API endpoints, external service calls), add an `## Integration Boundaries` section to `00-spec.md`. For each boundary, scan the codebase for matching integration/e2e test files and set Status to `exists` or `absent`. The completion gate will run suites marked `exists` and skip `absent` silently. Remove the section for patch changes or changes with no cross-module impact.

**E2E / Integration Test Scenarios:** If the spec template includes an `## E2E / Integration Test Scenarios` section, evaluate whether your change needs e2e coverage. If it touches user-facing behaviour, API endpoints, or cross-module boundaries, write testable e2e ACs in that section. If the change is purely internal (refactor, config, etc.), remove the section. For guidance on writing e2e tests, invoke the relevant testing skill listed in the template comments (`/harness-browser-testing`, `/harness-mobile-testing`, or `/harness-e2e-testing`).

Set `status: in-progress` once all required docs exist.

**Declare the active change** so the SDD gate hook knows which change you are working on:
```bash
echo 'NNN-name' > .harness/current-change
```

**You may not touch source code until `00-spec.md` exists, `status: in-progress`, and `.harness/current-change` is set.**

### Step 3 — Implement

Work through the tasks. As each acceptance criterion is met, change its `- [ ]` to `- [x]` in `00-spec.md`. For feature changes, also check off tasks in `02-tasks.md` as they complete.

**Recommended — record/resume pattern (multi-task features):** For features with many tasks, record task-level progress to `execution.jsonl` so the agent can resume after a crash without re-doing completed work.

```bash
# Before starting a task
python .harness/tools/record_task_event.py --change NNN-name --task "Exact task text" --event started

# After completing a task (idempotent — safe to call multiple times)
python .harness/tools/record_task_event.py --change NNN-name --task "Exact task text" --event done

# To see current state (e.g. after a crash, to find where to resume)
python .harness/tools/show_execution_state.py --change NNN-name
```

`execution.jsonl` is an optional recovery artefact — changes without it still work. The idempotency guarantee means calling `--event done` twice for the same task is safe.

### Step 4 — Completion gate (all must pass before `status: done`)

Do not transition to `done` until every item below is true:

1. **Every `- [ ]` AC** in `00-spec.md` is now `- [x]`
2. **Every `- [ ]` task** in `02-tasks.md` is now `- [x]` (feature changes only)
3. **Every spec listed in "Specs to Update"** has been edited and the list entry is confirmed (change its `- [ ]` to `- [x]` or note it was verified current)
4. **`uv run pytest` passes** with no failures
4b. **Declared integration boundary tests pass** — if the spec has an `## Integration Boundaries` section, the gate runs each suite with `status: exists`. Test-logic failures block completion. Environment failures (connection refused, timeout, command not found) are classified as `skipped (env)` — the gate updates the spec status and appends a warning to `## Completion Notes` but does not block.
4c. **User-facing exercise (if applicable)** — if the change is user-facing (UI, CLI, API consumed by a human, mobile/web flow), exercise the change path end-to-end manually before transitioning to `done`. Mechanical AC checks ≠ "feature actually works"; click handlers, error messages, and edge-case interactions slip through automated tests. Skip for purely internal changes (refactors, library code, build config).
5. **`updated` date** in all change doc frontmatter is today's date
6. **`verify_completion.py` exits 0** — run it and confirm all gate checks pass:
   ```bash
   python .harness/tools/verify_completion.py --change NNN
   ```

Then set `status: done` in `00-spec.md`.

### Non-negotiable rules

- **No source code without a spec.** Every change — including one-line bug fixes — must have a `doc/changes/NNN-name/00-spec.md` before any source file is touched.
- **No `done` with open checkboxes.** A change is not done until all ACs are `[x]`.
- **Specs stay current.** If your change alters behaviour described in `doc/spec/`, update those specs before marking done. Stale specs are worse than no specs.
