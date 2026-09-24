# Task control

Status: **ACTIVE — governs how work is assigned, checked and closed**

This is the control system for a project where several AI sessions/models
and the owner all contribute. Each rule is followed by why it exists. The
aim is "tight enough that nothing slips, light enough that one person can
run it" — every rule here costs minutes, not hours.

## 1. One board, one place

All work lives in `TASKS.md` at the repo root. No task exists only in a
chat conversation.

Why: AI sessions don't share memory. Anything not written in the repo is
lost the moment a session ends.

## 2. Task card

```
### T-012 — Build usage-tracker tool
Status: READY | IN_PROGRESS | REVIEW | DONE | BLOCKED | NEEDS_DECISION
Owner: (who is doing it — "owner", or AI name + date claimed)
Role: Developer / Auditor / … (docs/warroom/ROLES.md)
Risk: L1 / L2 / L3 (section 3)
Goal: one sentence — what exists when this is done
Done when: checkable conditions
Budget: time/effort limit (section 6)
Links: related docs
```

Why: a card answers the six questions a newcomer needs — what, who,
under which role's authority, how risky, what "done" means, how much
effort is reasonable.

## 3. Risk levels decide the checking

| Level | Examples | Before it counts as DONE |
|---|---|---|
| L1 — routine, reversible | wording, config value, doc fix | Doer self-checks; logged in the card |
| L2 — affects real customers | new/changed workflow or tool, new bot type | Auditor check + owner approval |
| L3 — hard to undo | pricing, PDPA/data handling, deleting data, rules in `CUSTOMER_FACING_RULES.md`, business mode | Auditor check + owner approval + Decision Log entry with reasons |

When unsure, pick the higher level.

Why: checking everything heavily wastes money and time (this project has
already burned tokens that way); checking nothing lets mistakes reach
customers. Matching checks to risk is the balance.

## 4. Claiming work — one task, one owner

To start a task, set Status to IN_PROGRESS and fill Owner. Nobody works on
a task someone else has claimed. Two tasks that edit the same file are not
IN_PROGRESS at the same time.

Why: two AIs editing the same file in parallel silently overwrite each
other. A written claim is the cheapest lock there is.

A claim older than 7 days with no update returns to READY.

## 5. Work-in-progress limit

At most **3** tasks IN_PROGRESS and **5** in REVIEW at once.

Why: the owner is the approval bottleneck. Starting more work than can be
reviewed creates a pile of half-checked changes — the exact
"lots of activity, little finished" pattern this project had before.

## 6. Budgets and the stop rule

Every card has a budget (for example "½ day" or "one working session").
At **2×** the budget, stop, write what's done and what's blocking, and set
BLOCKED or NEEDS_DECISION. Do not keep going.

Why: overruns are usually a sign the task was misunderstood or is bigger
than thought. Stopping to re-plan is cheaper than finishing the wrong thing.

## 7. The path to DONE

READY → IN_PROGRESS → (test) → REVIEW → (audit / approval per risk level)
→ live → DONE after the "Done when" conditions are verified in the live
system, `PROJECT_STATE.md` is updated if something new now exists, and the
handoff note is written (`WORKING_POLICY.md` rule 5).

Why: "written" is not "working". Verifying live closes the gap between
documents and reality.

## 8. Protected documents

Changing these is always L3: `docs/product/PRICING_V1.md`,
`docs/product/CUSTOMER_FACING_RULES.md`, `docs/security/PDPA_COMPLIANCE.md`,
`docs/data/LITE_SCHEMA_V1.md`, `docs/product/INTEGRATIONS.md`, `docs/warroom/ROLES.md`, `WORKING_POLICY.md`,
this file.

Why: these are the rules everyone else relies on. A silent edit to them
changes the behavior of every AI that reads them next.

## 9. Weekly review (~30 minutes, owner)

1. `TASKS.md`: anything stuck, over budget, or claimed but idle?
2. Monitoring log: any red events this week? All resolved and logged?
3. Cost: real cost per bot vs `PRICING_V1.md`
4. Tenants: signups, cancellations, complaints
5. Autonomy ladder: any role ready to move up — or needing to move down?
6. Decision Log: anything decided this week but not written down?

Why: small drift is cheap to fix weekly and expensive to fix monthly.

## 10. Project-level checkpoints (go / adjust / stop)

| Checkpoint | Pass | If not |
|---|---|---|
| Step 1 done within ~4 weeks of starting | a test bot works end to end | shrink scope: one bot type, LINE only |
| Tenant #1 live, 2 weeks | owner confident in quality; real cost ≤ ~100 THB/bot | fix cost/quality before adding tenants |
| 3 months after first tenant | ≥ 10 paying tenants, most renewing | rethink segment, offer, or price before building more |
| 6 months | 25–30 paying, profitable | consider Phase B / C per `ROADMAP.md` |

Why: without agreed checkpoints a project can stay "almost ready" forever.
Deciding the stop/adjust rule in advance keeps the decision honest.
