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

## Cost policy — value first

Free and inexpensive paid models are both allowed. Choose the lowest-cost
model that can reliably perform the required task to the required
standard.

A stable inexpensive paid model may be preferred over an unstable free
model when it reduces retries, failures, latency, poor-quality output, or
wasted tokens.

### Self-approval guideline for NEW model selections

- Input: up to approximately **$0.25 per 1M tokens**
- Output: up to approximately **$1.00 per 1M tokens**

If a NEW candidate materially exceeds these limits, ask the Owner before
appointing it.

Models already listed in the current model roster are Owner-approved for
this pilot even if current market pricing temporarily exceeds the general
recruitment threshold. Do not repeatedly ask the Owner to re-approve an
already approved roster model.

## Fallback

Every tier keeps at least one alternative model from a different provider.
See the Retry/Failover policy below for exactly when the Primary is
retried and when the Backup takes over. If Primary and Backup both fail,
the bot sends the outage message in `docs/product/BUSINESS_OPERATIONS.md`
§1 and a red event is logged.

### Retry / failover policy

For transient failures (HTTP 429, HTTP 403 caused by provider
availability, timeout, provider overload, temporary server error,
malformed provider response, truncated response, temporary tool failure):

1. Retry the Primary **at most once** when reasonable.
2. If it fails again, switch to the approved Backup.
3. If the Backup also fails, **STOP and report the failure** to Project
   Lead / Owner.

Never create an endless retry loop.

### Quality failure policy

A technically successful API response may still count as a failure when
the model repeatedly produces incorrect work, hallucinated evidence, poor
instruction-following, missing required output, inappropriate tool use,
broken code, unacceptable review quality, severe formatting failures, or
repeated scope violations.

Allow **one** reasonable correction attempt. If the same model remains
unsuitable, switch to Backup rather than repeatedly prompting it.

## OpenCode Zen exception

OpenCode Zen is **FREE MODELS ONLY**. Never apply OpenRouter's paid-model
policy to OpenCode Zen, and never authorize a paid Zen model.

## Speed matters on LINE

Default models for end-customer replies must answer fast enough for LINE's
reply flow (Auditor measures this in Step 1). A smarter but slow model is
the wrong choice for chat replies.

## Free/cheap models

Explicitly in scope for routine tasks. OpenRouter's free tier and
sub-$0.10/M-token models are the default for anything that doesn't need
high accuracy. This is a cost-control mechanism, not a corner being cut —
see `docs/product/PRICING_V1.md` for why the margin depends on it.

## Work style

Prefer useful work over ceremony.

- Do not run unnecessary smoke tests after a model has already been
  accepted, unless a new failure provides a reason.
- When a real failure occurs: identify the failing component, fix or route
  around that specific problem, then continue the real task. Avoid
  restarting the entire validation process unnecessarily.
- Do not repeat completed work without a reason.

## Model Scout's job

Continuously watches for:
- New models that beat the current pick on price or quality for a given
  tier
- New providers worth adding to the routing options

Proposes swaps to Project Lead. Never swaps automatically — see
`docs/warroom/ROLES.md`.

## Never hardcode a model into a role

Model choice lives in the current model roster, not in role definitions or
agent prompts. A role (see `docs/warroom/ROLES.md`) is filled by whichever
approved model is suitable at the time. Model Scout proposes swaps and
Project Lead approves — no role permanently owns a specific model name.

## What never changes because of this policy

Customer-facing behavior (`CUSTOMER_FACING_RULES.md`) is identical
regardless of which model or provider is actually serving a given message.
Model policy is entirely a backend concern.
