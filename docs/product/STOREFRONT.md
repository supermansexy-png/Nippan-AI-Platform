# Storefront (public website)

Status: **ACTIVE — Phase A, built in playbook Step 3**

## Goal

A prospect understands the offer in under a minute, tries a real bot
before paying, and starts onboarding with one click.

## Page structure (one page)

1. **Headline** — what they get, in the customer's words
   ("Your shop's assistant, answering LINE 24 hours")
2. **Live demo** — a working demo bot for a sample shop, via
   `web-chat-channel`. Visitors chat before signing up. This is the main
   selling point: proof instead of promises.
3. **What it does** — three items max (answers questions, takes bookings,
   sends reminders)
4. **Price** — one number, 299 THB/month, what's included, "cancel anytime"
5. **One button** — "Set up my bot", which opens the Onboarding assistant
6. **Small print links** — privacy notice (PDPA), terms, contact

## Rules

- Same honesty rules as every bot (`CUSTOMER_FACING_RULES.md`): the demo
  says it is an assistant; no model names anywhere on the site.
- The demo bot runs on the cheapest model tier and has its own daily cap,
  so a flood of curious visitors cannot run up a bill.
- The demo never collects personal data beyond the chat itself, and shows
  the same short consent notice as tenant bots.

## Not in Phase A

Account dashboards, online payment automation, multiple pricing pages.
Payment in Phase A is manual (bank transfer / PromptPay, recorded by the
owner) — fine for up to 30 tenants.
