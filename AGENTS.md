# AGENTS.md

This file provides guidance to AI coding agents (Codex, Jules, Cursor, Factory, and others) when working in this repository. The canonical project description, build/test recipe, and directory map live in the harness-scaffold-managed `## Postiz` / `## Build & Test` / `## Directory Map` sections further down — read those first if you need orientation. The sections below cover the rules and conventions that the scaffold doesn't.

## Tooling & Package Management

- pnpm only — never use npm or yarn. Workspace is pnpm + the workspaces declared in `pnpm-workspace.yaml` (`apps/*`, `libraries/*`).
- Node `>=22.12.0 <23.0.0` (per `package.json` engines). Install runs `prisma-generate` automatically via `postinstall`.
- Linting and tests run **only from the repo root** (root has the single shared `eslint.config.mjs` and `jest.config.ts`).
- Never install frontend components from npmjs — write native components instead.

## Common commands

Run all from the repo root unless noted.

```bash
# Install (auto-runs prisma generate)
pnpm install

# Development
pnpm run dev                # all apps in parallel (extension, orchestrator, backend, frontend)
pnpm run dev-backend        # backend + frontend only
pnpm run dev:backend        # backend only (other dev:<app> scripts also exist)
pnpm run dev:docker         # spin up local Postgres/Redis/Temporal via docker-compose.dev.yaml

# Build
pnpm run build              # frontend, backend, orchestrator (workspace-concurrency=1)
pnpm run build:frontend     # individual app builds also available

# Tests
pnpm test                                                # full suite with coverage + junit reporter
pnpm exec jest path/to/file.spec.ts                      # single test file
pnpm exec jest -t "name of test"                         # filter by test name

# Prisma (schema lives at libraries/nestjs-libraries/src/database/prisma/schema.prisma)
pnpm run prisma-generate
pnpm run prisma-db-push     # push schema (accepts data loss)
pnpm run prisma-reset       # force-reset DB
```

## Repository layout

Monorepo with TypeScript path aliases defined in `tsconfig.base.json`. Use these aliases — do not write deep relative imports across packages:

| Alias | Path |
|---|---|
| `@gitroom/backend/*` | `apps/backend/src/*` |
| `@gitroom/frontend/*` | `apps/frontend/src/*` |
| `@gitroom/orchestrator/*` | `apps/orchestrator/src/*` |
| `@gitroom/extension/*` | `apps/extension/src/*` |
| `@gitroom/helpers/*` | `libraries/helpers/src/*` |
| `@gitroom/nestjs-libraries/*` | `libraries/nestjs-libraries/src/*` |
| `@gitroom/react/*` | `libraries/react-shared-libraries/src/*` |

### Apps

- `apps/backend` — NestJS HTTP API. Controllers under `src/api/routes` (auth-required) and `src/public-api/routes` (public API). Auth/permissions logic in `src/services/auth`. The backend should stay thin: most logic lives in `libraries/nestjs-libraries`.
- `apps/orchestrator` — NestJS + Temporal worker. `src/workflows` holds workflow definitions (post, autopost, refresh-token, digest-email, streak, missing-post). `src/activities` holds activity implementations. This is where background jobs run — scheduling a post triggers a Temporal workflow, not an in-process queue.
- `apps/frontend` — Next.js 16 (React 19). Routing in `src/app` (route groups: `(app)`, `(extension)`, `(provider)`). Components in `src/components`. UI primitives in `src/components/ui`. Global styles: `src/app/colors.scss`, `src/app/global.scss`.
- `apps/extension` — Browser extension (Vite + CRX).
- `apps/sdk`, `apps/commands` — programmatic SDK and CLI commands.

### Libraries

- `libraries/nestjs-libraries` — the bulk of server-side logic. Notable subtrees:
  - `database/prisma/<entity>/` — each entity has `<entity>.service.ts` and `<entity>.repository.ts` (Prisma). Schema in `database/prisma/schema.prisma`.
  - `integrations/social/` — one provider file per social network (`x.provider.ts`, `linkedin.provider.ts`, `bluesky.provider.ts`, etc.). New social channels are added here behind `social.abstract.ts` / `social.integrations.interface.ts`. The `IntegrationManager` discovers providers.
  - Other top-level modules: `agent`, `chat`, `crypto`, `emails`, `openai`, `redis`, `sentry`, `temporal`, `throttler`, `track`, `upload`, `videos`.
- `libraries/helpers` — cross-cutting helpers: `auth`, `configuration`, `decorators`, `subdomain`, `swagger`, `utils` (includes `custom.fetch.tsx` — see frontend rules below).
- `libraries/react-shared-libraries` — shared frontend pieces: `form`, `helpers`, `sentry`, `toaster`, `translation`.

## Backend architecture rules

- Strictly layered: **Controller → Service → Repository** (no shortcuts). For more complex flows: **Controller → Manager → Service → Repository**.
- Controllers in `apps/backend` should be thin — import services from `libraries/nestjs-libraries`. Most server logic belongs in libs/server, not in `apps/backend`.
- New social platform support goes in `libraries/nestjs-libraries/src/integrations/social/<name>.provider.ts` following the `social.abstract.ts` interface.
- Background work (post publishing, token refresh, digests) runs as Temporal workflows in `apps/orchestrator`, not as in-process schedulers.

## Frontend architecture rules

- Tailwind 3 (`apps/frontend/tailwind.config.cjs` + repo-level `tailwind.config.js`). Before writing a component, check `apps/frontend/src/app/colors.scss`, `apps/frontend/src/app/global.scss`, and the tailwind config. **The `--color-custom*` CSS variables are deprecated — do not use them.** Look at existing components in `src/components` for the right design.
- Data fetching: always use SWR via the `useFetch` hook from `libraries/helpers/src/utils/custom.fetch.tsx`.
- Each SWR hook must be a separate function and comply with `react-hooks/rules-of-hooks`. **Never** add `eslint-disable-next-line` to bypass it.

  Valid:
  ```ts
  const useCommunity = () => useSWR<CommunitiesListResponse>('communities', getCommunities);
  ```

  Invalid (hook returning hooks):
  ```ts
  const useCommunity = () => ({
    communities: () => useSWR(...),
    providers: () => useSWR(...),
  });
  ```

## Logging (Sentry)

The Sentry logger is the standard logging interface. Import as:

```ts
import * as Sentry from '@sentry/nextjs'; // or '@sentry/nestjs' on the server
const { logger } = Sentry;
```

Use `logger.fmt` template literal for structured variable interpolation:

```ts
logger.info('Updated profile', { profileId: 345 });
logger.debug(logger.fmt`Cache miss for user: ${userId}`);
```

Sentry init should set `enableLogs: true`. `Sentry.consoleLoggingIntegration({ levels: [...] })` can forward console calls automatically.

## Environment

- Apps load env via `dotenv -e ../../.env` (root `.env`). Keep `.env.example` updated when adding new variables.
- The Prisma schema, Postgres, Redis (BullMQ + cache), Temporal, and Resend (email) are core infra dependencies. Local dev brings them up with `pnpm run dev:docker`.

<!-- harness-scaffold: begin project-context -->
## Postiz

AI-driven social media scheduling tool that posts to 28+ channels (publishing, calendar, analytics, team management, media library). See [`doc/spec/product/00-overview.md`](doc/spec/product/00-overview.md) for the canonical product overview and [`doc/spec/tech/R00-system-architecture.md`](doc/spec/tech/R00-system-architecture.md) for the system architecture.

## Build & Test

> Postiz is **pnpm-only**. Do not use `npm` or `yarn`. Node `>=22.12.0 <23.0.0`. See the "Common commands" section above for the full list — the snippets below are the harness-scaffold-managed minimum.

```bash
# Install dependencies (auto-runs prisma generate)
pnpm install

# Build (workspace-concurrency=1)
pnpm run build

# Run tests (jest, from repo root only)
pnpm test
```

## Directory Map

```
├── apps/                       # NestJS / Next.js / extension apps
│   ├── backend/                # NestJS HTTP API (thin controllers)
│   ├── commands/               # CLI commands
│   ├── extension/              # Browser extension (Vite + CRX)
│   ├── frontend/               # Next.js 16 + React 19
│   ├── orchestrator/           # NestJS + Temporal worker (workflows, activities)
│   └── sdk/                    # Programmatic SDK
├── libraries/
│   ├── helpers/                # Cross-cutting helpers (auth, configuration, fetch)
│   ├── nestjs-libraries/       # Bulk of server logic (database, integrations, services)
│   └── react-shared-libraries/ # Shared frontend pieces (form, toaster, translation)
├── doc/
│   ├── changes/                # Append-only SDD change history (NNN-name/)
│   └── spec/                   # Product + tech specs (sources of truth)
├── .harness/                   # Harness-scaffold tooling, templates, gates
└── .github/                    # GitHub workflows + issue/PR templates
```
<!-- harness-scaffold: end project-context -->

<!-- harness-scaffold: begin reference-index -->
## Harness Engineering Index

**Skills** — invoke with `/skill-name` when starting the relevant activity:

| Skill | When to use |
|---|---|
| `/harness-sdd-workflow` | Starting any code change (mandatory — read first) |
| `/harness-tdd-workflow` | Writing or reviewing tests |
| `/harness-retrospective` | After completing a change |
| `/harness-sync-specs` | Auditing spec freshness |
| `/harness-import-spec` | Importing external docs into specs |
| `/harness-test-advisor` | Advising on integration/e2e test coverage |
| `/harness-gc` | Scanning codebase for golden principle / rule violations |
| `/harness-browser-testing` | Validating UI changes in the browser |
| `/harness-e2e-testing` | Writing or running integration / e2e tests |

**Reference docs** — read from `.harness/docs/` when relevant:

| When you are... | Read this file |
|---|---|
| Writing or reviewing typescript code | `.harness/docs/engineering-rules-typescript.md` |
| Running in a multi-agent session | `.harness/docs/sandbox.md` + `.harness/docs/worktree-guide.md` |

**Verification:** Before writing any code, state: "I have read [file names] for this task."
<!-- harness-scaffold: end reference-index -->

<!-- harness-scaffold: begin spec-index -->
## Spec Index

### Product Specs (`doc/spec/product/`)
- [00-overview.md](doc/spec/product/00-overview.md) — Postiz Product Overview
- [01-publishing-and-scheduling.md](doc/spec/product/01-publishing-and-scheduling.md) — Publishing and Scheduling
- [02-channels-and-providers.md](doc/spec/product/02-channels-and-providers.md) — Channels and Providers
- [03-analytics.md](doc/spec/product/03-analytics.md) — Analytics
- [04-marketplace-and-collaboration.md](doc/spec/product/04-marketplace-and-collaboration.md) — Marketplace and Collaboration
- [05-programmatic-access.md](doc/spec/product/05-programmatic-access.md) — Programmatic Access

### Tech Specs (`doc/spec/tech/`)
- [R00-system-architecture.md](doc/spec/tech/R00-system-architecture.md) — Postiz System Architecture
- [R01-code-conventions.md](doc/spec/tech/R01-code-conventions.md) — Code Conventions
- [R02-golden-principles.md](doc/spec/tech/R02-golden-principles.md) — Golden Principles & Agent Rules
<!-- harness-scaffold: end spec-index -->
