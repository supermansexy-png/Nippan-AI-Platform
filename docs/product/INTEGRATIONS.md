# Integrations — connecting to any platform

Status: **ACTIVE — the contract every integration must follow**

## Goal

The platform must be able to connect to platforms that exist today and
ones that don't exist yet — chat apps, marketplaces, payment providers,
accounting, calendars, marketing tools, other AI services. This is a core
source of the system's flexibility, so it is designed as a **standard
plug**, not a list of individual integrations.

## The rule

**The core never knows which platform it is talking to.** Bots, memory,
policy and the database only see the normalized formats below. Everything
platform-specific — authentication, signature checks, message formats,
rate limits, delivery costs — lives inside one adapter per platform.

Consequence: adding a platform means writing one adapter. Nothing in the
core, the bots, the memory system or the schema changes.

Why: if platform details leak into the core, every new platform becomes a
change to shared code, and every change risks breaking every existing
tenant. Keeping them in adapters makes each integration small, isolated,
testable, and removable.

## Three kinds of adapter

| Kind | Direction | Examples (today and future) |
|---|---|---|
| **Channel** | conversations in and out | LINE OA, web chat, Facebook Messenger, Instagram, WhatsApp, TikTok, Telegram, email, SMS, voice |
| **Connector** | the bot reads/writes a business system | POS, online shop, stock sheet, calendar, accounting, CRM, delivery tracking |
| **Event source** | something happens elsewhere → the bot reacts | payment received, order placed, review posted, form submitted, stock low |

## Normalized formats (the "plug shape")

### Inbound message (channel → core)
```
tenant_id, bot_id, channel_id
end_customer_ref      platform user id, scoped to this tenant
message_id            platform's id — used to drop duplicates
received_at
content               list of parts: text | image | file | location | sticker | button_reply
reply_handle          opaque; only the adapter knows how to use it (e.g. LINE reply token + expiry)
```

### Outbound message (core → channel)
```
tenant_id, bot_id, channel_id, end_customer_ref
kind                  reply | proactive     (proactive = bot-initiated; counts against push quotas)
content               same parts as inbound, plus quick_replies / buttons
reply_handle          when kind = reply
```
If a channel cannot render a part (e.g. buttons), the adapter degrades it
to text — the core never needs to know.

### Connector call (core → business system)
```
tenant_id, bot_id
capability            e.g. "check_stock", "create_booking", "get_order_status"
input                 per-capability schema
risk                  read | write_low | write_important | financial
```
Bots ask for **capabilities**, not platforms. "Check stock" works the same
whether the shop uses POS brand A, brand B or a Google Sheet.

### Event (event source → core)
```
tenant_id, event_type, occurred_at, payload, source_event_id (for de-duplication)
```

## What every adapter must do

1. **Verify authenticity** before trusting anything (e.g. LINE: HMAC-SHA256
   of the raw body with the channel secret, checked before JSON parsing).
2. **Map** platform identifiers to `tenant_id` / `bot_id` / `channel_id` —
   an unmapped request is rejected, never guessed.
3. **Normalize** into the formats above.
4. **Drop duplicates** using the platform's message/event id (platforms
   retry; the same message must not be answered twice).
5. **Respect platform limits** — time windows, rate limits, message
   quotas (e.g. LINE push cap in `PRICING_V1.md`).
6. **Report cost and usage** to `usage-tracker` and errors to `monitor-log`.
7. **Keep credentials out of the database** — only a reference
   (`channels.credential_ref`), secrets stay in n8n's credential store.

## Registering an adapter

Each adapter is recorded (in `docs/product/adapters/` as one short file)
with: kind, platform, capabilities or content types supported, auth
method, known limits, cost model (free / per message / % fee), risk level,
and status (`planned` / `building` / `live` / `retired`).

Adding one follows the normal path in `MCP_TOOLS_V1.md`: task card →
build → Cost Guard → Auditor → Project Lead approval.

## Risk rules by integration type

| Type | Default rule |
|---|---|
| Read-only (check stock, read calendar, read ad results) | L2 |
| Writes to a tenant's system (create booking, update order) | L2, and the bot confirms with the end customer before writing |
| Anything that posts publicly (social posts, review replies) | L3 — AI drafts, owner approves each post |
| Anything touching money (payment links, refunds, charges) | L3 — never fully automatic in Phase A/B |

## When no adapter exists yet — fallback paths

So a tenant is never told "we can't connect to that":

1. **Generic webhook in / HTTP out** — any system that can send or receive
   a webhook can be connected with configuration only.
2. **n8n's built-in integrations** — n8n already ships nodes for hundreds
   of services; an adapter can often be a thin wrapper around one.
3. **Spreadsheet bridge** — the tenant's system exports to a Google Sheet;
   the bot reads the sheet. Crude, but works for almost anything.
4. **Third-party MCP servers** — many services now publish MCP servers; one
   can be registered as a connector if it passes the same checks.
5. **Email** — the universal last resort for notifications and hand-offs.

## Priority is demand-driven

This document defines *how* anything connects, not *what* gets built
next. Marketing collects requests; an adapter is built when real tenants
ask for it (`docs/warroom/ROLES.md`). Known candidates and their
constraints are in the Candidates table below — it is a menu, not a plan.

## Candidates (reference, not commitments)

| Platform | Kind | Notable constraint |
|---|---|---|
| LINE OA | Channel | **live in Phase A**; reply free, push capped (`PRICING_V1.md`) |
| Web chat | Channel | **Phase A Step 3** |
| Facebook Messenger / Instagram | Channel | Meta business verification; messaging-window rules |
| WhatsApp Business | Channel | charged per conversation/message — cost model differs from LINE |
| TikTok / Shopee / Lazada chat | Channel | partner-program access varies; verify per platform |
| Email / SMS | Channel | SMS costs per message |
| PromptPay QR (static) | Connector | free, no gateway; payment not confirmed automatically |
| Payment gateways (Omise, 2C2P, GB Prime Pay…) | Connector + Event | per-transaction fee; confirms payment automatically |
| Google Calendar | Connector | per-tenant OAuth consent |
| Accounting (e.g. FlowAccount) | Connector | L3 when it issues documents |
| POS / online shop backends | Connector + Event | varies widely — spreadsheet bridge first |
| Google Business Profile / review sites | Event + Connector | public replies are L3 |
