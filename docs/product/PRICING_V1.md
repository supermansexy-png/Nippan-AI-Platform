# Pricing v1 — Phase A

Status: **ACTIVE**

## Price

299 THB/month, flat. One tier. No annual discount, no multi-tier ladder in
Phase A — the target segment wants a number they can decide on immediately,
not a comparison table.

## What's included

- One bot type per subscription (chat / secretary / etc. — see
  `CUSTOMER_SEGMENTS.md` for the catalog)
- 500-800 messages/month (exact number set by Cost Guard based on real
  observed cost per message; do not commit to a number until Phase A week
  1-2 usage data exists)
- Onboarding via the conversational assistant, free, one-time

## Multiple bots

A customer wanting more than one bot type pays per additional bot — not
folded into a single "unlimited" price. Never offer unlimited usage at this
price point; see cost analysis below for why.

## Over-quota handling

When a tenant approaches their quota (yellow-tier per `MONITORING.md`):
1. Notify the customer before they hit the ceiling, not after
2. Offer an easy top-up, not a hard cutoff — the bot should not go silent
   mid-conversation with an end customer
3. Never silently downgrade quality (e.g., swap to a worse model) without
   telling the tenant

## Why flat pricing, no unlimited tier

Cost per tenant at 600 messages/month on a cheap model
(Gemini Flash-class, ~$0.075-0.84 per million tokens) runs roughly
5-30 THB/month. Infrastructure (n8n hosting) adds roughly 20-60 THB/tenant
at 30-tenant scale. Total cost is comfortably under the 299 THB price, but
the margin only holds if usage stays bounded. An unlimited tier removes
that bound and turns one heavy user into a loss.

## Trigger to revisit

Reconsider pricing structure (tiers, per-message pricing, or a specialized
high-price low-volume track) when either:
- Real Phase A cost data diverges meaningfully from the estimate above
- The owner activates the specialized/high-value pivot option described in
  `docs/decisions/PIVOT_OPTION.md`
