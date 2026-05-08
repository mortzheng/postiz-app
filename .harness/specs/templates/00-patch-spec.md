---
id: <NNN>
title: "Fix: <short description>"
status: draft
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---

## Problem

<!-- What is broken and why. Include root cause if known. -->

## Fix

<!-- What was changed to address it. Reference files and functions. -->

## Tests Added

<!-- Test cases added to prevent regression. Remove section if none. -->

- `test_<name>` — <what it verifies>

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
