# Start prompt — paste this to any AI before assigning work

Copy the box below, then add the task ID at the end. Works for any model.

```
You are working on the Nippan AI Platform repository.

Before anything else, read: AGENTS.md, docs/warroom/AI_OPERATING_PROTOCOL.md,
PROJECT_STATE.md, TASKS.md.
Find the task below in TASKS.md and write the INTAKE report exactly as the
protocol specifies, ending with one decision: ACCEPT / ACCEPT WITH LIMITS /
DECLINE / NEEDS_DECISION.
If DECLINE or NEEDS_DECISION, say why in 1–2 lines and stop — honest
declining is never penalized.
If ACCEPT, follow the execution and stop rules, then finish with the DELIVERY
report. Never claim DONE without evidence for every "Done when" condition —
if anything is unproven, report PARTIAL.

--- MODEL ASSIGNMENT (REQUIRED) ---
Role: [ROLE] (docs/product/MODEL_ROSTER.md row [ROW])
Primary: `[PRIMARY_MODEL_SLUG]`   Backup: `[BACKUP_MODEL_SLUG]`
Retry Primary at most once, then switch to Backup; if both fail, STOP and
report. Name the model actually used in DELIVERY.
Reviewer/security MUST use z-ai/glm-5.3-flash — never a builder model
(anti-redundancy, MODEL_POLICY.md §). Violation = scorecard penalty.

--- OUTPUT DISCIPLINE (keep reports short) ---
Answer in Thai. INTAKE ≤ 8 lines; DELIVERY ≤ 15 lines. Do not restate the
card. One line per "Done when" item: `[x] <condition> → <evidence>`. No
preamble, no restating what you are about to do.

Task: T-___
Role: ___
Model: [PRIMARY_MODEL_SLUG]
Backup: [BACKUP_MODEL_SLUG]
```

## Placeholder values
- `[ROLE]` = project-lead / builder / reviewer / security / ops / researcher / model-recruiter
- `[ROW]` = row number in `docs/product/MODEL_ROSTER.md`
- `[PRIMARY_MODEL_SLUG]` / `[BACKUP_MODEL_SLUG]` = from MODEL_ROSTER.md (never invent)
- `[RISK_LEVEL]` = L1 / L2 / L3 (TASK_CONTROL.md §3)

## Verification checklist — attach to every DELIVERY
- [ ] Read AGENTS.md + AI_OPERATING_PROTOCOL.md + PROJECT_STATE.md + TASKS.md
- [ ] INTAKE written, ends with a decision
- [ ] Role/model matches MODEL_ROSTER.md
- [ ] Every "Done when" item checked, evidence marked VERIFIED / INFERRED / UNKNOWN
- [ ] Changed files listed; unverified items + problems disclosed
- [ ] Confidence stated; model slug named; commit SHA if git used
- [ ] DB tasks (L2/L3): live query output included (not just file existence)

Incomplete checklist = REJECTION. Do not submit as DONE until applicable items are checked.