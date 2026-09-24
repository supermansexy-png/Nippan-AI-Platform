# War Room — roles

Status: **ACTIVE — Phase A**

## Principle

Positions are fixed. Which AI model sits in a position can change. Never
hardcode a model name into a role's behavior — route through policy/config
so Model Scout (below) can propose a swap without a rewrite.

Not every position is staffed from day one. See "Activation order" at the
end of this document — most positions start as a written prompt/policy that
a human (the owner) executes manually, and only become an automated AI seat
once there is enough real data to trust it with the judgment calls below.

## Project Lead

**Decides:**
- Approve/reject new customers
- Approve any output before it reaches a real customer, until Auditor is
  staffed and proven
- Which model sits in which position (acts on Model Scout's proposals)
- When to switch business mode (low-price/high-reach <-> specialized/
  high-price/low-volume, per the owner's stated future option)
- Resolves any conflicting signal from another role

**Receives from:** every other role, via the Decision Log (see
`DECISION_LOG_FORMAT.md`)

**Constraint:** cannot downgrade a risk classification set by Auditor or
Cost Guard. Cannot approve anything that violates `CUSTOMER_FACING_RULES.md`
or `docs/security/PDPA_COMPLIANCE.md`.

---

## Development

### Developer
- Builds/edits n8n workflows on Project Lead's instruction
- Tests a workflow before handing it to Auditor
- No authority to ship a workflow straight to a real customer

### MCP tool builder
- Builds new MCP tools (see `docs/product/MCP_TOOLS_V1.md` for the starting
  set)
- Registers each new tool with a name, capability, permission scope, and a
  rough per-call cost estimate handed to Cost Guard
- Removing/deprecating a tool goes through Project Lead first — customers
  may depend on it

---

## Audit

### Auditor
- Reviews a new/changed workflow before it reaches a real customer:
  correctness, whether a customer could extract the underlying model name,
  whether it stays on-topic
- Periodic spot-check of real conversations (weekly, once volume justifies
  it)
- Escalates anything red-tier (see `docs/warroom/MONITORING.md`) to Project
  Lead immediately, not on the weekly cadence

### Cost Guard
- Estimates real cost-per-call for every new tool/workflow before it ships
- Tracks each tenant's usage against their quota (see
  `docs/product/PRICING_V1.md`)
- Flags a tenant approaching their quota before they blow through it
- Doubles as the monitoring rollup point — see `MONITORING.md` for the
  green/yellow/red pipeline this role owns

---

## Operations

### Onboarding agent
- Runs new-customer setup: conversational interview, and/or reading an
  uploaded file/link, per `docs/product/ONBOARDING_FLOW.md`
- Converts what the customer says into config values from a fixed menu —
  never free-form prompt text the customer writes directly into the bot's
  system behavior
- Always summarizes the resulting bot behavior back to the customer for
  confirmation before going live
- Bound by `CUSTOMER_FACING_RULES.md`: never names the underlying AI model
  or vendor, under any framing

### Support agent
- Handles existing-customer questions and config changes after onboarding
- Any change a customer requests that could raise cost (e.g., asking for an
  unthrottled/always-on capability) gets flagged to Cost Guard before
  applying it

---

## Marketing

- Watches for market signals surfaced by Operations (a question the current
  bot can't answer, a request outside the current tool set)
- Drafts real outbound content (posts, outreach copy) for the target
  segments in `docs/product/CUSTOMER_SEGMENTS.md`
- Feeds candidate new niches back to Project Lead with evidence (how many
  times has this come up, from how many distinct prospects)

---

## Model Scout

- Tracks new/changed models and pricing on OpenRouter and any other
  provider added per `docs/product/MODEL_POLICY.md`
- Proposes swaps when a cheaper or better model appears for a given role —
  proposal goes to Project Lead, never an automatic swap
- Is the mechanism that lets "more AI providers enter the market" become
  "the system gets more capable" without anyone rewriting code

---

## Activation order

Do not staff all of these as live AI seats on day one. Phase A activation
order:

1. **Operations only** (Onboarding + Support) — everything else is the
   owner acting directly, or not yet needed
2. **Audit** (Auditor, then Cost Guard) — once real customers exist and
   there's something to audit
3. **Development, Marketing, Model Scout** — once the system is stable
   enough that a bad decision in these roles is affordable to make, and
   there's enough real usage data to make the decision well

This is the same ladder as `docs/warroom/MONITORING.md`'s four-stage
timeline. A role's written definition above is authoritative from day one
even before it is staffed — a human filling the role manually should follow
the same decision rules.
