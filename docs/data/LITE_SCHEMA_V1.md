# Lite schema v1 — Phase A

Status: **ACTIVE — Phase A**

## Principle

Shaped after `docs/future/data/IDENTITY_TENANCY_CONTRACT_V1.md` so growing
into the full contract later is additive, not a rewrite — but sized for
n8n + one plain relational database (self-hosted PostgreSQL is fine) at up
to ~30 tenants.

Scope chain: **tenant → bot → channel → end customer → conversation**.

- A tenant (a business) can have more than one bot (see
  `docs/product/PRICING_V1.md`: extra bots are paid add-ons).
- A bot can be reachable on more than one channel (LINE OA, web chat).
- Every row that holds customer data carries both `tenant_id` and `bot_id`.
  `tenant_id` is the isolation and PDPA boundary
  (`docs/security/PDPA_COMPLIANCE.md`, Layer 3). `bot_id` keeps one bot's
  memory from mixing with another bot of the same tenant.

## Tables

### `tenants` — the businesses renting bots
| Column | Notes |
|---|---|
| `tenant_id` | primary key |
| `business_name` | |
| `owner_contact` | how the platform reaches the business owner |
| `signup_date` | |
| `status` | active / paused / cancelled |
| `consent_accepted_at` | when the owner accepted the tenant agreement (PDPA controller/processor terms) |

### `bots` — one row per bot; config produced by Onboarding
| Column | Notes |
|---|---|
| `bot_id` | primary key |
| `tenant_id` | FK |
| `bot_type` | chat / secretary / … from `docs/product/CUSTOMER_SEGMENTS.md` |
| `tone` | fixed-menu value (`docs/product/CUSTOMER_FACING_RULES.md`) |
| `business_info` | structured fields (hours, prices, policies) — never raw customer-written prompt text |
| `enabled_tools` | list of MCP tools this bot may call |
| `monthly_message_quota` | chat reply quota for this bot (`PRICING_V1.md`) |
| `monthly_push_quota` | push/reminder cap for this bot — default 200 (`PRICING_V1.md`) |
| `status` | active / paused |

### `channels` — where a bot is reachable
| Column | Notes |
|---|---|
| `channel_id` | primary key |
| `tenant_id`, `bot_id` | FK |
| `channel_type` | `line_oa` / `web_chat` |
| `credential_ref` | reference to the secret stored in n8n credentials — **never the token itself in this table** |

### `end_customers` — the tenant's own customers
| Column | Notes |
|---|---|
| `end_customer_id` | primary key |
| `tenant_id`, `bot_id` | FK |
| `channel_id` | where first seen |
| `external_user_ref` | e.g. LINE userId — scoped to this tenant only |
| `consent_notice_shown_at` | PDPA Layer 1 notice timestamp |
| `last_active_at` | drives retention |

### `conversations` — recent turns (memory layers 1–2)
| Column | Notes |
|---|---|
| `tenant_id`, `bot_id`, `end_customer_id` | FK |
| `role` | user / bot |
| `message` | |
| `created_at` | |

### `memory_summaries` — long-term memory (layer 3)
| Column | Notes |
|---|---|
| `tenant_id`, `bot_id`, `end_customer_id` | FK |
| `summary` | short fact, keyword-searchable — not a transcript |
| `created_at` | |
| `expires_at` | **required** (retention) |

### `usage_log` — owned by Cost Guard
| Column | Notes |
|---|---|
| `tenant_id`, `bot_id` | FK |
| `date` | |
| `reply_count` | LINE reply messages — free delivery, cost is model call only |
| `push_count` | LINE push messages — capped at `bots.monthly_push_quota` |
| `model_tokens` | |
| `estimated_cost_thb` | |

## Memory layers mapped to tables

1. **Current conversation** — the last N rows of `conversations` for this
   `bot_id` + `end_customer_id` (N capped; never the whole history)
2. **Rolling summary** — a scheduled job condenses older `conversations`
   rows into `memory_summaries`, then deletes the source rows
3. **Long-term memory** — `memory_summaries`, keyword match in Phase A
   (vector search is a `docs/future/` upgrade)
4. **Business info** — `bots.business_info`; config, not memory; cheapest
   layer to serve

## Retention and deletion (PDPA Layer 2)

- `memory_summaries.expires_at` is mandatory; a daily job deletes expired rows.
- `conversations` older than the active window are summarized or deleted.
- End customers inactive past the retention period (set with a compliance
  advisor) are deleted with all their rows.
- A deletion request deletes every row for that `end_customer_id`.
- Cancelling a tenant: data is kept for a short grace period, then all
  rows for that `tenant_id` are deleted (`docs/product/BUSINESS_OPERATIONS.md`).

## Isolation rule every query must follow

Every read and write filters by `tenant_id` **and** `bot_id`. Phase A has no
database-enforced row-level security, so this is enforced by (a) one shared
n8n sub-workflow for all data access that always takes both IDs, and (b)
Auditor testing cross-tenant access before any new workflow goes live. This
is the largest known gap versus the full design in `docs/future/` and a
reason to graduate from this schema before scaling past Phase A.

## Deliberately left out (Phase A)

Database-enforced RLS, vector search, versioned bot config history,
formal audit-event tables (Phase A uses the Decision Log and monitoring
log in `docs/warroom/`).
