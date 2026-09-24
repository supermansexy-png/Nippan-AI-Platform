# Lite schema v1 — Phase A

Status: **ACTIVE — Phase A**

## Principle

Shaped after `docs/future/data/IDENTITY_TENANCY_CONTRACT_V1.md` so growing
into the full contract later is additive, not a rewrite — but implemented
at a fraction of the complexity, sized for n8n + a plain relational
database at up to ~30-60 tenants.

Every table below carries `tenant_id`. No exceptions. This is both the
multi-tenant isolation boundary and the PDPA cross-tenant-leakage control
(see `docs/security/PDPA_COMPLIANCE.md`, Layer 3).

## Tables

### `tenants`
The businesses renting a bot.

| Column | Notes |
|---|---|
| `tenant_id` | primary key |
| `business_name` | |
| `package` | Phase A: always the single 299 THB tier |
| `signup_date` | |
| `status` | active / paused / cancelled |

### `bot_configs`
One row per tenant's bot setup, produced by Onboarding
(`docs/product/ONBOARDING_FLOW.md`). Values come from the fixed menus in
`docs/product/CUSTOMER_FACING_RULES.md` — never raw customer-authored
prompt text.

| Column | Notes |
|---|---|
| `tenant_id` | foreign key |
| `bot_type` | chat / secretary / etc, from `CUSTOMER_SEGMENTS.md` |
| `tone` | from fixed menu |
| `business_info` | hours, prices, policies — structured, not free text |
| `enabled_tools` | which MCP tools this tenant's bot can call |

### `conversations`
Current/recent conversation turns (memory layer 1-2, see below).

| Column | Notes |
|---|---|
| `tenant_id` | foreign key — isolation boundary |
| `end_customer_id` | identifies the tenant's own customer, not a platform-wide user |
| `message` | |
| `role` | user / bot |
| `timestamp` | |

### `memory_summaries`
Long-term memory (layer 3) — summarized, not full transcripts.

| Column | Notes |
|---|---|
| `tenant_id` | foreign key |
| `end_customer_id` | |
| `summary` | short, retrievable-by-keyword fact, not a full log |
| `created_at` | |
| `expires_at` | **required** — see retention note below |

### `usage_log`
Owned by Cost Guard.

| Column | Notes |
|---|---|
| `tenant_id` | foreign key |
| `date` | |
| `message_count` | |
| `estimated_cost` | |

## Memory layers, mapped to tables

1. **Current conversation** — recent rows in `conversations`, capped in
   count, not stored as an ever-growing log fed whole into the model
2. **Rolling summary** — periodic batch job condenses old `conversations`
   rows into `memory_summaries`, then the source rows can be pruned
3. **Long-term searchable memory** — `memory_summaries`, queried by simple
   keyword match in Phase A (not vector search — that's a `docs/future/`
   upgrade once volume justifies pgvector)
4. **Business info** — `bot_configs.business_info`; not really "memory" at
   all, just config, and the cheapest layer to serve

## Retention (PDPA layer 2)

`memory_summaries.expires_at` is mandatory on every row. A scheduled job
prunes expired rows. `conversations` rows older than the active window
either get summarized into `memory_summaries` or dropped — they don't
accumulate indefinitely either way. Exact retention period: set with a
compliance advisor per `docs/security/PDPA_COMPLIANCE.md`.

## What this intentionally leaves out (Phase A)

- Row-level security (RLS) enforced at the database layer — Phase A relies
  on every query being tenant_id-scoped by convention/code review, not a
  database-enforced guarantee. This is the biggest gap versus the full
  contract in `docs/future/` and the main reason to graduate off this
  schema before scaling past Phase A's tenant ceiling.
- Vector search / pgvector
- Versioned agent config / activation history
- Formal audit-event tables (Phase A logs to the Decision Log and
  Monitoring pipeline instead — see `docs/warroom/`)
