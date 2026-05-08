---
title: Programmatic Access
status: draft
created: 2026-05-07
updated: 2026-05-07
---

# Programmatic Access

## Overview

Postiz exposes the same core functionality through multiple machine-facing surfaces: a Public REST API, an official NodeJS SDK, a CLI, an MCP server for AI agents, an n8n custom node, and a Make.com integration. All surfaces share the same API key / OAuth2 credential system and the same 30 req/hour rate limit.

## Target Users

- Developers building integrations or workflows against Postiz.
- Automation builders using n8n, Make.com, or Zapier.
- AI agents (Claude, GPT, etc.) operating Postiz via the MCP server.
- Shell/script authors using the CLI.

## Features

### Public REST API

**Base URLs:**
- Cloud: `https://api.postiz.com/public/v1`
- Self-hosted: `https://{NEXT_PUBLIC_BACKEND_URL}/public/v1`

**Authentication:**

| Method | Format | How to obtain |
|---|---|---|
| API key | `Authorization: <api-key>` | Settings → Developers → Public API |
| OAuth2 token | `Authorization: pos_<token>` | OAuth2 flow via `/public-api/oauth` |

OAuth2 tokens allow acting on behalf of other users — intended for multi-user integrations and third-party apps.

**Rate limit:** 30 requests per hour per key. Schedule multiple posts per request to batch efficiently.

**Terminology note:** The UI calls them "channels"; the API calls them "integrations". Same thing: a connected social account.

**Core endpoints:**

| Resource | Endpoints |
|---|---|
| Posts | `POST /posts`, `GET /posts`, `PUT /posts/{id}/status`, `DELETE /posts/{id}`, `DELETE /posts/group/{groupId}`, `GET /posts/missing-content`, `PUT /posts/{id}/release-id` |
| Integrations | `GET /integrations`, `GET /integrations/connect`, `DELETE /integrations/{id}`, `GET /integrations/find-slot`, `GET /integrations/{id}/is-connected` |
| Analytics | `GET /analytics/{integration}?date=N`, `GET /analytics/post/{postId}?date=N` |
| Uploads | `POST /uploads/upload-file`, `POST /uploads/upload-from-url` |
| Video | `GET /video/function`, `POST /video/generate` |
| Notifications | `GET /notifications/list` |

#### Acceptance Criteria
- [ ] `POST /posts` with a valid API key returns 200 and `[{ postId, integration }]`.
- [ ] `GET /integrations` returns the list of connected channels for the authenticated user.
- [ ] Requests beyond 30/hour return a throttled response.
- [ ] API key auth and OAuth2 (`pos_` prefix) both resolve to a valid user context.

### NodeJS SDK

An official NodeJS SDK is published to npm. It wraps the Public API with typed methods.

#### Acceptance Criteria
- [ ] `npm install @postiz/node` (or equivalent) installs the SDK.
- [ ] The SDK exposes at minimum: post creation, integration listing, and analytics retrieval.

<!-- TODO: docs.postiz.com/sdk is not in the llms.txt index; SDK API surface is not formally documented. Derive from apps/sdk. -->

### CLI (`postiz`)

The `postiz` CLI wraps the Public API for terminal and shell-script use. All commands emit JSON output.

**Install:** `npm install -g postiz` (or pnpm).

**Authentication:**
- Preferred: `postiz auth:login` — device-flow OAuth2; credentials saved to `~/.postiz/credentials.json`.
- Alternative: set `POSTIZ_API_KEY` env var. OAuth2 credentials take priority when both are present.
- Self-hosted: set `POSTIZ_API_URL` env var.

**Commands:**

| Group | Commands |
|---|---|
| Auth | `auth:login` |
| Posts | create, list, delete by ID |
| Integrations | list (with settings schemas) |
| Analytics | platform analytics, post analytics |
| Media | upload file |
| Advanced | trigger dynamic tools, manage missing release IDs |

#### Acceptance Criteria
- [ ] `postiz auth:login` completes the device-flow and writes credentials to `~/.postiz/credentials.json`.
- [ ] `postiz --help` lists all command groups.
- [ ] All commands return valid JSON (parseable by `jq`).
- [ ] `POSTIZ_API_URL` redirects all commands to a self-hosted backend.

### MCP server

The MCP server lets AI agents (Claude, n8n AI nodes, etc.) manage Postiz social media programmatically via 8 standardised tools.

**Endpoint:**
- Bearer token: `Authorization: Bearer <api-key>` at `https://api.postiz.com/mcp`
- URL-embedded: `https://api.postiz.com/mcp/<api-key>`

**Tools:**

| Tool | Purpose |
|---|---|
| `integrationList` | List connected social accounts (returns integration ID, name, avatar, platform). |
| `integrationSchema` | Get platform-specific posting rules — max char length, required settings, helper tools. |
| `triggerTool` | Run platform helper functions (e.g. fetch channel list, subreddit suggestions, page IDs). |
| `schedulePostTool` | Primary post creation: accepts `socialPost[]` with `integrationId`, UTC datetime, link shortening, type (`draft`/`schedule`/`now`), content array, platform settings. |
| `generateImageTool` | Generate an AI image from a prompt; returns `{ mediaId, url }`. |
| `generateVideoOptions` | List available video generation types, orientations, and parameter schemas. |
| `videoFunctionTool` | Run video-generator helpers (e.g. fetch voice options) before generation. |
| `generateVideoTool` | Generate a video by identifier, orientation, and custom params; returns a video URL. |

**Typical agent workflow:**
1. `integrationList` → find integration IDs.
2. `integrationSchema(platform)` → get constraints.
3. `schedulePostTool(socialPost[])` → submit the post.

#### Acceptance Criteria
- [ ] An MCP client can authenticate using either bearer-token or URL-embedded key format.
- [ ] `integrationList` returns at least `id`, `name`, and `platform` per connected account.
- [ ] `schedulePostTool` with a valid `socialPost[]` creates a post and returns its ID.
- [ ] `generateImageTool` returns a `mediaId` usable in a subsequent `schedulePostTool` call.
- [ ] `generateVideoTool` returns a video URL usable in a subsequent `schedulePostTool` call.

### n8n custom node

Postiz publishes an n8n custom node (`n8n-nodes-postiz` on npm) that exposes Postiz actions as n8n workflow nodes.

#### Acceptance Criteria
- [ ] Installing `n8n-nodes-postiz` in an n8n instance adds Postiz nodes to the node palette.

<!-- TODO: specific node actions and configuration are not in docs.postiz.com. -->

### Make.com integration

Postiz has a native Make.com (formerly Integromat) app.

#### Acceptance Criteria
- [ ] A Make.com user can authenticate with their Postiz API key via the official app at apps.make.com/postiz.
- [ ] At least post scheduling is available as a Make action.

<!-- TODO: specific Make modules and triggers are not in docs.postiz.com. -->

## Out of Scope

- **Webhooks** — `POST /webhooks` endpoint exists in the codebase but is not detailed in docs.postiz.com.
- **Zapier integration** — referenced in the README introduction ("platforms like N8N, Make.com, Zapier") but has no dedicated docs page.
- **SDK version compatibility and changelog** — not in docs.postiz.com.
