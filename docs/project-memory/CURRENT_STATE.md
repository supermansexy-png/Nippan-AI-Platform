# Nippan AI Platform — Current State

Last updated: 2026-09-27 (session 10 — Owner 8-step instruction: T-071 rework, T-072 MCP, 3 new structure cards, Owner queue, tool survey, ChatGPT Issues)
Status: ACTIVE — PHASE A MARKET TEST PIVOT (dev-time)

**สถานะโครงการ: ยังไม่มีผู้เช่า ไม่มีผู้ใช้ ระบบยังไม่เปิด (pre-G1) — ฐานข้อมูล Supabase เป็นของทดสอบ ไม่มีข้อมูลลูกค้าจริง งานทดสอบ/backup/restore ทำบนฐานจริงได้โดยตรง ไม่ต้องกันข้อมูลผู้เช่า (ที่ยังไม่มี) แต่ยังห้ามแตะระบบ production เก่า Ai-bot-Nippan**

> **One home per fact (card T-058):** model pins live **only** in
> `docs/product/MODEL_ROSTER.md` · what to do next lives **only** in
> `docs/project-memory/SESSION_HANDOFF.md` · the rules live in `AGENTS.md`,
> `docs/warroom/AI_OPERATING_PROTOCOL.md` and `docs/warroom/TASK_CONTROL.md`.
> This file records what is actually built / shared today — not designs, and not
> history (completed work is in `docs/archive/TASKS_DONE_ARCHIVE.md` and
> `docs/warroom/decision-log.md`).

## Session 10 state (2026-09-27) — Owner instruction via advisor (8 steps executed)

**Owner verbatim:** "แจ้งเตือนให้ทำเป็นหน้าให้กรอกได้ ให้เลือกกรอกทางเมล์ หรือทางไลน์ ผมจะกรอกเองเมือเปิดใช้งาน ตอนนี้ให้เขียนรอไว้ เรามี mcp ของ supabase ใช้ทางนั้นได้เลย และไม่เห็นจ่ายงานให้ chatgpt ให้เพิ่มงานที่ต้องเขียนโค๊ด งานที่ต้องวางเวิกโฟรใน n8n งานที่ต้องวางระบบฐานข้อมูล ให้ตรงกับดีไซต์ของโปรเจ๊ดที่ออกแบบมา อันไหนต้องเอาข้อมูลผม ยังไม่ต้องเอา ให้ไปจัดการวางโครงสร้างทั้งหมดให้เป็นรูปร่างก่อน ไม่งั้นมาติดอยู่ตรงนี้ ไม่มีเครื่องมืออะไรให้แจ้งที่เดียว ไม่ใช่ทำไปแจ้งไป ให้ลองสำรวจเครื่องมือทั้งหมดของเรา เรามีครบ และให้ ที่ปรึกาษาคุมงานโดยละเอียดทุกขั้นตอน ตรวจทานรอบสุดท้้ายกับ pl เมือผ่านแล้วให้อนุมัติได้เลย งานจะได้เดินต่อเนื่อง"

### 8 Steps executed:
1. **T-071 REWORK** — Settings page with Email|LINE selector, pluggable transports (EmailTransport, LineTransport stubs), config JSONB nullable fail-closed, SMTP credential blocker CANCELLED, PR #92 adjusted on branch `t-071-alert-channel`
2. **T-072 UPDATED** — Backup/restore proof via Supabase MCP (not pg_dump/CLI) to separate schema `t072_restore`
3. **3 New cards created**: T-074 (Code stream), T-075 (n8n workflow stubs), T-076 (DB schema/migrations) — each references design source files, Goal = "วางโครงสร้างให้เป็นรูปร่างก่อน", no Owner data/credentials needed
4. **OWNER_ACTION_QUEUE.md** created at `docs/warroom/OWNER_ACTION_QUEUE.md` — single queue for all Owner-wait items (5 OPEN, 8 DONE)
5. **Tool survey completed** — All tools enabled: Supabase MCP, n8n MCP, Render MCP, OpenRouter MCP, GitHub CLI, OpenCode Go pool (43 models). nippan-gateway = disabled (intentional)
6. **GitHub Issues for ChatGPT**: #93 (T-074), #94 (T-075), #95 (T-076) — all `ai:ready` label, queued for external assistant per two-lane Git channel
7. **Reviewer assignments** per T-065 roster: T-071/T-072/T-074/T-075 reviewer = `opencode/muse-spark-1.3-contributor-free` (Primary); T-076 security = `openrouter/deepseek/deepseek-v4.1-flash` (Primary). Advisor final review with PL then advisor approves merge
8. **ADVISOR_LOG.md** entry appended with full Owner verbatim, receiver=project-lead, auditor=space-bunny-free, verdict=pending

### Board state:
- **T-071** — IN_PROGRESS (rework started on PR #92, branch `t-071-alert-channel`)
- **T-072** — IN_PROGRESS (awaiting Supabase project ref, Supabase MCP ready)
- **T-073** — READY for INTAKE (awaiting Owner approval to start design)
- **T-074** — READY for INTAKE (Issue #93 ai:ready)
- **T-075** — READY for INTAKE (Issue #94 ai:ready)
- **T-076** — READY for INTAKE (Issue #95 ai:ready)
- **T-032** — pilot A DONE, pilot B pending (external assistant)
- **T-033** — War Room pilot ready for next round
- **T-050** — roadmap draft awaiting Owner review (DRAFT — NOT APPROVED)

### Model roster (T-065): all 9 dev roles re-staffed per the T-065 table (`MODEL_ROSTER.md` § "Per-role staffing"); runtime pins written to `.opencode/agents/*.md` + `opencode.json` (uncommitted). Post-restart live verification: **8/9 seats VERIFIED** (reviewer/ops/security/builder/researcher/advisor/assistant/model-recruiter); **project-lead NOT confirmed** — a resumed session keeps its own model; a brand-new session is required.

### Google free tier: key linked + verified in opencode (provider `google`, type=api, FREE tier); 2 models adopted — `google/gemini-flash-lite-latest` and `google/gemini-3.8-flash` — for **non-sensitive use only**.

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
