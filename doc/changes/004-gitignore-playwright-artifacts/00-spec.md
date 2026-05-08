---
id: 4
title: "Fix: ignore Playwright run artifacts"
status: done
created: 2026-05-08
updated: 2026-05-08
---

## Problem

`npx playwright test` (run by `harness verify_completion` and by humans locally) writes `playwright-report/` and `test-results/` at the repo root. Neither directory is in `.gitignore`, so they show up as untracked after every gate run.

## Fix

Add `/playwright-report` and `/test-results` to `.gitignore` under a `# Playwright artifacts` heading.

## Acceptance Criteria

- [x] `.gitignore` contains a line `/playwright-report` (verified by `grep -x '/playwright-report' .gitignore` printing one match).
- [x] `.gitignore` contains a line `/test-results` (verified by `grep -x '/test-results' .gitignore` printing one match).
- [x] `git status --short` does not list `playwright-report/` or `test-results/` as untracked.
