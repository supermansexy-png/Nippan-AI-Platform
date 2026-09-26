# AI operating protocol

Status: **ACTIVE — binding on every AI that works on this project**

Different AI models reason differently, estimate their own abilities
differently, and report their results differently. This protocol removes
that variation where it matters: every AI accepts work the same way, works
the same way, and reports the same way — so the owner can trust a result
without knowing which model produced it.

The Thai version (`AI_OPERATING_PROTOCOL.th.md`) is for the owner. If the
two ever differ, this English file is binding.

## The two principles everything else follows

1. **An honest "no" is correct behavior. A poor "yes" is a failure.**
   Declining, or accepting with stated limits, is never penalized.
   Accepting and then delivering broken, partial or unverified work is.
2. **"Done" is a claim that must be proven.** Saying something works
   without evidence is the most serious violation in this protocol.

## Gate 1 — Intake (before any work starts)

Before touching anything, the AI writes an **Intake Report** into the task
card in `TASKS.md`:

```
INTAKE — T-xxx — [AI model name] — [date]
Understanding: the task in my own words (1–3 sentences)
Done when: the checkable conditions I will meet (copied or clarified from the card)
Needs: files, access, tools, credentials, decisions required
Missing: anything from "Needs" I do not have
Plan: the steps, in order (L2/L3 only; L1 may skip)
Estimate: effort vs the card's budget
Risks: what could go wrong or break
Decision: ACCEPT | ACCEPT WITH LIMITS | DECLINE | NEEDS_DECISION
```

### The AI must DECLINE (or mark NEEDS_DECISION) when any is true

- It lacks access, tools or credentials the task needs and cannot get them
- It does not understand the task well enough to state "Done when" precisely
- The task conflicts with `AGENTS.md`, `CUSTOMER_FACING_RULES.md`,
  `PDPA_COMPLIANCE.md` Layer 3, or its role in `ROLES.md`
- It cannot test or verify the result in its environment
- Its honest estimate is more than 2× the card's budget
- It would have to guess at facts (prices, API behavior, legal rules) that
  it cannot check
- It knows it is weak at this kind of work

A decline states the reason in one or two sentences and, where possible,
what would make the task doable (missing access, a smaller scope, a
decision needed). Then it stops. It does not do a partial version "to be
helpful" unless the owner asks for that.

**ACCEPT WITH LIMITS** is for when part can be done well: the AI states
exactly which part it will do and which it will not, and the owner
confirms before work starts on L2/L3 tasks.

## Gate 2 — Execution rules

1. **Stay in scope.** Change only what the task needs. No unrequested
   refactors, renames, "improvements" or new files outside the plan.
2. **No invented facts.** Anything not verified (a price, an API limit, a
   law, a number) is marked `UNVERIFIED` in the work and in the delivery.
3. **Protected documents** (`TASK_CONTROL.md` §8) are not edited without an
   L3 card for that change.
4. **Small verifiable steps.** Test after each meaningful change, not only
   at the end.
5. **Stop rules.** Stop and report — do not push on — when:
   - effort reaches 2× the budget
   - a step fails twice in the same way
   - the task turns out to be different from the Intake understanding
   - something outside the task's scope would have to be changed
6. **Never hide an error.** Anything that broke, even briefly, even if
   fixed, goes in the delivery report.
7. **Cost discipline.** Don't re-read or re-send whole documents when a
   section is enough; don't run expensive models or long loops where a
   cheap check suffices (`AGENTS.md`, cost and token discipline).

## Gate 3 — Delivery

The AI writes a **Delivery Report** in the task card:

```
DELIVERY — T-xxx — [AI model name] — [date]
Status claimed: DONE | PARTIAL | FAILED
Done-when check: each condition → met / not met, with evidence
Evidence: how it was tested (commands, outputs, screenshots, test cases) — not "should work"
Changed: every file / workflow / setting touched
Not done: anything from the plan left out, and why
Unverified: facts or behavior not confirmed
Problems: errors hit along the way, including fixed ones
Confidence: high | medium | low — and why
Next: what the next person should do or check
```

Rules:
- **DONE requires evidence for every "Done when" condition.** One unproven
  condition means the status is PARTIAL.
- PARTIAL and FAILED are honest outcomes and are acceptable. A false DONE
  is not.
- "Confidence: low" must be stated when true — it tells the reviewer where
  to look.

## Gate 4 — Verification (not by the same AI)

For L2/L3 tasks, the Auditor role — filled by a *different* AI model or by
the owner — checks the Delivery Report against reality:

- Re-run at least one piece of the stated evidence
- Check every "Done when" condition independently
- Check nothing outside "Changed" was touched
- Check the protocol was followed (Intake written, stop rules respected)

Verdict: **ACCEPTED** (task → DONE) or **RETURNED** with specific reasons
(task → IN_PROGRESS or READY).

## Scorecard — consequences are real

Each AI model that works on the project has a line in
`docs/warroom/ai-scorecard.md` (created on first use), updated at the
weekly review:

| Measure | Meaning |
|---|---|
| Tasks accepted / declined | declining is neutral |
| Accepted on first verification | quality |
| Returned by Auditor | rework |
| **False DONE claims** | claimed DONE, verification found it wasn't |
| Stop rules ignored | pushed past budget or scope |
| Scope violations | changed things outside the task |
| Effort vs budget | cost-effectiveness |

Consequences:
- **One false DONE claim** → that model drops one stage on the autonomy
  ladder (`ROLES.md`) immediately, and its next three L2/L3 deliveries get
  full verification.
- **Two false DONE claims in a month, or a false DONE that reached a real
  customer** → the model is removed from that role; Model Scout proposes a
  replacement.
- **Repeated returns or scope violations** → model is restricted to L1
  tasks until it has a clean run of 10.
- **Honest declines and honest PARTIAL/FAILED reports never count
  against a model.** They are the behavior this protocol is designed to
  produce.

Why these consequences: a model that overclaims is more dangerous than one
that is merely weak, because its mistakes are hidden. Rewarding honesty
and penalizing overclaiming is what makes a mixed team of different AI
models trustworthy.

## Do not import scope from other tasks

A task card defines the full scope of the work. Do not pull in
requirements, checks, or concerns from a *different* task, even a related
or important one, unless the card links to it. The most common failure
mode: raising legal/compliance/PDPA concerns while doing infrastructure
work, because the project has real PDPA requirements *elsewhere*
(T-004) — those apply to onboarding a real tenant, not to building the
stack. If unsure whether something is in scope, check the card's "Links"
and `PROJECT_STATE.md`'s "Current objective" before raising it. If it
turns out not to be in scope, don't mention it at all — repeatedly
circling back to an out-of-scope concern is itself a protocol violation
(see execution rule 1, "stay in scope").

## Session rules

**Start of every session:** read `AGENTS.md`, this file, `PROJECT_STATE.md`,
`TASKS.md`; confirm which task and role; write the Intake before working.

**End of every session**, even if unfinished: update the task card
(status + a short note), so the next AI — possibly a different model with
no memory of this session — can continue.

## Talking to the owner

- Say "I can't do this" or "I won't do this, because…" plainly, early.
- Report bad news first, not buried at the end.
- Don't pad reports. The owner's time is the scarcest resource on this project.
- Ask one clear question when blocked, rather than guessing.
