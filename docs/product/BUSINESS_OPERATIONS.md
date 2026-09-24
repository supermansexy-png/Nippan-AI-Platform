# Business operations — Phase A

Status: **ACTIVE — Phase A**

What happens when things go wrong, and how the first customers are found.
Each section states the rule and why.

## 1. Outage

Rule: if a bot cannot answer (n8n down, model provider down), the customer
gets a fixed fallback message — "The shop's assistant is temporarily
unavailable; the shop will reply as soon as possible" — and the owner is
notified (red event if longer than 15 minutes).

Why: silence looks like the shop is ignoring its customers. A fallback
protects the tenant's reputation, which is what they are paying for.

Also: keep at least one alternative model per tier in the routing policy,
so a single provider outage switches models instead of stopping service.

## 2. Wrong answers

Rule: bots answer prices, stock and policies only from the tenant's own
business info, and hand off anything uncertain (`handoff-to-owner`). The
tenant agreement states the bot is an assistant, the owner remains
responsible for the business information they provide, and the platform
fixes errors caused by the bot promptly.

Why: the most likely real damage is a confidently wrong price or promise.
Keeping answers tied to the owner's own data, and handing off when unsure,
prevents most of it; the agreement makes responsibility clear before
anything happens. Have a lawyer review the agreement wording.

## 3. Cancellation and refunds

Rule: monthly, cancel anytime, no refund for a partly used month, except
a full refund in the first 7 days if the bot did not work as promised.
After cancellation, the tenant's data is kept 30 days (so they can come
back), then deleted (`docs/data/LITE_SCHEMA_V1.md`).

Why: simple rules the owner can apply by hand for 30 tenants; the 7-day
guarantee lowers the risk of trying for a hesitant small-business owner;
the 30-day deletion satisfies PDPA without losing a returning customer.

## 4. Platform rules (LINE and others)

Rule: bots only reply to people who message the business, never send
unsolicited mass messages, and follow LINE's Official Account terms. Each
tenant's account belongs to the tenant.

Why: a platform ban hits the tenant's own business account. We must never
be the reason a customer loses their LINE OA.

## 5. Payments

Rule: Phase A collects payment manually (bank transfer / PromptPay),
recorded by the owner, with a reminder before each renewal. A bot is
paused — not deleted — if payment is 7 days late.

Why: payment automation is real work and unnecessary below ~30 tenants.

## 6. Finding the first customers

Rule: the first 5–10 tenants come from people the owner can reach
directly — existing contacts, local shops, the owner's own business
network — not from ads. Offer the first month free in exchange for honest
feedback and permission to use their bot (anonymized) as a case example.

Why: early tenants need close support and will find the problems; they
should be people who will tell the owner the truth. Paid ads before the
product is proven spend money to learn nothing. Mix at least 2–3
"expected" tenants (online shops) with 2–3 from underserved segments
(`CUSTOMER_SEGMENTS.md`) to learn which group actually responds.
