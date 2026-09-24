# Decision log format

Status: **ACTIVE — Phase A**

## Purpose

A running record of decisions and why they were made, so any person or AI
picking up work can see the reasoning without asking. Different from the
monitoring log: monitoring records events; this records decisions.

## When to log

- tenant approved or rejected
- a workflow/tool approved to go live
- a model swapped in any role
- a quota, price or config changed outside self-service
- a role moved up or down the autonomy ladder (`ROLES.md`)
- business mode switched
- any red event and how it was resolved

## Format

One append-only file: `docs/warroom/decision-log.md` (created on first
entry).

```
## YYYY-MM-DD — [role] — [one-line summary]
Context: what triggered it
Decision: what was decided
Reason: why, in 1–2 sentences
Task: link to the task card, if any (TASK_CONTROL.md)
```

Short entries. If it needs more than a few sentences, write a proper
document and link to it.

## Ownership

Project Lead owns the log. Whoever makes a decision writes its entry; the
weekly review (`TASK_CONTROL.md`) checks nothing is missing.
