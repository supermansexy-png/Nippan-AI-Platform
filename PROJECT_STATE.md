# Project State

Updated: 2026-09-24

## Phase

**PHASE A — MARKET TEST**

Rewritten after a pivot decided 2026-09-24. See `ROADMAP.md` for the full
3-phase structure and `docs/future/README.md` for what the original
11-phase plan turned into.

## Current objective

**Right now: build the infrastructure. There are zero real tenants.**
Nobody is being onboarded yet. Do not act as if a live customer exists —
if a task description implies one does, that's a signal to re-read this
file, not to proceed as if it's true.

The current work is standing up the Phase A stack per
`docs/warroom/STARTUP_PLAYBOOK.md` Step 0-1: n8n core, lite schema,
starting MCP tools, Onboarding assistant. Onboarding the first real
tenant is Step 2 — a later, separate milestone, not something happening
now.

**PDPA is designed, not blocking.** The compliance approach
(`docs/security/PDPA_COMPLIANCE.md`) is already written. The one thing
still open is T-004 (a lawyer reviewing the tenant agreement) — that task
runs in parallel with infrastructure work and only has to finish before
Step 2 (onboarding tenant #1). It does not need to finish before, or
block, any Step 0/1 infrastructure task. If a task card doesn't mention
PDPA, don't bring it up.

## What's built vs. what's designed but not yet implemented

This project has a documentation-heavy history — see the note at the
bottom of this file. Track actual build status here, separately from the
design docs, so it stays honest.

### Designed (documents exist, ready to build from)
- Lite database schema — `docs/data/LITE_SCHEMA_V1.md`
- PDPA compliance approach — `docs/security/PDPA_COMPLIANCE.md`
- War Room roles, autonomy ladder, monitoring, decision log, task control, playbook — `docs/warroom/`
- Product docs: pricing, segments, customer-facing rules, onboarding flow,
  MCP tool catalog, model policy, storefront, business operations — `docs/product/`

### Not yet built
- Nothing is built yet: no n8n instance, no workflows
- No database (lite schema is designed, not instantiated)
- No MCP tools implemented (catalog is designed, not built)
- No tenants onboarded
- War Room roles are written policy, not staffed AI seats — see
  `docs/warroom/ROLES.md`, "Activation order". Phase A starts with the
  owner executing most of this manually.

## Next steps

See `docs/warroom/STARTUP_PLAYBOOK.md` (build order) and `TASKS.md`
(current task cards). They are deliberately not repeated here, so the
three files can never disagree.

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
