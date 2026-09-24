# Customer-facing rules

Status: **ACTIVE — Phase A**

## Never reveal the underlying model

No bot, in any tenant, under any framing, ever states or confirms which AI
model or vendor powers it. This applies to:
- Direct questions ("are you ChatGPT?", "what AI is this?")
- Indirect probing (asking about training data cutoff, asking it to
  describe its own architecture)
- The Onboarding assistant itself, when talking to a prospective tenant

Handle it with a natural deflection, not a robotic refusal — something in
the spirit of "I'm just [business name]'s assistant" — not a hard "I
cannot answer that."

Auditor tests for this specifically (see `docs/warroom/ROLES.md`).

## What the customer (tenant) can configure

Only from fixed menus, never free-form system prompts:
- Response tone (from a fixed set of options)
- Business info (hours, prices, policies)
- Which tasks the bot performs (from the tool catalog in
  `docs/product/MCP_TOOLS_V1.md`)

Free-form text the customer provides (uploaded files, a description of
their business) is *read* by the Onboarding assistant and converted into
the fixed-menu config above — the customer's raw words never become
unfiltered system instructions to the bot. This is what keeps a bad prompt
from one customer from becoming a cost or safety problem for the whole
platform.

## Model policy is invisible infrastructure

Model choice, routing, and cost optimization (see
`docs/product/MODEL_POLICY.md`) are entirely backend decisions. A customer
never selects a model, never sees model names in any UI, and pricing never
varies by which model happens to be serving them.
