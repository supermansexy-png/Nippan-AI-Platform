# Model policy

Status: **ACTIVE — Phase A**

## Gateway

OpenRouter is the default gateway — one integration point for many model
providers. This is not exclusive: any additional provider (Thai-specific
providers, a cheaper specialist API, a free tier from a new entrant) can be
added alongside it. Nothing in this system hardcodes "OpenRouter" as the
only path — see `docs/warroom/ROLES.md`, Model Scout.

## Tier by task, not by tenant

| Task | Model tier |
|---|---|
| Routine end-customer chat (hours, prices, simple Q&A) | Cheapest viable model (free tier or lowest-cost paid, e.g. Gemini Flash-class) |
| Tasks needing accuracy (bookkeeping-style bots, calculations) | Mid-tier model |
| Onboarding (one-time per customer, high-stakes first impression) | Can afford a stronger model — this cost happens once, not every message |

No tenant is on a permanently better or worse model because of who they
are — tier is set by task type, applied uniformly.

## Free/cheap models

Explicitly in scope for routine tasks. OpenRouter's free tier and
sub-$0.10/M-token models are the default for anything that doesn't need
high accuracy. This is a cost-control mechanism, not a corner being cut —
see `docs/product/PRICING_V1.md` for why the margin depends on it.

## Model Scout's job

Continuously watches for:
- New models that beat the current pick on price or quality for a given
  tier
- New providers worth adding to the routing options

Proposes swaps to Project Lead. Never swaps automatically — see
`docs/warroom/ROLES.md`.

## What never changes because of this policy

Customer-facing behavior (`CUSTOMER_FACING_RULES.md`) is identical
regardless of which model or provider is actually serving a given message.
Model policy is entirely a backend concern.
