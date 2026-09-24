# War Room — roles

Status: **ACTIVE — Phase A**

## Principles

1. **Positions are fixed; the occupant can change.** Any role may be filled
   by the owner, by an AI model, or later by a different AI model. Never
   hardcode a model name into a role — Model Scout proposes swaps,
   Project Lead approves (`docs/product/MODEL_POLICY.md`).
2. **A role is written policy before it is an AI seat.** In Phase A most
   roles are performed by the owner by hand, following this document. A
   role becomes an automated AI seat only when it climbs the autonomy
   ladder at the end of this file.
3. **Nobody approves their own work.** Whoever builds something is never
   the one who approves it for real customers.

## Project Lead (Phase A: the owner)

Decides: approving/rejecting tenants, approving anything before it reaches
real customers (until Auditor is proven), model swaps, business-mode switch
(`docs/decisions/PIVOT_OPTION.md`), and conflicts between roles.

Owns: the Decision Log (`DECISION_LOG_FORMAT.md`).

Cannot: downgrade a risk level set by Auditor or Cost Guard, or approve
anything that breaks `docs/product/CUSTOMER_FACING_RULES.md` or
`docs/security/PDPA_COMPLIANCE.md` Layer 3.

## Development

**Developer** — builds/edits n8n workflows on an approved task card
(`TASK_CONTROL.md`), tests them, hands them to Auditor. Cannot ship to
real customers.

**MCP tool builder** — builds new MCP tools, registers name, capability,
permission scope and a per-call cost estimate for Cost Guard. Removing a
tool goes through Project Lead (a tenant may depend on it).

## Audit

**Auditor** — before anything reaches a real customer, checks: it works,
tenant/bot isolation holds (no cross-tenant data), it cannot be made to
name its underlying model, it never claims to be human, it stays on topic.
Spot-checks real conversations weekly once volume exists. Reviews the
monitoring log (`MONITORING.md`) and escalates red events immediately.

**Cost Guard** — cost only: per-call cost estimates for new tools/
workflows, per-bot usage against quota, early warning before a bot or
tenant becomes unprofitable, proposals for cheaper model tiers. Writes
cost events into the monitoring log; does not own the whole pipeline.

## Operations

**Onboarding agent** — runs setup per `docs/product/ONBOARDING_FLOW.md`,
turns what the owner says/uploads into fixed-menu config, shows a sample
conversation for confirmation, never names the underlying model.

**Support agent** — handles existing tenants' questions and config
changes; anything that could raise cost is flagged to Cost Guard first.

## Marketing

Collects demand signals from Operations (questions bots can't answer,
requests outside the tool set), drafts outreach for the segments in
`docs/product/CUSTOMER_SEGMENTS.md`, and brings candidate niches to Project
Lead **with evidence** (how often, from how many different prospects).

## Model Scout

Tracks models and prices on OpenRouter and any other provider, proposes
swaps with a cost/quality comparison. Never swaps automatically.

## Autonomy ladder (applies to every role)

| Stage | What the role does | Who approves its output | Move up when |
|---|---|---|---|
| 1. Manual | Owner does the job by hand using this document | Owner | The job is repetitive and well understood |
| 2. Drafting | AI prepares the work, owner decides | Owner, every time | ~20 consecutive drafts accepted with no substantive correction |
| 3. Supervised | AI acts on routine (green) cases itself; yellow/red go to owner | Owner reviews a weekly sample | A full month with no red incident caused by the role |
| 4. Autonomous | AI acts; owner sees summaries and red alerts only | Monitoring + Auditor | — |

Moving **down** is immediate: any red incident caused by a role drops it
one stage until the cause is fixed. Stage changes are Decision Log entries.

Phase A starting points: Operations at stage 2; everything else at stage 1.
Audit roles are the first candidates to climb, because every other role's
autonomy depends on the checking being reliable.
