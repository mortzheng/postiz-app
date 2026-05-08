---
title: Document Schemas
status: active
created: 2026-03-10
updated: 2026-03-18
---

# Document Schemas

This meta-spec defines the required structure for all documents in `specs/` and `changes/`. Both humans and agents must follow these schemas when creating or editing docs.

## Frontmatter

Every document starts with a YAML frontmatter block:

```markdown
---
title: <string>          # Document title
status: <string>         # See allowed values below
created: <YYYY-MM-DD>    # Date created
updated: <YYYY-MM-DD>    # Date last modified
id: <NNN>                # Numeric ID (changes only)
---
```

**Status values for specs**: `active`, `draft`, `deprecated`

**Status values for changes**: see [Change Lifecycle](./change-lifecycle.md)

---

## Spec Document Schemas

### Required frontmatter for all `doc/spec/` files

Every file under `doc/spec/product/` and `doc/spec/tech/` **must** include a `title:` field in its frontmatter. The spec index generator uses this field to build the navigation index in CLAUDE.md. Missing titles fall back to the filename with a warning.

```markdown
---
title: My Spec Title    # REQUIRED — used by harness-install index
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### Business Specs (`specs/business/`)

Business specs are numbered and scoped by level:

- `00-project-overview.md` — Project-level overview (one per project)
- `NN-[container]-behavior.md` — Container-level behavior spec (one per container)
- `NN-[container]-data-schema.md` — Container-level data schema (one per container)

The `00` prefix is project-level. `01`, `02`, etc. correspond to container numbers from `specs/tech/`.

#### Overview Spec (`00-project-overview.md`)

| Section            | Required | Description                                       |
|--------------------|----------|---------------------------------------------------|
| Frontmatter        | yes      | title, status, created, updated                   |
| Purpose            | yes      | What this capability/system does and why           |
| Target Users       | yes      | Who uses it                                        |
| Core Capabilities  | yes      | Numbered list of what the system can do            |
| Design Principles  | no       | Guiding principles for implementation              |

#### Behavior Spec (`NN-[container]-behavior.md`)

| Section            | Required | Description                                       |
|--------------------|----------|---------------------------------------------------|
| Frontmatter        | yes      | title, status, created, updated                   |
| Interaction Model  | yes      | How the agent receives input and produces output   |
| Response Behaviors | yes      | One H3 per scenario, each with **Trigger** and **Expected behavior** |
| Tool Usage         | no       | Table mapping scenarios to tools used              |
| Constraints        | no       | Things the agent must never do or always do        |

**Response behavior format**:

```markdown
### Scenario Name

**Trigger**: <when this behavior activates>

**Expected behavior**:
1. Step one
2. Step two
```

#### Data Schema Spec (`NN-[container]-data-schema.md`)

| Section            | Required | Description                                       |
|--------------------|----------|---------------------------------------------------|
| Frontmatter        | yes      | title, status, created, updated                   |
| Overview           | yes      | What this data model represents                   |
| Entity Tables      | yes      | One H2 per entity, each with a Field/Type/Required/Description table |
| Enums / Constants  | no       | Named value sets referenced by entity fields       |
| Constraints        | no       | Cross-field or cross-entity validation rules        |

**Entity table format**:

```markdown
## EntityName

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| ...   | ...  | yes/no   | ...         |
```

### Tech Specs (`specs/tech/`) — C4 Model

Tech specs follow the [C4 model](https://c4model.com/) and are numbered:

- `R00-system-architecture.md` — System Context level (one per project)
- `NN-[container].md` — Container level (one per container)

Component-level details (C4 Level 3) are embedded in the container doc.

#### System Context Spec (`R00-system-architecture.md`)

| Section            | Required | Description                                       |
|--------------------|----------|---------------------------------------------------|
| Frontmatter        | yes      | title, status, created, updated                   |
| System Context     | yes      | Diagram + tables for Persons, Software System, External Systems with relationships |
| Container Overview | yes      | Table listing all containers (name, technology, purpose, link to container spec) |
| Project Structure  | no       | Directory tree showing key paths                   |

#### Container Spec (`01-[name].md`, `02-[name].md`, ...)

| Section            | Required | Description                                       |
|--------------------|----------|---------------------------------------------------|
| Frontmatter        | yes      | title, status, created, updated                   |
| Container Overview | yes      | Table with name, technology, purpose, entry point  |
| Components         | yes      | Diagram + one H3 per component with responsibilities |
| SDK Configuration  | no       | Table of SDK options and their values              |
| Runtime & Build    | no       | Table of build/run tooling                         |
| Dependencies       | no       | Table of packages with versions and purpose        |

### Meta Spec (`specs/meta/*.md`)

| Section            | Required | Description                                       |
|--------------------|----------|---------------------------------------------------|
| Frontmatter        | yes      | title, status, created, updated                   |
| (free-form)        | yes      | Content defines process, schemas, or conventions   |

---

## Change Document Schemas

Each change lives in `changes/NNN-name/`. There are two change types with different required documents.

### Feature Change

New behaviour, refactor, or multi-step work. Three documents required.

#### 00-spec.md

| Section                    | Required | Description                                      |
|----------------------------|----------|--------------------------------------------------|
| Frontmatter                | yes      | id, title, status, created, updated              |
| Summary                    | yes      | 1–2 sentence description of the change           |
| What This Change Introduces| yes      | Numbered list of what's new or modified           |
| Specs to Update            | no       | List of spec files that need updating; each becomes a `- [x]` when confirmed done |
| Acceptance Criteria        | yes      | Checkbox list — all must be `- [x]` before `done` |

#### 01-design.md

| Section                    | Required | Description                                      |
|----------------------------|----------|--------------------------------------------------|
| Frontmatter                | yes      | title, created, updated                          |
| Architecture               | yes      | How the change fits into the system               |
| Technology Choices          | no       | Table of decisions with rationale                |
| Trade-offs                 | no       | Alternatives considered and why they were rejected|

#### 02-tasks.md

| Section                    | Required | Description                                      |
|----------------------------|----------|--------------------------------------------------|
| Frontmatter                | yes      | title, created, updated                          |
| Task List                  | yes      | Markdown checkbox list — all must be `- [x]` before `done` |

#### execution.jsonl (optional recovery artefact)

An append-only JSONL file written to `changes/NNN-name/execution.jsonl` during implementation. Each line records a task-level event:

```json
{"ts": "2026-03-18T10:22:00Z", "task": "Write failing tests", "event": "done"}
```

| Field  | Type   | Required | Description                                      |
|--------|--------|----------|--------------------------------------------------|
| `ts`   | string | yes      | ISO-8601 UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`)  |
| `task` | string | yes      | Exact task description (matched by exact string) |
| `event`| string | yes      | One of: `started`, `done`, `failed`, `skipped`  |

This file is **not required** for a change to be valid. It is a recovery artefact — if an agent crashes mid-change, `show_execution_state.py --change NNN` can identify completed vs incomplete tasks so implementation can resume. See `change-lifecycle.md` and CLAUDE.md for usage.

### Patch Change

Bug fix or small single-file tweak. One document only.

#### 00-spec.md (patch format)

| Section             | Required | Description                                      |
|---------------------|----------|--------------------------------------------------|
| Frontmatter         | yes      | id, title, status, created, updated              |
| Problem             | yes      | What is broken and why                           |
| Fix                 | yes      | What was changed to address it                   |
| Tests Added         | no       | Test cases added to prevent regression            |
| Acceptance Criteria | yes      | Checkbox list — all must be `- [x]` before `done` |

---

## Multi-Agent Document Schemas

These schemas define the required structure for documents used in multi-agent (Planner → Builder → Evaluator) workflows. Projects that do not use multi-agent coordination can ignore this section.

### Product Spec (`doc/spec/product/NN-name.md`)

| Section | Required | Description |
|---|---|---|
| Frontmatter | yes | title, status, created, updated |
| Overview | yes | What the product does and why |
| Target Users | yes | Who uses it |
| Features | yes | One H2 per feature with Acceptance Criteria sub-section |
| Out of Scope | yes | Explicit list of what is NOT in this build |

Acceptance Criteria format (machine-checkable):

```markdown
#### Acceptance Criteria
- [ ] Running `<exact command>` produces `<exact output or observable state>`
- [ ] `<File path>` exists and contains `<required content or structure>`
- [ ] `<Endpoint/action>` returns `<specific response>`
```

### Features List (`doc/multi-agent/features.json`)

```json
{
  "version": "1",
  "project": "<project name>",
  "features": [
    {
      "id": "F001",
      "name": "<feature name>",
      "description": "<one sentence>",
      "sprint": 1,
      "depends_on": [],
      "acceptance_criteria": [
        "<exact, machine-checkable criterion>"
      ],
      "status": "pending | in-progress | done"
    }
  ]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Feature identifier in `F001` format |
| `name` | string | yes | Short feature name |
| `description` | string | yes | One-sentence description |
| `sprint` | integer | yes | Sprint number this feature is scheduled for |
| `depends_on` | list of strings | yes | Feature IDs this feature depends on (empty list if none) |
| `acceptance_criteria` | list of strings | yes | Exact commands or observable states — must be machine-checkable |
| `status` | string | yes | One of: `pending`, `in-progress`, `done` |

### Sprint Contract (`doc/multi-agent/sprint-contract.md`)

| Section | Required | Description |
|---|---|---|
| Frontmatter | yes | title, sprint, builder-session, created |
| Sprint Scope | yes | List of feature IDs from features.json covered in this sprint |
| Out of Scope | yes | Explicit list of features NOT being built this sprint |
| Acceptance Criteria | yes | One checkbox per AC from features.json for included features |
| Definition of Done | yes | All tests pass, E2E if present, all ACs checked |

### Evaluation Report (`doc/multi-agent/evaluation-N.md`)

| Section | Required | Description |
|---|---|---|
| Frontmatter | yes | title, sprint, evaluator-session, verdict, created |
| Verdict | yes | PASS or FAIL (bold, first line after frontmatter) |
| Acceptance Criteria Results | yes | One row per AC: criterion + PASS/FAIL + evidence |
| Grading | yes | Four dimensions: Design Quality / Product Depth / Functionality / Code Quality, each scored 1–5 |
| Remediation Notes | if FAIL | Specific list of what must be fixed before re-evaluation |

Frontmatter `verdict` field: `pass` or `fail` (lowercase).

---

## Templates

Copyable templates for change docs are in `specs/meta/templates/`:

| Template                | Use for                                    |
|-------------------------|--------------------------------------------|
| `00-change-spec.md`     | Feature `changes/NNN-name/00-spec.md`      |
| `01-change-design.md`   | Feature `changes/NNN-name/01-design.md`    |
| `02-change-tasks.md`    | Feature `changes/NNN-name/02-tasks.md`     |
| `00-patch-spec.md`      | Patch `changes/NNN-name/00-spec.md`        |

Copy the template, replace `<placeholders>`, and fill in the sections.
