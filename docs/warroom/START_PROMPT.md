# Start prompt — paste this to any AI before assigning work

Copy everything in the box below into a new AI session, then add the task
ID at the end. Works for any AI model.

```
You are working on the Nippan AI Platform repository.

Before doing anything else:
1. Read AGENTS.md, docs/warroom/AI_OPERATING_PROTOCOL.md,
   PROJECT_STATE.md and TASKS.md.
2. Find the task I give you below in TASKS.md.
3. Write the INTAKE report exactly as the protocol specifies, and end it
   with one decision: ACCEPT, ACCEPT WITH LIMITS, DECLINE, or NEEDS_DECISION.
4. If you DECLINE or need a decision, tell me plainly why and stop.
   Declining honestly is the correct behavior here and is never penalized.
   Accepting and delivering poor or unverified work is penalized.
5. If you ACCEPT, follow the protocol's execution rules and stop rules,
   and finish with the DELIVERY report. Never claim DONE without evidence
   for every "Done when" condition — if anything is unproven, report
   PARTIAL.

Answer me in Thai. Keep reports short.

Task: T-___
```

## ① Task Assignment Template — copy this to any AI session

Copy everything in the box below into a new AI session, then add the task
ID at the end. Works for any AI model.

```
You are working on the Nippan AI Platform repository.

Before doing anything else:
1. Read AGENTS.md, docs/warroom/AI_OPERATING_PROTOCOL.md,
   PROJECT_STATE.md and TASKS.md.
2. Find the task I give you below in TASKS.md.
3. Write the INTAKE report exactly as the protocol specifies, and end it
   with one decision: ACCEPT, ACCEPT WITH LIMITS, DECLINE, or NEEDS_DECISION.
4. If you DECLINE or need a decision, tell me plainly why and stop.
   Declining honestly is the correct behavior here and is never penalized.
   Accepting and delivering poor or unverified work is penalized.
5. If you ACCEPT, follow the protocol's execution rules and stop rules,
   and finish with the DELIVERY report. Never claim DONE without evidence
   for every "Done when" condition — if anything is unproven, report
   PARTIAL.

--- MODEL ASSIGNMENT (REQUIRED) ---
The Project Lead has assigned you to role "[ROLE]". Per MODEL_ROSTER.md row [ROW_NUMBER]:
- Your PRIMARY model is `[PRIMARY_MODEL_SLUG]` ($[INPUT_PRICE]/$[OUTPUT_PRICE])
- Your BACKUP model is `[BACKUP_MODEL_SLUG]` ($[INPUT_PRICE]/$[OUTPUT_PRICE])
If your primary model fails quality check or becomes unavailable during execution, switch to backup. Report which model was used in DELIVERY.
Reviewers/security must use z-ai/glm-5.3-flash (Primary). DO NOT substitute qwen3.7-flash or any builder model under any circumstances — this violates anti-redundancy cross-checks per MODEL_POLICY.md §. Any violation triggers immediate scorecard deduction and potential HR blacklist.

Answer me in Thai. Keep reports short.

Task: T-___
Role: ___
Model: [YOUR_ASSIGNED_MODEL_SLUG]
Backup: [YOUR_BACKUP_MODEL_SLUG]
```

## ② English version — paste to any AI before assigning work

Copy everything in the box above into a new AI session, then replace the template placeholders with actual values from MODEL_ROSTER.md before sending:
- [ROLE] = project-lead / builder / reviewer / security / ops / researcher / model-recruiter
- [ROLE_NAME] = full role name (e.g., "Project Lead", "Builder")
- [PRIMARY_MODEL_SLUG] = e.g., `qwen/qwen3.7-flash`, `z-ai/glm-5.3-flash`
- [BACKUP_MODEL_SLUG] = e.g., `nvidia/nemotron-3.5-lightning`, `thinkingmachines/inkling:free`
- [TICKET_NUMBER] = task ID, e.g., T-002
- [RISK_LEVEL] = L1 / L2 / L3 per TASK_CONTROL §3
- [DONE_WHEN] = copy "Done when" conditions from the task card in TASKS.md

## ③ Verification Checklist — attach to every DELIVERY report

Every agent submission MUST complete this checklist. Incomplete checklist = rejection.

### A. Pre-execution
- [ ] Read AGENTS.md ✅
- [ ] Read docs/warroom/AI_OPERATING_PROTOCOL.md ✅
- [ ] Read PROJECT_STATE.md ✅
- [ ] Read TASKS.md ✅
- [ ] Role/model matches MODEL_ROSTER.md entry ✅
- [ ] Written INTAKE report ending with ACCEPT / ACCEPT WITH LIMITS / DECLINE / NEEDS_DECISION ✅

### B. Execution
- [ ] Followed protocol execution rules ✅
- [ ] Observed stop rules (budget limit = X time/token) ✅
- [ ] No scope creep beyond task card definition ✅

### C. DELIVERY Evidence
- [ ] All "Done when" conditions checked with [x] or [ ] ✅
- [ ] Evidence marked VERIFIED / INFERRED / UNKNOWN ✅
- [ ] Changed files listed ✅
- [ ] Not done items stated (if any) ✅
- [ ] Unverified items disclosed ✅
- [ ] Problems found documented ✅
- [ ] Confidence level stated (high/medium/low) ✅
- [ ] Next steps identified ✅

### D. Database-related tasks ONLY (L2/L3 schema/data access)
- [ ] Live query evidence included (supabase_execute_sql output OR supabase_list_tables output) ✅
- [ ] Evidence shows actual database state, not just migration file existence ✅
- [ ] Before applying changes: current state inspected first ✅

### E. Final
- [ ] Agent named the model slug used in final report ✅
- [ ] Commit SHA recorded (if git operations performed) ✅

**Incomplete checklist = REJECTION.** Do not submit as DONE until all applicable items are checked.
