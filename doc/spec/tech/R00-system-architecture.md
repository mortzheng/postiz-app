---
title: Postiz System Architecture
status: draft
created: 2026-05-07
updated: 2026-05-07
---

# Postiz System Architecture

Follows the C4 model: System Context → Containers → Components.

## System Context

```
[End user / team member] ─┐
[Developer / automation]  ├──► [Postiz] ──► [Social platforms × 28+]
[AI agent (MCP client)]   ┘                ──► [Stripe] (billing, hosted)
                                            ──► [Resend] (email notifications)
                                            ──► [OpenAI / AI providers] (post + video gen)
                                            ──► [Cloudflare R2 / local FS] (media)
```

| Element | Type | Description |
|---|---|---|
| End user / team member | Person | Schedules posts via the Next.js web UI. |
| Developer / automation | Person | Drives Postiz via Public API, NodeJS SDK, CLI, n8n node, or Make.com. |
| AI agent (MCP client) | Person/system | Connects to the MCP server; uses 8 tools to manage posts. |
| Postiz | Software System | This system. Schedules, publishes, and analyses cross-channel posts. |
| Social platforms | External | 28+ providers (X, LinkedIn, Facebook, Instagram, YouTube, TikTok, …). OAuth2 only. |
| Stripe | External | Subscription billing for the hosted product. |
| Resend | External | Transactional and digest email delivery. |
| AI providers | External | OpenAI and others, used for post generation and the Agent Media UGC video integration. |
| R2 / local FS | External | Object/file storage for uploaded media. |

<!-- TODO: Stripe/Resend/OpenAI inferred from package.json + CLAUDE.md, not from a single docs.postiz.com page. Confirm the external-system list matches operational reality before promoting. -->

## Container Overview

| Container | Technology | Purpose | Spec |
|---|---|---|---|
| frontend | Next.js 16, React 19, Tailwind 3 | Web UI (calendar, composer, analytics, settings) | apps/frontend |
| backend | NestJS 10 (HTTP) | Public + private REST APIs, auth, OAuth callbacks, Stripe webhooks, MCP entry | apps/backend |
| orchestrator | NestJS + Temporal worker | Executes durable workflows: post publishing, token refresh, digest email, streak, missing-post | apps/orchestrator |
| extension | Vite + React (CRX) | Chrome extension for cookie-based integrations (e.g. Skool) | apps/extension |
| sdk / commands | TypeScript packages | Published NodeJS SDK and internal CLI commands | apps/sdk, apps/commands |
| postgres | PostgreSQL 17 | Primary data store; schema managed by Prisma | libraries/nestjs-libraries/.../prisma |
| redis | Redis 7.2 | Caching, throttler storage, BullMQ where used | — |
| temporal | Temporal server + UI + ES | Durable workflow engine; UI on port 8080 | — |
| storage | Local FS or Cloudflare R2 | Media uploads | configuration/r2 |

## Project Structure

```
postiz-app/
├── apps/
│   ├── frontend/        # Next.js (web UI)
│   ├── backend/         # NestJS HTTP API (thin controllers)
│   ├── orchestrator/    # NestJS + Temporal worker (workflows + activities)
│   ├── extension/       # Chrome extension
│   ├── sdk/             # NodeJS SDK package
│   └── commands/        # CLI commands package
├── libraries/
│   ├── nestjs-libraries/  # Server logic — DB repositories, integrations/social/*, agent, chat, temporal, …
│   ├── helpers/           # Cross-cutting helpers (auth, swagger, useFetch)
│   └── react-shared-libraries/  # Shared frontend (form, sentry, toaster, translation)
├── docker-compose.dev.yaml
└── libraries/nestjs-libraries/src/database/prisma/schema.prisma
```

## Layer Architecture

| Layer | Contents | May call |
|---|---|---|
| Controller | `apps/backend/src/api/routes/*`, `apps/backend/src/public-api/routes/*` | Service, Manager |
| Manager (optional) | Cross-service orchestration in `libraries/nestjs-libraries` | Service |
| Service | `libraries/nestjs-libraries/src/.../<entity>.service.ts`, integration providers | Repository, other Services |
| Repository | `libraries/nestjs-libraries/src/database/prisma/<entity>/<entity>.repository.ts` | Prisma client only |
| Workflow (Temporal) | `apps/orchestrator/src/workflows/*` | Activities only — no direct DB / HTTP |
| Activity (Temporal) | `apps/orchestrator/src/activities/*` | Service / Repository |

**Agent gate:** Each layer may only call layers listed in "May call". A controller calling a repository directly, or a workflow doing DB I/O, is a violation — surface it before proceeding.

## Key Constraints

- **3-layer rule (Controller → Service → Repository).** No shortcuts. Manager is permitted between Controller and Service for complex flows.
- **Background work must be a Temporal workflow.** Post publishing, token refresh, digest emails, streak tracking, missing-content checks — all live in `apps/orchestrator`. Do not introduce in-process schedulers or cron-in-the-API.
- **Workflows are deterministic.** All I/O (DB, HTTP, AI calls) happens in activities; workflows orchestrate activities only.
- **OAuth-only for social providers.** No platform-API-key paste flow; no scraping. New providers conform to `social.abstract.ts` (`refreshToken`, `generateAuthUrl`, `authenticate`, `post`).
- **Single shared `.env`.** Unlike typical NX layouts, all apps load the same root `.env` via `dotenv -e ../../.env`.
- **Linting/testing only from repo root.** Single `eslint.config.mjs` and `jest.config.ts`.
- **Frontend data fetching uses SWR via `useFetch`.** Each SWR call must be a separate hook complying with `react-hooks/rules-of-hooks`.

## Security Guidelines

- **Never store or proxy users' platform API keys.** Authenticate via OAuth2 against each platform. The hosted product never asks users to paste platform credentials.
- **Public API auth.** Either an API key (`Authorization: <key>`) from Settings → Developers → Public API, or an OAuth2 token prefixed `pos_`. Rate limit: 30 req/hour.
- **JWT secret.** `JWT_SECRET` must be unique per installation.
- **Sentry logging.** Use `Sentry.logger` (with `enableLogs: true`) — see CLAUDE.md.
- **Credential refresh.** Token rotation runs as a Temporal workflow; do not refresh tokens in request handlers.

## Golden Principles & Agent Rules

See `doc/spec/tech/R02-golden-principles.md` for project-specific invariants and agent retrospective rules. Run `/harness-gc` to scan for violations.

## Boot Command

```bash
# 1. Bring up Postgres / Redis / Temporal locally
pnpm run dev:docker

# 2. Run all apps (extension, orchestrator, backend, frontend)
pnpm run dev
```

Default ports:

| Service | Port |
|---|---|
| frontend (dev) | 4200 |
| backend | 3000 |
| frontend (docker-compose self-host) | 4007 |
| Temporal UI | 8080 |

## Architecture Decisions

| Decision | Choice | Rejected alternatives | Reason |
|---|---|---|---|
| Background job engine | Temporal | BullMQ-only, in-process cron | Durable retries, deterministic replay, per-platform task-queue isolation, built-in monitoring UI. |
| Database ORM | Prisma | TypeORM, raw SQL | Single schema source of truth in `schema.prisma`; codegen for both backend and orchestrator. |
| Frontend framework | Next.js 16 + React 19 | Pure Vite SPA | App-router routing groups, server components for parts of the UI, easier hosted deployment. |
| Monorepo tool | pnpm workspaces | npm/yarn workspaces, Nx-everything | pnpm-only policy; NX Jest preset still used but no project graph required. |
| Provider extension model | One DTO + provider class in `integrations/social/` + frontend `withProvider` HOC | Plugin runtime loading | Compile-time registration via `IntegrationManager` keeps types end-to-end. |
| Auth for hosted social platforms | Official OAuth2 only | API-key paste, scraping | Platform compliance; documented in README "Postiz Compliance". |
| Single shared `.env` | All apps load `../../.env` | Per-app `.env` | Simpler local + Docker deployment. |
