# Pricing v1 — Phase A

Status: **ACTIVE**

## Price

**299 THB/month per bot**, flat. One tier. No annual plan in Phase A — the
target customer should be able to decide on one number.

A second bot for the same business is another 299 THB (a discount can be
tested later; do not promise one now).

## Included

- one bot, on the business's own LINE Official Account and/or a web chat
- a monthly message quota (starting value: 600 replies; confirm or adjust
  after the first real tenants — see `docs/warroom/STARTUP_PLAYBOOK.md` Step 2)
- conversational onboarding, free, once

## Who pays for LINE

Each business connects **its own** LINE Official Account (free plan). The
platform never runs one shared LINE account for all tenants.

Why: LINE OA's free plan includes a limited number of *push* messages per
month (300 on the free plan at the time of writing; paid plans start
around 1,280 THB/month). Replies to a customer's message are handled
differently from pushes. A single shared account would put every tenant's
reminders on our bill and destroy the margin. With each tenant on its own
free account, normal replies cost the platform nothing, and only features
that *push* (reminders, follow-ups) consume the tenant's own free quota.

Onboarding must tell the owner this plainly: reminders are limited by
their LINE plan. Re-check LINE's current terms before launch — they change.

## Over quota

1. Warn the owner at 80% (yellow in `docs/warroom/MONITORING.md`)
2. Offer a simple top-up — never let the bot go silent mid-conversation
3. Never silently switch to a worse model without telling the owner

## Why flat, and why never "unlimited"

Estimated platform cost per bot per month:

| Item | Estimate |
|---|---|
| AI model (600 replies on cheap models, some mid-tier) | ~5–30 THB |
| Server share (self-hosted n8n + database, ~30 bots) | ~20–60 THB |
| One-time onboarding (stronger model) | ~5–10 THB, once |
| **Total** | **~30–100 THB** vs 299 THB revenue |

The margin holds only while usage is bounded. "Unlimited" removes the bound
and lets one heavy user erase the profit of several others.

These are estimates. Step 2 of the playbook replaces them with real numbers.

## Revisit when

- real cost differs from this table by more than ~50%
- the specialized/high-value option is activated (`docs/decisions/PIVOT_OPTION.md`)
