# AI Collaboration Protocol

This file defines how any AI working on Nippan AI Platform must behave.

## Required reading order

Before proposing or changing anything:
1. `README.md`
2. `.ai/project.yaml`
3. `PROJECT_STATE.md`
4. `ROADMAP.md`
5. `WORKING_POLICY.md` and `docs/warroom/TASK_CONTROL.md` — how to operate,
   claim work, size review to risk, and hand off
6. `TASKS.md` — the task board
7. `docs/warroom/ROLES.md` — which role you're acting as, and its limits
8. `docs/warroom/STARTUP_PLAYBOOK.md` — the current concrete step, if the
   task is general "keep building Phase A" rather than a specific brief
9. Relevant product/data/security documents for the task at hand
10. The assigned task card

Do not pull anything from `docs/future/` into active work unless
`docs/future/README.md`'s trigger condition for that document is actually
met. It is a blueprint for later, not current scope.

## Work rules

- Do not modify the protected production systems listed in `ROADMAP.md`.
- Do not put secrets, API keys, tokens, passwords, customer PII, or production credentials in the repository.
- Do not hard-code model names in distributed application logic. Use model policy/presets/config — see `docs/product/MODEL_POLICY.md` and `docs/warroom/ROLES.md` (Model Scout).
- Prefer a single source of truth for each data domain.
- Separate conversation memory, long-term semantic memory, structured business records, and files — see `docs/data/LITE_SCHEMA_V1.md` for the Phase A shape of this.
- Do not send full history/catalog/data sets to a model when retrieval can select only relevant context.
- Expensive/reliable models should be escalation paths, not the default for all tasks.
- A worker model must not be the sole approver of high-risk/destructive actions — see `docs/warroom/ROLES.md` (Auditor, Project Lead) and `docs/warroom/MONITORING.md` (red-tier escalation).
- High-risk architecture/security/data changes require independent review — proportional to actual risk; do not default to two-model review for routine Phase A changes (see Cost/token discipline below).
- Any new managed service must justify operational benefit versus added complexity and recurring cost.
- Do not add a second tool/service for something n8n or the database already does, without a measured reason.
- Design every reusable component to be scoped by bot/tenant/user/channel where appropriate. Every Phase A table holding customer data carries `tenant_id` and `bot_id` with no exceptions — see `docs/data/LITE_SCHEMA_V1.md`.
- Never reveal the underlying AI model/vendor, and never let a bot claim to be human — see `docs/product/CUSTOMER_FACING_RULES.md`.
- Never use tenant conversation data to train/fine-tune any model without separate, explicit, advance consent — see `docs/security/PDPA_COMPLIANCE.md`, Layer 3.

## Cost and token discipline

Guidance, not a hard rule for every case — use judgment proportional to
actual risk and stakes:

- Match review depth to risk. A routine Phase A change (a small workflow
  tweak, a config value) does not need independent multi-model review.
  Reserve that for genuinely high-risk changes (see the work rules above).
- Prefer editing/patching over re-sending whole documents when only a part
  changed.
- Don't re-review something already reviewed and unchanged just because a
  planning direction shifted elsewhere — re-review only what actually
  changed.
- When in doubt about whether a review needs to be heavyweight, default to
  the lighter option and let Project Lead escalate if it turns out to need
  more.

## Model swap policy

See `docs/warroom/ROLES.md` (Model Scout, Project Lead) for the live
process. In short: Model Scout proposes, Project Lead approves, nothing
swaps automatically. This is what lets new AI providers enter the market
without any code rewrite — the system is built to route through policy,
not a hardcoded model name, specifically so this stays true.

## Status protocol

Allowed task states:
- BACKLOG
- READY
- IN_PROGRESS
- REVIEW
- BLOCKED
- NEEDS_DECISION
- DONE

If a major architectural decision is unresolved, mark it NEEDS_DECISION rather than silently choosing.

## Handoff format

Every AI contribution should end with:

### Findings
Facts verified from code/docs/data.

### Recommendation
What should change and why.

### Risks
Failure modes, security/privacy/cost/complexity concerns.

### Decisions needed
Items requiring owner/architect choice.

### Next task
The concrete next piece of work, including dependencies.

## Review principle

AI reviewers should challenge assumptions. Agreement is not required.
A review is more useful when it finds:
- duplicated infrastructure
- unnecessary model calls
- hidden token growth
- failure recovery gaps
- data ownership ambiguity
- privacy leaks
- vendor lock-in
- missing idempotency
- concurrency/state issues
- migration risks
- operational complexity
