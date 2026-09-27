# Message flow v1 — from customer message to bot reply

Status: **DRAFT v1.2 — ND-1…ND-7 resolved by the Owner 2026-09-27; adapter-boundary
fixes applied (§0, §1, §7, §9, new §14); awaiting different-model review** (2026-09-27)
Audience: the implementer (n8n workflows / code). This document describes the
system to be built — it is an instruction to the runtime, not a record of
something already running.

Sources of truth (this document introduces **no new rule**):
`docs/data/LITE_SCHEMA_V1.md` · `docs/product/MCP_TOOLS_V1.md` ·
`docs/product/MODEL_POLICY.md` · `docs/product/PRICING_V1.md` ·
`docs/product/CUSTOMER_FACING_RULES.md` · `docs/product/BUSINESS_OPERATIONS.md` ·
`docs/product/INTEGRATIONS.md` · `docs/product/adapters/line-oa.md` ·
`docs/security/PDPA_COMPLIANCE.md` · `docs/architecture/FOUNDATION_V1.md` ·
`docs/warroom/MONITORING.md`

If a source disagrees with anything below, **the source wins** — this document
is a map of the sources, not a replacement.

---

## 0. Scope and vocabulary

One path is documented: **an end customer sends a message on a channel → the bot
answers.** Proactive/push messages (reminders) are a separate entry point and are
covered in §9.

| Term | Meaning |
|---|---|
| **Adapter** | The channel-specific plug (Phase A: `line_oa`, `web_chat`). Owns signature verification, identity mapping, message formats, platform limits. The core never knows which platform it is talking to (`INTEGRATIONS.md`). |
| **Core** | Bot logic: context, memory, policy, model call, reply. |
| **Tool** | An MCP capability from `MCP_TOOLS_V1.md` (`data-access`, `usage-tracker`, `monitor-log`, `line-channel`, `chat-bot-core`, `memory-store`, `handoff-to-owner`, …). |
| **Scope key** | `tenant_id` + `bot_id`. Both, every query, no exception (`LITE_SCHEMA_V1.md`, PDPA Layer 3). |
| **reply** (normalized `kind: reply`) | The bot answering a message the customer sent first — channel-neutral. *LINE case: uses the reply token; delivery is free and unlimited, so the only cost is the model call.* |
| **proactive** (normalized `kind: proactive`; a "push") | The bot starting a message (e.g. a reminder). Counts against `bots.monthly_push_quota` — **platform cap 200/bot/month**. *LINE case: set below LINE's own free-plan ceiling by design.* |

### Flow overview

```text
[CUSTOMER] --message--> (1) CHANNEL ADAPTER
                          signature -> identity -> dedup -> normalize
                                   |
                                   v
                        (2) SCOPE + CONTEXT LOAD          [data-access]
                                   |
                                   v
                        (3) PDPA FIRST-CONTACT NOTICE
                                   |
                                   v
                        (4) QUOTA / POLICY GATE           [usage-tracker]
                                   |
                                   v
                        (5) MODEL CALL + TOOLS            [chat-bot-core, memory-store]
                                   |
                                   v
                        (6) PRE-SEND ANSWER CHECK         (honesty / scope)
                                   |
                                   v
                        (7) SEND REPLY                    [line-channel / web-chat-channel]
                                   |
                                   v
                        (8) LOG                           [memory-store, usage-tracker, monitor-log]
```

Two hard invariants for the whole path:

- **I1 — Scope.** No query touches customer data without `tenant_id` **and**
  `bot_id`. Phase A enforces this with one shared `data-access` sub-workflow plus
  `lite_*` RLS (`SET LOCAL app.tenant_id` / `app.bot_id`); a missing scope
  resolves to zero rows / a rejected write — **fail-closed**.
- **I2 — Honesty/scope.** No reply leaves the system that names the model or
  vendor, claims to be human, or answers outside the tenant's own business
  (`CUSTOMER_FACING_RULES.md` rules 1, 2, 5).

---

## 1. Ingress — channel adapter

> **Boundary rule.** Everything in §1 is the **adapter's** job; the core starts at
> §2. The core never sees a platform's field names, headers, error codes or
> delivery rules — only the normalized message produced at S1.5
> (`INTEGRATIONS.md`: "The core never knows which platform it is talking to").
> Everything that looks LINE-specific below is an **example**, not a rule of the
> flow.

**S1.1 — Receive.** The adapter accepts the platform webhook over HTTPS
(LINE: `POST` to the LINE channel endpoint).

**S1.2 — Verify authenticity (MANDATORY, FIRST, BEFORE PARSING).**
- **General contract:** the adapter verifies the caller is genuine **by its own
  means, before it parses or trusts anything** (`INTEGRATIONS.md` "What every
  adapter must do" #1). The mechanism belongs to the adapter.
- **Example (LINE):** `x-line-signature` =
  `base64(HMAC-SHA256(channel_secret, raw_body))`, computed over the **raw
  request body bytes** and checked **before** the body is parsed as JSON
  (`adapters/line-oa.md`).
- Credentials always come from the credential store
  (`channels.credential_ref` → n8n credentials), never from the database, never
  from the request.
- **If verification fails → drop the request. Do not parse it, do not answer, do
  not continue.** Write a `monitor-log` event and return a non-2xx response that
  does **not** trigger a platform retry storm. **STOP.** *(ND-6 resolved
  2026-09-27.)*

**S1.3 — De-duplicate.** Platforms retry; the same message must never be answered
twice. Drop on the platform's event id (`webhookEventId` for LINE; `message_id`
in the normalized format) (`adapters/line-oa.md`).
- **Dedup store (ND-1 resolved 2026-09-27):** a small `lite_processed_events`
  table — scoped by `tenant_id` + `bot_id`, keyed by the platform event id, with
  a short TTL. Specified in `LITE_SCHEMA_V1.md`; the migration is tracked by
  **card T-077**.
- **Fallback:** if the dedup store is unavailable, treat the message as a
  duplicate and drop it (answering twice is worse than answering once) and raise
  an alert.

**S1.4 — Map identity (never guess).** The adapter maps the **platform bot id**
→ the `channels` row → `tenant_id` + `bot_id`, and the **platform user id** →
`end_customers.external_user_ref`, scoped to that tenant. *(LINE example:
`destination` → the channel; `source.userId` → the end customer —
`adapters/line-oa.md`.)*
- **If the destination is not mapped to a channel → reject the request. Never
  guess a tenant. STOP.** Log to `monitor-log`.

**S1.5 — Normalize.** Produce the inbound format from `INTEGRATIONS.md`
(`tenant_id, bot_id, channel_id, end_customer_ref, message_id, received_at,
content[], reply_handle`). `reply_handle` is opaque — for LINE it carries the
reply token and its expiry.
- If a channel cannot render a part (e.g. buttons), the adapter degrades it to
  text — the core never needs to know (`INTEGRATIONS.md`).

**Tables/tools:** `channels` (read), `monitor-log`.

---

## 2. Scope + context load

**S2.1 — Open the scoped session.** All reads/writes below go through the
`data-access` tool with `tenant_id` + `bot_id` set for the transaction
(`SET LOCAL app.tenant_id` / `SET LOCAL app.bot_id`).

**S2.2 — Load bot config.** Read `bots` (scoped): `tone`, `business_info`,
`enabled_tools`, `monthly_message_quota`, `monthly_push_quota`, `status`.
- If `bots.status` ≠ active → do not answer. **STOP** (quietly; the tenant
  paused/cancelled this bot).

**S2.3 — Resolve end customer.** Find or create the `end_customers` row for
(`tenant_id`, `bot_id`, `external_user_ref`); the row carries
`consent_notice_shown_at` and `last_active_at`.

**S2.4 — Load memory.** `memory-store` reads (a) the last N turns of
`conversations` for this `bot_id` + `end_customer_id` (never the whole history)
and (b) relevant `memory_summaries` (Phase A: keyword match).
`bots.business_info` is config, not memory, and always outranks inferred memory
(`FOUNDATION_V1.md` §12).

**Fallback if any read fails:** the bot cannot answer safely → go to the outage
path (§7). **Do not answer from a partial context. STOP.**

**Tables/tools:** `bots`, `end_customers`, `conversations`, `memory_summaries`
via `data-access` + `memory-store`.

---

## 3. PDPA first-contact notice

**S3.1 — Detect first contact.** If `end_customers.consent_notice_shown_at` is
`NULL`, this is the end customer's first message.

**S3.2 — Show the Layer 1 notice.** Before (or attached to) the first reply,
send the short, plain-language notice of what is collected and why
(`PDPA_COMPLIANCE.md` Layer 1). Then set `consent_notice_shown_at`.
- The notice is a **reply** (the customer messaged first) → free, not counted
  against the push cap.
- Do **not** send a long legal document.

**S3.3 — Notice cannot be sent?** If the notice cannot be delivered, do not
answer the underlying question yet (the notice comes first). Retry per the
adapter's rule; if it still fails, take the outage path.
- *(ND-4 resolved 2026-09-27: the short notice is attached to the first answer —
  one message, one reply.)*

**Tables/tools:** `end_customers` via `data-access`; `line-channel` /
`web-chat-channel` to send.

---

## 4. Quota / policy gate (before any model call)

Cost Guard checks **before** calling a model — a model call is the only real
variable cost (`PRICING_V1.md`).

**S4.1 — Classify the message.** `reply` (customer messaged first) or `push`
(bot-initiated). Only `reply` reaches here on the inbound path; the push path is
in §9.

**S4.2 — Check the reply quota.** Platform reply quota =
`bots.monthly_message_quota` (starting value 600/month — `PRICING_V1.md`;
confirm after the first real tenants). This bounds **model calls** — delivery cost
is the adapter's concern, not this gate's. *(LINE case: reply delivery is free and
unlimited.)*
- At **80%** → warn the owner (yellow, `MONITORING.md`).
- Over quota, no top-up (**ND-2 resolved 2026-09-27**) → the bot sends **one
  fixed message** telling the customer to contact the shop directly, quoting the
  fallback number/channel from `bots.business_info`, then **stops answering** —
  no further model calls until the quota is topped up or a new month begins.
  The message is sent **once**, not repeated on every later message (track the
  "quota notice sent" state per `end_customer_id` for the month).
- This still honours `PRICING_V1.md`: the customer is told where to go rather
  than met with silence, and the model is never silently downgraded.
- *Requires `bots.business_info` to carry a fallback contact (phone / LINE) —
  add it when the bot-config schema is finalised (card T-077).*

**S4.3 — Check the push cap (proactive path only).** Cap =
`bots.monthly_push_quota` (default 200/bot/month). *(LINE case: set below LINE's
free-plan ceiling as a safety margin.)*
- At **80%** → warn the owner.
- At the cap → **pause proactive messages for the rest of the month. Do not
  exceed. STOP** for that proactive message. Reply messages are unaffected.

**S4.4 — Check tool permission.** Only tools listed in `bots.enabled_tools` may
be called (`MCP_TOOLS_V1.md`).

**Tables/tools:** `bots` via `data-access`; quota counters via `usage-tracker`.

---

## 5. Model call

**S5.1 — Assemble context.** Deterministic assembly (`FOUNDATION_V1.md` §11):
raw current request → recent turns → `bots.business_info` → relevant memory →
token budget. The raw customer request is always retained.

**S5.2 — Choose the tier by task, not by tenant** (`MODEL_POLICY.md`): routine
chat (hours, prices, simple Q&A) → cheapest viable; accuracy tasks (bookkeeping,
calculations) → mid-tier; onboarding → stronger (one-time per customer).
**Speed matters on chat channels** (LINE especially) — a smarter-but-slow model
is the wrong choice for chat replies.

**S5.3 — Call with failover** (`MODEL_POLICY.md` "Retry / failover policy"):
1. Call the **Primary**. On a transient failure (429 / 403-by-availability /
   timeout / provider overload / temporary server error / malformed or truncated
   response), retry the Primary **at most once**.
2. Still failing → switch to the **Backup**, which must be a **different
   provider**.
3. Backup also fails → **STOP** and take the outage path (§7). Never an endless
   retry loop.

**S5.4 — Tool use (only if the task needs it).** Tools come only from
`enabled_tools`; every tool call needs schema validation, policy check, risk
mapping, timeout, idempotency for side effects, and an audit record
(`FOUNDATION_V1.md` §14). Money and public posts are never fully automatic in
Phase A/B (`INTEGRATIONS.md`).

**S5.5 — Model identity never reaches the customer** — the chosen model is
invisible infrastructure (`CUSTOMER_FACING_RULES.md` rule 4; `MODEL_POLICY.md`
"What never changes"). Model identifiers live in central policy/config, never in
workflows or prompts.

**Tables/tools:** model gateway (per `MODEL_POLICY.md`); `chat-bot-core`,
`memory-store`, `handoff-to-owner`, plus any business tool in `enabled_tools`.

---

## 6. Pre-send answer check (honesty / scope)

The draft answer is checked **before it is sent**. This is the code-level
enforcement of invariant **I2** — policy enforced by code, not by model opinion
(`FOUNDATION_V1.md` §2, §13).

| Check | Rule | Action on failure |
|---|---|---|
| **No model/vendor name** | Rule 2 — never name or confirm the model or company | Replace with the natural deflection: "I'm [business name]'s assistant — how can I help?" and send that. |
| **No human claim** | Rule 1 — never claim or imply being human, never invent a human persona that denies being a bot | Send the honest line ("I'm an automated assistant for this business") and offer to pass the conversation to the owner. |
| **No off-lane answer** | Rule 5 — only the tenant's own business info; no medical/legal/financial advice beyond their published info | Replace with `handoff-to-owner` rather than guessing (a confidently wrong price is worse than "let me check with the shop"). |
| **Uncertain** | Rules 1, 2, 5 | `handoff-to-owner` (notify the business owner) instead of answering. |

- If a check cannot be completed → **do not send the draft**; use the safe
  deflection/handoff instead. **Fail-closed.**
- **Implementation (ND-3 resolved 2026-09-27):** a **deterministic filter only**
  — keyword/pattern checks (model-name denylist + human-claim patterns + an
  explicit "unsure → handoff"). **No second model call** at this stage: there are
  no real customers yet and a per-message checker call is not worth the cost. If
  the deterministic filter proves too weak in real use, upgrading to a checker
  model is reconsidered later — with a price approval under `MODEL_POLICY.md` at
  that time.

**Tables/tools:** deterministic pre-send filter (ND-3); `handoff-to-owner`;
`monitor-log`.

---

## 7. Send reply + outage path

**S7.1 — Send.** The adapter sends the checked answer through its own channel
mechanism (`INTEGRATIONS.md`: delivery is the adapter's job).
- **LINE case — reply token:** a LINE `reply` uses the reply token, which is
  **short-lived** (`adapters/line-oa.md`); the answer must be produced inside that
  window. Delivery is free and unlimited.
- **LINE case — reply token expired (ND-5 resolved 2026-09-27):** the answer
  cannot be sent as a free reply. **Do not auto-convert it to a proactive
  message** (that would spend the tenant's quota). Log the miss, count it against
  a reply-quality metric, and set a maximum wait budget per reply so this happens
  as rarely as possible. *(A channel with no reply token — e.g. web chat — has no
  such window; this rule does not apply to it.)*
- **Fallback if the channel send fails:** retry per the adapter's rule; if it
  keeps failing, alert the owner (not the customer — the customer already has
  nothing to answer).

**S7.2 — Outage path (`BUSINESS_OPERATIONS.md` §1).** When the bot cannot answer
(n8n down, model provider down):
- The customer gets the fixed fallback message: *"The shop's assistant is
  temporarily unavailable; the shop will reply as soon as possible."*
- The owner is notified; a **red event** is logged if it lasts longer than **15
  minutes** (`monitor-log`; threshold per `BUSINESS_OPERATIONS.md` §1 /
  `MONITORING.md`).
- Keep at least one alternative model per tier in routing, so a single provider
  outage switches models instead of stopping service.
- **Total outage — ND-7 resolved 2026-09-27 (Phase A, lightweight only):** use a
  free external uptime monitor (e.g. UptimeRobot or equivalent) that pings n8n
  every 1–5 minutes; if there is no answer for more than 15 minutes it alerts the
  owner **directly on the owner's alert channel** (T-071 Settings page), entirely
  outside n8n — because a watchdog that lives inside n8n cannot run when n8n is
  down. **No automatic customer fallback message during a total n8n outage in
  Phase A** — that needs a separate, more complex fallback system and is not
  built now. This limitation is accepted and recorded in
  `BUSINESS_OPERATIONS.md` §1. *(The model-provider-outage case above still gets
  its fixed customer fallback message, because n8n is still running then.)*

**Tables/tools:** `line-channel` / `web-chat-channel`; `monitor-log`; the owner
alert transport from the Settings page (T-071: Email or LINE).

---

## 8. Logging (always, after the reply is sent)

Logging must not block the customer's reply once it has been sent — but a
logging failure must raise an alert, because a lost `usage_log` row means the
quota counter drifts and the cap can be exceeded (on LINE, that risks pushing the
tenant's own account into LINE's paid tier).

**S8.1 — Conversation memory.** Append the user turn and the bot turn to
`conversations` (scoped by `tenant_id`, `bot_id`, `end_customer_id`).

**S8.2 — Usage accounting (owned by Cost Guard).** Upsert today's `usage_log`
row (scoped) and increment the **correct** counter:
- `reply` → `reply_count` — **do not** touch `push_count`.
- `push` → `push_count` — this is the counter the 200/bot/month cap reads.
- Always record `model_tokens` and `estimated_cost_thb`.
- Reply and push are counted **separately** (`LITE_SCHEMA_V1.md`,
  `PRICING_V1.md`) — a mis-mapped counter either breaks the cap or blocks free
  replies.

**S8.3 — Monitoring events.** Write `monitor-log` events for: signature failure,
unmapped identity, duplicate drop, quota warnings (80%), quota hard-stop, model
failover, pre-send check replacement, outage (red at >15 min), and logging
failure.

**S8.4 — Logging failure direction.** The customer reply is already sent and is
not retracted. Raise an alert and retain the pending usage increment for retry
so the quota counter does not drift silently.

**Tables/tools:** `conversations`, `usage_log` via `data-access` /
`memory-store` / `usage-tracker`; `monitor-log`.

---

## 9. Background / proactive path (push)

This is the **other** entry point: the bot starts a message. It never goes
through §1 (no inbound signature to verify — there is no inbound request). It
exists only as a scheduled/triggered n8n workflow (`FOUNDATION_V1.md` §8: n8n is
for scheduled work, not the default synchronous chat runtime).

**S9.1 — Trigger.** A schedule or an event (e.g. a reminder due) fires inside
n8n for a specific (`tenant_id`, `bot_id`).

**S9.2 — Quota gate (hard).** Check `bots.monthly_push_quota` via
`usage-tracker` **before** building or sending anything.
- At 80% → warn the owner.
- At the cap → **pause for the rest of the month. STOP.** Never exceed — this
  protects the tenant's own quota (`PRICING_V1.md`; on LINE, it keeps the tenant
  inside LINE's free tier).

**S9.3 — Compose + check.** Compose the proactive message; it still passes §6
(honesty/scope). It may not name a model, claim to be human, or leave the
tenant's lane.

**S9.4 — Send (proactive).** The adapter sends the proactive message through its
own channel mechanism. *(LINE case: the push API — this counts against LINE's
plan quota **and** the platform cap above. A channel with no such platform
quota, e.g. web chat, counts only against the platform cap.)*

**S9.5 — Log.** Increment `push_count` + `model_tokens` + `estimated_cost_thb`
in `usage_log`; append any created conversation turn to `conversations`.

**S9.6 — Reminder/booking specifics.** Secretary bots (`secretary-bot` in
`MCP_TOOLS_V1.md`) use this path for reminders; the booking reply itself is a
free reply, only the proactive reminder is a push.

---

## 10. Stop rules (where the flow must not continue)

| # | Condition | Action |
|---|---|---|
| 1 | Adapter authenticity check fails (LINE: signature) | Drop, do not parse, do not answer. **STOP.** |
| 2 | Destination not mapped to a tenant/channel | Reject, never guess a tenant. **STOP.** |
| 3 | `bots.status` ≠ active | Do not answer. **STOP.** |
| 4 | Scope keys (`tenant_id` + `bot_id`) cannot be established | Fail-closed; no query, no answer. **STOP.** |
| 5 | Context load fails | Outage path (§7). **STOP** answering. |
| 6 | PDPA first-contact notice cannot be sent | Do not answer the underlying question yet. **STOP** until it can. |
| 7 | Push cap reached (proactive only) | Pause proactive messages for the month. **STOP.** Replies unaffected. |
| 8 | Primary + Backup both fail | Outage path + red event. **STOP** (no endless retry). |
| 9 | Pre-send honesty/scope check cannot complete | Do not send the draft; use safe deflection/handoff. **STOP** the draft. |
| 10 | Duplicate message (already processed) | Drop. **STOP.** |

---

## 11. Tool / table map (quick reference)

| Step | MCP tool | Tables |
|---|---|---|
| Ingress, signature, identity, dedup, normalize | adapter (`line-channel` / `web-chat-channel`) | `channels`, `lite_processed_events` |
| Scope + context load | `data-access`, `memory-store` | `bots`, `end_customers`, `conversations`, `memory_summaries` |
| PDPA notice | adapter; `data-access` | `end_customers` |
| Quota gate | `usage-tracker`; `data-access` | `bots`, `usage_log` |
| Model call + tools | `chat-bot-core`, `memory-store`, `handoff-to-owner` + `enabled_tools` | — |
| Pre-send check | deterministic filter (ND-3), `handoff-to-owner`, `monitor-log` | — |
| Send reply / push | `line-channel`, `web-chat-channel`, `secretary-bot` | — |
| Log | `memory-store`, `usage-tracker`, `monitor-log` | `conversations`, `usage_log` |

**Note on table names:** `LITE_SCHEMA_V1.md` lists logical names (`bots`,
`usage_log`, …); the physical Phase A tables are the `lite_*` set with RLS
ENABLE + FORCE (`lite_bots`, `lite_usage_log`, …). The runtime always sets
`app.tenant_id` + `app.bot_id` per transaction.

---

## 12. Resolved decisions (formerly NEEDS_DECISION)

All seven open points were decided by the Project Owner on 2026-09-27. They are
recorded here and in `docs/warroom/decision-log.md` (L3 — they affect the real
runtime behaviour of the system).

| ID | Decision |
|---|---|
| **ND-1** | De-duplication uses a new `lite_processed_events` table (scoped by `tenant_id` + `bot_id`, keyed by the platform event id, short TTL), specified in `LITE_SCHEMA_V1.md`; the migration is tracked by card **T-077**. If the store is unavailable → drop the message (fail-closed). |
| **ND-2** | Over the reply quota with no top-up → the bot sends **one fixed message** pointing the customer to the shop's direct fallback contact (from `bots.business_info`), then stops answering — no model calls until top-up or a new month. Sent once, not repeated. |
| **ND-3** | The pre-send check is a **deterministic filter only** (keyword/pattern: model-name denylist, human-claim patterns, "unsure → handoff"). No second model call at this stage; an upgrade is reconsidered later with a price approval. |
| **ND-4** | The PDPA first-contact notice is **attached to the first answer** — one message, one reply. |
| **ND-5** | If the LINE reply token expires before the answer is ready → **do not auto-push** (would spend the tenant's quota); log the miss, count it against a reply-quality metric, and set a maximum wait budget per reply. |
| **ND-6** | A failed signature check returns a **non-2xx** response that does not trigger a platform retry storm, and every occurrence is logged. |
| **ND-7** | Total n8n outage: a **free external uptime monitor** (e.g. UptimeRobot) pings n8n every 1–5 min and, after more than 15 min, alerts the owner directly on the owner's alert channel — fully outside n8n. **No automatic customer fallback message** during a total n8n outage in Phase A; the accepted limitation is recorded in `BUSINESS_OPERATIONS.md` §1. |

---

## 13. Traceability

Every rule above maps to a source document. Anything **not** covered by a source
is listed in §12 as NEEDS_DECISION rather than being invented here.

| Rule in this document | Source |
|---|---|
| Signature check before parsing, drop on failure | `adapters/line-oa.md`; `INTEGRATIONS.md` #1 |
| De-duplicate on platform event id | `adapters/line-oa.md`; `INTEGRATIONS.md` #4 |
| Identity mapping, never guess | `INTEGRATIONS.md` #2 |
| Every query scoped by `tenant_id` + `bot_id` | `LITE_SCHEMA_V1.md`; `PDPA_COMPLIANCE.md` Layer 3 |
| PDPA first-contact notice | `PDPA_COMPLIANCE.md` Layer 1; `LITE_SCHEMA_V1.md` |
| Reply free/unlimited vs push capped 200/bot/month | `PRICING_V1.md`; `adapters/line-oa.md` |
| Tier by task; failover to a different-provider Backup | `MODEL_POLICY.md` |
| Answer checks (no model name, no human claim, stay in lane) | `CUSTOMER_FACING_RULES.md` rules 1, 2, 5 |
| Outage fallback message + red alert (>15 min) | `BUSINESS_OPERATIONS.md` §1 |
| `conversations` + `usage_log` (separate reply/push counts) | `LITE_SCHEMA_V1.md` |
| Tool contracts | `MCP_TOOLS_V1.md` |
| Adapter/tool failure, risk, idempotency | `FOUNDATION_V1.md` §13, §14, §16; `INTEGRATIONS.md` |

---

## 14. Adding a new channel — what changes, what must not

This is the working test of the adapter boundary (`INTEGRATIONS.md`): a new
channel must cost **one new adapter**, not a change to the core flow.

**Must NOT change when a new channel is added** (these are channel-neutral):

| Section | Why it is channel-neutral |
|---|---|
| §2 Scope + context load | reads the database, not the channel |
| §3 PDPA first-contact notice | driven by `end_customers`, not the channel |
| §4 Quota / policy gate | reads `bots`, not the channel |
| §5 Model call | model policy, not channel mechanics |
| §6 Pre-send answer check | honesty/scope rules are channel-independent |
| §8 Logging | writes `conversations` / `usage_log`, channel-neutral |

**May change (adapter surface only):**

| Section | What changes |
|---|---|
| §1 Ingress (S1.1–S1.5) | a new adapter: its own endpoint, its own authenticity check, identity mapping, event id, normalization |
| §7 Send reply / §9 proactive send | the adapter's own send mechanism (S9 uses the same adapter) |
| §0 vocabulary notes / §11 tool–table map | optionally, the new channel's economics as a *note*, and one adapter row |

**Test — adding `web_chat` (planned in Step 3):** it should touch only **§1 and
§7/§9** (the adapter surface) — **core sections §2–§8 stay unchanged**. If a
change is needed anywhere else, platform detail has leaked into the core, and
that leak is the bug (not the new channel).