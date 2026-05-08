---
title: Marketplace and Collaboration
status: draft
created: 2026-05-07
updated: 2026-05-07
---

# Marketplace and Collaboration

## Overview

Postiz includes two socially-oriented features that go beyond solo scheduling: a **marketplace** where members exchange or purchase posts from one another, and **team collaboration** tooling for shared calendar management within an organisation.

<!-- TODO: docs.postiz.com does not have dedicated pages for marketplace or team collaboration. The feature descriptions below are derived from the README, introduction page, and CLAUDE.md only. Confirm all behaviours against the live product before promoting this spec to active. -->

## Target Users

- Creators who want to source or monetise post content through the marketplace.
- Agencies and teams managing a shared social calendar across members.
- Admins inviting colleagues and controlling what each member can do.

## Features

### Marketplace

Members can list posts for sale or exchange, and other members can acquire them through the marketplace.

#### Acceptance Criteria
- [ ] A user can create a marketplace listing from a post.
- [ ] A user can browse, search, or filter marketplace listings.
- [ ] A user can acquire (buy or exchange) a listed post and import it into their own calendar.

<!-- TODO: listing format, pricing model, transaction flow, and settlement (Stripe? credits?) are not documented in docs.postiz.com. The README says "Exchange or buy posts from other members on the marketplace" without further detail. -->

### Team management

Multiple members can be invited into a workspace. Members collaborate on the shared post calendar with role-based access.

#### Acceptance Criteria
- [ ] An admin can invite a user by email.
- [ ] Invited members can view and act on the shared calendar (schedule, comment, etc.) per their role.
- [ ] A member can be removed from the workspace.

<!-- TODO: role enumeration (admin, editor, viewer, etc.) and specific per-role permission boundaries are not described in docs.postiz.com. -->

### Post comments

Team members can comment on scheduled posts before publishing.

#### Acceptance Criteria
- [ ] A member with comment permission can add a comment to a post visible to other workspace members.
- [ ] Comments are threaded at the post level.

<!-- TODO: comment notification behaviour (email digest, in-product notification) is documented in the orchestrator workflows (digest-email, notifications) but not in docs.postiz.com feature documentation. -->

### Notifications

A `GET /notifications/list` endpoint surfaces in-product notifications. Digest emails are delivered via Resend.

#### Acceptance Criteria
- [ ] `GET /notifications/list` returns an array of notification objects for the authenticated user.
- [ ] Digest emails are sent via Resend when the `digest.email.workflow` fires.

## Out of Scope

- **Billing and payment processing** between marketplace participants — not described in docs.postiz.com.
- **Fine-grained RBAC details** — not described; confirm from the codebase (`apps/backend/src/services/auth/permissions/`).
- **Analytics tied to marketplace transactions** — not documented.
