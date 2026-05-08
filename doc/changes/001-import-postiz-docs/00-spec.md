---
id: 1
title: "Import: Postiz product overview, system architecture, and per-feature specs from docs.postiz.com"
status: done
created: 2026-05-07
updated: 2026-05-08
---

## Problem

The repository's `doc/spec/product/` and `doc/spec/tech/` directories hold harness-scaffold template stubs. They do not yet describe Postiz itself — what it does, how it is built, or its sub-features — so neither humans nor agents have an authoritative spec to read.

## Fix

Import the canonical product and architecture content from https://docs.postiz.com (introduction, howitworks, developer-guide, quickstart, providers/overview, public-api/introduction, public-api/posts/create, public-api/analytics/{platform,post}, configuration/reference, configuration/create-provider, installation/docker-compose, mcp/introduction, mcp/tools, cli/introduction) and restructure into the harness spec schemas:

- Replace `doc/spec/product/00-overview.md` (project-level overview).
- Replace `doc/spec/tech/R00-system-architecture.md` (C4 system context + container overview + project structure + key constraints + boot command + ADRs).
- Add per-feature product specs: `01-publishing-and-scheduling.md`, `02-channels-and-providers.md`, `03-analytics.md`, `04-marketplace-and-collaboration.md`, `05-programmatic-access.md`.
- Record sources in `doc/spec/.import-manifest.json` for future `harness-import-spec` sync runs.

All new specs use `status: draft`; sections without docs.postiz.com source material are marked with explicit TODO comments rather than invented content.

## Acceptance Criteria

- [x] `doc/spec/product/00-overview.md` exists with `status: draft` frontmatter and contains Purpose, Mental Model, Target Users, Core Capabilities (numbered list of ≥10 capabilities), Out of Scope, and Design Principles sections.
- [x] `doc/spec/tech/R00-system-architecture.md` exists with `status: draft` frontmatter and contains System Context, Container Overview (table with frontend/backend/orchestrator/postgres/redis/temporal rows), Project Structure, Layer Architecture, Key Constraints, Boot Command, and Architecture Decisions sections.
- [x] Per-feature product specs `01-publishing-and-scheduling.md`, `02-channels-and-providers.md`, `03-analytics.md`, `04-marketplace-and-collaboration.md`, `05-programmatic-access.md` exist under `doc/spec/product/` with `status: draft` frontmatter.
- [x] `doc/spec/.import-manifest.json` exists, parses as valid JSON, and lists every target spec file in a single combined entry whose `source_ref` references the docs.postiz.com pages used.
- [x] Every section that lacked source material in docs.postiz.com is marked with a `<!-- TODO: ... -->` comment in-place — no invented content.
