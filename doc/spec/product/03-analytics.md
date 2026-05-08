---
title: Analytics
status: draft
created: 2026-05-07
updated: 2026-05-07
---

# Analytics

## Overview

Postiz exposes two analytics surfaces: **platform-level** (an entire connected channel — e.g., follower count over time on an X account) and **post-level** (engagement on a specific scheduled post — likes, comments, shares, impressions). Both are accessible through the UI, the Public REST API, and the CLI.

## Target Users

- Creators tracking growth on individual channels.
- Marketers correlating campaign posts with engagement.
- Data consumers pulling analytics into dashboards via the Public API or CLI.

## Features

### Platform analytics

Per-channel time-series of metrics like Followers, Impressions, and Likes.

#### Acceptance Criteria
- [ ] `GET /analytics/{integration}` returns 200 for a connected integration.
- [ ] The response is an array of `{ label, data: [{ total, date }], percentageChange }` objects.
- [ ] The `date` query parameter accepts a lookback in days (e.g. `7`, `30`, `90`).
- [ ] `total` values are returned as strings; `date` values follow `YYYY-MM-DD`.
- [ ] Available across the 27 platforms documented under `public-api/providers/*`.

### Post analytics

Per-post engagement metrics (likes, comments, shares, impressions, etc.) over the lookback window. The exact metric set varies by platform.

#### Acceptance Criteria
- [ ] `GET /analytics/post/{postId}` returns 200 for a published post.
- [ ] The response shape mirrors platform analytics: array of `{ label, data: [{ total, date }], percentageChange }`.
- [ ] The `date` query parameter accepts a lookback in days.
- [ ] The metric set adapts per platform (e.g., Likes, Comments, Shares, Impressions).

### Rate limiting

Analytics endpoints share the Public API rate limit.

#### Acceptance Criteria
- [ ] All analytics endpoints are subject to the 30 requests/hour limit per API key.
- [ ] Hitting the limit returns the standard rate-limited response of the throttler.

### CLI access

Analytics are also accessible from the command line via `postiz analytics:*`.

#### Acceptance Criteria
- [ ] `postiz analytics --help` lists at least platform and post-level subcommands.
- [ ] CLI analytics commands return JSON output (compatible with `jq` and shell scripting).

## Out of Scope

- **Cross-channel rollups, custom dashboards, and exports** — not documented in docs.postiz.com.
- **Historical data backfill semantics** — not documented; treat platform constraints as the source of truth.
- **Realtime / streaming analytics** — analytics is snapshot/lookback, not streaming.

<!-- TODO: docs.postiz.com analytics pages cover the API shape but not retention windows, sampling, or behaviour for newly-connected integrations. Confirm before promoting. -->
