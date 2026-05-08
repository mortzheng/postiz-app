Use when specs in `doc/spec/` may be drifting from the codebase — typically after a major refactor, before a release, or on explicit request.

**Steps:**

1. Read all files in `doc/spec/product/` and `doc/spec/tech/` (skip READMEs).
2. For each spec, identify the code area it describes — look for references to modules, classes, endpoints, or subsystems by name.
3. Scan the corresponding source files (use the spec's content as a guide for where to look).
4. For each spec, classify:
   - **Current** — spec accurately describes the code
   - **Stale** — spec describes behaviour or structure that has changed in the code
   - **Missing** — significant code areas exist with no corresponding spec
5. Produce a concise report:

```
## Spec Sync Audit

### Current
- [filename] — matches code

### Stale
- [filename] — <specific discrepancy: what the spec says vs what the code does>

### Missing coverage
- <code area> — no spec describes <behaviour/component>
```

6. For each **Stale** entry, ask: "Would you like me to update `[filename]` now?"
7. For each **Missing** entry, ask: "Would you like me to draft a new spec for `<area>`?"
8. On confirmation, update or create the spec files. Use the frontmatter format required by `.harness/specs/meta/spec-schemas.md` (title, status: active, created, updated).
