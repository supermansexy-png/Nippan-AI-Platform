# Onboarding flow

Status: **ACTIVE — Phase A**

## Principle

The customer talks to an AI assistant the way they'd talk to a person
setting this up for them — not a form. They can describe their business,
upload something, share a link, or any mix, and the assistant fills in the
gaps by asking.

## Accepted inputs (any combination)

| Input | How it's used |
|---|---|
| Plain conversation | Assistant asks follow-up questions to fill required fields |
| Website link | `web-fetch` tool pulls relevant pages (home + menu/product pages only — not a full site crawl) |
| Uploaded file (PDF/Excel/image of a menu or price list) | `file-reader` tool extracts structured info |

## Flow

1. Customer describes their business or shares what they have
2. Assistant reads/extracts what it can automatically
3. Assistant asks only for what's still missing (tone, hours if not found,
   which tasks they want the bot to do)
4. Assistant shows a short sample conversation ("your bot will say
   things like...") for the customer to review
5. Customer confirms or asks for adjustments
6. Bot goes live

## Cost controls on ingestion

- Cap document/page size per onboarding session (exact cap set by Cost
  Guard; this is a one-time cost, so it can tolerate a higher per-session
  spend than an ongoing message, but not an unbounded one)
- Web fetch limited to the business's own site's relevant pages, not a
  full-site crawl
- The onboarding conversation itself may use a stronger/pricier model than
  ongoing chat, since it happens once per customer, not per message

## What this produces

The output is entirely fixed-menu config values (see
`CUSTOMER_FACING_RULES.md`) — never a raw prompt built from the customer's
words. The assistant's job is translation, not pass-through.
