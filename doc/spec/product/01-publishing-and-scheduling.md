---
title: Publishing and Scheduling
status: draft
created: 2026-05-07
updated: 2026-05-07
---

# Publishing and Scheduling

## Overview

The publishing-and-scheduling subsystem is Postiz's core: composing a post once and having it published to one or more channels, either immediately, on a schedule, or after manual review. Every post lives on a calendar; a Temporal workflow takes ownership of the post at the requested time and drives it to the connected channel.

## Target Users

- Creators and social media managers who plan content ahead.
- Teams who collaborate on draft posts before publishing.
- Automation users (Public API, CLI, MCP) submitting posts programmatically.

## Features

### Calendar view

User-facing schedule visualisation. Posts appear on the calendar by their scheduled time, with their target channel and current state.

#### Acceptance Criteria
- [ ] Calendar lists posts ordered by scheduled UTC datetime.
- [ ] Each calendar entry surfaces the target integration (channel) and post state.

<!-- TODO: docs.postiz.com does not document calendar UX in detail (drag-drop semantics, re-schedule rules, recurring posts). Confirm against the live UI before promoting. -->

### Post composer

Compose post content per integration. Supports HTML formatting (specific tags only), platform-specific settings, link shortening, tags, and media attachments.

#### Acceptance Criteria
- [ ] A post submission accepts an array of `posts`, each binding `integration.id` to a `value` (content array) and `settings` (per-platform).
- [ ] Each `settings` object carries a required `__type` discriminator that matches the platform.
- [ ] The composer supports a `shortLink` boolean to opt into link shortening.
- [ ] The composer accepts `tags` as an array of tag objects.

### Post lifecycle states

A post moves through three top-level types: `draft`, `schedule`, and `now`. Scheduled posts are owned by a Temporal workflow until execution.

#### Acceptance Criteria
- [ ] `POST /posts` accepts `type` ∈ {`draft`, `schedule`, `now`}.
- [ ] When `type` is not `draft`, the request must include a non-empty `posts` array; drafts may be saved without one.
- [ ] When `type` is `schedule`, `date` is an ISO-8601 datetime in UTC.
- [ ] Successful submission returns HTTP 200 with an array of `{ postId, integration }`.

### AI content generation

Postiz can generate post copy with AI. The MCP server additionally exposes `generateImageTool` and a video pipeline (`generateVideoOptions` → `videoFunctionTool` → `generateVideoTool`) for image and video assets attached to posts.

#### Acceptance Criteria
- [ ] AI-generated images return a media ID + image URL that can be attached to a post.
- [ ] AI-generated videos return a video URL that can be attached to a post.
- [ ] Video generation supports multiple orientations (orientation parameter is `output`).

<!-- TODO: docs.postiz.com mentions "Generate posts with AI" but does not document the in-product AI composer flow (model used, prompt UX, regeneration). Confirm before promoting. -->

### Agent Media UGC video integration

Partner integration for AI-generated UGC videos. The introduction page calls out Agent Media for "engaging video content" scheduled directly through Postiz.

#### Acceptance Criteria
- [ ] Videos produced via Agent Media can be attached to a post and scheduled like any other media asset.

<!-- TODO: depth of the Agent Media partnership (auth, billing, supported formats) is not in docs.postiz.com. Treat as TODO. -->

### Media library

Upload, store, and reuse images and videos. Storage backend is local FS by default; Cloudflare R2 is supported via configuration.

#### Acceptance Criteria
- [ ] `POST /uploads/upload-file` accepts a file upload and returns a media reference usable by `POST /posts`.
- [ ] `POST /uploads/upload-from-url` accepts an external URL and ingests the asset into the media library.
- [ ] The storage backend is selectable between local FS and Cloudflare R2 via env vars.
- [ ] When `DISABLE_IMAGE_COMPRESSION=true`, uploaded images are not recompressed.

### Background reliability

Each post is published by an orchestrator workflow. Workflows are durable, retry on failure, and isolate per platform via Temporal task queues. The same orchestrator runs `refresh.token.workflow`, `digest.email.workflow`, `missing.post.workflow`, `streak.workflow`, `autopost.workflow`, and `send.email.workflow`.

#### Acceptance Criteria
- [ ] A post scheduled at a future time is published by a Temporal workflow at (≈) that time.
- [ ] A failed post-publishing workflow retries automatically per its Temporal retry policy.
- [ ] Operators can observe workflow state in the Temporal UI on port 8080 in local dev.

### Post management

List, change status, delete, and inspect posts. Posts can be grouped (delete-by-group) and have release IDs that may need to be reconciled.

#### Acceptance Criteria
- [ ] `GET /posts` returns paginated post list.
- [ ] `PUT` (or equivalent) on the change-status endpoint moves a post between states.
- [ ] `DELETE /posts/{id}` and `DELETE /posts/group/{groupId}` remove individual or grouped posts.
- [ ] `GET /posts/missing-content` returns posts that need release-ID reconciliation.
- [ ] `PUT /posts/{id}/release-id` updates the release ID for a post.

## Out of Scope

- **Cross-posting analytics correlation** is handled separately — see [03-analytics.md](03-analytics.md).
- **Channel onboarding (OAuth flow)** is owned by [02-channels-and-providers.md](02-channels-and-providers.md).
- **Programmatic submission contracts** (Public API, CLI, MCP, SDK) are detailed in [05-programmatic-access.md](05-programmatic-access.md).
