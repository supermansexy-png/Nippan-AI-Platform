# Nippan AI Platform — Current State

Last updated: 2026-09-24
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

Independent paid Audit is PAUSED by the Project Owner. Do not invoke paid
Independent Auditor unless the Project Owner re-enables it. Normal code review,
security review, tests, CI and evidence verification remain allowed.

## Protected Production System

`Ai-bot-Nippan` production is OUT OF SCOPE unless the Project Owner explicitly
authorizes changes. Do not modify its service, data, credentials or workflows.

## Immediate Next Step

Forward plan is the Phase A market test build order in
`docs/warroom/STARTUP_PLAYBOOK.md`. Continue from Step 0 foundations
(self-hosted n8n + PostgreSQL, lite schema tables, data-access/usage-tracker/
monitor-log tools, owner alert channel, legal review). Work cards live in
`TASKS.md` (T-001..T-004 READY).

1. DO NOT build further War Room feature work from the old runtime history.
2. Treat `docs/future/` as archived blueprint; a step needing it must be
   flagged NEEDS_DECISION for Project Lead.
3. Do not use the template folder anymore — it is merged into this workspace.
4. Dev-time team = repo agents in `.opencode/agents/`; do not confuse them with
   runtime roles.

## Source-of-Truth Rule

Repository and runtime evidence override this document whenever they disagree.
Correct this document when verified state changes.