# Nippan AI Platform — Roadmap v1

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
Status: CONTRACTS FROZEN / DDL DESIGN STARTED

Deliver:
- Tenant / Workspace / Application / Agent / Channel schemas
- Agent Profile and versioned configuration
- Model / Memory / Tool / Data / Risk / Privacy policies
- request_id / trace envelope
- usage/cost telemetry contract
- PostgreSQL logical schema + pgvector
- RLS/isolation design
- idempotency contract
- migration framework
- benchmark/eval fixtures

Exit:
- contracts reviewed and frozen
- schema migrations reproducible
- isolation tests specified
- no production bot migrated

Current handoff:
- `docs/reviews/PHASE1_REVIEW_GATE_FINAL.md`
- `docs/data/POSTGRES_LOGICAL_SCHEMA_V1.md`

## Phase 2 — Core Runtime Skeleton
Status: NEXT AFTER POSTGRES/RLS DESIGN REVIEW

Deliver:
- FastAPI Core AI Service
- health/readiness endpoints
- policy engine
- config loader
- request tracing
- OpenRouter adapter
- deterministic context assembler interface
- MCP client/tool authorization interface
- basic telemetry

Exit:
- synthetic end-to-end request works
- no production traffic

## Phase 3 — Edge and Reliability

Deliver:
- thin Cloudflare Worker gateway
- signature/auth verification
- rate limiting
- request normalization
- persistent idempotency
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
