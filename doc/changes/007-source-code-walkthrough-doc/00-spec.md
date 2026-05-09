---
id: 7
title: "Add source code walkthrough doc to onboard new engineers and AI agents"
status: done
created: 2026-05-08
updated: 2026-05-08
---

## Problem

The existing tech specs explain *what* and *why* but not *where*:

- [R00-system-architecture.md](../../spec/tech/R00-system-architecture.md) — C4 boxes, layer rules, architecture decisions. Stays at the container/component level; doesn't say "here is the file you edit when you want to do X".
- [R01-code-conventions.md](../../spec/tech/R01-code-conventions.md) — placeholder template, currently empty.
- [R02-golden-principles.md](../../spec/tech/R02-golden-principles.md) — invariants and retrospective rules. Tells you what *not* to do; doesn't show you the codebase.
- [CLAUDE.md](../../../CLAUDE.md) — operational rules (pnpm, aliases, lint scope, frontend SWR). Useful but not a tour.

A new engineer or AI agent landing here has to reverse-engineer file layout, request flow, controller↔service↔repository wiring, the workflow/activity split, and the social-provider extension model from scratch. That ramp-up is repeated by every new contributor and every fresh agent session.

## Fix

Add a new tech spec, [doc/spec/tech/R03-source-code-walkthrough.md](../../spec/tech/R03-source-code-walkthrough.md), as a guided code tour:

- A 60-second mental model with two reference flows (sync HTTP and background workflow).
- Per-app deep dives (`apps/backend`, `apps/orchestrator`, `apps/frontend`) naming the entry-point file and the canonical example file in each (e.g. `posts.controller.ts`, `post.workflow.v1.0.2.ts`, the `(app)/(site)/` route group).
- A library deep dive (`libraries/nestjs-libraries`) including the per-entity service+repository pattern under `database/prisma/`, the social provider contract (`social.abstract.ts` + `integration.manager.ts`), and the chat/MCP entry point.
- "Where common changes go" recipes — every file you touch to add an HTTP endpoint, social provider, workflow, entity, MCP tool, or frontend page.
- Conventions you'll trip over (pnpm-only, lint-from-root, path aliases, single `.env`, Sentry logger, deterministic workflows, no editing old workflow versions).
- A "where to look when something breaks" symptom→file table.

Followed by the standard tech spec frontmatter (`status: draft`, today's `created`/`updated`), so it slots into the existing `R00`/`R01`/`R02` series.

## Acceptance Criteria

- [x] `doc/spec/tech/R03-source-code-walkthrough.md` exists and parses with frontmatter `title: Source Code Walkthrough`, `status: draft` (verified by `grep -E '^title:|^status:' doc/spec/tech/R03-source-code-walkthrough.md` printing both lines).
- [x] The walkthrough names the canonical posts controller path `apps/backend/src/api/routes/posts.controller.ts` (verified by `grep -F 'apps/backend/src/api/routes/posts.controller.ts' doc/spec/tech/R03-source-code-walkthrough.md` matching).
- [x] The walkthrough names the social abstract path `libraries/nestjs-libraries/src/integrations/social.abstract.ts` (verified by `grep -F 'libraries/nestjs-libraries/src/integrations/social.abstract.ts' doc/spec/tech/R03-source-code-walkthrough.md` matching).
- [x] The walkthrough references the versioned post workflow `post.workflow.v1.0.2.ts` (verified by `grep -F 'post.workflow.v1.0.2.ts' doc/spec/tech/R03-source-code-walkthrough.md` matching).
- [x] The walkthrough contains a "Where common changes go" (or equivalent recipe) section (verified by `grep -i -E 'common changes|common change recipes|where common changes go' doc/spec/tech/R03-source-code-walkthrough.md` matching).
- [x] The walkthrough contains a "where to look when something breaks" troubleshooting table (verified by `grep -i 'when something breaks' doc/spec/tech/R03-source-code-walkthrough.md` matching).
- [x] [CLAUDE.md](../../../CLAUDE.md) "Spec Index → Tech Specs" section lists the new R03 entry (verified by `grep -F 'R03-source-code-walkthrough.md' CLAUDE.md` matching).
