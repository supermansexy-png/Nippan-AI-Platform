# Project State

Updated: 2026-09-22

## Phase
FOUNDATION V1 ACCEPTED / IMPLEMENTATION FOUNDATION

## Current objective
Build the minimum durable platform foundation without touching production bots.

## Accepted architecture
See:
- `docs/architecture/FOUNDATION_V1.md`
- `docs/decisions/ADR-0001-runtime-topology.md`
- `docs/decisions/ADR-0002-control-plane-and-multitenancy.md`
- `docs/decisions/ADR-0003-model-routing.md`
- `docs/decisions/ADR-0004-data-memory-retrieval.md`
- `docs/decisions/ADR-0005-policy-tools-and-approval.md`
- `docs/decisions/ADR-0006-infrastructure-simplicity.md`

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
- Tenant -> Application -> Agent -> Channel -> Conversation model
- SaaS/rental readiness through isolation, quotas, usage attribution and versioned configuration

## Protected systems
- `supermansexy-png/Ai-Nippan`: production; do not modify during foundation implementation
- existing Personal Assistant / n8n workflows: do not migrate yet

## First implementation gate
Define contracts and schemas before deploying runtime infrastructure:
1. platform identity and tenancy contract
2. Agent/Application configuration contract
3. request/trace envelope
4. model policy contract
5. tool/risk/privacy policy contracts
6. usage/cost telemetry contract
7. initial PostgreSQL logical schema
8. benchmark/eval plan

## Explicitly deferred
Cloudflare AI Gateway, Hyperdrive, Durable Objects, Analytics Engine, Redis, D1, Vectorize, Cloudflare Workflows, dedicated vector DB, Kubernetes and unnecessary microservices.

## Next task
Create the Foundation contracts/schema package and database design; no production migration yet.
