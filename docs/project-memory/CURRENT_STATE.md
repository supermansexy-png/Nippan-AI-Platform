# Nippan AI Platform — Current State

Last updated: 2026-09-25 (session 2 — rules settled, Git work channel chosen, meeting closed)
Status: ACTIVE — PHASE A MARKET TEST PIVOT (dev-time) — work dispatched over Git; bridge dropped

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
- ~~No DB-level RLS (Phase A isolation at n8n sub-workflow level)~~ **SUPERSEDED 2026-09-25 — DB-level RLS is LIVE** on the real Supabase project `xzxwakvsbdzkdybijbzs`: all 7 `lite_*` tables FORCE RLS, policy role `nippan_runtime`, scope set per transaction from `app.tenant_id` / `app.bot_id`; the runtime login role `nippan_n8n` is a member of `nippan_runtime` and is **not** BYPASSRLS (T-026 + T-RLS-01; migrations `20260925120000_lite_rls_v1.sql`, `20260925130000_n8n_runtime_login_role.sql`; PR #83 merged). The n8n-side read/write proof is still open = T-030.
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

**Two things were sharing one name — separated by the Owner on 2026-09-25 (see `AGENTS.md` §Independent Audit Status):**
- **Independent Audit (the gated process + the standalone third-party Auditor) — OFF.** The 25/50/75/90/100 progress gates are **cancelled outright** (2026-09-25), on top of the 2026-09-24 suspension. The Owner runs **one single large audit when the work is complete** — defined by the Owner on 2026-09-26 as **"ตอนปิดโปรเจ็คนี้ก่อนจะนำไปใช้งานจริง"** (at project close, before this project is put into real use), **not** when an internal track such as the War Room reaches 100%. Do not invoke a paid Independent Auditor unless the Owner re-enables that process.
- **L4 review tier — ALLOWED.** `anthropic/claude-opus-5.5:batch` for critical per-card verification only (security boundary, tenant/bot isolation, data handling). It is **not** an Independent Audit. Per-use approval: the Owner, **or the PL on the Owner's behalf when the Owner is away**; must go through the Batch API; use rarely and check credit first.
- Normal code review, security review, tests, CI and evidence verification remain allowed. Historical audit records under `docs/audits/` are preserved and must not be rewritten.

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

## Immediate Next Step (2026-09-25, session 2 — authoritative)

**Board: T-030 (READY) + T-032 (READY for INTAKE).** T-031 is DROPPED (Git is the work channel, not the bridge). Details and cards: `TASKS.md`, `TASKS_PARKED.md`.

Order the Owner set (2026-09-25): **finish the War Room first** (it is needed as the meeting room), then the n8n work.

1. **Restart opencode — DONE 2026-09-26.** Result: the 3 n8n workflow tools ARE now registered (`n8n_validate_workflow`,
   `n8n_create_workflow_from_code`, `n8n_execute_workflow` all used successfully). Still broken after the restart: the subagent model
   pins for `ops` and `researcher` resolve to the removed `opencode/muse-spark-1.2-contributor-free` (they cannot launch; the
   `.opencode/agents/*.md` files pin 1.3). `assistant` launches normally and was used as the stand-in.
2. **War Room D-01** (T-007, parked, 5/6 acceptance items met) — the last item is "owner loads `/war-room/` remotely"; PR #73/#79 remote auth is merged but D-01 was never formally closed, and Issues #35/#30 are still OPEN. Verify, then close.
3. **T-030 — work and evidence complete 2026-09-26; awaiting Owner approval.** Workflows `CVhNSU5pjpGgzquB` (v1) and `eohtRWY8YEvEuS7n` (v2) in folder `Nippan Phase A`; executions `5842` / `5844` prove RLS read isolation, write isolation (cross-tenant INSERT rejected 42501) and the connected role `nippan_n8n`; tables left empty (rollback). Reviewer `opencode/space-bunny-free` pass 2 = ACCEPT-WITH-FINDINGS, both pass-1 findings answered. Evidence: `docs/n8n/T-030-execution-evidence.md`.
4. **T-032** — dispatch work over Git: Owner answers the two open settings questions (branch protection on `dev-workspace`; the Codex-side values), then pilot A (read-only) → pilot B (one real PR).
5. Housekeeping (PL, delegated after restart): move the T-031 record into `TASKS_PARKED.md`, record the origin of the Owner's 3 manual commits (`625365d`, `d4ec435`, `01a49ac` — made while credit was exhausted), and one operator command: `git restore .opencode/bridge/server.mjs` (remove the deleted watcher's wiring).
6. **n8n environment note (2026-09-26):** `n8n_update_workflow` writes a new workflow version, but a manual execution still runs the OLD
   query until the workflow is published — so an edited workflow needs `n8n_publish_workflow` (currently `false` in `opencode.json`).
   `create_workflow_from_code` is immediately runnable.

**Standing rules for this phase (do not re-derive them):** file-type rule for who writes which files; dev-time approval = Owner, or PL when the Owner is away (deploy preview and architecture always need the Owner); protected-doc phase rule; audit/L4 as above; Context Discipline (heavy reading → subagent; no raw output in the main chat; close the chat when the card closes).

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

## Session 2026-09-25 (3) — PR #83 merged, RLS on the real Supabase, Bridge Watcher PARKED

- **PR #83 = MERGED** (2026-09-25 14:06 UTC) into `phase2/postgres-logical-schema`.
  It carried the T-026 lite RLS work, the bridge role/guards and the CI wiring.
- **RLS is now live on the real Supabase project** `xzxwakvsbdzkdybijbzs`
  (previously the T-026 proof existed only on an embedded PostgreSQL 16):
  - `20260925120000_lite_rls_v1.sql` applied → all 7 `lite_*` tables report
    `rls_on=true`, `forced=true`, exactly 1 policy each.
  - `20260925130000_n8n_runtime_login_role.sql` applied → role `nippan_n8n`
    (LOGIN, INHERIT, member of `nippan_runtime`, **not** BYPASSRLS, so the lite
    policies bind to it). The `postgres` role is BYPASSRLS, so connecting as
    `postgres` would silently defeat the whole isolation model.
  - Live boundary proof (run inside a transaction and rolled back, no residue):
    with scope set to tenant A, `tenants_visible=1`, `tenantB_visible=0`,
    `bots_visible=1`, `botB_visible=0`.
  - **Still pending (Owner)**: set the role password himself
    (`alter role nippan_n8n password '...'` in the Supabase SQL editor — never in
    chat) and create the n8n Postgres credential. A custom role through the
    Supabase pooler is **UNVERIFIED**; the direct connection is the known-good path.
- **n8n folder** `Nippan Phase A` created (personal project, id `zClFVASPRDPnaeuQ`).
- **Bridge Watcher v1 = IN_PROGRESS / PARKED, NOT DONE.** The bridge is pull-based, so
  the watcher records the real polling cadence from served traffic instead of probing:
  `watcher.mjs` (middleware + snapshot) wired into `server.mjs` (`app.use`, loopback-only
  `GET /watch` with optional `x-watch-token`, JSONL log `watch.jsonl`, gitignored).
  It records method/path/JSON-RPC method/tool name/status/timing and **never** message
  content or tool arguments. State: code partially written, **tests never run, no
  evidence, no reviewer** → must not be reported as DONE.
  Uncommitted files (5): `.opencode/bridge/watcher.mjs` (new),
  `.opencode/bridge/watcher.test.mjs` (new), `.opencode/bridge/server.mjs` (+42),
  `.gitignore`, `migrations/20260925130000_n8n_runtime_login_role.sql` (new; the only
  file committed — the repo must match the applied DB state).
  Owner options for the unverified watcher work: (ก) commit as WIP on a separate branch,
  (ข) park uncommitted, (ค) delete.
- **Cost stop**: the OpenRouter credit balance is down to ~$1.81. No paid model,
  subagent or worker may be started until the Owner says otherwise.

## Source-of-Truth Rule

Repository and runtime evidence override this document whenever they disagree.
Correct this document when verified state changes.