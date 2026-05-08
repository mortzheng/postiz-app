---
title: Postiz Product Overview
status: draft
created: 2026-05-07
updated: 2026-05-07
---

# Postiz Product Overview

## Purpose

Postiz is a social media scheduling and management platform. It lets users publish, schedule, and analyse posts across 28+ social, video, community, design, and blogging channels from a single place; generate post content with AI; and exchange or buy posts through a built-in marketplace. Postiz runs as a hosted service or as a self-hosted installation — feature parity is maintained between the two.

## Mental Model

A user composes a post and drops it onto a calendar against one or more connected channels (called "integrations" in the API). The backend hands the post to a Temporal workflow which publishes it to the right platform at the right time, with automatic retries and per-platform task-queue isolation. The same workflow engine handles token refresh, missing-content detection, digest emails, and streak tracking — so anything time-bound or platform-bound is a workflow, not a request handler.

## Target Users

- Individual creators and social media managers scheduling content across many channels.
- Teams and agencies that need shared calendars, member invites, and post-trading.
- Developers and automation builders using the Public API, NodeJS SDK, n8n node, Make.com integration, MCP server, or CLI to drive Postiz programmatically.

<!-- TODO: docs.postiz.com does not formally enumerate target users; the list above is derived from feature surface area (team collaboration, marketplace, public API/CLI/MCP). Confirm or tighten before promoting status to active. -->

## Core Capabilities

1. **Multi-channel scheduling.** Schedule posts and articles to 28+ channels: X, LinkedIn, LinkedIn Page, Facebook, Instagram, Instagram Standalone, Threads, Bluesky, Mastodon, Warpcast (Farcaster), Nostr, VK, YouTube, TikTok, Reddit, Lemmy, Discord, Slack, Telegram, Pinterest, Dribbble, Medium, Dev.to, Hashnode, WordPress, Google My Business, Listmonk, MeWe, Skool, Whop, Kick, Twitch, Moltbook.
2. **Calendar view.** Visualise the publishing schedule and reschedule by drag-and-drop.
3. **AI content generation.** Generate post copy and AI-assisted UGC videos (via the Agent Media integration) directly inside Postiz.
4. **Analytics.** Platform-level and post-level analytics, accessible via UI, Public API, and CLI.
5. **Marketplace.** Exchange or buy posts from other Postiz members.
6. **Team collaboration.** Invite team members to comment, schedule, and manage posts together.
7. **Media library.** Upload images and videos for reuse; supports local file storage or Cloudflare R2.
8. **Programmatic access.**
   - Public REST API at `/public/v1` (API key or OAuth2 with `pos_` tokens).
   - Official NodeJS SDK on npm.
   - CLI (`postiz`) wrapping the Public API for terminal/script use.
   - MCP server exposing 8 tools for AI agents (Claude, n8n nodes, etc.).
   - n8n custom node and Make.com integration.
9. **Browser extension.** Chrome extension for cookie-based platform integrations (e.g. Skool).
10. **Self-host or cloud.** Deploy via Docker, Docker Compose, or Kubernetes (Helm); or use the hosted version at platform.postiz.com.
11. **Background reliability.** Temporal-backed workflows for posting, token refresh, digest emails, missing-post detection, and streak tracking — durable, retryable, observable in the Temporal UI.

## Out of Scope

The hosted product makes explicit non-goals (per Postiz Compliance, README and docs):

- **No scraping or automation outside platform APIs.** Postiz uses only official, platform-approved OAuth flows.
- **No user-supplied API keys for social platforms in the hosted product.** Users authenticate directly with each platform via OAuth; Postiz does not collect, store, or proxy platform API keys or access tokens.
- **Self-managed integrations are the operator's responsibility.** No social providers are configured by default in self-hosted installs — the operator must register OAuth credentials per platform via env vars.
- **API throughput is rate-limited.** 30 requests per hour per API key on the Public API; bulk scheduling is supported by allowing multiple posts per request.

## Design Principles

<!-- TODO: docs.postiz.com does not name design principles explicitly. Inferred from the compliance and architecture sections — confirm before promoting status to active.

- Platform compliance first: only official OAuth flows; never scrape.
- Durable execution for time- and platform-bound work: anything that must "happen later" or "succeed eventually" is a Temporal workflow, not an in-process job.
- Hosted/self-hosted feature parity.
- Extensibility via a structured provider model (one DTO + one provider class + one frontend component per channel).
-->

## Sub-feature Specs

Detailed behaviour and acceptance criteria for each capability live in:

- [01-publishing-and-scheduling.md](01-publishing-and-scheduling.md) — calendar, post composer, scheduling lifecycle, AI content + video generation, media library
- [02-channels-and-providers.md](02-channels-and-providers.md) — supported channels, OAuth onboarding, per-platform settings
- [03-analytics.md](03-analytics.md) — platform and post analytics
- [04-marketplace-and-collaboration.md](04-marketplace-and-collaboration.md) — marketplace, teams, member invites, comments
- [05-programmatic-access.md](05-programmatic-access.md) — Public API, OAuth2, NodeJS SDK, CLI, MCP server, n8n, Make.com
