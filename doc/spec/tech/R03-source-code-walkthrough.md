---
title: Source Code Walkthrough
status: draft
created: 2026-05-08
updated: 2026-05-08
---

# Source Code Walkthrough

A guided tour of the Postiz repository for new engineers and AI agents. Tells you **where things are**, **how a request flows end-to-end**, and **where to make common changes**. Assumes you have read [CLAUDE.md](../../../CLAUDE.md), [R00-system-architecture.md](R00-system-architecture.md), and [R02-golden-principles.md](R02-golden-principles.md) first — those answer *what* and *why*; this answers *where* and *how*.

## How to use this doc

- **Onboarding day 1:** read top-to-bottom once, then run `pnpm install && pnpm run dev:docker && pnpm run dev` and click around the calendar in the browser.
- **Picking up a ticket:** jump to the *Where common changes go* section, find the recipe, and follow the layered path it gives you.
- **Reviewing a PR:** use the layer table in [R00](R00-system-architecture.md#layer-architecture) plus the file paths here to verify the change touched the right places — no controller-to-repository shortcuts, no DB I/O in workflows, etc.

## 60-second mental model

Postiz is a monorepo of cooperating apps that share one Prisma schema and one library tree:

```
HTTP / OAuth / MCP                    Browser
        │                                │
        ▼                                ▼
┌──────────────────┐              ┌──────────────┐
│ apps/backend     │  ◄── REST ── │ apps/frontend│  (Next.js 16, React 19, SWR via useFetch)
│ (NestJS, thin)   │              └──────────────┘
└────────┬─────────┘
         │  service calls
         ▼
┌────────────────────────────────────────────────────┐
│ libraries/nestjs-libraries  (the bulk of logic)    │
│   ├── database/prisma/<entity>/                    │   ← Service + Repository per entity
│   ├── integrations/social/<provider>.provider.ts   │   ← One file per social network
│   ├── agent / chat / openai / temporal / upload …  │
└──────┬─────────────────────────────────────────────┘
       │  repository.* → Prisma client
       ▼
   PostgreSQL  +  Redis  +  Temporal  +  R2 / FS
       ▲
       │  workflow.execute() / signal()
       │
┌──────┴──────────────┐
│ apps/orchestrator   │  Temporal worker — workflows orchestrate, activities do I/O
│ workflows/*         │
│ activities/*        │
└─────────────────────┘
```

Two flows you must internalise:

**1. Synchronous HTTP (e.g. "user clicks Save"):**
Frontend `useSWR` → `apps/backend/src/api/routes/<x>.controller.ts` → service in `libraries/nestjs-libraries/src/database/prisma/<entity>/<entity>.service.ts` → repository → Prisma → response.

**2. Background work (e.g. "publish this post at 3pm"):**
Controller persists state → kicks off a Temporal workflow (`temporalService.startWorkflow(...)`) → workflow in `apps/orchestrator/src/workflows/*` proxies activities → activities in `apps/orchestrator/src/activities/*` call services → services hit DB and the social provider in `libraries/nestjs-libraries/src/integrations/social/*`.

If a change does not fit one of these two shapes, stop and ask why — `/harness-design-critique` exists for exactly this.

## Top-level layout

```
postiz-app/
├── apps/
│   ├── backend/        # NestJS HTTP API (port 3000)
│   ├── orchestrator/   # NestJS + Temporal worker (port 3002, talks to Temporal at 7233)
│   ├── frontend/       # Next.js 16 / React 19 (dev port 4200)
│   ├── extension/      # Browser extension (Vite + CRX)
│   ├── sdk/            # Published NodeJS SDK
│   └── commands/       # Internal CLI commands
├── libraries/
│   ├── nestjs-libraries/      # ~80% of the server logic lives here
│   ├── helpers/               # Cross-cutting helpers (auth, swagger, useFetch, configuration checker)
│   └── react-shared-libraries/# Shared frontend pieces (form, sentry, toaster, translation)
├── doc/
│   ├── spec/                  # Product + tech specs (canonical source of truth)
│   └── changes/               # Append-only SDD change history (NNN-name/)
├── docker-compose.dev.yaml    # Postgres / Redis / Temporal for local dev
├── eslint.config.mjs          # ONE shared lint config — only runs from repo root
├── jest.config.ts             # ONE shared jest config — only runs from repo root
├── pnpm-workspace.yaml        # apps/* + libraries/*
└── tsconfig.base.json         # Defines @gitroom/* path aliases (use them, never deep relatives)
```

### Entry points (where execution starts)

| App | Entry file | What it does |
|---|---|---|
| backend | [apps/backend/src/main.ts](../../../apps/backend/src/main.ts) | Boots NestJS, mounts CORS / pipes / Swagger / MCP, listens on `PORT` (default 3000) |
| orchestrator | [apps/orchestrator/src/main.ts](../../../apps/orchestrator/src/main.ts) | Boots NestJS health server (port 3002); the Temporal worker is started by `getTemporalModule(true, ...)` inside [apps/orchestrator/src/app.module.ts](../../../apps/orchestrator/src/app.module.ts) |
| frontend | [apps/frontend/src/app/](../../../apps/frontend/src/app/) | Next.js App Router — there is no single `main.ts`; routing groups `(app)` / `(extension)` / `(provider)` are the top-level entry points |
| extension | [apps/extension/](../../../apps/extension/) | Vite + CRX manifest |

## Backend deep dive (`apps/backend`)

The backend is intentionally **thin**. Controllers receive HTTP, validate via DTOs, and call services that live in `libraries/nestjs-libraries`. If you find yourself writing more than a few lines in a controller, the logic belongs in a service.

```
apps/backend/src/
├── main.ts                         # bootstrap (CORS, validation pipe, Swagger, MCP)
├── app.module.ts                   # root module — wires APP_GUARD (PoliciesGuard, ThrottlerBehindProxyGuard)
├── api/
│   ├── api.module.ts               # registers all authenticated controllers + AuthMiddleware
│   └── routes/
│       ├── auth.controller.ts      # /auth, /auth/oauth/:provider, /auth/forgot, /auth/activate, …
│       ├── posts.controller.ts     # /posts            ← canonical example, read this one first
│       ├── integrations.controller.ts  # /integrations  (connect / list / disconnect social channels)
│       ├── analytics.controller.ts # /analytics
│       ├── billing.controller.ts   # /billing          (Stripe-fronted)
│       ├── stripe.controller.ts    # /stripe/webhook   (raw body parsed for signature)
│       ├── oauth.controller.ts     # internal OAuth2 server (issues `pos_*` tokens for public API)
│       ├── webhooks.controller.ts  # outbound webhook config
│       └── … one controller per feature
├── public-api/
│   ├── public.api.module.ts        # public REST API (rate-limited, key-or-token auth)
│   └── routes/v1/
│       └── public.integrations.controller.ts  # `/public/v1/...` — the surface used by SDK / n8n / Make
└── services/auth/
    ├── auth.middleware.ts          # cookie/JWT auth — applied to /api routes
    ├── public.auth.middleware.ts   # API-key / `pos_*` token auth — applied to /public-api routes
    ├── auth.service.ts             # signup / login / password reset / activation
    ├── permissions/
    │   ├── permissions.guard.ts    # APP_GUARD — invokes @CheckPolicies(...) decorators on controllers
    │   ├── permissions.service.ts
    │   └── permission.exception.class.ts  # `Sections` + `AuthorizationActions` enums
    └── providers/                   # Social-login providers (GitHub, Google, Farcaster, Wallet, generic OAuth)
```

### Canonical controller pattern

Read [apps/backend/src/api/routes/posts.controller.ts](../../../apps/backend/src/api/routes/posts.controller.ts) as the reference shape:

- `@ApiTags('Posts')` + `@Controller('/posts')` — Swagger picks these up.
- Constructor injects services from `@gitroom/nestjs-libraries/...`, never repositories directly.
- `@GetOrgFromRequest()` and `@GetUserFromRequest()` (in [libraries/nestjs-libraries/src/user/](../../../libraries/nestjs-libraries/src/user/)) extract the auth-resolved org and user that `AuthMiddleware` placed on the request.
- DTOs live in [libraries/nestjs-libraries/src/dtos/](../../../libraries/nestjs-libraries/src/dtos/), grouped by feature (`dtos/posts/create.post.dto.ts`, etc.). The global `ValidationPipe({ transform: true })` in `main.ts` validates them.
- `@CheckPolicies(...)` declares what permission the action requires — the `PoliciesGuard` enforces it.

### Auth & request shape

- `/api/*` (authenticated): `auth` cookie or header → `AuthMiddleware` resolves user → `showorg` header selects the active org → request gets `req.user` and `req.org`.
- `/public-api/v1/*`: `Authorization: <api-key>` (Settings → Developers) **or** `Authorization: Bearer pos_*` (issued by [oauth.controller.ts](../../../apps/backend/src/api/routes/oauth.controller.ts)). Rate limit: 30 req/hour, configurable via `API_LIMIT`.

## Orchestrator deep dive (`apps/orchestrator`)

All durable background work lives here. **No in-process cron, no BullMQ-only queues for new work** — everything goes through Temporal.

```
apps/orchestrator/src/
├── main.ts
├── app.module.ts                     # imports getTemporalModule(true, …) — the `true` boots a worker
├── health.controller.ts              # /health (k8s probe)
├── workflows/
│   ├── index.ts                      # the workflow bundle Temporal compiles
│   ├── post-workflows/
│   │   ├── post.workflow.v1.0.1.ts   # versioned — older history replays against this
│   │   └── post.workflow.v1.0.2.ts   # current
│   ├── autopost.workflow.ts          # AI-generated recurring posts
│   ├── refresh.token.workflow.ts     # token rotation per integration
│   ├── digest.email.workflow.ts      # daily / weekly digest scheduling
│   ├── send.email.workflow.ts
│   ├── streak.workflow.ts            # posting-streak gamification
│   └── missing.post.workflow.ts      # "you haven't posted in N days" reminders
├── activities/                        # ALL I/O happens here — not in workflows
│   ├── post.activity.ts
│   ├── autopost.activity.ts
│   ├── email.activity.ts
│   └── integrations.activity.ts
└── signals/                           # Temporal signals (poke / cancel)
```

### Workflow ↔ activity contract

Workflows must be **deterministic** — they cannot read clocks, call APIs, or touch the DB. Activities do that work and return values. The pattern in `post.workflow.v1.0.2.ts`:

```ts
const { getPostsList, updatePost, sendWebhooks /* ... */ } =
  proxyActivities<PostActivity>({
    startToCloseTimeout: '10 minute',
    retry: { maximumAttempts: 3, backoffCoefficient: 1, initialInterval: '2 minutes' },
  });
```

The `PostActivity` class is a regular `@Injectable()` NestJS service — registered in `app.module.ts` `activities = [...]` — and it injects `PostsService`, `IntegrationService`, etc. from `libraries/nestjs-libraries`. So a workflow's "DB call" is really `activity → service → repository → Prisma`.

### Workflow versioning

Posting has **versioned files** (`post.workflow.v1.0.1.ts`, `post.workflow.v1.0.2.ts`) because in-flight workflow executions must replay deterministically against the bytecode they started under. **Never edit an old version** — copy to a new `vX.Y.Z` file and migrate code that triggers new executions to use it.

### Temporal infrastructure helpers

- [libraries/nestjs-libraries/src/temporal/temporal.module.ts](../../../libraries/nestjs-libraries/src/temporal/temporal.module.ts) — `getTemporalModule(asWorker, workflowsPath?, activities?)`. Backend imports it with `false`; orchestrator with `true`.
- [libraries/nestjs-libraries/src/temporal/temporal.search.attribute.ts](../../../libraries/nestjs-libraries/src/temporal/temporal.search.attribute.ts) — typed search attributes (`postId`, `organizationId`) used to query workflows in the Temporal UI.
- [libraries/nestjs-libraries/src/temporal/temporal.register.ts](../../../libraries/nestjs-libraries/src/temporal/temporal.register.ts) and `infinite.workflow.register.ts` — register search attributes and start the long-lived recurring workflows (autopost, digest, streak) on boot.

## Frontend deep dive (`apps/frontend`)

Next.js 16 App Router. Routing happens via three top-level **route groups** (parens are Next.js syntax for "group without contributing to the URL"):

```
apps/frontend/src/app/
├── (app)/          # logged-in product (calendar, settings, billing, analytics, …)
│   ├── (site)/     # the main product chrome (sidebar, top nav, layout.tsx)
│   │   ├── launches/        ← post calendar / composer
│   │   ├── analytics/
│   │   ├── billing/
│   │   ├── settings/
│   │   ├── media/
│   │   ├── plugs/
│   │   ├── third-party/
│   │   ├── admin/
│   │   └── agents/
│   ├── (preview)/  # post-preview surfaces
│   ├── api/        # Next.js route handlers (proxy to backend, OG image, etc.)
│   ├── auth/       # login / register / forgot-password screens
│   ├── integrations/   # social-channel connect callback UI
│   ├── oauth/      # internal OAuth2 user-consent screens
│   └── layout.tsx
├── (extension)/    # iframe surfaces hosted inside the Chrome extension
│   └── modal/
└── (provider)/     # surfaces rendered for embedded provider previews
```

UI primitives: [apps/frontend/src/components/](../../../apps/frontend/src/components/) — one folder per feature (`launches`, `analytics`, `settings`, …) plus `ui/` for the reusable design-system pieces. Reach for `ui/` first; only build new primitives when the existing ones really don't fit.

Global styles: [apps/frontend/src/app/colors.scss](../../../apps/frontend/src/app/colors.scss) and [global.scss](../../../apps/frontend/src/app/global.scss). The `--color-custom*` CSS variables are deprecated — do not use them in new code.

### Data fetching: SWR via `useFetch`

The hook lives in [libraries/helpers/src/utils/custom.fetch.tsx](../../../libraries/helpers/src/utils/custom.fetch.tsx) and is provided through `<FetchWrapperComponent>` near the root. Every data fetch must:

1. Be its own named hook function (one hook per resource).
2. Call `useSWR` directly inside that hook — never wrap a hook returning hooks.
3. Comply with `react-hooks/rules-of-hooks` — never `eslint-disable` it.

Valid:

```ts
const useCommunity = () =>
  useSWR<CommunitiesListResponse>('communities', getCommunities);
```

Invalid (will fail review):

```ts
const useCommunity = () => ({
  communities: () => useSWR(...),  // hook returning hooks
  providers: () => useSWR(...),
});
```

### Frontend libraries to know

- [libraries/react-shared-libraries/src/form/](../../../libraries/react-shared-libraries/src/form/) — form primitives shared with the extension.
- [libraries/react-shared-libraries/src/toaster/](../../../libraries/react-shared-libraries/src/toaster/) — `toast.show(...)` for user-visible feedback.
- [libraries/react-shared-libraries/src/translation/](../../../libraries/react-shared-libraries/src/translation/) — i18n.

## Library deep dive (`libraries/nestjs-libraries`)

This is where the bulk of the server lives. Each top-level folder is a domain area:

| Folder | What's in it |
|---|---|
| `database/prisma/` | Per-entity service + repository pairs; `schema.prisma`; `database.module.ts` exports them all |
| `integrations/social/` | One provider class per social network (28+ files), all extending `social.abstract.ts` |
| `integrations/integration.manager.ts` | Discovers and exposes the provider list; consumed by activities and the integrations controller |
| `agent/` | LangGraph-style "agent graph" services that drive AI-assisted post generation |
| `chat/` | MCP server entry (`start.mcp.ts`), Mastra-based assistant, agent tool interfaces, OAuth middleware for the MCP surface |
| `openai/` | OpenAI client + content-extraction service |
| `temporal/` | Module factory, search-attribute registry, recurring-workflow bootstrapping |
| `redis/` | `ioRedis` singleton (used by throttler storage and feature caches) |
| `emails/` | Resend-fronted transactional email layer |
| `crypto/` | NowPayments crypto-billing client |
| `upload/` | Storage abstraction — local FS or Cloudflare R2 picked via `UploadFactory` |
| `videos/` | Agent Media UGC video generation |
| `track/` | Lightweight analytics/telemetry |
| `throttler/` | The `ThrottlerBehindProxyGuard` used in `app.module.ts` |
| `dtos/` | Validated request/response shapes — grouped by feature |
| `services/` | Cross-cutting services that don't belong to a single entity (Stripe, email, codes, exception filter) |

### Database / Prisma

Schema: [libraries/nestjs-libraries/src/database/prisma/schema.prisma](../../../libraries/nestjs-libraries/src/database/prisma/schema.prisma). One file. `pnpm run prisma-generate` re-emits the client; `pnpm run prisma-db-push` applies schema changes to the dev DB.

Each entity gets its own folder with two files (and only two files):

```
database/prisma/posts/
├── posts.service.ts       # business logic — talks to repository + other services
└── posts.repository.ts    # ONLY layer that calls the Prisma client
```

`PrismaRepository<'post'>` is a typed wrapper around `prisma.post` injected into repositories. See [posts.repository.ts](../../../libraries/nestjs-libraries/src/database/prisma/posts/posts.repository.ts) for the constructor pattern.

[database/prisma/database.module.ts](../../../libraries/nestjs-libraries/src/database/prisma/database.module.ts) is `@Global` — services and repositories are exported once and consumed everywhere.

### Social integrations

[libraries/nestjs-libraries/src/integrations/social.abstract.ts](../../../libraries/nestjs-libraries/src/integrations/social.abstract.ts) defines the contract every provider extends:

- `identifier: string` — the provider's id (e.g. `'x'`, `'linkedin'`).
- `maxConcurrentJob: number` — provider-level concurrency cap respected by activities.
- `handleErrors(body, status)` — translate provider-specific failure shapes into `{ type: 'refresh-token' | 'bad-body' | 'retry', value }`.
- `fetch(url, options, identifier, retries, ignoreConcurrency)` — wrapped HTTP that auto-retries on 429/500 and throws typed `RefreshToken` / `BadBody` failures Temporal can match on.
- `mention(token, query, id, integration)` — autocomplete for @-mentions in the composer.

The provider interface (`SocialProvider`, in `social/social.integrations.interface.ts`) adds `generateAuthUrl`, `authenticate`, `refreshToken`, `post`, `analytics`, etc. New providers implement both.

[integration.manager.ts](../../../libraries/nestjs-libraries/src/integrations/integration.manager.ts) is the registry — it imports every provider class explicitly. **Adding a provider means editing this file**; there is no runtime plugin loader.

## Where common changes go

The recipes below name every file you'll touch for the change. Use them as a checklist.

### Add a new HTTP endpoint

1. **DTO**: add `libraries/nestjs-libraries/src/dtos/<feature>/<thing>.dto.ts` with `class-validator` decorators.
2. **Service method**: add to existing `libraries/nestjs-libraries/src/database/prisma/<entity>/<entity>.service.ts` (or create the `<entity>/`-pair if the entity is new — see *Add a new entity*).
3. **Repository method**: if it touches Prisma, add to `<entity>.repository.ts`. Controllers/services must not use the Prisma client directly.
4. **Controller method**: add to `apps/backend/src/api/routes/<feature>.controller.ts` (existing) or register a new controller in `apps/backend/src/api/api.module.ts`. Apply `@CheckPolicies(...)` if it's a permissioned action.
5. **Public API?** If yes, also expose in `apps/backend/src/public-api/routes/v1/<feature>.controller.ts` with the public-API auth middleware applied.
6. **Test**: add an integration test next to the service. See `/harness-test-advisor`.
7. **Frontend hook**: add a single SWR hook function in `apps/frontend/src/components/<feature>/` calling the new endpoint via `useFetch`.

### Add a new social provider

1. Create `libraries/nestjs-libraries/src/integrations/social/<name>.provider.ts` extending `SocialAbstract` and implementing `SocialProvider`. Implement `generateAuthUrl`, `authenticate`, `refreshToken`, `post`, `handleErrors`, and `analytics` (when supported).
2. Register the class in [integration.manager.ts](../../../libraries/nestjs-libraries/src/integrations/integration.manager.ts) — both import and the provider list.
3. Frontend integration card / preview: add a folder under [apps/frontend/src/components/launches/providers](../../../apps/frontend/src/components/launches/) (look at how `x` or `linkedin` is structured) and wire it into the channel-picker.
4. Document required env vars in `.env.example` and the README's compliance section.
5. **No DB migration needed** for a new provider — `Integration.providerIdentifier` is already free-form text.

### Add a new background workflow

1. Decide if it belongs alongside posts (`workflows/post-workflows/` — version it!) or as a new top-level workflow file.
2. Add the workflow file: `apps/orchestrator/src/workflows/<name>.workflow.ts`. Keep it deterministic — only `proxyActivities` calls, no I/O.
3. Add the activity: `apps/orchestrator/src/activities/<name>.activity.ts`, an `@Injectable()` with `@Activity()` + `@ActivityMethod()` decorators (see `post.activity.ts`).
4. Register the activity in [apps/orchestrator/src/app.module.ts](../../../apps/orchestrator/src/app.module.ts) `activities = [...]`.
5. Re-export the workflow from [apps/orchestrator/src/workflows/index.ts](../../../apps/orchestrator/src/workflows/index.ts) so the worker picks it up.
6. To start it from the backend: inject `TemporalService` from `nestjs-temporal-core` and call `startWorkflow(...)` with typed search attributes from [temporal.search.attribute.ts](../../../libraries/nestjs-libraries/src/temporal/temporal.search.attribute.ts). For long-lived recurring workflows, register them in [infinite.workflow.register.ts](../../../libraries/nestjs-libraries/src/temporal/infinite.workflow.register.ts).

### Add a new database entity

1. Edit [schema.prisma](../../../libraries/nestjs-libraries/src/database/prisma/schema.prisma); run `pnpm run prisma-db-push` (dev) or generate a proper migration for prod.
2. Run `pnpm run prisma-generate` (also runs automatically on `pnpm install`).
3. Create the folder pair: `libraries/nestjs-libraries/src/database/prisma/<entity>/<entity>.service.ts` + `<entity>.repository.ts`.
4. Register both in [database.module.ts](../../../libraries/nestjs-libraries/src/database/prisma/database.module.ts) `providers` and `exports`.
5. DTOs in `libraries/nestjs-libraries/src/dtos/<entity>/`.
6. Then proceed as for *Add a new HTTP endpoint*.

### Add a new MCP tool

1. New tool file under [libraries/nestjs-libraries/src/chat/tools/](../../../libraries/nestjs-libraries/src/chat/tools/) implementing the agent-tool interface ([agent.tool.interface.ts](../../../libraries/nestjs-libraries/src/chat/agent.tool.interface.ts)).
2. Register in [load.tools.service.ts](../../../libraries/nestjs-libraries/src/chat/load.tools.service.ts).
3. The MCP server entry is [start.mcp.ts](../../../libraries/nestjs-libraries/src/chat/start.mcp.ts), invoked from [apps/backend/src/main.ts](../../../apps/backend/src/main.ts) — no changes needed there.

### Add a new frontend page

1. Create the route under the right group: usually `apps/frontend/src/app/(app)/(site)/<route>/page.tsx`. The `(site)/layout.tsx` provides the chrome.
2. Components under `apps/frontend/src/components/<feature>/`.
3. Data hooks alongside components, each its own function calling `useSWR` via `useFetch`.
4. Use existing primitives from `components/ui/` and tokens from `colors.scss` — do not introduce new component libraries from npm.
5. Validate the change in a browser before reporting done — see `/harness-browser-testing`.

## Conventions you'll trip over

- **pnpm only**, Node `>=22.12.0 <23.0.0`. `npm install` will silently drift the lockfile — don't.
- **Lint and tests run only from the repo root.** `pnpm exec jest path/to.spec.ts` works; `cd apps/backend && pnpm test` does not.
- **Path aliases over deep relatives.** Always `@gitroom/nestjs-libraries/...`, never `../../../libraries/nestjs-libraries/...`.
- **One `.env` for everything.** Apps load `../../.env` via `dotenv -e ../../.env`. Update `.env.example` whenever you add a variable.
- **Logging is `Sentry.logger`.** `import * as Sentry from '@sentry/nestjs'` (or `@sentry/nextjs`), then `const { logger } = Sentry`. Use `logger.fmt\`...\`` for variable interpolation.
- **OAuth2-only for social providers.** Never accept platform API keys; never scrape. The compliance section of the README is normative.
- **Workflows are deterministic.** No `Date.now()`, no `Math.random()`, no `fetch()`, no DB calls in workflow code — push it to an activity.
- **Don't edit old workflow versions.** Copy and bump.
- **No `eslint-disable react-hooks/rules-of-hooks`.** Restructure the hook.

## Where to look when something breaks

| Symptom | Start here |
|---|---|
| 401/403 on a logged-in route | [apps/backend/src/services/auth/auth.middleware.ts](../../../apps/backend/src/services/auth/auth.middleware.ts) and the `@CheckPolicies(...)` on the controller |
| 401 on a public-API call | [apps/backend/src/services/auth/public.auth.middleware.ts](../../../apps/backend/src/services/auth/public.auth.middleware.ts); check the `Authorization` header form (`<api-key>` vs `Bearer pos_*`) |
| Post stuck in `QUEUE` / `ERROR` | Temporal UI at `localhost:8080` — find by `postId` search attribute; then `apps/orchestrator/src/activities/post.activity.ts` |
| Token refresh failing | [refresh.token.workflow.ts](../../../apps/orchestrator/src/workflows/refresh.token.workflow.ts) and [refresh.integration.service.ts](../../../libraries/nestjs-libraries/src/integrations/refresh.integration.service.ts) |
| Provider 4xx/5xx | The provider's `handleErrors` in `libraries/nestjs-libraries/src/integrations/social/<provider>.provider.ts` — Temporal classifies failures from its return value |
| Frontend showing stale data | The `useSWR` cache key — make sure mutations call `mutate(key)` after writing |
| Throttler errors (`429 Too Many Requests`) | `API_LIMIT` env var, applied in [app.module.ts](../../../apps/backend/src/app.module.ts) `ThrottlerModule.forRoot(...)` |
| Stripe webhook signature mismatch | [stripe.controller.ts](../../../apps/backend/src/api/routes/stripe.controller.ts) — relies on `rawBody: true` set in `main.ts` |
| MCP tool not callable | [start.mcp.ts](../../../libraries/nestjs-libraries/src/chat/start.mcp.ts), [load.tools.service.ts](../../../libraries/nestjs-libraries/src/chat/load.tools.service.ts) |

## When in doubt

- For *what* and *why* questions about a feature: read the matching [`doc/spec/product/`](../product/) file.
- For *what layer am I in* questions: [R00-system-architecture.md](R00-system-architecture.md).
- For *can I do this* questions: [R02-golden-principles.md](R02-golden-principles.md), then `/harness-design-critique` if still unclear.
- For *is this test enough* questions: `/harness-test-advisor`.
- For *did I just break a rule* sweeps: `/harness-gc`.

Once you've spent a week here, this doc should feel obvious. Submit corrections to it as part of the change that proves it wrong — `/harness-sync-specs` is the formal sweep, but inline fixes in any PR that touches the relevant area are welcome.
