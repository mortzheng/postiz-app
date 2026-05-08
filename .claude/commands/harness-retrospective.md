Use after a change reaches `status: done` to capture engineering lessons, scope-creep findings, and rule updates from the most recently completed change.

**Steps:**

1. Read `doc/changes/<NNN>-<name>/00-spec.md` — understand what was built and what the ACs were.
2. Read `doc/changes/<NNN>-<name>/01-design.md` if it exists — review the design decisions and trade-offs.
3. Read `doc/changes/<NNN>-<name>/02-tasks.md` if it exists — look at the task list for implementation patterns.
4. Think about:
   - What went smoothly that should be repeated?
   - What caused friction, rework, or bugs that should be prevented next time?
   - Are there patterns (naming, structure, testing approach) worth standardising?
   - Are there anti-patterns observed that should be explicitly forbidden?
5. Read `doc/spec/tech/R02-golden-principles.md` — understand the existing rules.
6. Propose 1–3 new rules or amendments to existing rules derived from this retrospective. Each rule should be:
   - Specific and actionable (not vague principles)
   - Grounded in what actually happened in this change
   - Written in the imperative: "Always X", "Never Y", "When Z, do W"
7. Show the proposed additions/changes and ask for confirmation before editing `R02-golden-principles.md`.
8. If confirmed, append or update the rules in `doc/spec/tech/R02-golden-principles.md`.
9. Check the change spec's `## Integration Boundaries` table (if present). If any boundary has `status = absent` or `status = skipped (env)`, add this note to the retrospective output:

   > This change has uncovered integration boundaries. Consider running `/harness-test-advisor` to get recommendations for test coverage.
