# Nippan AI Platform — Current State

Last updated: 2026-09-25
Status: ACTIVE — PHASE A MARKET TEST PIVOT (dev-time)

## Repository & Workspace

Repository:
supermansexy-png/Nippan-AI-Platform

Working location (single source):
C:\opencode\nippan — branch `dev-workspace`, created from
`docs/post-remediation-state @ 71c0640` (real code + full history).

The template folder
`C:\Users\chetgo\Desktop\github\Nippan-AI-Platform-phase-a` was the design
template only. On 2026-09-24 the owner approved copying the finished template
set into the real workspace and **stopped using the template folder**.
Do not read or edit the template folder anymore. Verified copy:

- `.opencode/agents/*` — 7 dev-time agents, already present and identical
  (builder, model-recruiter, ops, project-lead, researcher, reviewer, security)
- `docs/warroom/*` — 10 files (AI_OPERATING_PROTOCOL, TASK_CONTROL, ROLES,
  DEV_WORKING_GUIDE, STARTUP_PLAYBOOK, START_PROMPT, TASK_CONTROL, ai-scorecard,
  DECISION_LOG_FORMAT, MONITORING)
- `docs/product/*` — shown in git tree (incl. MODEL_POLICY.md)
- `TASKS.md`, `WORKING_POLICY.md`
- Missing-only merge of 29 other template files (docs/future/, LITE_SCHEMA_V1,
  PIVOT_OPTION, PDPA_COMPLIANCE, FEASIBILITY_REVIEW.th.md, README.th.md, ...)

Existing workspace files (AGENTS.md, PROJECT_STATE.md, README.md, ROADMAP.md,
docs/decisions/ADR-*, docs/data contracts, etc.) were kept as-is (not
overwritten) because they are project-specific.

## Primary working branch (new design)

`dev-workspace` — created 2026-09-24 from `docs/post-remediation-state`
(base for T-001 work on the real code). History of prior War Room remediation
lives in `docs/post-remediation-state`.

Default branch (template artifact): source of the copied set, kept as history.

## Pivot Note

On 2026-09-24 the owner approved pivoting the plan to Phase A market test:
rent AI bots to up to 30 small Thai businesses at 299 THB/mo, running on a
self-hosted n8n + PostgreSQL lite schema, with OpenRouter as model gateway.

The previous full-stack design (FastAPI + Cloudflare + pgvector/RLS etc.) was
NOT deleted. It is preserved under `docs/future/` as the archived blueprint,
and prior Git history remains in the repository.

## Phase A Database — Lite Schema V1

7 tables applied to Supabase project `nippan-ai-platform` (`lite_` prefix to avoid
name conflict with existing Phase 2 core tables):

- `lite_tenants` — businesses renting bots
- `lite_bots` — bot configs with quotas (message + push), enabled tools
- `lite_channels` — reachability adapters (line_oa, web_chat)
- `lite_end_customers` — tenant's customers with PDPA consent tracking
- `lite_conversations` — recent turns partitioned by tenant+bot+customer+time
- `lite_memory_summaries` — long-term memory facts with mandatory expires_at
- `lite_usage_log` — reply/push counts, model tokens, estimated cost

Schema properties:
- Every customer-carrying table has BOTH `tenant_id` AND `bot_id` as FKs
- `memory_summaries.expires_at` is NOT NULL (mandatory retention deadline)
- No DB-level RLS (Phase A isolation at n8n sub-workflow level)
- Full column spec verified against `docs/data/LITE_SCHEMA_V1.md` via information_schema.columns
- INSERT/SELECT test passed confirming FK chain works
- Migration committed at `ab8c0d6`

## Dev-Time Team (current working model)

Dev-time team = the repo agents in `.opencode/agents/`:
- `project-lead.md` — Project Lead (dev-time): owns repo work, picks the
  smallest needed dev specialists, follows TASK_CONTROL / AI_OPERATING_PROTOCOL
  (INTAKE/DELIVERY, L1–L3, WIP, budget stop), reports to owner in Thai.
- `model-recruiter.md` — HR / Model Recruiter (dev-time): finds models for the
  dev team under `MODEL_POLICY.md` cost/value rules ($0.25/$1.00 thresholds,
  Zen free-only, retry/failover, quality-failure).
- `builder.md`, `reviewer.md`, `security.md`, `ops.md`, `researcher.md`, `assistant.md` —
  dev-time specialists, all following the same protocol. `assistant` (added 2026-09-25,
  T-023) is a free-model general helper for support work.

All 7 roles are staffed (approved by owner 2026-09-24): Primary + Backup per
role verified against the whole OpenRouter catalogue (T-014) with prices,
provider diversity and anti-redundancy cross-checks passing — see
`docs/product/MODEL_ROSTER.md` (single source for model choice; do not copy
model names into role definitions). Rules enforced: value-first cost policy,
catalogue-wide recruitment (Owner rule), anti-redundancy (reviewer/security
must be a different model from builder's Primary AND Backup).

Runtime roster (Developer/Model Scout/Cost Guard/Onboarding/Support/Router
etc.) in `docs/warroom/ROLES.md` is the post-launch ecosystem; it is not built
at dev time.

## Model Policy

`docs/product/MODEL_POLICY.md` — cost/value policy, OpenCode Zen exception,
retry/failover, quality failure, work style, never-hardcode-a-model-into-a-role
(applies to agent definitions; dev-time reporting may name the actual model).

## War Room Remote Auth (historical record)

PR #73 and PR #79 remote auth remediation are MERGED (4ab568f). These remain
verified evidence but the forward plan no longer builds on that runtime.
JWKS refresh throttling from the old remediation is closed history.

## Runtime Containment

Historical: pre-remediation War Room runtime `https://chetgo.onrender.com`
verified; after PR #79 direct Render requests returned HTTP 403 and Cloudflare
Access handled auth. This runtime is no longer the forward plan.

## Audit

Independent Audit System is **SUSPENDED** by the Project Owner (2026-09-24).
Progress gates do not block milestones. Do not invoke the paid Independent
Auditor unless the Project Owner re-enables it. Normal code review, security
review, tests, CI and evidence verification remain allowed. Historical audit
records under `docs/audits/` are preserved.

## War Room (resumed 2026-09-24)

Owner ordered War Room work brought back:
1. for dev-time use in the AI team workflow
2. as a backstage ecosystem for AI when the system runs

Increment C audit-accepted progress remains 13/16 (81.25%); Track D
(D-01/D-02/D-03) is the remaining acceptance work. Planning card: T-006
(IN_PROGRESS). Draft cards: T-007 (D-01), T-008 (D-02), T-009 (D-03),
T-010 (preview auth), T-011 (dual-use positioning).

Dual-use positioning note written: `docs/proposals/WAR_ROOM_DUAL_USE_POSITIONING.md` (2026-09-24).

## Protected Production System

`Ai-bot-Nippan` production is OUT OF SCOPE unless the Project Owner explicitly
authorizes changes. Do not modify its service, data, credentials or workflows.

## Immediate Next Step

Owner accepted T-005 (audit suspension) and ordered War Room planning.
T-006 IN_PROGRESS: draft cards T-007..T-011 ready for owner direction
approval. Then execute Track D sequence T-007 → T-008 → T-009 (with T-010
auth in parallel if scope allows) alongside Phase A Step 0 (T-001..T-004)
within WIP limits (max 3 IN_PROGRESS).

1. War Room feature work is NO LONGER deferred — owner explicitly resumed it
   for dev-time use and runtime backstage ecosystem.
2. Treat `docs/future/` as archived blueprint; a step needing it must be
   flagged NEEDS_DECISION for Project Lead.
3. Do not use the template folder anymore — it is merged into this workspace.
4. Dev-time team = repo agents in `.opencode/agents/`; do not confuse them with
   runtime roles.
5. Independent Audit System remains suspended — do not invoke paid auditor.

## Model Enforcement Fix (2026-09-25)

Root cause found: agent files in `.opencode/agents/` had NO `model:` pinned, so
opencode fell back to other models — the approved MODEL_ROSTER.md was never
enforced at runtime (verified in opencode.log: builder ran on deepseek, reviewer
on qwen). Fixed by pinning `model:` in every agent frontmatter (commit 454e123).
Verified after restart: `agent=builder` → `qwen/qwen3.7-flash`,
`agent=reviewer` → `z-ai/glm-5.3-flash`. **SUPERSEDED 2026-09-25 (Owner order):
builder is now `z-ai/glm-5.3-flash` (locked, not to be swapped) and reviewer
L1–L3 is `opencode/space-bunny-free`; L4 is `anthropic/claude-opus-5.5:batch`.
See "Team update 2026-09-25" in MODEL_ROSTER.md.**

Current leadership (2026-09-25):
- project-lead: `deepseek/deepseek-v4.1-flash` (previous `qwen3.7-flash` suspended
  for protocol violations — see ai-scorecard.md, decision-log.md)
- model-recruiter (HR): `openai/gpt-6-luna` (previous `qwen3.7-flash` dismissed for
  False DONE)

## T-015 Repo Integrity Cleanup — DONE (2026-09-25)

HR audit found multiple cards marked DONE whose artifacts were only uncommitted.
T-015 committed all genuine pending work (T-010 auth code+tests, T-001 artifacts,
T-011 doc, T-005 doc edits, SYSTEM_CONSTRAINTS), removed junk
`services/core/_debug_test.py`, corrected T-001/T-007 to PARTIAL, and fixed the
T-014 cross-check. Independently verified by reviewer (live DB: 7 `lite_*` tables
confirmed) and security (no real secrets committed). See TASKS.md T-015.

## Cost Reduction (T-018) — DONE (2026-09-25)

Owner approved item 2 of the cost plan. Trimmed the always-read preamble and
added report-length caps: `START_PROMPT.md` 112→53 lines; agent prompts
`project-lead` 146→88 and `model-recruiter` 99→68, plus a 4-line output cap in
`builder/reviewer/security/ops/researcher`. No protected doc touched. Evidence is
line counts only (realized token saving not measured). Requires an opencode
restart to reload the agent prompts.

## Review Tiers — free models for review (T-020) — DONE (2026-09-25)

Owner approved using OpenCode Zen free models for reviewer/security at all levels:
L1/L2 → `opencode/nemotron-3-ultra-free`; L3/sensitive → `opencode/space-bunny-free`
(only stated zero-retention model); paid fallback `z-ai/glm-5.3-flash`. Applied to
`MODEL_ROSTER.md` ("Review tiers"), `START_PROMPT.md` and the reviewer/security agent
prompts. Zen's free tier works ONLY inside opencode (raw HTTP → 403 `FreeTierError`),
and the Zen provider is NOT yet connected in opencode auth — so this does not take
effect until the Owner connects Zen and opencode is restarted. A key was shared in
chat and must be rotated. In the test, 8/11 free Zen models passed a planted-bug
review task; `jev-1.13-free`, `deepseek-v4-flash-free`, `mimo-v2.5-free` failed.

## Model Policy — paid builder + free helper roles + paid L4 (T-022/T-023) — DONE (2026-09-25)

Owner policy (corrected by T-023): the Project Lead thinks/plans only. The **main builder
stays on the paid model** (`z-ai/glm-5.3-flash`, Owner-locked 2026-09-25); free OpenCode Zen models are used for the
**helper positions** (assistant, ops, researcher) and for review/security at L1/L2/L3.
**L4 (critical / high-accuracy verification) uses paid `anthropic/claude-opus-5.5:batch` (Owner-selected).** Reviewer
(`nemotron-3-ultra-free`) and security (`big-pickle`) use **different** free models.
Recorded in `MODEL_ROSTER.md`, `START_PROMPT.md`, the agent files and `opencode.json`
(`small_model` free). Needs an opencode restart to load. Free tier may log/train → no
secrets in prompts.

## Free OpenRouter model test (T-024) — DONE (2026-09-25)

Owner ordered the same free-model role-suitability screening as T-021 but for
OpenRouter `:free` models (12 candidates, all endpoint-VERIFIED live at $0/M).
6 models were initially blocked by the OpenRouter workspace guardrail ("Free
model training violation") — Owner opened the setting, then they were tested on
the coding line (builder + reviewer, T-020 planted-bug task). Full record:
`docs/product/FREE_MODEL_OPENROUTER_TEST_T024.md`.

Scored (10 models): `nex-n2.5-mini:free` 5/5 and `nex-n2.5-pro:free` 5/5 (but
uptime ~90%, p99 ~3min flagged) — best; `north-mini-code:free` 4/5 and
`qwen3.8-27b:free` 4/5 (both failed hr precision: "Yes" ผิดบน partial index
`now()`); coding line: `inkling-small:free` builder PASS + reviewer 2/2 (best),
`inkling` + `nemotron-3-ultra-550b` builder FAIL (wrote files instead of inline
code), `laguna-s/xs` + `nemotron-3-super` reviewer FAIL 1/2 (missed the
tenant/bot isolation bug). `gemma-4-26b/31b:free` — no score (rate-limited all
session). RECORD ONLY — no roster change (Owner order). Reviewer
(`space-bunny-free`) verified score tables against raw files (13 files) — ACCEPTED.

## Free model fallback guide (T-025) — DONE (2026-09-25)

Owner ordered a consolidated reference for free-model substitutes across
both tested camps (Zen T-021 + OpenRouter T-024): `docs/product/FREE_MODEL_FALLBACK_GUIDE.md`.
Ranked best→worst per role + per-role substitute table (1st/2nd/3rd pick) +
avoid list (models that missed the isolation bug or answered precision wrong).
Record only — MODEL_ROSTER.md untouched; anti-redundancy respected; $0.

## War Room T-008/T-009 fix round (2026-09-25, builder z-ai/glm-5.3-flash)

REVIEW (2026-09-25) returned both cards. Fixes delivered (uncommitted, dev-workspace):
- T-008 fix 1: `SUBMIT_OWNER_DECISION` now carries the owner's decision content
  (text or reference + acting owner principal_id) on the ROOM_STATE_CHANGED event;
  `PostgresRoomEventSink` projects it into `public.project_room_decisions`
  (OWNER_DECISION/ACCEPTED + decided_at) in the same locked transaction; invalid
  payload fails closed before any write. No schema change (table already existed).
- T-008 fix 2: preview local-access fallback now verifies the request really
  arrives over a loopback socket; otherwise 403 `war_room_preview_loopback_only`
  (fail-closed; loopback dev use preserved).
- Hygiene: transport docstring + `services/core/README.md` corrected ("no route
  invokes run_next_turn" was stale — it runs when model turns are enabled, default
  OFF); dated correction appended to `WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md`;
  old qwen DELIVERY blocks in TASKS.md marked INVALID (kept as record).
- Evidence: `python -m pytest -q` from services/core = 138 passed, 6 skipped
  (was 120 passed; +18 new tests, none weakened). 6 skipped = PostgreSQL
  integration tests (no DSN in this env).
- T-009: no code defect; static wiring VERIFIED via live-passing fast tests;
  live render with real usage_events still UNVERIFIED → PARTIAL.

## War Room T-008/T-009 — COMPLETE (dev-time) (2026-09-25, final)

Both War Room acceptance cards are DONE on branch `dev-workspace`:
- T-008 (D-02): the `owner_decision` payload key that violated the frozen event
  schema was removed; the owner decision now rides only frozen fields
  (`content_text` / `content_reference`, `message_type=OWNER_DECISION`, top-level
  `participant_id` = acting owner principal). `PostgresRoomEventSink` projects it
  into `public.project_room_decisions` in the same transaction and fails closed on
  invalid data. A non-UUID owner principal (`preview-owner`) no longer breaks the
  append: `project_room_messages.participant_id` is stored NULL for owner-decision
  events only, while every other event type keeps strict UUID validation.
- T-008 (transport): the preview local-access fallback now verifies the real socket
  peer (`_request_is_loopback`, IPv4-mapped IPv6 handled); non-loopback → 403
  `war_room_preview_loopback_only`. Residual documented: a proxy/tunnel bound to
  127.0.0.1 can still relay a remote client — do not tunnel the preview.
- T-009 (D-03): live proof obtained — a real embedded PostgreSQL 16 (pgserver, all
  7 migrations applied) ran the whole suite: **152 passed, 0 skipped**. All 6
  previously-skipped integration tests executed (bootstrap, persistence under RLS,
  preview seed ×2, read-model projection from real `usage_events`, HTTP transport
  persisting owner commands with zero provider spend).
- Gates: reviewer `opencode/space-bunny-free` = ACCEPT (7-file diff); security
  `opencode/muse-spark-1.2-contributor-free` = ACCEPT (the primary
  `nex-n2.5-mini:free` produced no answer — token limit); anti-redundancy satisfied.
- Local harness (gitignored, `runs/`): `pg_it.py` + `winloop_plugin.py` +
  `extract_text.mjs`; a pgcrypto shim was added under pgserver's site-packages
  extension dir (local test only).
- Residual / next: the deployed Supabase preview itself was not exercised (no DSN) —
  an Owner-only deploy/preview step (item 8). All work committed locally on
  `dev-workspace`.

## T-026 Lite RLS + bridge guards + board state (2026-09-25, final)

- T-026 (L3, tenant/bot isolation) DONE and archived. `migrations/20260925120000_lite_rls_v1.sql`
  enables + forces RLS on all 7 `lite_*` tables; policies keyed `tenant_id` (+`bot_id`) for role
  `nippan_runtime`. `services/dev/tools/data_access.py` sets `app.tenant_id`/`app.bot_id` per
  transaction and now forces one transaction (autocommit off + commit/rollback) — fixes the
  autocommit-reset bug that silently returned 0 rows; regression-tested.
- Evidence: embedded PostgreSQL 16 — three SQL invariant suites PASS; `test_data_access.py`
  = 29 passed; core live suite = 156 passed / 3 skipped. CI `A-001 DB privilege regression`
  now runs the lite RLS invariant + dev-tools tests (run 36126088741, success).
- Bridge `.opencode/bridge/server.mjs`: external dev-time assistant scoped under the PL —
  session allowlist + 8000-char cap; `opencode_start_task`/`opencode_abort_task` registered only
  when env-enabled + token match; live MCP test passed (session outside allowlist rejected).
- Board: T-026 archived → `TASKS.md` ACTIVE is now empty (0 open cards). Commits on
  `dev-workspace`: b86dfe9, 5dd62b8, 11e8802, 50a8f2f (pushed to origin).
- Residual (documented, not fixed): the n8n credential path connects outside `data_access.py`;
  superuser / SECURITY DEFINER can still bypass RLS.
- Next: pick the next card; parked T-001 (n8n + PostgreSQL hosting) still blocked on Docker;
  the T-026 residual could become a follow-up card.

## Session 2026-09-25 (2) — bridge, n8n MCP, gateway recon

- **Bridge** (`.opencode/bridge/server.mjs`) = the dev-time link to the external OpenAI
  assistant (gpt-5.6-sol) via the Cloudflare tunnel-client → `127.0.0.1:4100`. Fixes this
  session: `/.well-known/*` now returns **JSON 404** (was the Express HTML page, which broke
  the OpenAI connector's OAuth discovery); guardrails added — audit log
  (`.opencode/bridge/privileged-audit.log`), 10-minute session rate limit, `abort_task`
  limited to sessions this bridge created, and a **PAUSE** kill switch
  (`.opencode/bridge/PAUSE` suspends all mutating tools with no restart). The Owner
  re-enabled the privileged tools (`opencode_start_task` / `opencode_abort_task`) with a
  token; live-verified: 7 tools, wrong token rejected, PAUSE blocks `send_message`.
- **opencode MCP config**: added `n8n` remote MCP (`https://n8n.nippan.org/mcp-server/http`,
  bearer from env `N8N_MCP_TOKEN`) — verified working (39 tools). Every mutating n8n tool is
  disabled except `create_folder` (Owner order: the existing n8n work is **legacy — read-only,
  do not touch**). Added `nippan-gateway` (`https://mcp.nippan.org/mcp`, Cloudflare Access) but
  left `enabled: false`: its OAuth needs the redirect URI
  `http://127.0.0.1:19876/mcp/oauth/callback` registered in the Cloudflare OAuth client.
- **n8n recon (read-only)**: 5 active workflows — Personal Assistant - LINE, Bot n8n MCP Tools,
  Task Reminder - LINE, Personal Assistant - LINE Group, Skill Loader (all the Owner's legacy
  personal automation); 2 data tables (`line_sessions`, `group_members`); 10 credentials
  (LINE Messaging, Google, Gemini, SerpApi, WooCommerce, `nippan-ai-bot` basic auth) —
  **no PostgreSQL credential yet**. Conclusion: Step 0 "n8n + HTTPS" is satisfied by the
  existing host; the missing link is **n8n → PostgreSQL lite schema**.
- **Board**: empty (T-026 archived). **PR #83 is OPEN** (waiting for the Owner to merge).
  Suggested next card **T-030 — wire n8n → PostgreSQL lite schema** (needs the Owner: Supabase
  connection string + permission to create new workflows inside a dedicated folder
  `Nippan Phase A`).
- **Owner actions pending**: restart opencode after the config changes; confirm/create the n8n
  folder; merge PR #83.

## Source-of-Truth Rule

Repository and runtime evidence override this document whenever they disagree.
Correct this document when verified state changes.