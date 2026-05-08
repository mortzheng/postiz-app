---
title: Golden Principles & Agent Rules
status: active
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# Golden Principles & Agent Rules

This file contains two types of project-specific rules:

1. **Golden Principles** — proactive invariants you declare upfront ("always X / never Y")
2. **Agent Retrospective Rules** — reactive rules discovered from past agent mistakes

Both are project-owned. Run `/harness-gc` periodically to scan the codebase for violations.

---

## Principles

Good principles are: **mechanical** (checkable without judgement), **opinionated**
(pick one way), and **agent-legible** (stated as "always X" / "never Y" with
a concrete example).

<!-- Uncomment and adapt these examples, or write your own.

### No direct database queries outside the repository layer

- Always: access data through repository classes
- Never: write SQL or ORM queries in service/controller code
- Why: keeps data access testable and migration-safe

### API responses use envelope format

- Always: return `{"data": ..., "error": ...}` from all endpoints
- Never: return bare objects or arrays at the top level
- Why: consistent client-side error handling

### Feature flags gate all new user-facing behaviour

- Always: wrap new features in a flag check before exposing to users
- Never: deploy new behaviour unconditionally
- Why: safe rollback without redeployment

### No hardcoded secrets or environment-specific values

- Always: read from environment variables or a secrets manager
- Never: commit API keys, connection strings, or passwords
- Why: security and multi-environment deployment

### File size limit

- Always: keep source files under 500 lines
- Never: let a single file grow beyond 500 lines without splitting
- Why: large files are harder to review, test, and navigate

-->

---

## Agent Retrospective Rules

Mistakes that AI agents have made in this project and must not repeat. Rules here are added by `/harness-retrospective` after completed changes, when a recurring or surprising failure is identified.

**What belongs here:** Agent-specific failure modes — wrong assumptions, missed call sites, hallucinated APIs, omitted steps, violated boundaries. Each rule should be traceable to a real incident.

**What does NOT belong here:**
- General code style and formatting → `.harness/docs/engineering-rules-*.md`
- Architectural invariants and layer boundaries → `doc/spec/tech/R00-system-architecture.md`
- Project-level coding conventions → `doc/spec/tech/R01-code-conventions.md`

**How to use:** Read before starting any implementation work. When you observe a failure that matches a rule, note which rule it violates in the change spec.

### Agent Failure Patterns

Mistakes where the agent acted on an incorrect assumption about the codebase.

#### Rule 1 — Verify Method Names on the Actual Class

**Root cause category**: Interface mismatches

When calling a method on an object, verify the method name exists on the actual class. This is especially common when renaming methods during refactors or calling methods from memory.

**Rules:**
- Before writing `obj.some_method()`, grep the source file for `def some_method` to confirm it exists.
- When renaming a method, grep the entire codebase for all callers before committing.
- If documentation and code disagree, the code is authoritative.

### Omission Failures

Mistakes where the agent completed a task but forgot a required downstream step.

#### Rule 2 — Thread All Parameters Through from the Entry Point

**Root cause category**: Incomplete propagation

New parameters added to a function signature must be threaded all the way from the entry point through every intermediate caller. Missing a caller results in the parameter silently defaulting or causing a `TypeError`.

**Rules:**
- When adding a parameter to a function, trace every call site from the entry point down and update each one.
- Use grep to find all call sites before committing.
- Write a test that passes the new parameter end-to-end, not just at unit level.

### Boundary Violations

Mistakes where the agent crossed an architectural or operational boundary it should not have.

#### Rule 3 — Log All Exceptions; Never Silently Swallow Errors

**Root cause category**: Debugging visibility

Silent exception handling hides bugs, makes debugging impossible, and causes mysterious failures.

**Rules:**
- All `except` blocks must at minimum log the exception with context.
- Never use bare `except:` — always catch specific exceptions or `Exception` with logging.
- In status/result dicts, always populate the `message` field with error details — not just `{"status": "error"}`.

```python
# WRONG
try:
    do_thing()
except Exception:
    pass

# CORRECT
try:
    do_thing()
except Exception as e:
    logger.exception("do_thing failed")
    return {"status": "error", "message": str(e)}
```

<!-- Add project-specific rules below as your retrospectives produce them. -->
<!-- Format: #### Rule N — Short Title                                     -->
<!--          Root cause category, description, rules, code examples.     -->
<!-- Place each rule under the most relevant section heading above.        -->
