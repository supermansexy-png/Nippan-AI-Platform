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

LINE has two different message mechanisms, and only one of them costs
anything:

- **Reply messages** — the bot answering a message the end customer sent
  first (uses LINE's reply token). **Free, unlimited**, on any plan. This
  covers the entire chat-bot use case: someone messages the shop, the bot
  answers.
- **Push messages** — the bot messaging someone who did not just message
  it (e.g. a booking reminder sent ahead of time). LINE's free plan
  includes a limited number of these per month (300 at the time of
  writing; paid plans start around 1,280 THB/month if a tenant needs
  more). Re-check LINE's current terms before launch — they change.

**Platform rule: push messages are capped at 200/month per bot** — set
below LINE's own free-plan ceiling (300) as a safety margin, so a bot can
never push a tenant's account into LINE's paid tier on its own. Ordinary
chat replies are unaffected by this cap; it only limits bot-initiated
messages like reminders.

Why one shared LINE account for all tenants is never an option: it would
put every tenant's reminders on one bill and make usage impossible to
separate per tenant. Each tenant on their own free account means normal
chat replies cost the platform nothing regardless of volume, and only the
push-based features (reminders) are capped and tracked per bot.

Onboarding must tell the owner plainly: chat replies are unlimited;
scheduled reminders are capped at 200/month.

## Over quota

Two independent quotas, checked separately:

- **Chat replies** (the message quota above): warn the owner at 80%
  (yellow, `docs/warroom/MONITORING.md`), offer a simple top-up, never let
  the bot go silent mid-conversation, never silently downgrade the model
  without telling the owner.
- **Push/reminders** (200/month cap): warn at 80%; once the cap is hit,
  reminders pause for the rest of the month rather than risk pushing the
  tenant's own LINE account into a paid tier. Chat replies are unaffected
  — they are free and have their own separate quota above.

## Why flat, and why never "unlimited"

Estimated platform cost per bot per month:

| Item | Estimate |
|---|---|
| AI model, chat replies (LINE reply = free delivery; the cost is only the model call, ~600 messages) | ~5–30 THB |
| AI model, push/reminders (capped at 200/month above) | ~2–10 THB |
| Server share (self-hosted n8n + database, ~30 bots) | ~20–60 THB |
| One-time onboarding (stronger model) | ~5–10 THB, once |
| **Total** | **~30–110 THB** vs 299 THB revenue |

LINE delivery itself costs the platform nothing either way — reply
messages are free and push messages stay under LINE's own free-tier limit
by design. The AI model call is the real variable cost, and the message
quota (chat) and push cap (reminders) both exist to keep it bounded.
"Unlimited" on either would remove that bound and let one heavy user erase
the profit of several others.

These are estimates. Step 2 of the playbook replaces them with real numbers.

## Revisit when

- real cost differs from this table by more than ~50%
- the specialized/high-value option is activated (`docs/decisions/PIVOT_OPTION.md`)
