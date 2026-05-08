Use when starting work that's vague, multi-pronged, or "build a thing that does X" — refines purpose, constraints, and approach into a clear scope before any spec is written.

## When to use

- The user request is open-ended ("build a feature for X", "improve Y", "make X better").
- Multiple viable approaches exist; the right one is not obvious.
- The request bundles 2+ independent subsystems — they need to be decomposed before any one is brainstormed.
- You cannot write specific acceptance criteria yet without first exploring trade-offs.
- The user has not yet articulated what "done" looks like.

## Skip when

- Bug fix with a clear reproduction.
- Single-file refactor (rename, dead-code removal, type-only edit).
- Specific feature request with crisp scope ("add field X to form Y").
- Mechanical cleanup (dependency bump, lockfile sync, format pass).
- Reverting a recently-shipped change with the same scope.
- The user has already articulated the design in detail — proceed directly to `/harness-sdd-workflow`.

## Hard gate

Until this brainstorm is complete and the user has approved the written summary in Step 6, do **not**:

- Write any source code, tests, or scaffolding.
- Run `/harness-sdd-workflow` past Step 1 (Step 1 is read-only and harmless).
- Run `/harness-builder`, `/harness-planner`, `/harness-evaluator`, or any TDD skill (`/harness-tdd-workflow-*`).
- Create files in the project (other than this brainstorm conversation's eventual `00-spec.md` via the SDD handoff).

This applies even when the project feels too simple to need a design — those are exactly the cases where unexamined assumptions cost the most rework.

## Steps

### 1. Explore project context

Before asking the user anything, understand what's already there:

- `cat .harness/current-change` — is there an in-flight change you should resume rather than start fresh?
- `git log --oneline -20` — what's been touched recently?
- Read relevant files in `doc/spec/product/` and `doc/spec/tech/` for the area being changed.
- `grep -rl "<keyword>" doc/changes/` — has this problem (or a near-neighbour) been considered before? Read the 2–3 most relevant prior change specs.

If a closely related change already exists or is in flight, surface it before starting a new brainstorm — the right answer may be "extend that change" or "wait for it to land," not a new change cycle.

### 2. Decompose if too large

If the request describes 2+ independent subsystems (e.g. "build a platform with chat, storage, billing, and analytics"), don't try to brainstorm the whole thing. Present a decomposition:

> "I see N independent pieces here:
> - Sub-project A: …
> - Sub-project B: …
> - Sub-project C: …
>
> Each gets its own change cycle. Recommend brainstorming **A** first — B and C depend on its data model. OK to proceed with A?"

Wait for user approval. Then brainstorm just sub-project A.

### 3. Ask clarifying questions, one at a time

Goal: until you can articulate the problem in a single sentence the user agrees with, and you can list 2–3 acceptance criteria.

Rules:
- **One question per message.** Never bundle. If you have a follow-up, ask it next turn.
- **Prefer multiple-choice** when the option space is small enough:
  > "Cache strategy: A) write-through, B) write-back, C) write-around. Which?"
- **Open-ended is fine** when MCQ would be artificial ("what's the integration constraint with the existing scheduler?").
- **Focus the questions** on: purpose, constraints, success criteria, what's explicitly out of scope, who the user/caller is.

Stop asking when you can write a one-sentence problem statement and the user agrees with it.

### 4. Propose 2–3 approaches with trade-offs

Once the problem is clear, present 2–3 approaches. Lead with your recommendation:

> **Recommended: Approach A.** [What it does, in 2–3 sentences.]
> - Trade-off: gives up X to get Y. Costs ~N hours.
>
> **Alternative: Approach B.** [What it does.]
> - Trade-off: gets X but at cost Z.
>
> **Alternative: Approach C.** [Why it's a serious option even if not picked.]

Don't hedge. If the user asks "which do you actually recommend?", give a real opinion with reasoning. Wait for the user to pick before continuing.

### 5. Present the design in sections

Once an approach is chosen, walk the design in *sections, not all at once*. After each section, ask: "Does this look right so far?"

Sections to cover (skip those that don't apply):

- **Components and responsibilities** — what files / classes / modules will exist, what each owns
- **Data flow** — how state moves through the system
- **Error handling** — what fails, what does the system do
- **Testing** — what gets tested, at what layer (unit / integration / e2e)
- **Out of scope** — explicit items deferred or rejected, with one-line reasoning each

Scale each section to its complexity: 1–2 sentences for trivial, up to a paragraph for nuanced. Don't pad.

### 6. Hand off to /harness-sdd-workflow

When the user approves the full design, summarize the brainstorm in this exact format:

> **Problem:** [1–2 sentences — the WHY this change exists.]
>
> **Approach:** [1–2 sentences naming the chosen approach.]
>
> **Acceptance criteria (draft):**
> - [criterion 1 — exact, observable, evaluator-checkable]
> - [criterion 2]
> - [criterion 3]
>
> **Out of scope:**
> - [explicit non-goal 1, with reason]
> - [explicit non-goal 2]
>
> **Open questions (if any):**
> - [question that did not resolve during brainstorm — flag for spec author]

Then tell the user:

> "Brainstorm complete. Next: invoke `/harness-sdd-workflow` to read prior art (Step 1) and write the change spec (Step 2). The summary above seeds the spec's Summary, Motivation, Out of Scope, and Acceptance Criteria sections."

The brainstorm output stays in conversation — it does **not** get its own file. The structured artifact is the `00-spec.md` produced by SDD Step 2 from this summary.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Bundling 3 questions in one message | One question per message — wait between turns. |
| Open-ended when MCQ would do | "What style?" → "A) minimal, B) rich, C) opinionated. Which?" |
| Skipping decomposition for a multi-subsystem ask | Present sub-projects, get user approval, brainstorm only the first. |
| Writing the spec yourself instead of section-by-section approval | Each design section is its own message. Wait for "looks good" before next. |
| Combining brainstorm output with implementation in one message | Brainstorm ends with the Step 6 handoff. Stop there. The user re-invokes `/harness-sdd-workflow` to start the spec. |
| "This is obviously approach A" — when 2+ sane approaches exist | Present both, recommend one with reasoning, let the user pick. |
| Hedging on which approach you'd pick when asked | Give a real opinion. Hedging wastes the user's time. |

## Red flags — STOP and restart

If you catch yourself thinking any of these, the brainstorm is broken:

- "I think the user means X" — without having asked them to confirm.
- "I'll just start with X and we can pivot later" — pivoting = rework. Brainstorm now.
- "The user said 'build a thing,' so I'll write the spec and they'll correct it" — the spec is the wrong place to discover what the user wants.
- "This is too simple to need brainstorming" — apply Step 1 (context exploration) at minimum. The simpler the request, the cheaper this is.
- "I've asked enough questions" — until you can write the 1-sentence problem statement and the user agrees, you haven't.
