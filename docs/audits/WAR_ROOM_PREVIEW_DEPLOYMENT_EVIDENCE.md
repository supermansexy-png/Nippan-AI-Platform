# War Room Preview Deployment Evidence

Date: 2026-09-23  
Scope: non-production War Room preview infrastructure only  
Integrated source baseline: `e672a77bbb932d05b88e7ce01eb290e02a544356`

## Purpose

Record durable, source-controlled evidence for the isolated War Room preview deployment created under the non-production preview infrastructure exception in `docs/audits/AUDIT_SYSTEM_V1.md`.

This document does not authorize production deployment, provider/model turns, automatic `run_next_turn`, or a public authentication bypass.

## Governance

PR #69 added the narrow non-production preview infrastructure exception.

The exception does not waive:

- normal 25% / 50% / 75% / 90% / 100% audit gates;
- security/authentication immediate-audit triggers;
- PostgreSQL/schema/RLS immediate-audit triggers;
- production authorization requirements.

Remote/mobile authentication is therefore tracked separately from the preview infrastructure recorded here.

## Render Core preview

Repurposed service:

- service name: `chetgo`
- service ID: `srv-dajprr5g1s2s73bnoed0`
- region: Singapore
- plan: free
- repository: `supermansexy-png/Nippan-AI-Platform`
- branch: `phase2/postgres-logical-schema`
- root directory: `services/core`
- start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- health endpoint: `/health`
- primary URL: `https://chetgo.onrender.com`

The protected Render service `Ai-bot-Nippan` was not modified.

Latest verified deployment after the database DSN correction was LIVE. Application logs showed normal Uvicorn startup and recurring `GET /health 200` responses.

## Preview database

Active runtime preview database:

- provider: Supabase
- project name: `nippan-war-room-preview`
- project ref: `cjzrjdznijxtigmzgyzm`
- region: `ap-northeast-2`
- status at provisioning verification: `ACTIVE_HEALTHY`
- production/main Supabase project was not used for this preview deployment

The Render service uses the isolated preview database through `NIPPAN_DATABASE_URL`. No database password or connection URI is recorded in source control.

## Applied reviewed migrations

The following repository migrations were applied successfully to the isolated Supabase preview project, in order:

1. `20260922174011_phase2_core_foundation.sql`
2. `20260922174227_phase2_core_fk_indexes.sql`
3. `20260922180029_phase2_request_trace_telemetry.sql`
4. `20260922180107_phase2_idempotency_usage_audit.sql`
5. `20260922193829_phase2_a001_least_privilege.sql`
6. `20260922231000_war_room_v1_increment_b.sql`

No new preview-only migration, RLS policy or grant behavior was introduced.

## Deterministic preview seed evidence

Verified rows for room `c3333333-3333-4333-8333-333333333333`:

- rooms: 1
- active participants: 8
- agenda items: 1

The participant set is Project Owner plus seven AI roles:

- Chair
- Architect
- Builder
- Security Reviewer
- Cost & Ops Reviewer
- Independent Auditor
- Secretary

The seed also contains the existing non-billable preview finding/proposal artifacts.

## Database connection evidence

After correcting the Supabase Session Pooler DSN:

- the latest Render deployment completed as LIVE;
- Core application startup completed;
- the post-deploy log window contained no `password authentication`, host-resolution, circuit-breaker or pool connection errors;
- `Database.open()` opens the configured async PostgreSQL pool during application lifespan startup.

A direct external `/ready` probe was not captured by the available connector in this evidence pass, so this document does not claim an independently recorded HTTP `/ready 200`.

## Historical Render PostgreSQL experiment

A separate Render PostgreSQL preview instance was created earlier for evaluation:

- name: `nippan-war-room-preview`
- ID: `dpg-dapli7ou01pc73d2s5og-a`
- PostgreSQL 17 / Singapore / free plan

The reviewed Supabase-oriented migration set could not be replayed unchanged there because the managed Render database user was not permitted to execute `ALTER DEFAULT PRIVILEGES FOR ROLE postgres`.

The attempted startup failed closed with `psycopg.errors.InsufficientPrivilege: permission denied to change default privileges`.

The Render bootstrap flag was then disabled. This Render PostgreSQL instance is not the active runtime database path.

## Remote/mobile boundary

The deployed preview transport still enforces:

`war_room_preview_loopback_only`

for non-loopback requests.

Therefore the current deployment does not provide public/mobile War Room access. Relaxing this boundary requires secure remote authentication and remains a separate security/authentication change subject to the independent-audit rules.

## Provider and production boundary

The preview remains non-billable:

- no browser route invokes `run_next_turn`;
- no auto-advance or turn chaining is enabled;
- no funded OpenRouter credential is enabled by this deployment;
- no Supabase production migration was performed;
- no `Ai-bot-Nippan` or production n8n workflow was modified.

## Acceptance status

This deployment evidence does not mark Track D deliverables accepted.

Audit-accepted Increment C progress remains:

`13 / 16 = 81.25%`

D-01, D-02 and D-03 remain unaccepted until formal end-to-end acceptance evidence is recorded under the project governance process.
