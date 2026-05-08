Use before scoping a design proposal that adds a new artifact, schema, file, gate, hook, or persistence layer — especially when the proposal feels obvious or appeals to "best practice X says we should…".

## When to invoke

- You are proposing a new artifact, schema, file, gate, hook, skill, or persistence layer.
- You are about to cite "the wiki / blog / talk / case study says…" as justification.
- The proposal feels *obviously good* — that's the strongest trigger; obvious-feeling proposals are where second-pass thinking has the highest yield.
- You are extending an existing schema with new fields the wiki or some doc prescribes.
- You are about to scope a change > 100 lines without a concrete failure-mode story.
- Multiple layers of similar machinery already exist and you're adding another.

## Skip when

- Bug fix with a clear repro.
- Single-file refactor (rename, dead-code removal, type-only edit).
- Mechanical cleanup (dependency bump, lockfile sync, format pass).
- Test addition for existing behaviour.
- Documentation typo or stale-fact correction.
- Reverting a recently-shipped change with the same scope.

## The 8-question checklist

Answer each concretely. Vague answers are the failure mode.

1. **What does this duplicate?** What artifact / spec / skill / tool / test / persistence layer already covers this ground? Name it. If you can't name what's adjacent, you haven't looked.
2. **What's the marginal value over what already exists?** Compare to "do nothing." What specifically breaks if we don't ship this? If the answer is "agent might not follow X," that's weak — agents already follow most things.
3. **Who's the customer?** Library author / product builder / single-agent / multi-agent / web / mobile / CLI. Different customers have different needs. "Everyone" usually means "no one specifically."
4. **What's the failure mode if half-implemented or stale?** Dead-letter pointers to files that don't ship, schema drift, half-done migrations, and obligations that decay are signals.
5. **What's the simpler alternative?** Could 80% of the value come from a one-line prompt edit instead of a new artifact? Could a CLAUDE.md sentence replace the new file? If yes, do that.
6. **Is this solving a real problem you've hit, or one a doc told you about?** Be honest. "We saw failure mode X last week" is a real problem. "The wiki has a section on this" is not.
7. **What obligations does this create?** "We'd also need to ship Y to make this useful" is a tell. "We'd need a migration path for existing installs" is a tell. Hidden costs surface here.
8. **What's the evidence bar?** "Wiki / blog / talk / case study prescribed it" is too low. "Three projects used it and it worked" is medium. "We hit failure mode X and need this to prevent recurrence" is high.

## Calibration examples (recent walked-back proposals)

These are real failures from this project's history. Pattern-match against them rather than reasoning abstractly.

**`claude-progress.txt` line in the SDD session-start block** — Change 071 added `cat claude-progress.txt if present` to the session-start protocol. Walked back in Change 072. The driving question that should have caught it: **#1 (duplication)**. The structured change-spec system (`.harness/current-change` → `doc/changes/NNN/00-spec.md` with checkboxed ACs) plus git history plus auto-memory already cover the cross-session "what was done / where to resume" use case. The wiki prescribed the file before those layers existed; carrying the instruction now obligates shipping a redundant fourth persistence layer.

**`features.json` verification gate (passes + steps)** — proposed as Change 073, dropped before any code shipped. The driving question that should have caught it: **#3 (customer)**. The wiki uses `features.json` for product-style projects (image editor, DAW) where features are user-visible and benefit from explicit manual e2e verification. For library-style projects (this scaffold itself), `features.json` is mostly redundant with change-spec ACs + automated tests + `doc/spec/product/`. Right pattern, wrong customer.

**Verbose Step 1b in the SDD workflow** — Change 069 shipped a 16-line "Verify the starting state" section. Superseded in Change 071 by a 4-line bullet block. The driving question that should have caught it: **#5 (simpler alternative)**. The actionable content was four sentences; the rest was prose elaboration that the agent didn't need.

## Output format

Produce a verdict drawn from this fixed vocabulary:

- **`ship`** — proposal survived the checklist; proceed to scoping.
- **`narrow scope`** — proposal has a real core but ships too much. Trim to the core, drop the rest.
- **`defer`** — real value, but missing prerequisite (e.g., another artifact must ship first; or wait until a real customer surfaces).
- **`drop`** — duplication, hypothetical problem, or redundant with existing layers. Do not scope.

State the verdict explicitly, name the question(s) that drove it, and (if `narrow scope`) name what survives versus what gets cut. Then proceed to Step 0 of the SDD workflow with the surviving scope, or stop if `drop`.

## Anti-patterns

- "Just one more layer of safety." If 3 layers exist, the 4th rarely earns its keep.
- "Future-proofing" for hypothetical needs. Add when the need surfaces.
- "Schema additions" without a concrete user need. Schemas calcify; remove the field later is harder than not adding it.
- Rationalizing your own proposal. The point of this skill is to argue *against* your prior message; if you find yourself defending the proposal, you're not running the gate.
