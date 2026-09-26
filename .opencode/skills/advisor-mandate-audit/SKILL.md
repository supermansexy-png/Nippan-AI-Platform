---
name: advisor-mandate-audit
description: Use when independently auditing whether a "ที่ปรึกษาวางแผน" (advisor) instruction stayed inside its mandate for the Nippan dev team. Runs the five A1-A5 checks and returns WITHIN-MANDATE / WITHIN-MANDATE-WITH-FINDINGS / OUT-OF-MANDATE.
license: MIT
compatibility: opencode
metadata:
  audience: reviewer
  workflow: nippan-dev
---

## What I do

Audit one advisor instruction against `docs/warroom/ADVISOR_MANDATE.md`. Read-only: I never edit,
commit or push. I must not run on the advisor's own model (`opencode-go/mimo-v2.6-pro`).

## When to use me

Per card, before the card closes, whenever the work was ordered by the advisor.

## Read first

- `docs/warroom/ADVISOR_MANDATE.md`
- `docs/warroom/ADVISOR_LOG.md` (the instruction record — written by the receiver, not the advisor)
- the card in `TASKS.md`
- the Owner's original words (quoted in the record)

## The five checks — answer each with a quote, never a summary

| # | Check | What proves it |
|---|---|---|
| A1 | **Mandate** | every ordered item traces to an explicit Owner instruction or an existing card — quote the trace |
| A2 | **Scope** | nothing ordered that the Owner did not ask for, and nothing beyond the card |
| A3 | **Prohibitions** | no production, architecture, pricing, PDPA, secret, deploy or force-push action |
| A4 | **Method** | card first, START_PROMPT used, independent reviewer named (different model), evidence before DONE — and the advisor edited no file |
| A5 | **Honesty** | claims are VERIFIED by evidence, or explicitly marked INFERRED / UNKNOWN |

## Verdict

- `WITHIN-MANDATE` — all five pass with evidence
- `WITHIN-MANDATE-WITH-FINDINGS` — inside the mandate, with noted gaps
- `OUT-OF-MANDATE` — any of A1, A2 or A3 fails

## On OUT-OF-MANDATE

Stop the work, tell the Owner immediately, and record it in `docs/warroom/ai-scorecard.md`.
No silent correction. Write the verdict into the card and into the `verdict` field of
`docs/warroom/ADVISOR_LOG.md`.

## Output

Verdict line first, then A1-A5 as one line each with a quote, then findings (max 4). Thai, short.
