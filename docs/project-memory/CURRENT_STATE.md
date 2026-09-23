# Nippan AI Platform — Current State

Last updated: 2026-09-23
Status: ACTIVE — REMOTE AUTH REMEDIATION DEPLOYED

## Repository

Repository:
supermansexy-png/Nippan-AI-Platform

Integration branch:
phase2/postgres-logical-schema

Verified integration head:
4ab568f157a8ffb20f3fb7332e41f5c8cc7024b1

Local workspace:
C:\opencode\nippan

Remote Auth remediation was developed on
`security/war-room-access-remediation` and merged through PR #79. The current
documentation follow-up branch is `docs/post-remediation-state`.

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

Issue #74 is CLOSED after remediation, exact-head CI and deployed runtime
verification. The historical finding remains valid evidence for the vulnerable
PR #73 implementation.

PR #75 is CLOSED as obsolete. It changes the design to shared-token and
signed-session authentication and was not merged. Replacing Cloudflare Access
with that architecture remains NEEDS_OWNER_DECISION.

## Required Remediation

PR #79 is MERGED as
`4ab568f157a8ffb20f3fb7332e41f5c8cc7024b1`. It preserves the Cloudflare
Access architecture.

Implementation commit `faf6e052aa3a1e506656ba0c00f7564116680b0a` makes the
smallest fail-closed change. The verified remediation code head is
`295513a4005bec01d9abec0065f1f4a38a0f047d`, including a Windows-portable
source check and Python artifact ignores. The remediation:

- requires valid remote authentication regardless of apparent client address;
- makes local preview an explicit opt-in that is disabled by default;
- removes unconditional test-environment authentication bypass;
- does not use proxy-derived client address or spoofable forwarding headers as
  an authentication boundary;
- protects every War Room surface consistently;
- adds negative-control tests and exact-head CI evidence.

Exact-head verification completed successfully:

- local Python 3.12 dedicated suite: `39 passed`;
- War Room Remote Auth run `35835142835` — SUCCESS;
- Phase 2 PostgreSQL regression run `35835142839` — SUCCESS.

Normal internal security review found no blocking Issue #74 finding. A residual
availability risk remains because attacker-selected JWT key IDs/signatures can
trigger forced JWKS refresh attempts. Authentication still fails closed. Route
protection is also manually repeated, so future War Room routes must be added to
the authorization coverage matrix.

The Project Owner approved merge, deployment verification and closure of Issue
#74 and obsolete PR #75.

## Runtime Containment

Status: `RUNTIME_CONTAINMENT_VERIFIED`

No Render CLI or Render API credential was available to inspect active
environment variables. Read-only public probes against
`https://chetgo.onrender.com` nevertheless confirmed the vulnerable boundary:

- `GET /health` returned HTTP 200;
- unauthenticated `GET /war-room/` returned HTTP 403;
- the same unauthenticated request with loopback-looking `X-Forwarded-For` and
  `X-Real-IP` headers returned HTTP 200 with the War Room HTML.

Those probes proved the pre-remediation vulnerability. After PR #79 deployment,
read-only verification confirmed:

- `GET /health` returns HTTP 200;
- direct Render UI, assets, snapshot, SSE and owner-command requests with
  loopback-looking forwarding headers return HTTP 403;
- an invalid Cloudflare JWT returns HTTP 403;
- `https://warroom.nippan.org/war-room/` redirects unauthenticated requests to
  Cloudflare Access with HTTP 302.

Deployment configuration was not changed manually during verification.

## Audit

Independent paid Audit is PAUSED by the Project Owner.

Do not call OpenRouter, Claude Opus or another paid Independent Auditor unless
the Project Owner explicitly re-enables Independent Audit. Normal code review,
security review, tests, CI and evidence verification remain allowed.

## Protected Production System

`Ai-bot-Nippan` production is OUT OF SCOPE unless the Project Owner explicitly
authorizes changes. Do not modify its service, data, credentials or workflows.

## Immediate Next Step

1. Do not start additional War Room feature work from the remediation branch.
2. Review priorities and agree a new plan with the Project Owner before starting
   `ASK_ALL` rotation, clear-view UI or unrelated platform work.
3. Track JWKS refresh throttling as non-blocking security hardening.

## Source-of-Truth Rule

Repository and runtime evidence override this document whenever they disagree.
Correct this document when verified state changes.
