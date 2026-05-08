---
title: Channels and Providers
status: draft
created: 2026-05-07
updated: 2026-05-07
---

# Channels and Providers

## Overview

A "channel" (UI) and "integration" (API) refer to the same concept: a connected social account on a third-party platform. Postiz owns the OAuth flow, token storage, and per-platform posting rules for each provider. New providers are added by contributing a backend provider class plus a frontend component — the system is designed to be extended.

## Target Users

- End users connecting their own social accounts.
- Operators of self-hosted Postiz instances configuring OAuth credentials per platform.
- Contributors adding support for a new social platform.

## Features

### Supported channels

Postiz currently supports the following providers (per `docs.postiz.com/providers/*` and `docs.postiz.com/public-api/providers/*`):

**Social**: X (Twitter), LinkedIn, LinkedIn Page, Facebook, Instagram, Instagram Standalone, Threads, Bluesky, Mastodon, Warpcast (Farcaster), Nostr, VK, MeWe.
**Video**: YouTube, TikTok, Twitch, Kick.
**Community**: Reddit, Lemmy, Discord, Slack, Telegram, Skool, Whop.
**Design**: Pinterest, Dribbble.
**Blogging**: Medium, Dev.to, Hashnode, WordPress.
**Business**: Google My Business, Listmonk, Moltbook.

#### Acceptance Criteria
- [ ] Connecting a supported provider creates a row exposed by `GET /integrations` (the integration list).
- [ ] Each connected integration has a stable `id` usable as `integration.id` when creating a post.
- [ ] `GET /integrations/{id}/is-connected` reports whether the integration is currently usable.

### OAuth onboarding

For platforms with OAuth2 (the majority), Postiz drives the standard authorization-code flow and stores the resulting tokens. Tokens are refreshed by a background workflow (`refresh.token.workflow`).

#### Acceptance Criteria
- [ ] `GET /integrations/connect` returns an authorization URL for the requested platform.
- [ ] After user authorization, the OAuth callback exchanges the code for tokens via the provider's `authenticate()` method.
- [ ] Token refresh runs on a Temporal workflow, not in-line in request handlers.

### Self-hosted operator configuration

In self-hosted installs, no providers are enabled by default. The operator must register OAuth client credentials per platform via env vars in the root `.env`. After changing env vars, containers must be recreated (`docker compose down && docker compose up`).

#### Acceptance Criteria
- [ ] On a fresh self-hosted install, `GET /providers/available` (or equivalent) lists only providers whose OAuth credentials are present in env.
- [ ] Adding new env-var-configured providers requires a container restart in the Docker Compose deployment.

### Cookie-based integrations (Skool, etc.)

Some platforms have no public OAuth API. Postiz supports them via a Chrome extension that captures cookies for the user's session. The `EXTENSION_ID` env var ties an installation to its extension build.

#### Acceptance Criteria
- [ ] When `EXTENSION_ID` is configured, the Chrome extension can supply cookies for cookie-based providers.
- [ ] Skool (and similar platforms) are usable via the cookie pathway.

### Per-platform posting rules

Each provider declares its own posting rules: max character length, required settings, allowed media types, and helper tools. The MCP `integrationSchema` tool exposes these rules to AI agents.

#### Acceptance Criteria
- [ ] `integrationSchema` returns max character length, required settings schema, and helper tools array per platform.
- [ ] `POST /posts` rejects a post whose content violates a platform's published constraints.

<!-- TODO: docs.postiz.com lists per-provider settings on individual `public-api/providers/*` pages but does not aggregate the validation matrix. Confirm validation behaviour against the live API. -->

### Provider extension model (for contributors)

Adding a new provider requires:

1. **DTO** — at `libraries/nestjs-libraries/src/dtos/posts/providers-settings/<name>.dto.ts` (skip if no per-post settings).
2. **Provider class** — at `libraries/nestjs-libraries/src/integrations/social/<name>.provider.ts` implementing `refreshToken()`, `generateAuthUrl()`, `authenticate()`, and `post()` from `social.abstract.ts`.
3. **Manager registration** — register the provider in `libraries/nestjs-libraries/src/integrations/integration.manager.ts`.
4. **Frontend component** — a settings + preview component using the `withProvider` HOC.
5. **Custom hooks (optional)** — `useCustomProviderFunction` for dynamic platform queries.
6. **Frontend registration** — add to `apps/frontend/src/components/launches/providers/show.all.providers.tsx`.

#### Acceptance Criteria
- [ ] A new provider is discoverable through `IntegrationManager` once registered.
- [ ] The frontend renders the new provider's settings + preview only when the provider is registered in `show.all.providers.tsx`.
- [ ] The provider passes `refreshToken`, `generateAuthUrl`, `authenticate`, and `post` integration tests (or equivalents) before merge.

## Out of Scope

- **Per-platform settings details** — see the `public-api/providers/*.md` pages on docs.postiz.com.
- **Analytics endpoints** — see [03-analytics.md](03-analytics.md).
- **Posting flow** — see [01-publishing-and-scheduling.md](01-publishing-and-scheduling.md).
