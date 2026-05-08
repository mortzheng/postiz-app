---
id: 2
title: "Fix: align CLAUDE.md with harness scaffold and Postiz tooling reality"
status: done
created: 2026-05-08
updated: 2026-05-08
---

## Problem

`CLAUDE.md` carries the harness-scaffold default `project-context` block (lines 125–170) unchanged from initial scaffold. As a result it contradicts the curated Postiz section above it:

- Two `## Project` headings — first says "Postiz is an AI-driven social media scheduling tool…", second says only `gitroom` plus a `<!-- TODO -->`.
- A second `## Build & Test` block that prescribes `npm install` / `npm run build` / `npm test`. The repo is **pnpm-only** per the curated section above and per `package.json` engines (`pnpm@…`, `engines.node >=22.12.0 <23.0.0`).
- A `## Directory Map` that lists `Jenkins/` and stops at `apps/<name>/src/` granularity, omitting the `libraries/` tree where the bulk of server logic lives. The "Repository layout" section above already covers this with apps + libraries + path aliases.

Net effect: an agent reading top-to-bottom sees pnpm rules, then sees the scaffold block claim npm — the rules contradict each other and the scaffold block adds no information that the curated section above doesn't already cover better.

## Fix

Edit `CLAUDE.md` in place between the `<!-- harness-scaffold: begin project-context -->` and `<!-- harness-scaffold: end project-context -->` markers so the managed block reflects this repo:

- Replace `## Project` body — name it Postiz, keep the one-line description consistent with `doc/spec/product/00-overview.md`.
- Replace `## Build & Test` commands with the pnpm equivalents already documented in `doc/spec/tech/R00-system-architecture.md` (`pnpm install`, `pnpm run build`, `pnpm test`).
- Rewrite `## Directory Map` to match the actual top-level layout (apps/, libraries/, doc/, .harness/) — drop `Jenkins/`, surface `libraries/` and its subpackages.

The harness-scaffold managed markers stay intact so future `harness-install` syncs can still locate the section. The hash in `.harness/harness.toml` (`project-context = "d29e72af5f18f604"`) will drift after this edit; that drift is expected for a customised scaffold block and will be re-pinned the next time `harness-install` runs.

The reference-index and spec-index sections (lines 172–214) are already accurate and stay untouched.

## Acceptance Criteria

- [x] `CLAUDE.md` contains exactly one `## Project` heading (verified by `grep -c '^## Project$' CLAUDE.md` returning `1`).
- [x] `CLAUDE.md` contains exactly one `## Build & Test` heading (verified by `grep -c '^## Build & Test$' CLAUDE.md` returning `1`, after removing the duplicate).
- [x] No bare `npm install`, `npm run build`, or `npm test` commands appear in `CLAUDE.md` (verified by `grep -nE '(^| |\t)npm (install|run build|test)' CLAUDE.md` returning nothing — the word-boundary form is required so `pnpm install` is not a false positive).
- [x] The managed harness-scaffold block (between `<!-- harness-scaffold: begin project-context -->` and `<!-- harness-scaffold: end project-context -->`) names the project as `Postiz`, not `gitroom`, and contains no `<!-- TODO -->` placeholder.
- [x] The Directory Map inside the managed block lists `apps/`, `libraries/`, `doc/`, and `.harness/` as top-level entries and does not list `Jenkins/`.
- [x] The harness-scaffold begin/end markers for `project-context` and `reference-index` are still present in `CLAUDE.md` (verified by `grep -c 'harness-scaffold: begin' CLAUDE.md` returning `≥2`).

## Completion Notes

- Completion gate ran clean once the dev environment was set up (Node 22 via brew, `pnpm install`) and after change `003-fix-test-baseline` repaired the long-broken `jest.config.ts` (`@nx/jest` import) and removed the failing `e2e/example.spec.ts` Playwright scaffold. Gate now exits 0 for `001`, `002`, and `003`.
