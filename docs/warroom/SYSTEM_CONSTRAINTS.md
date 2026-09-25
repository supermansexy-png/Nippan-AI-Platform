# System Constraints — Enforcement Layer

Status: **ACTIVE — binds every AI session that picks up work on this project**

This file sits **on top of** `docs/warroom/AI_OPERATING_PROTOCOL.md`.
Where the Protocol says what to do, this file defines **mechanical gates** that prevent skipping steps. If you cannot pass a gate, you STOP and report — you do NOT fabricate passing it.

These constraints exist because writing rules in markdown does not force compliance. A different model, a fresh session, or the same model tired at 02:00 may ignore soft advice. Hard gates remove that possibility.

## Constraint ① — INTAKE Gate (no INTAKE → no IN_PROGRESS)

### Rule
A card CANNOT transition from READY (or any non-claiming state) to IN_PROGRESS unless ALL of these exist under the card in `TASKS.md`:

```
INTAKE — T-xxx — [model name] — [date]
Understanding: <1–3 sentences>
Done when: <checkable conditions copied from card>
Needs: <files, access, tools, credentials needed>
Missing: <anything from Needs that the AI does NOT currently have>
Plan: <ordered steps; L2/L3 must include independent verification step>
Estimate: <effort vs budget>
Risks: <what could go wrong>
Decision: ACCEPT | ACCEPT WITH LIMITS | DECLINE
```

### Enforcement mechanism
When a new AI session reads the card and finds it marked IN_PROGRESS (or claims it by setting that status) WITHOUT an INTAKE block present:

1. **REVERT** the status back to READY (or REMOVE if already claimed by someone else).
2. Report: *"Cannot continue T-xxx — missing INTAKE. Card reverted to READY."*
3. Do NOT start the work. Write what was needed and what was missing. Decline if nothing enables the work.

### When DECLINE is mandatory
An AI MUST set Decision = DECLINE (and leave the card READY) when ANY of:
- The card requires a tool, credential, or external resource the AI literally cannot access (e.g., production database admin access, cloud account credentials). Declining states exactly what is missing.
- The card requires testing the AI cannot perform in its environment (e.g., live HTTP call to a remote endpoint the AI cannot reach). Declining offers what CAN be tested instead.
- The AI knows its weakness at the domain (e.g., SQL RLS policy review for a Python-only AI). Declining suggests who should do it.
- Any condition from `AI_OPERATING_PROTOCOL.md` Gate 1 §DECLINE applies.

**Decline is never penalized.** Accepting without ability IS the violation.

---

## Constraint ② — Stop & Block Enforced (failure → immediate halt, not continuing)

### Rule
When ANY of the following occur during execution, the AI MUST immediately STOP all work on that card:

| Trigger | What to do |
|---|---|
| Tool/API call fails (error response, timeout, connection refused) | Write `BLOCKED: <reason>` note under the card. Do NOT retry the same thing >2×. Do NOT read surrounding code pretending to work around it. |
| Builder subprocess/agent process cancelled or exited with error | Write `BLOCKED: agent process terminated — <error summary>`. Report to owner before doing anything else. |
| Test suite fails (any assertion/error, even unrelated test) | STOP. Do NOT silence warnings. Do NOT skip tests. Record which test failed and why. |
| Effort exceeds 2× estimated budget | STOP. Document what was done. Write `PARTIAL` with unverified items. Do NOT push past budget hoping the next attempt succeeds. |
| Discovery that scope is different from Intake understanding | STOP. Write `NEEDS_DECISION` with what the discovery was. Do NOT adjust scope silently. |

### Enforcement mechanism
After stopping due to any trigger above:

1. Set card Status to **BLOCKED** (with reason) or **NEEDS_DECISION** (if owner choice needed).
2. Write a short note: `BLOCKED — <one-sentence cause>`. Under that, list: what was attempted, exact error/message, what would unblock it.
3. **Do NOT** switch to another card or read unrelated code pretending progress. The session ends here for this task.
4. Notify owner if the blocker prevents forward motion.

### Never acceptable after a stop trigger
- Reading 200 lines of related code "just to understand context"
- Writing pseudo-code or design drafts while the original failure is unresolved
- Silently switching cards to hide the failure
- Continuing past budget hoping results improve

If the AI catches itself doing any of these — it should stop and record: *"Self-detected continuation after failure. Stopped and reporting."*

---

## Constraint ③ — Evidence-Before-DONE (DONE claim must have verifiable proof)

### Rule
A card CANNOT be marked DONE (or transition through REVIEW toward DONE) unless the DELIVERY block contains AT LEAST ONE of these forms of evidence FOR EVERY "Done when" condition:

| Condition type | Required evidence |
|---|---|
| File created/modified | `git diff --stat` output listing changed files (VERIFIED) OR inline snippet showing key content |
| Code compiles/tests pass | Actual test command output (e.g., `pytest ... PASSED`) — NOT "should work", NOT "intended to work" |
| API endpoint exists/routes correctly | `curl` response or equivalent HTTP output showing actual status code and body |
| Configuration value set | Snapshot of config file showing the value, or Settings.field dump |
| Database migration applied | Migration run output (`psql` or migration runner log line confirming success) |
| Documentation updated | Diff or screenshot showing the new/updated content |

### Enforcement mechanism
Before transitioning a card from IN_PROGRESS → REVIEW → DONE:

1. List every single "Done when" condition in the card.
2. For EACH condition, provide explicit evidence. If zero evidence exists for a condition, the status is PARTIAL — NOT DONE.
3. If evidence cannot be obtained (e.g., requires live server the AI cannot reach), mark the condition as UNVERIFIED and the overall status as PARTIAL.
4. Owner/Auditor can independently reproduce at least one piece of evidence.

### Forbidden evidence formats (these do NOT count)
- "Intentionally designed to..." / "Architecture supports..." / "Should work once deployed..."
- Copy-pasting the card's own Goal text as evidence
- Screenshot of code that was only written but not tested
- "Test was skipped" / "CI passed" without showing the test result details

---

## Constraint ④ — Scorecard With Consequences (empty table = broken system)

### Rule
Every AI that performs work under a task card MUST have a corresponding row in `docs/warroom/ai-scorecard.md`. Empty scorecard = accountability vacuum = repeated failures.

### Automatic population
When an AI finishes work (claims DONE, PARTIAL, or FAILS), it writes to the scorecard:

```
|[model]| accepted: N | declined: M | passed first check: Y/N | returned by auditor: N | false DONE: N | stop rules ignored: N | scope violations: N | effort vs budget: within/over | ladder stage: N | Notes: <free text> |
```

### Mandatory deductions (no discretion)

| Violation | Deduction | Consequence |
|---|---|---|
| Claimed DONE without evidence for any Done-when condition (false DONE) | +1 to `false DONE` column | Drops 1 stage on autonomy ladder immediately. Next 3 L2/L3 deliveries get full independent verification. |
| Continued working after a documented stop/block trigger | +1 to `stop rules ignored` | Same consequence as false DONE. |
| Changed files outside the card's scope | +1 to `scope violations` | Restricted to L1 tasks until clean run of 10. |
| Attempted over 2× stated budget | Flagged in `effort vs budget` column | Review required at weekly meeting. |
| Failed to write INTAKE before claiming IN_PROGRESS | Noted in `Notes` column | Repeats accumulate → stage drop after 3 occurrences. |
| Honest decline or honest PARTIAL/FAILED report | **No penalty** — recorded neutrally | Encourages truthful reporting. |

### Weekly enforcement
During the weekly review (per `TASK_CONTROL.md` §9):

1. Auditor or owner reviews every row with `false DONE > 0`, `stop rules ignored > 0`, or `scope violations > 0`.
2. Applies stage drops or restrictions from the table above — NO discretion to override.
3. Writes the updated scorecard to `ai-scorecard.md` in the repo.

### Enforcement of enforcement
If a session skips scorecard update after finishing work:
- The delivery report is incomplete — treat as PARTIAL until scorecard entry exists.
- Repeated omissions (more than 2 sessions) flagged to owner during weekly review.

---

## How this interacts with the Protocol

| Situation | Which rule applies |
|---|---|
| Protocol says "honest no is correct"; Constraint ① enforces it mechanically | Constraint ① (gate blocks progress without INTAKE) |
| Protocol says "stop and report"; Constraint ② specifies exact triggers and actions | Constraint ② (auto-halts on defined triggers) |
| Protocol says "DONE requires evidence"; Constraint ③ defines what counts | Constraint ③ (forbids weak evidence formats) |
| Protocol describes scorecard consequences; Constraint ④ makes them auto-populated and non-discretionary | Constraint ④ (mandatory columns + forced stage drops) |

This constraint layer does NOT replace the Protocol. It adds mechanical teeth to Protocol principles that rely on self-discipline.

---

## Implementation notes for this repository

These constraints are enforced through **process discipline**, not software CI gates (yet). The practical enforcement relies on:

1. **Task cards act as checkpoints** — any new AI reader sees IN_PROGRESS without INTAKE and reverts.
2. **Owner weekly review** checks scorecard for violations and applies stage drops.
3. **Cross-AI accountability** — when AI B picks up a card, AI B checks whether AI A followed these constraints. If not, AI B reports it.
4. **Git history as permanent record** — deleted commits, force pushes, or edited git logs undermine all of the above. Git safety rules remain in effect.

To make enforcement stronger in the future: consider adding pre-commit hooks or linting scripts that scan TASKS.md for missing INTAKE blocks or empty scorecards.
