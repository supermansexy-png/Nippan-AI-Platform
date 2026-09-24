# Project State

Updated: 2026-09-23

## Phase
FOUNDATION V1 ACCEPTED / PHASE 2 IN PROGRESS

## Current objective
Complete the first Core Runtime Skeleton on top of the verified Supabase PostgreSQL/RLS foundation without touching protected legacy production systems.

## Accepted architecture
See:
- `docs/architecture/FOUNDATION_V1.md`
- `docs/decisions/ADR-0001-runtime-topology.md`
- `docs/decisions/ADR-0002-control-plane-and-multitenancy.md`
- `docs/decisions/ADR-0003-model-routing.md`
- `docs/decisions/ADR-0004-data-memory-retrieval.md`
- `docs/decisions/ADR-0005-policy-tools-and-approval.md`
- `docs/decisions/ADR-0006-infrastructure-simplicity.md`
- `docs/decisions/ADR-0007-supabase-schema-baseline.md`

## Phase 1 progress

### FROZEN
- Issue #7: Identity & Multi-Tenant Contract
  - `docs/data/IDENTITY_TENANCY_CONTRACT_V1.md`
  - `schemas/platform-identity-v1.schema.json`
  - independent review: Issue #12
- Issue #8: Agent Profile & Policy Contract
  - `docs/data/AGENT_POLICY_CONTRACT_V1.md`
  - `schemas/agent-config-v1.schema.json`
  - independent review: Issue #13
- Issue #9: Request / Trace / Usage Contract
  - `docs/data/REQUEST_TRACE_USAGE_CONTRACT_V1.md`
  - `schemas/request-envelope-v1.schema.json`
  - `schemas/usage-event-v1.schema.json`
  - independent review: Issue #14
- Issue #11: Benchmark & Evaluation Specification
  - `benchmarks/BENCHMARK_SPEC_V1.md`
- PR #16: Phase 1 review gate final
  - `docs/reviews/PHASE1_REVIEW_GATE_FINAL.md`
  - merged 2026-09-22

## Phase 2 progress

### PostgreSQL / Supabase
Applied to Supabase `nippan-ai-platform`:
- `20260922174011_phase2_core_foundation.sql`
- `20260922174227_phase2_core_fk_indexes.sql`
- `20260922180029_phase2_request_trace_telemetry.sql`
- `20260922180107_phase2_idempotency_usage_audit.sql`

Current data foundation includes:
- identity/config baseline
- request state and W3C-compatible trace/span identifiers
- async trace links
- AI/tool/retrieval telemetry
- persistent idempotency records
- immutable deduplicated UsageEvent ledger
- append-only audit events
- tenant-scoped RLS on all current tenant-owned tables
- direct `anon`, `authenticated` and `service_role` table grants revoked

Verification:
- Supabase security advisor: no findings
- performance advisor: only expected unused-index notices on the empty database
- rollback tests passed for request scope, zero trace ID rejection, usage dedupe, append-only usage, and idempotency uniqueness
- repeatable full isolation/invariant suite checked in at `tests/sql/phase2_isolation_invariants.sql`

### Core Runtime Skeleton
Initial FastAPI skeleton is checked in at `services/core`:
- `/health`
- `/ready`
- PostgreSQL pool
- transaction-local tenant/application/request context
- active PUBLISHED Agent config loader
- no production model/tool traffic

## Core direction
- Thin Cloudflare Worker edge gateway
- FastAPI Core AI Service for realtime runtime
- PostgreSQL + pgvector source of truth
- OpenRouter primary model gateway
- deterministic context assembly; Context Compiler conditional only
- modular Nippan MCP with deterministic permissions/risk policy
- Cloudflare Queues + n8n for background/automation
- R2 for machine files
- Control Plane / Dashboard separated from runtime Data Plane
- Tenant -> Application -> Agent/Channel -> Conversation ownership model
- explicit Agent <-> Channel bindings
- SaaS/rental readiness through isolation, quotas, usage attribution and versioned configuration

## Independent Audit System
Status: ACTIVE

Authoritative protocol:
- `docs/audits/AUDIT_SYSTEM_V1.md`

Mandatory progress gates:
- 25%
- 50%
- 75%
- 90%
- 100%

Immediate triggers:
- major architecture changes
- major security/authorization changes
- major PostgreSQL/schema/RLS changes

Independence:
- Builder cannot self-approve
- BLOCKER findings halt milestone advancement
- remediation of a BLOCKER requires independent re-audit
- 100% must PASS before milestone DONE
- Primary Independent Auditor: Claude Opus 5 through OpenRouter, replaceable by configuration
- specialist auditors may supplement the primary auditor

Phase 2 catch-up status:
- current ROADMAP enumerates 19 Phase 2 deliverables
- 11 are recorded complete and 8 pending
- equal-weight baseline progress: 57.9%
- highest crossed gate: 50%
- catch-up 50% audit is now due
- evidence packet: `docs/audits/PHASE2_50_AUDIT_EVIDENCE_PACKET.md`
- tracking: Issue #18
- independent audit outcome: PENDING
- milestone implementation advancement: ON HOLD until independent audit outcome permits continuation

## Parallel implementation track — Nippan AI War Room V1
Status: INCREMENT B MERGED / INCREMENT C STARTED

Tracking:
- Issue #19
- Increment C: Issue #30
- Frozen orchestrator contract: Issue #31
- proposal: `docs/proposals/WAR_ROOM_V1_PROPOSAL.md`

Completed:
- Increment A deterministic contracts and bounded scheduler
- Increment B seven-table PostgreSQL/RLS migration
- Independent Audit #28: PASS_WITH_FINDINGS; all migration blockers closed
- PR #29 merged at `3d4d4f0848bebfab2dfdd940c1bb4e4b39150717`

Current design includes:
- visible multi-agent project chat
- Chair / Architect / Builder / Security / Cost & Ops / Independent Auditor / Project Owner roles
- human owner final authority
- bounded two-round automatic discussion
- Pause / Resume / Stop / Owner Decision controls
- token/cost hard limits
- logical room/message/finding/decision/action-item model
- Free Discussion / Formal Meeting / Audit Review modes
- formal Independent Audit remains separately governed

Increment C builds the Core orchestrator and `/war-room` skeleton from one
frozen command/event/model/budget contract. This parallel track does not count
toward Phase 2 progress. Supabase production application and all production
deployment remain unauthorized.

## AI team policy
Specialist models may draft/review work, but architecture remains governed by Foundation + ADRs + assigned issues.

High-priority benchmark candidate:
- Jev for structured routing/classification/decision support

Jev or any model never replaces deterministic authorization, risk or privacy policy.

## Protected systems
- `supermansexy-png/Ai-Nippan`: production; do not modify during foundation implementation
- existing Personal Assistant / n8n workflows: do not migrate yet

## Explicitly deferred
Cloudflare AI Gateway, Hyperdrive, Durable Objects, Analytics Engine, Redis, D1, Vectorize, Cloudflare Workflows, dedicated vector DB, Kubernetes and unnecessary microservices.

## Immediate next gate
1. Merge the Increment C orchestrator contract before implementation tracks.
2. Implement backend, model/budget, verification and frontend tracks against it.
3. Stop for the normal 75% Independent Audit when 12 of 16 Increment C
   deliverables have acceptance evidence, or sooner for an immediate trigger.
4. Keep memory/pgvector tables deferred until embedding benchmarks choose
   model/dimension.

## Production migration
Not allowed in current phase.
