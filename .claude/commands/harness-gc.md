Use when auditing the codebase for violations of golden principles, retrospective rules, or engineering rules — typically before a release or after significant refactor activity.

**Steps:**

1. Read the following rule sources:
   - `doc/spec/tech/R02-golden-principles.md` — project-specific invariants and agent retrospective rules
   - `.harness/docs/engineering-rules-*.md` — language-specific engineering rules
2. Extract all actionable rules (skip commented-out examples). If no uncommented rules exist in golden principles, note that and continue with retrospective + engineering rules only.
3. For each rule, scan relevant source files:
   - Use Grep to search for violation patterns (e.g., banned imports, missing patterns)
   - Use Read to verify suspected violations in context
   - Skip test files, generated files, and vendored code
4. Produce a concise report:

```
## GC Scan Report

### Violations found
- [file:line] — <rule name>: <what's wrong and how to fix it>

### Clean
- <rule name> — no violations found

### Skipped
- <rule name> — unable to check mechanically (explain why)
```

5. For each violation, ask: "Would you like me to fix this now?"
6. If confirmed, fix the violations. For multi-file fixes, create a change spec first using `/harness-sdd-workflow`.
7. If no violations are found, report the codebase is clean.
