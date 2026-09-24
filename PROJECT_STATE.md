# Project State

Updated: 2026-09-24

## Phase

**PHASE A — MARKET TEST**

Rewritten after a pivot decided 2026-09-24. See `ROADMAP.md` for the full
3-phase structure and `docs/future/README.md` for what the original
11-phase plan turned into.

## Current objective

Stand up the Phase A stack (n8n core, lite schema, starting MCP tools,
Onboarding assistant, PDPA layer, War Room Operations) and onboard the
first real tenants — up to 30, at 299 THB/month flat.

## What's built vs. what's designed but not yet implemented

This project has a documentation-heavy history — see the note at the
bottom of this file. Track actual build status here, separately from the
design docs, so it stays honest.

### Designed (documents exist, ready to build from)
- Lite database schema — `docs/data/LITE_SCHEMA_V1.md`
- PDPA compliance approach — `docs/security/PDPA_COMPLIANCE.md`
- War Room roles, monitoring, decision log format — `docs/warroom/`
- Product docs: pricing, segments, customer-facing rules, onboarding flow,
  MCP tool catalog, model policy — `docs/product/`

### Not yet built
- No n8n workflows exist yet
- No database (lite schema is designed, not instantiated)
- No MCP tools implemented (catalog is designed, not built)
- No tenants onboarded
- War Room roles are written policy, not staffed AI seats — see
  `docs/warroom/ROLES.md`, "Activation order". Phase A starts with the
  owner executing most of this manually.

## Immediate next steps

Follow `docs/warroom/STARTUP_PLAYBOOK.md` for the concrete step-by-step
order — it supersedes the numbered list below once work actually starts;
this list is the same content, kept here as a quick-glance summary.

1. Stand up n8n instance
2. Implement the lite schema as real tables
3. Build `chat-bot-core` and `memory-store` MCP tools — minimum needed for
   one working bot type end to end
4. Build the Onboarding assistant flow
5. Onboard tenant #1 manually, watched closely, before opening to more

## A note on this project's history

Earlier work on this repository (2026-09-22 to 2026-09-24, ~50 commits)
produced an extensive full-scale architecture: identity/tenancy and agent
policy contracts, 6 ADRs, a PostgreSQL/pgvector data model, and a Phase 1
review gate — almost entirely documents, no working code. That work is not
wrong; it was sized for a larger, more capital-intensive version of this
business than the current plan. It's preserved in `docs/future/` as a
blueprint for when this project's scale actually calls for it — see that
folder's README for the trigger conditions per document.

The lesson carried forward: this file should reflect what's actually
running, not what's been planned. Update the "built vs. designed" section
above as things actually ship, not when a document about them is written.

## Production migration

Not allowed in current phase. Protected systems: see `ROADMAP.md`.
