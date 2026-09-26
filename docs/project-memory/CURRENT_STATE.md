# Nippan AI Platform — Current State

Last updated: 2026-09-27 (session 8 — doc cleanup, card T-058)
Status: ACTIVE — PHASE A MARKET TEST PIVOT (dev-time)

> **One home per fact (card T-058):** model pins live **only** in
> `docs/product/MODEL_ROSTER.md` · what to do next lives **only** in
> `docs/project-memory/SESSION_HANDOFF.md` · the rules live in `AGENTS.md`,
> `docs/warroom/AI_OPERATING_PROTOCOL.md` and `docs/warroom/TASK_CONTROL.md`.
> This file records what is actually built / shared today — not designs, and not
> history (completed work is in `docs/archive/TASKS_DONE_ARCHIVE.md` and
> `docs/warroom/decision-log.md`).

## Provider & model pins — single source, not copied here

The dev team runs on the **OpenCode Go** paid provider as the primary pool, with
OpenRouter / OpenCode Zen as backup (card T-035). The per-role Primary/Backup
table lives in `docs/product/MODEL_ROSTER.md` § "Per-role staffing" — do not copy
it here; a second copy drifts (it already did once, which is why this copy is gone).

Two rules that are easy to get wrong and stay written out because they are cheap to restate:

- A Go model slug **must** be written `opencode-go/<id>`. A Zen-style `opencode/<id>` for a Go
  model fails with an opaque `Unexpected server error` that looks like a permission problem but
  is a naming problem — check the slug before reporting a model broken.
- `qwen/qwen3.7-flash` is **permanently banned** (Owner order, False-DONE incident).

## Repository & Workspace

Repository: `supermansexy-png/Nippan-AI-Platform`

Working location (single source): `C:\opencode\nippan` — branch `dev-workspace`,
created from `docs/post-remediation-state @ 71c0640` (real code + full history).

The template folder `C:\Users\chetgo\Desktop\github\Nippan-AI-Platform-phase-a`
was the design template only. On 2026-09-24 the Owner approved copying the
finished template set into the real workspace and **stopped using the template
folder**. Do not read or edit the template folder anymore.

Existing workspace files (`AGENTS.md`, `README.md`, `docs/decisions/ADR-*`,
data contracts, …) were kept as-is rather than overwritten, because they are
project-specific.

## Primary working branch

`dev-workspace` — created 2026-09-24 from `docs/post-remediation-state` (base for
T-001 work on the real code). History of the earlier War Room remediation lives in
`docs/post-remediation-state`.

## Pivot Note

On 2026-09-24 the Owner approved pivoting the plan to the Phase A market test:
rent AI bots to up to 30 small Thai businesses at 299 THB/mo, running on a
self-hosted n8n + PostgreSQL lite schema.

The previous full-stack design (FastAPI + Cloudflare + pgvector/RLS …) was **not**
deleted. It is preserved under `docs/future/` as the archived blueprint, and the
prior Git history remains. Do not pull anything out of `docs/future/` for current
work — see `docs/future/README.md` for the conditions.

## Phase A Database — Lite Schema V1

7 tables on Supabase (`lite_` prefix, to avoid a name conflict with the existing
Phase 2 core tables):

- `lite_tenants` — businesses renting bots
- `lite_bots` — bot configs with quotas (message + push), enabled tools
- `lite_channels` — reachability adapters (line_oa, web_chat)
- `lite_end_customers` — the tenant's customers, with PDPA consent tracking
- `lite_conversations` — recent turns, partitioned by tenant+bot+customer+time
- `lite_memory_summaries` — long-term memory facts with mandatory `expires_at`
- `lite_usage_log` — reply/push counts, model tokens, estimated cost

Schema properties:

- Every customer-carrying table has **both** `tenant_id` and `bot_id` as FKs
- `memory_summaries.expires_at` is NOT NULL (mandatory retention deadline)
- Full column spec verified against `docs/data/LITE_SCHEMA_V1.md` via `information_schema.columns`
- FK-chain INSERT/SELECT test passed; migration committed at `ab8c0d6`

**RLS is LIVE** on the real Supabase project `xzxwakvsbdzkdybijbzs`: all 7
`lite_*` tables FORCE RLS, policy role `nippan_runtime`, scope set per transaction
from `app.tenant_id` / `app.bot_id`; the runtime login role `nippan_n8n` is a
member of `nippan_runtime` and is **not** BYPASSRLS (T-026 + T-RLS-01, migrations
`20260925120000_lite_rls_v1.sql`, `20260925130000_n8n_runtime_login_role.sql`,
PR #83 merged).

The n8n-side read/write proof was **the open item T-030 — now DONE** (Owner
approved 2026-09-26): RLS read isolation, write isolation (cross-tenant INSERT
rejected 42501) and the connected role are proven, evidence in
`docs/n8n/T-030-execution-evidence.md`. Owner scope condition: n8n read/write is
allowed **only inside the `Nippan Phase A` folder**.

Residual (documented, not fixed): the n8n credential still has `Ignore SSL
Issues`; the credential path connects outside `services/dev/tools/data_access.py`,
so the app-level scope helper is not what enforces isolation on that path — RLS is.

## Protected Production System

`Ai-bot-Nippan` production is OUT OF SCOPE unless the Project Owner explicitly
authorizes changes. Do not modify its service, data, credentials or workflows.

## Source-of-Truth Rule

Repository and runtime evidence override this document whenever they disagree.
Correct this document when verified state changes.
