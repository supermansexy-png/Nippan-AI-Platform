# Nippan AI Platform — Roadmap

Status: **Phase A active**

Rewritten 2026-09-24 after a market-test pivot: 30-tenant, 299 THB/month AI
bot rental, on n8n. The original 11-phase, FastAPI + Cloudflare +
PostgreSQL/pgvector roadmap is preserved intact in `docs/future/` — see
`docs/future/README.md` for what triggers pulling each piece back into
active work.

## Phase A — Market test foundation (current)

Goal: prove the market wants this, at the lowest complexity that can carry
real tenants safely.

Deliver:
- n8n as the runtime core (not FastAPI — see `docs/future/decisions/
  ADR-0001-runtime-topology.md` for why the full version chose otherwise,
  and `docs/future/README.md` for when to revisit)
- Lite database schema (`docs/data/LITE_SCHEMA_V1.md`)
- 4-layer memory system, lightweight (same file)
- Starting MCP tool set (`docs/product/MCP_TOOLS_V1.md`)
- Onboarding assistant (`docs/product/ONBOARDING_FLOW.md`)
- PDPA compliance layer (`docs/security/PDPA_COMPLIANCE.md`)
- War Room, staffed per the activation order in
  `docs/warroom/ROLES.md` — Operations first, other roles as volume
  justifies them
- Monitoring pipeline (`docs/warroom/MONITORING.md`)
- Flat pricing (`docs/product/PRICING_V1.md`)

Exit: 25-30 tenants signed up, retained, and profitable at the estimated
cost-per-tenant, or a clear signal the market isn't there.

## Phase B — Expand breadth

Goal: more bot types, more customer segments, same infrastructure.

Deliver:
- Additional MCP tools per `docs/product/CUSTOMER_SEGMENTS.md`'s
  underserved-segment list, added one at a time as Marketing/Operations
  surface real demand
- Remaining War Room roles staffed as live AI seats (Development,
  Marketing, Model Scout) if not already active from Phase A
- First real use of Model Scout to swap in a new/cheaper model

Exit: Nippan can onboard a genuinely new bot type/segment in days, not
weeks, without touching core infrastructure.

## Phase C — Scale decision point

Trigger: Phase A/B succeeds and either (a) demand pushes past what n8n at
~30-60 tenants can carry, or (b) the owner activates the specialized/
high-value pivot (`docs/decisions/PIVOT_OPTION.md`).

This is where `docs/future/` gets pulled back in — FastAPI Core Service,
Cloudflare Worker edge, PostgreSQL + pgvector with RLS, a real Control
Plane dashboard, and eventually the SaaS/rental-readiness work
(entitlements, metering, billing) from the original roadmap. None of this
is scoped in detail here; `docs/future/README.md` has the trigger table
for which document to open first.

## Protected production systems

- `supermansexy-png/Ai-Nippan` — production, do not modify
- Existing Personal Assistant / n8n production workflows — do not migrate

These protections carry over unchanged from the original roadmap.
