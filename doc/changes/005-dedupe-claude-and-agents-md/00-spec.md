---
id: 5
title: "Dedupe CLAUDE.md and bring AGENTS.md to parity"
status: in-progress
created: 2026-05-08
updated: 2026-05-08
---

## Problem

Two issues in the agent-guidance docs at the repo root:

1. CLAUDE.md duplicates the project description — the manual `## Project` section at the top says the same thing as the harness-scaffold-managed `## Postiz` section further down (and the scaffold version is strictly better, with spec links).
2. AGENTS.md still holds the unfilled harness-scaffold stub: project name `gitroom`, `<!-- TODO: add a one-line project description -->`, `npm install` / `npm run build` / `npm test` examples (Postiz is pnpm-only), and a sparse directory map. Codex / Cursor / Factory and other non-Claude agents read AGENTS.md and currently get no useful guidance from it.

## Fix

- Drop the duplicate `## Project` section at the top of CLAUDE.md and add a one-line pointer to the canonical scaffold-managed sections.
- Rewrite AGENTS.md so its body mirrors CLAUDE.md (Tooling, Common commands, Repository layout, backend/frontend rules, Sentry logging, Environment) and its harness-scaffold blocks match the populated content used by CLAUDE.md (project description with spec links, pnpm-based build/test stub, accurate directory map, harness reference index, spec index).

## Acceptance Criteria

- [x] CLAUDE.md no longer contains the manual `## Project` heading at the top; readers are pointed to the scaffold-managed `## Postiz` section instead.
- [x] AGENTS.md `## Postiz` (or equivalent) section names Postiz, describes it, and links to `doc/spec/product/00-overview.md` and `doc/spec/tech/R00-system-architecture.md` — no `<!-- TODO: add a one-line project description -->` placeholder remains.
- [x] AGENTS.md Build & Test snippet uses `pnpm install`, `pnpm run build`, `pnpm test` (no `npm`/`yarn` examples).
- [x] AGENTS.md contains the same Tooling, Common commands, Repository layout (path aliases + Apps + Libraries), backend/frontend architecture rules, Sentry logging, and Environment guidance as CLAUDE.md.
- [x] AGENTS.md Directory Map matches the populated map in CLAUDE.md (apps/, libraries/, doc/, .harness/, .github/) instead of the sparse stub.
- [x] AGENTS.md Spec Index lists the same six product specs and three tech specs as CLAUDE.md.
