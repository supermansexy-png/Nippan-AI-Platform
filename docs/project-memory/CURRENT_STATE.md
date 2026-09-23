# Nippan AI Platform — Current State

Last updated: 2026-09-23
Status: ACTIVE — SECURITY REMEDIATION REQUIRED

## Repository

Repository:
supermansexy-png/Nippan-AI-Platform

Integration branch:
phase2/postgres-logical-schema

Verified integration head:
0cead2215e6b3f4cd0f678d66925f576e20f5dca

Local workspace:
C:\opencode\nippan

The remediation branch is `security/war-room-access-remediation`, created
directly from the verified integration head. The historical
`war-room/increment-b-schema-implementation` branch must not be used as the
base for this remediation.

## Current Platform State

Nippan AI Platform Phase 2 is in progress.

War Room has been implemented and deployed for an isolated non-production
preview. Repository deployment evidence records:

- GitHub as the source of truth for code, issues, PRs and CI;
- Supabase PostgreSQL as the isolated preview database;
- Render service `chetgo` as the preview runtime;
- Cloudflare as the intended remote access layer;
- one room, eight active participants and one agenda item in the preview seed.

The repository later added bounded low-cost model-turn capability. It remains
disabled by default through `war_room_preview_model_turns_enabled = False`.
Runtime enablement must be verified independently from repository defaults.

## War Room Remote Auth

PR #73, `War Room: add Cloudflare Access remote preview authentication`, is
MERGED.

- PR head: `0f613ccc138d52e9146e350b87877584c3849537`
- merge commit: `e328cfc880d93b290d520b6656a26a30664bc2d0`
- exact-head CI run: `35823492418` — SUCCESS

The implementation retains Cloudflare Access application JWT verification for
the War Room UI, snapshot, SSE and owner-command surfaces. Remote access is
disabled by default in repository settings, but repository defaults do not
prove the current Render environment configuration.

Issue #74 is OPEN and contains a real technical security blocker. The merged
transport currently permits authentication bypass before Cloudflare JWT
verification for test environments and loopback-looking ASGI clients. A public
reverse proxy client address must not be treated as proof of local access.

PR #75 is OPEN with merge state DIRTY and mergeability CONFLICTING. It changes
the design to shared-token and signed-session authentication and must not be
merged. Replacing Cloudflare Access with that architecture is
NEEDS_OWNER_DECISION.

## Required Remediation

Create remediation from the exact integration head, not from the historical
local branch. Preserve the Cloudflare Access architecture and make the smallest
fail-closed change that:

- requires valid remote authentication regardless of apparent client address;
- makes local preview an explicit opt-in that is disabled by default;
- removes unconditional test-environment authentication bypass;
- does not use proxy-derived client address or spoofable forwarding headers as
  an authentication boundary;
- protects every War Room surface consistently;
- adds negative-control tests and exact-head CI evidence.

Do not merge remediation until the Project Owner reviews the evidence.

## Runtime Containment

Status: `RUNTIME_CONTAINMENT_FAILED`

No Render CLI or Render API credential was available to inspect active
environment variables. Read-only public probes against
`https://chetgo.onrender.com` nevertheless confirmed the vulnerable boundary:

- `GET /health` returned HTTP 200;
- unauthenticated `GET /war-room/` returned HTTP 403;
- the same unauthenticated request with loopback-looking `X-Forwarded-For` and
  `X-Real-IP` headers returned HTTP 200 with the War Room HTML.

This proves that the deployed proxy/runtime path can turn spoofed forwarding
headers into the loopback client value trusted by the merged transport. Do not
enable or advertise remote/public War Room access. Deployment configuration was
not changed during verification.

## Audit

Independent paid Audit is PAUSED by the Project Owner.

Do not call OpenRouter, Claude Opus or another paid Independent Auditor unless
the Project Owner explicitly re-enables Independent Audit. Normal code review,
security review, tests, CI and evidence verification remain allowed.

## Protected Production System

`Ai-bot-Nippan` production is OUT OF SCOPE unless the Project Owner explicitly
authorizes changes. Do not modify its service, data, credentials or workflows.

## Immediate Next Step

1. Remediate Issue #74 while preserving Cloudflare Access.
2. Run negative-control tests and obtain exact-head CI evidence.
3. Perform normal internal security and diff review.
4. Report results to the Project Owner without merging.

## Source-of-Truth Rule

Repository and runtime evidence override this document whenever they disagree.
Correct this document when verified state changes.
