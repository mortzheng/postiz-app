Use when deciding how much integration or e2e test coverage a change warrants — surfaces integration boundaries and recommends where tests will pay off, but never blocks completion or writes tests.

**Steps:**

### Step 1 — Read the active change spec

1. Read `.harness/current-change` to get the active change directory (e.g., `doc/changes/054-test-advisor-skill`).
2. Read `<change-dir>/00-spec.md` — look for the `## Integration Boundaries` table and the `## What This Change Introduces` section.
3. If the spec has no `## Integration Boundaries` table, report that and suggest adding one per the spec schema, then stop.

### Step 2 — Extract boundaries and affected modules

1. Parse the `## Integration Boundaries` table. Each row has columns: Boundary, Type, Test location, Status.
2. Parse `## What This Change Introduces` to identify the modules, layers, and components this change touches.
3. Build a list of all declared boundaries with their current status (`covered`, `absent`, `skipped (env)`, etc.).

### Step 3 — Scan for existing test coverage

For each boundary, check whether matching test files exist in conventional directories:

| Language/Platform | Directories to check |
|---|---|
| Python | `tests/integration/`, `tests/e2e/` |
| TypeScript | `tests/integration/`, `tests/e2e/`, `e2e/` |
| Java | `src/test/java/**/integration/`, `src/test/java/**/e2e/` |
| React Native | `e2e/` |

Also check:
- Any test file paths explicitly listed in the Integration Boundaries table
- Test files whose names match the module names from Step 2

For each boundary, classify:
- **Covered** — a matching test file exists and contains tests relevant to this boundary
- **Uncovered** — no matching test file found, or the test file does not exercise this boundary

### Step 4 — Risk-rank uncovered boundaries

Rank each uncovered boundary by risk category:

| Risk | Boundary type | Examples |
|---|---|---|
| **HIGH** | Data mutation | DB writes, file system writes, state changes |
| **HIGH** | Cross-service | API calls, message queues, webhooks, external services |
| **MEDIUM** | Configuration/wiring | Dependency injection, middleware ordering, route registration |
| **LOW** | Read-only | Cache reads, config lookups, static asset serving |

Use keywords in the boundary description and type column to classify:
- DB, database, write, insert, update, delete, mutation → HIGH (data)
- API, HTTP, REST, gRPC, queue, message, webhook, external → HIGH (cross-service)
- config, middleware, DI, inject, wire, route, register → MEDIUM
- read, cache, lookup, fetch, get, static → LOW

### Step 5 — Check environment readiness

For each recommended test, verify whether the required test infrastructure is likely available:

| Infrastructure | How to detect |
|---|---|
| Database | `docker-compose.yml` with db/postgres/mysql service, or DB config in test settings |
| API services | `docker-compose.yml` with service definitions, or mock server config |
| Playwright browsers | `npx playwright install` output, or `node_modules/playwright/.local-browsers/` |
| Detox / mobile emulators | `.detoxrc.js` present, or Xcode/Android SDK paths |
| Message queues | `docker-compose.yml` with rabbitmq/redis/kafka service |

### Step 6 — Output the report

Produce a structured report in this format:

```
## Test Coverage Assessment for Change <NNN>

### Covered Boundaries
| Boundary | Test suite | Notes |
|---|---|---|
| <boundary> | <test file path> | <brief note on what's tested> |

### Uncovered Boundaries (by risk)
| Risk | Boundary | Why it matters | Suggested test location |
|---|---|---|---|
| HIGH | <boundary> | <consequence of not testing> | <recommended file path> |
| MEDIUM | <boundary> | <consequence> | <recommended file path> |
| LOW | <boundary> | <consequence> | <recommended file path> |

### Recommended Test Scenarios
#### <test file path> (new file / extend existing)
- <scenario 1: specific test case description>
- <scenario 2: specific test case description>
- <scenario 3: specific test case description>

### Environment Readiness
| Dependency | Status | Setup needed |
|---|---|---|
| <dependency> | <found / not found> | <setup command or "ready"> |
```

If all boundaries are covered, say so and suggest reviewing whether the existing tests are sufficient for the change's scope.

---

## Rules

- **Never write tests.** This skill only advises — the human decides what to implement.
- **Never modify the spec.** Do not update the Integration Boundaries table or any other part of the spec.
- **Ground recommendations in the actual codebase.** Check that suggested test locations follow the project's existing test directory structure and naming conventions.
- **Be specific about test scenarios.** Instead of "test the auth flow", say "test that expired token triggers refresh and returns new token".
- **Flag environment gaps early.** If a recommended test requires infrastructure that is not detected, say so explicitly in the Environment Readiness section.
- **Flag manual exercise gaps for user-facing changes.** If the change touches a UI, CLI, API consumed by a human, or any user interaction path, and no end-to-end test exercises that path, recommend a manual exercise step before `status: done`. Mechanical gates miss interaction-layer bugs.
