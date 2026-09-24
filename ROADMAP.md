# Nippan AI Platform — Roadmap v1

> **STATUS (2026-09-25): ARCHIVED BLUEPRINT — NOT THE CURRENT BUILD PLAN.**
> This roadmap describes the earlier full-stack platform (Phases 0–10: FastAPI
> core, Cloudflare edge, pgvector, RLS, Control Plane, War Room, Ai-Nippan
> migration). The current, authoritative plan for the Phase A market test
> (self-hosted n8n + PostgreSQL lite schema + OpenRouter, rent bots to small
> Thai businesses) is `docs/warroom/STARTUP_PLAYBOOK.md`. Everything below is
> preserved as archived design reference only; the preserved blueprint lives
> under `docs/future/`.

## Project-wide Independent Audit System
Status: **SUSPENDED by Project Owner (2026-09-24)** — see `docs/warroom/decision-log.md` and `docs/audits/AUDIT_SYSTEM_V1.md`

Progress-based independent Audit Gates are **not blocking** while suspended:
- 25%
- 50%
- 75%
- 90%
- 100%

Progress is calculated from explicit milestone deliverables, not time elapsed. If no weights are defined, deliverables are equally weighted.

Immediate audit is also required for major:
- architecture changes
- security/authorization changes
- PostgreSQL/schema/RLS changes

Governance:
- Builder cannot self-approve
- BLOCKER findings halt milestone advancement
- BLOCKER remediation requires independent re-audit
- 100% gate must PASS before DONE
- Primary Independent Auditor: Claude Opus 5 via OpenRouter, replaceable by configuration
- audit protocol: `docs/audits/AUDIT_SYSTEM_V1.md`
- report template: `docs/audits/AUDIT_REPORT_TEMPLATE.md`

## Phase 0 — Foundation Architecture
Status: DONE

Completed:
- independent architecture reviews
- runtime topology decision
- control-plane/data-plane decision
- multi-tenant product model
- data/memory direction
- model gateway direction
- tool/risk/privacy principles
- infrastructure defer list

## Phase 1 — Contracts and Data Foundation
Status: DONE / FROZEN V1

Deliver:
- Tenant / Workspace / Application / Agent / Channel schemas
- Agent Profile and versioned configuration
- Model / Memory / Tool / Data / Risk / Privacy policies
- request_id / trace envelope
- usage/cost telemetry contract
- PostgreSQL logical schema
- RLS/isolation design
- idempotency contract
- migration framework
- benchmark/eval specification

Exit:
- contracts reviewed and frozen
- executable schema baseline started
- no production bot migrated

Handoff:
- `docs/reviews/PHASE1_REVIEW_GATE_FINAL.md`
- `docs/data/POSTGRES_LOGICAL_SCHEMA_V1.md`
- `docs/decisions/ADR-0007-supabase-schema-baseline.md`

## Phase 2 — Core Runtime Skeleton
Status: IN PROGRESS

Completed in current milestone:
- Supabase identity/config PostgreSQL baseline
- request/trace/model/tool/retrieval telemetry tables
- persistent idempotency table
- immutable UsageEvent ledger
- append-only audit events
- RLS and tenant-scope constraints on current tenant-owned tables
- repeatable SQL isolation/invariant suite checked in
- minimal FastAPI service package
- health/readiness endpoints
- tenant-scoped DB transaction boundary
- active PUBLISHED config loader

Audit baseline for this milestone:
- 19 currently enumerated deliverables
- 11 recorded complete
- 8 recorded pending
- baseline progress: 57.9% using equal weights
- highest crossed gate: 50%
- catch-up 50% independent audit required because the Audit System was introduced mid-Phase 2

Still deliver:
- policy engine boundary
- request persistence/tracing service
- OpenRouter adapter interface
- deterministic context assembler interface
- MCP client/tool authorization interface
- synthetic end-to-end request
- CI execution of isolation suite with runtime-role impersonation
- benchmark-gated memory/pgvector dimensions

Exit:
- synthetic end-to-end request works
- isolation/invariant suite runs repeatably
- no production traffic

## Parallel Implementation Track — Nippan AI War Room V1
Status: INCREMENT B MERGED / INCREMENT C IN PROGRESS

Tracking:
- Issue #19
- Increment C: Issue #30
- Contract freeze: Issue #31
- `docs/proposals/WAR_ROOM_V1_PROPOSAL.md`

Increment B schema/RLS implementation passed Independent Audit #28 and merged
in PR #29. Increment C Core orchestration work is authorized in source control
under its frozen contract. This track does not change Phase 2 progress and
does not authorize Supabase production application or production deployment.

Planned capability:
- visible multi-agent project chat room
- Project Owner can interrupt, ask one/all roles, pause/resume/stop
- controlled independent first round + bounded challenge round
- Chair synthesis and NEEDS_OWNER_DECISION gates
- token/cost budgets with hard stop
- Free Discussion / Formal Meeting / Audit Review modes
- durable decisions/action items
- formal Independent Audit remains separate and cannot be replaced by AI consensus

## Phase 3 — Edge and Reliability

Deliver:
- thin Cloudflare Worker gateway
- signature/auth verification
- rate limiting
- request normalization
- persistent idempotency integration at edge/runtime boundary
- Cloudflare Queues for background jobs
- DLQ/replay path
- R2 file adapter
- degraded-mode behavior

## Phase 4 — Memory and Context

Deliver:
- recent conversation
- active state
- rolling summary
- long-term memory
- provenance/conflict/expiry rules
- hybrid exact/keyword/vector retrieval
- token budgeting
- Context Compiler benchmark and optional implementation only if justified

## Phase 5 — Control Plane v1

Deliver a minimal dashboard for:
- tenants
- applications
- agents
- channels
- model/tool/memory/risk policies
- config Draft -> Test -> Publish -> Rollback
- requests/traces
- usage/cost
- errors
- approval queue
- Nippan AI War Room internal project collaboration surface, subject to accepted implementation plan

Do not build full SaaS billing yet.

## Phase 6 — Personal Assistant Pilot

Migrate the Personal Assistant as the first conversational pilot:
- feature flag
- rollback path
- memory v2
- MCP policies
- cost/trace visibility

## Phase 7 — Slip Application

Create Slip App/Agent:
- LINE group intake
- image extraction
- duplicate detection
- R2
- Postgres transactions
- reporting via n8n/Sheets when useful

## Phase 8 — Nippan Website AI

Connect nippan.org through platform APIs/Agents:
- support
- content/SEO/admin capabilities only as separately permissioned agents
- WordPress/WooCommerce tools via MCP policies

## Phase 9 — Ai-Nippan Migration

Adapter-based migration only:
- shadow/read-only comparison
- feature flags / traffic split
- gradual cutover
- rollback
- preserve proven commerce/order logic

## Phase 10 — External Customer / Rental Readiness

When business demand exists:
- tenant onboarding
- templates
- plan/entitlement management
- quotas
- usage metering
- billing integration
- customer-facing admin surface

## Optional infrastructure
Adopt only from measured need:
- Cloudflare AI Gateway
- Hyperdrive
- Durable Objects
- Analytics Engine
- Redis
- dedicated vector database
- service splitting
