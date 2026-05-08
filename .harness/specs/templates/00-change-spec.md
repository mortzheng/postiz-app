---
id: <NNN>
title: <Change Title>
status: draft
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

# Change <NNN>: <Change Title>

## Summary

<!-- 1–2 sentences describing what this change does and why. -->

## What This Change Introduces

1. <!-- First thing introduced or modified -->
2. <!-- Second thing -->

## Specs to Update

<!-- List spec files that need updating. Check each off when confirmed done. Remove section if none. -->

- [ ] `specs/...`

<!-- ACCEPTANCE CRITERIA QUALITY RULES:
     Criteria must be Evaluator-checkable without human judgement.

     BAD (subjective, unverifiable):
       - "the feature works correctly"
       - "code quality is good"
       - "the UI looks right"

     GOOD (exact, observable):
       - "running `harness-install init` creates `CLAUDE.md` with a `## SDD Workflow` section"
       - "`tests/test_installer.py::test_sdd_init` passes"
       - "`harness-install verify` exits 0 when all managed sections are present"
       - "`doc/multi-agent/features.json` exists and parses as valid JSON with at least one feature"

     Format: start with an action verb + exact command/path/observable state.
-->
## Acceptance Criteria

- [ ] <!-- Condition that must be true for this change to be "done" -->
- [ ] <!-- Another condition -->

## E2E / Integration Test Scenarios

<!-- WHEN TO USE THIS SECTION:
     Fill this in if your change touches user-facing behaviour, API endpoints,
     or cross-module boundaries that should be validated end-to-end.
     Remove this section if the change is purely internal (refactor, config, etc.).

     Write each scenario as a testable AC: action verb + exact command + observable state.
     For guidance on writing e2e tests, invoke the relevant skill:
       - Web projects: /harness-browser-testing
       - Mobile projects: /harness-mobile-testing
       - General integration/e2e: /harness-e2e-testing
-->

- [ ] <!-- E2E scenario: e.g., "Running `npx playwright test e2e/feature.spec.ts` passes" -->
- [ ] <!-- E2E scenario -->

<!-- INTEGRATION AC NOTE: If this change introduces a new long-running subsystem
     (background thread, scheduler, daemon, worker), add at least one integration AC
     verifying that the subsystem is started from the entry point with real dependencies
     (e.g. a real send_fn, real client, real config) — not stubs or no-ops. -->
