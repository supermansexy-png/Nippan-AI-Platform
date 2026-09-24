# Future blueprint — not active work

Status: **archived, not deleted**

Everything under `docs/future/` is the original full-scale design (contracts,
ADRs, MCP Hub roadmap, Phase 1 review gate, JSON schemas). It was accepted
and internally reviewed, but building it now is bigger than the business
needs at the current stage.

## Why this exists

The project pivoted on 2026-09-24 to a market test: rent AI bots to up to
30 small Thai businesses at a flat 299 THB/month, running on n8n instead of
a full FastAPI + Cloudflare Worker + PostgreSQL/pgvector stack.

The material here was not wrong — it was sized for 100+ tenants, multiple
concurrent AI operators, and SaaS-grade isolation. That is where this
project goes if the market test succeeds. Nothing here should be deleted or
rewritten to fit the smaller phase; it stays intact so the transition to
larger scale has an existing, reviewed blueprint to build from instead of
starting over.

## When to pull from this folder

Pull a document back into active work when its trigger condition is met:

| Document | Pull it back when |
|---|---|
| `architecture/FOUNDATION_V1.md`, `NIPPAN_MCP_HUB_FOUNDATION.md` | Moving off n8n to a FastAPI Core Service (~60+ concurrent tenants, or a shift to specialized high-value/low-volume work) |
| `data/IDENTITY_TENANCY_CONTRACT_V1.md`, `AGENT_POLICY_CONTRACT_V1.md`, `REQUEST_TRACE_USAGE_CONTRACT_V1.md` + schemas | Moving from the lite schema (`docs/data/LITE_SCHEMA_V1.md`) to full PostgreSQL + pgvector with RLS |
| `decisions/ADR-0001` through `ADR-0006` | Same trigger as above — these are the reasoning behind the full-scale architecture |
| `decisions/NIPPAN_AI_OS_ROADMAP_V2.md`, `mcp-hub/ROADMAP.md`, `mcp-hub/SERVER_REGISTRY.md` | Standing up a formal MCP Hub with GitHub/OpenRouter/Supabase connectors as separate services |
| `reviews/PHASE1_REVIEW_GATE_FINAL.md` | Reference only — shows the review process (Project Lead + independent model review) once War Room's Auditor role is doing the same kind of gate at scale |
| `AI_REVIEW_BRIEF.md` | Commissioning an independent review of the full-scale architecture |
| `benchmarks/BENCHMARK_SPEC_V1.md` | Formal model benchmarking once Model Scout's informal tracking isn't enough |

## Do not

- Do not implement anything from this folder while the active roadmap
  (`ROADMAP.md`) is still on Phase A/B.
- Review gates and "do not implement" instructions inside these documents
  applied to the full design only. They do not block Phase A work.
- Do not delete anything here to "clean up" — it is deliberately preserved.
- Do not treat this folder as documentation of the *current* system. See
  `PROJECT_STATE.md` at the repo root for that.
