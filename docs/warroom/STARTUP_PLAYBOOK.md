# Startup playbook â€” Phase A, step by step

Status: **ACTIVE â€” the build order for `ROADMAP.md` Phase A**

This file is the single source for "what comes next". `PROJECT_STATE.md`
says what exists; `TASKS.md` holds the task cards for the current step.

Scope note (2026-09-25): this playbook is the authoritative build plan for the Phase A
market test. ROADMAP.md (full-stack Phases 0-10) is archived design reference. The War
Room track remains an ACTIVE separate dev-time track (TASKS.md T-007/T-008/T-009) and
is not part of this playbook.

Steps are in dependency order. Each step ends with a go/adjust checkpoint
from `docs/warroom/TASK_CONTROL.md` section 10.

## Step 0 â€” Foundations (target: ~1â€“2 weeks)

- [ ] Self-hosted n8n + PostgreSQL on a small VPS, HTTPS, daily backups
      (self-hosting because a hosted n8n plan's execution limits would not
      fit ~18,000 messages/month at 30 tenants; verify current plans)
- [ ] Lite schema tables (`docs/data/LITE_SCHEMA_V1.md`)
- [ ] `data-access`, `usage-tracker`, `monitor-log` tools
- [ ] Owner's single alert channel working

Exit: empty but real system; a red test event reaches the owner.

## Step 1 â€” One bot, end to end, on LINE (target: ~2â€“3 weeks)

- [ ] `line-channel` â€” connect a *test* LINE OA with its own credentials
- [ ] `chat-bot-core`, `memory-store` (layers 1 and 4 first)
- [ ] `handoff-to-owner`, outage fallback message
- [ ] `web-fetch`, `file-reader`, Onboarding flow (`docs/product/ONBOARDING_FLOW.md`)
- [ ] Auditor test pass: isolation between two test tenants; cannot reveal
      model; admits being an assistant when sincerely asked; hands off
      when unsure; replies fast enough for LINE's reply flow

Exit: a test bot a real shop could use. Checkpoint: within ~4 weeks of start.

## Step 2 â€” Tenant #1, watched closely (target: 2 weeks live)

- [ ] Onboard tenant #1 with the owner present; tenant uses their own LINE OA
- [ ] Measure real cost per reply; update `PRICING_V1.md`
- [ ] Confirm the monthly quota value
- [ ] Daily read of the monitoring log

Exit: owner confident in quality; real cost within estimate.

## Step 3 â€” Tenants #2â€“10, storefront, second bot type

- [ ] `web-chat-channel` + storefront with live demo (`docs/product/STOREFRONT.md`)
- [ ] `secretary-bot` (reminders use the tenant's LINE push quota â€”
      explain this during onboarding)
- [ ] Rolling summary job (memory layer 2) and retention/deletion jobs
- [ ] Onboard tenants from direct contacts (`BUSINESS_OPERATIONS.md` Â§6),
      mixing expected and underserved segments
- [ ] Weekly review running

Exit: ~10 tenants; patterns visible (which segments stay, where cost differs).

## Step 4 â€” First roles climb the autonomy ladder

- [ ] Auditor to stage 2â€“3, then Cost Guard (`ROLES.md` ladder)
- [ ] Owner moves from doing checks to reading digests and red alerts

## Step 5 â€” Toward Phase B

At 25â€“30 retained, profitable tenants, switch from this fixed list to
demand-driven work (`ROADMAP.md` Phase B).

## Out of scope for this playbook

Anything in `docs/future/`. If a step seems to need it (real RLS, a
dashboard, FastAPI), mark the task NEEDS_DECISION for Project Lead.
