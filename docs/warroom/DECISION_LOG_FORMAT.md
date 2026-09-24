# Decision log format

Status: **ACTIVE — Phase A**

## Purpose

A running record of decisions made by any War Room role, so Project Lead
(and the owner) can see why something was decided without having to ask.
This is not the same as the monitoring log in `MONITORING.md` — monitoring
is events that happened; this is decisions that were made.

## When to log

Any of these triggers a log entry:
- A new customer is approved or rejected
- A workflow/tool is approved to go live
- A model is swapped in any role (Model Scout proposal + Project Lead
  approval)
- A customer's quota, pricing, or config is changed outside the normal
  self-service flow
- Business mode is switched (see `ROLES.md`, Project Lead)
- Anything escalated at red-tier per `MONITORING.md`

## Entry format

Plain text, one entry per decision, in a single running file
(`docs/warroom/decision-log.md` — created on first use, append-only):

```
## [DATE] — [ROLE] — [one-line summary]

Context: what triggered this decision
Decision: what was decided
Reasoning: why (1-2 sentences, not an essay)
```

Keep entries short. This is a log, not a report — if it needs more than a
few sentences to explain, it belongs in a proper doc elsewhere and the log
entry just links to it.

## Ownership

Cost Guard owns keeping this log complete (cross-checks that every
trigger event above actually produced an entry). Project Lead is the
primary reader.
