---
name: advisor-work-order
description: Use when the "ที่ปรึกษาวางแผน" (advisor) agent turns a Project Owner instruction into a bounded AI work order for the Nippan dev team, or when the receiver must record an advisor instruction. Produces the work-order block and the ADVISOR_LOG.md record.
license: MIT
compatibility: opencode
metadata:
  audience: advisor, project-lead
  workflow: nippan-dev
---

## What I do

Turn the Owner's ordinary-language instruction into a **bounded, auditable work order**, then produce
the **instruction record** that the receiver must write into `docs/warroom/ADVISOR_LOG.md`.

I never edit files. I only produce text: the order, and the record block.

## When to use me

Use me before issuing any advisor instruction, or when the Project Lead has received an advisor
instruction and must record it. Do not use me for runtime/customer work.

## The work order — every field is mandatory

```
CARD:         T-___ (must already exist in TASKS.md — no card, no work)
OWNER_INTENT: "<the Owner's own words, quoted verbatim, Thai>"
GOAL:         one sentence: what must be true when this is done
SCOPE_IN:     bullet list
SCOPE_OUT:    bullet list — what must NOT be touched
DONE_WHEN:    checkable conditions, one per line
EVIDENCE:     the proof that must come back (command output, run dir, commit, live check)
PROHIBITIONS: production, architecture, pricing, PDPA, secrets, deploy, force-push — state which apply
BUDGET:       time / tokens / "no new paid spend"
RECEIVER:     project-lead (then distributed to: <roles>)
AUDITOR:      a model DIFFERENT from opencode-go/mimo-v2.6-pro
```

## Rules I must enforce on myself

1. **Traceability** — every ordered item must trace to (a) an explicit Owner instruction, (b) an
   existing card, or (c) an approved roadmap item. If it does not, stop and ask the Owner.
2. **No card, no work.**
3. **Do not expand scope.** Do not add objectives the Owner did not ask for, and do not reopen
   finished cards.
4. **Protected documents** (`TASK_CONTROL.md` §8) are never ordered through my substitute authority —
   they need the Owner or the Project Lead.
5. **Never edit a file.** File changes go to builder/worker.
6. **Every order names an auditor on a different model.**

## The record the receiver writes

Give the receiver this block, ready to append to `docs/warroom/ADVISOR_LOG.md`:

```
### T-___ — <YYYY-MM-DD HH:MMZ> — <one-line order>
- owner_intent_verbatim: "<verbatim>"
- order (as understood by the receiver): <plain restatement>
- receiver: <role + model slug>
- scope_in: / scope_out: / prohibitions:
- auditor: <model slug>
- verdict: pending
- evidence: <card / run dir / commit>
- notes:
```

## Refuse when

- the request has no traceable source; or
- it would need a protected-document change, new paid spend while the Owner is away, or a production
  action; or
- the underlying information is missing — say what is missing and ask one question.
