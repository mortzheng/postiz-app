Use when implementing or fixing any TypeScript behaviour, before writing implementation code.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over. Implement fresh from a failing test.

**No exceptions:**
- Don't keep it as "reference" — you'll adapt it, that's testing-after.
- Don't "look at it for inspiration" while writing the test.
- Don't bracket it out and "use it later" — delete means delete.

**Violating the letter of this rule is violating the spirit of this rule.**

## TDD Workflow — write tests first

Every change that modifies source code follows RED → GREEN → REFACTOR:

1. **RED** — write a failing test that describes the new behaviour. Run and confirm it fails for the right reason.
2. **GREEN** — write the minimal implementation to make the test pass. Run and confirm green.
3. **REFACTOR** — clean up without breaking tests. Run again to confirm.

**Rules:**
- Tests use Jest or Vitest — check `package.json` for the configured runner.
- Each AC in `00-spec.md` must have at least one corresponding test case.
- Minimum coverage target: **80%**.
- Fix the implementation when a test fails, not the test — unless the test itself is wrong.

**Commands (Jest):**
```bash
# Run full suite
npx jest --verbose

# Run a single file — useful when diagnosing a specific failure
npx jest --verbose tests/foo.test.ts

# Watch mode during development
npx jest --watch

# Coverage report
npx jest --coverage --coverageReporters=text
```

**Commands (Vitest):**
```bash
# Run full suite
npx vitest run

# Run a single file
npx vitest run tests/foo.test.ts

# Watch mode during development
npx vitest

# Coverage report
npx vitest run --coverage
```

When a test fails, read the diff output in full. Jest and Vitest both show the expected vs. received values inline — identify the exact property or line before touching any code.

## Red Flags — STOP and start over

If you catch yourself thinking any of these, the discipline is broken:

- "Code first, test after — same outcome"
- "I already manually tested all the edge cases"
- "Tests after achieve the same purpose"
- "Just this once" / "It's a small change"
- "Deleting hours of work is wasteful"
- "The test would be trivial — skip it"
- "TDD is dogmatic; pragmatic means adapting"
- "I'll write tests once the design settles"
- "It's just a typo / config tweak / one-liner"
- "Tests would slow me down here"

**All of these mean: delete the code. Start with a failing test.**

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. The test takes 30 seconds. |
| "I'll write the test after — same outcome" | Tests-after answer "what does this do?" Tests-first answer "what should this do?" Different questions, different coverage. |
| "I already manually tested all edge cases" | Manual testing is ad-hoc — no record, can't re-run. Coverage degrades to memory. |
| "Deleting hours of work is wasteful" | Sunk cost. Keeping unverified code is unbounded debugging tax. |
| "Keep as reference — I'll write tests first" | You will adapt the reference. That's testing-after. Delete means delete. |
| "Need to explore first to find the shape" | Fine. Throw the exploration away. Start with TDD. |
| "Test is hard to write" | Listen to the test — hard to test = hard to use. Fix the design first. |
| "Existing code in this area has no tests" | You're improving it. Add tests for the existing code as part of this change. |
| "Pragmatic means adapting the rule" | TDD *is* pragmatic — finds bugs before commit, cheaper than debugging post-deploy. The "shortcut" is the slow path. |
| "It's just a refactor — no behaviour change" | Then your tests still pass. Refactor under green. If there are no tests, write them first. |
