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

## Rule 1 — Read state before acting, every time

Before doing anything, read in this order:
1. `PROJECT_STATE.md` — what's actually built right now, not what's
   designed
2. `ROADMAP.md` — which phase is active
3. `docs/warroom/decision-log.md` if it exists — recent decisions and why
4. The specific doc for the task at hand (`docs/product/`, `docs/data/`,
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

## Rule 3 — Match effort to what's actually being decided

Not every task deserves the same weight. Use judgment, calibrated by what
actually changes if the work is wrong:

- **Routine, reversible** (a config tweak, a minor copy change, adding a
  segment to a list) — just do it, log it per `docs/warroom/
  DECISION_LOG_FORMAT.md`, move on.
- **Meaningful but bounded** (a new MCP tool, a workflow change affecting
  real customers) — build it, but route it through Audit before it goes
  live (Rule 2's role boundaries exist for exactly this).
- **High-risk or hard to reverse** (anything touching pricing, PDPA/data
  handling, a new tenant's onboarding into an untested segment, switching
  business mode) — this needs Project Lead sign-off and a Decision Log
  entry with real reasoning, not just a note that it happened.

See `AGENTS.md`'s "Cost and token discipline" section for the same
principle applied specifically to how much review/token spend a change
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

## What "done" means for a Phase A task

A task is done when:
1. It works (tested, not just written)
2. It's logged (`docs/warroom/DECISION_LOG_FORMAT.md` if it was a
   decision, `docs/warroom/MONITORING.md`-tier if it was an event)
3. `PROJECT_STATE.md` reflects it, if it changed what's built
4. The handoff (Rule 5) is written

A design document describing a feature is not "done" — see Rule 4.
