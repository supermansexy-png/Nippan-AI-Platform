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
- `builder.md`, `reviewer.md`, `security.md`, `ops.md`, `researcher.md` —
  dev-time specialists, all following the same protocol.

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
`agent=reviewer` → `z-ai/glm-5.3-flash`.

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

## Model Policy — free execution + paid L4 (T-022) — DONE (2026-09-25)

Owner policy: the Project Lead thinks/plans only; execution (builder/ops/researcher)
and review/security for L1/L2/L3 run on **free OpenCode Zen** models; **L4 (critical /
high-accuracy verification) uses the paid `z-ai/glm-5.3-flash`**. Applied to
`MODEL_ROSTER.md`, `START_PROMPT.md`, the agent files and `opencode.json`
(`small_model` also set to a free model, fixing "Insufficient account funds" on session
titles). Needs an opencode restart to load. Free tier may log/train → no secrets in
prompts.

## Source-of-Truth Rule

Repository and runtime evidence override this document whenever they disagree.
Correct this document when verified state changes.