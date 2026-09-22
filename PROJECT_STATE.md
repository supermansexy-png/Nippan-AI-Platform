# Project State

Updated: 2026-09-23

## Phase
FOUNDATION V1 ACCEPTED / PHASE 2 STARTING

## Current objective
Convert frozen Phase 1 contracts into PostgreSQL/RLS design and the first Core Runtime Skeleton boundaries without touching production systems.

## Accepted architecture
See:
- `docs/architecture/FOUNDATION_V1.md`
- `docs/decisions/ADR-0001-runtime-topology.md`
- `docs/decisions/ADR-0002-control-plane-and-multitenancy.md`
- `docs/decisions/ADR-0003-model-routing.md`
- `docs/decisions/ADR-0004-data-memory-retrieval.md`
- `docs/decisions/ADR-0005-policy-tools-and-approval.md`
- `docs/decisions/ADR-0006-infrastructure-simplicity.md`

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
  - independent review: Issue #14
- Issue #11: Benchmark & Evaluation Specification
  - `benchmarks/BENCHMARK_SPEC_V1.md`
- PR #16: Phase 1 review gate final
  - `docs/reviews/PHASE1_REVIEW_GATE_FINAL.md`
  - merged 2026-09-22

### PHASE 2 STARTED
- Issue #10: PostgreSQL + pgvector logical schema
  - `docs/data/POSTGRES_LOGICAL_SCHEMA_V1.md`
  - status: draft implementation handoff; no executable DDL yet

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
1. Review `docs/data/POSTGRES_LOGICAL_SCHEMA_V1.md` against the frozen contracts.
2. Decide migration tooling, role names, enum/domain strategy and UUID generation source.
3. Write reproducible PostgreSQL migrations and isolation tests.
4. Build the minimal FastAPI Core skeleton against the accepted schema boundaries.
5. Build benchmark fixtures/runs before locking production model roles.

## Production migration
Not allowed in current phase.
