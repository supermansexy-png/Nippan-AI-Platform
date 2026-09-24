# Working policy

Status: **ACTIVE — governs all work on this project**

## Who this is for

Anyone or anything picking up work on this project — a new AI session, a
different AI model, a new human contributor — reads this file to know how
to behave, not just what has been decided. `AGENTS.md` says what to read
first and what never to do; this file says how to actually operate day to
day: what to check before acting, how to hand off, how to report back, and
what "done" means.

This project is expected to run with multiple AI sessions/models
contributing at different times, not one continuous operator. Every rule
below exists because of that — assume the next person picking this up has
zero memory of this conversation and only has the repo in front of them.

## Rule 00 — The AI operating protocol comes first

`docs/warroom/AI_OPERATING_PROTOCOL.md` governs how any AI accepts,
performs and delivers work. Where this file and the protocol overlap, the
protocol is stricter and wins.

## Rule 0 — Work only from a task card

Every piece of work has a card in `TASKS.md`, claimed before starting.
The card system — risk levels, claiming, work-in-progress limits, budgets,
the path to DONE, protected documents, weekly review, go/adjust/stop
checkpoints — is defined in `docs/warroom/TASK_CONTROL.md`. The rules
below assume it.

## Rule 1 — Read state before acting, every time

Before doing anything, read in this order:
1. `PROJECT_STATE.md` — what's actually built right now, not what's
   designed
2. `ROADMAP.md` — which phase is active
3. `TASKS.md` — what is claimed, in review, or blocked
4. `docs/warroom/decision-log.md` if it exists — recent decisions and why
5. The specific doc for the task at hand (`docs/product/`, `docs/data/`,
   `docs/security/`, `docs/warroom/`)

Never assume a document describes the live system. `PROJECT_STATE.md`'s
"built vs. designed" section is the only place that says what's real. This
project has a documented history of confusing "we wrote a design doc" with
"we shipped it" — see the note at the bottom of `PROJECT_STATE.md`. Do not
repeat that mistake.

## Rule 2 — Know which role you're acting as

Every piece of work maps to a role in `docs/warroom/ROLES.md`. Before
starting, identify which one you're filling (Developer, Auditor, Cost
Guard, Onboarding, Support, Marketing, Model Scout, or Project Lead), and
stay inside that role's stated authority. A Developer does not ship
straight to a real customer. An Onboarding agent does not set pricing. If
a task doesn't clearly belong to one role, flag it as `NEEDS_DECISION` (see
`AGENTS.md`'s status protocol) rather than freelancing.

## Rule 3 — Match effort to risk

Use the risk levels L1/L2/L3 in `docs/warroom/TASK_CONTROL.md` section 3 —
they decide how much checking a change needs. They are defined there only,
so there is one definition to follow. `AGENTS.md`'s "Cost and token
discipline" applies the same idea to how much review/token spend a change
deserves.

## Rule 4 — Every change updates its own status, not just the code

If a change makes something in `PROJECT_STATE.md`'s "not yet built" list
actually built, update that section in the same piece of work — don't
leave it for someone else to notice later. If a change touches pricing,
segments, tools, or model policy, update the relevant file under
`docs/product/` in the same change, not as a followup. Documentation
drifting from reality is this project's single biggest recurring failure
mode (see `docs/future/README.md` for the scale of what that produced
before this pivot) — every contributor is responsible for not
reintroducing it.

## Rule 5 — Handoff format

End any substantive piece of work with a short handoff, in the spirit of
`AGENTS.md`'s existing format:

- **What changed** — concretely, in the repo
- **What's still open** — the next concrete step, and any decision it's
  blocked on
- **What to double check** — anything the next person should verify before
  trusting this work (e.g., "cost estimate is a guess, confirm against
  real usage once tenant #1 is live")

This is what lets a different AI session or person pick this up cold. Do
not assume continuity of memory across sessions — write as if the next
reader has never seen this conversation.

## Rule 6 — Never contradict a hard rule to move faster

`AGENTS.md`'s work rules and `docs/product/CUSTOMER_FACING_RULES.md` and
`docs/security/PDPA_COMPLIANCE.md`'s Layer 3 rules are not negotiable for
convenience, deadline pressure, or a customer's request. If a task seems
to require breaking one of these, that's a `NEEDS_DECISION`, escalated to
Project Lead — never a unilateral judgment call to bend the rule "just
this once."

## What "done" means

Defined once, in `docs/warroom/TASK_CONTROL.md` section 7: verified in the
live system, `PROJECT_STATE.md` updated, handoff written. A design document
describing a feature is not "done".
