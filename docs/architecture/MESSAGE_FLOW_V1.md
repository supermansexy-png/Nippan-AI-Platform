# Message flow v1 — from customer message to bot reply

Status: **DRAFT — for Owner review** (2026-09-27)
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
| **reply** | The bot answering a message the customer sent first. Uses LINE's reply token. Delivery is **free and unlimited**; the platform's only cost is the model call. |
| **push** | The bot starting a message (e.g. a reminder). Counts against `bots.monthly_push_quota` — **platform cap 200/bot/month**, below LINE's own free-plan ceiling. |

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

**S1.1 — Receive.** The adapter accepts the platform webhook over HTTPS
(LINE: `POST` to the LINE channel endpoint).

**S1.2 — Verify authenticity (MANDATORY, FIRST, BEFORE PARSING).**
- LINE: verify `x-line-signature` = `base64(HMAC-SHA256(channel_secret, raw_body))`
  computed over the **raw request body bytes**, checked **before** the body is
  parsed as JSON (`adapters/line-oa.md`; `INTEGRATIONS.md` "What every adapter
  must do" #1).
- The channel secret always comes from the credential store
  (`channels.credential_ref` → n8n credentials), never from the database, never
  from the request.
- **If verification fails → drop the request. Do not parse it, do not answer, do
  not continue.** Write a `monitor-log` event. **STOP.**
- *(Minor open point — ND-6: HTTP status returned on a failed signature.)*

**S1.3 — De-duplicate.** Platforms retry; the same message must never be answered
twice. Drop on the platform's event id (`webhookEventId` for LINE; `message_id`
in the normalized format) (`adapters/line-oa.md`).
- **Fallback:** if the dedup store is unavailable, treat the message as a
  duplicate and drop it (answering twice is worse than answering once) and raise
  an alert. *(ND-1: the dedup store is not defined in `LITE_SCHEMA_V1.md`.)*

**S1.4 — Map identity (never guess).** `destination` (bot user id) → the
`channels` row → `tenant_id` + `bot_id`; `source.userId` →
`end_customers.external_user_ref`, scoped to that tenant (`adapters/line-oa.md`).
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
- *(ND-4: whether the notice is a separate message or attached to the first
  answer — design choice, not yet stated in a source.)*

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
confirm after the first real tenants). This bounds **model calls**, not LINE
delivery (LINE reply delivery is free and unlimited).
- At **80%** → warn the owner (yellow, `MONITORING.md`).
- Over quota → **never let the bot go silent mid-conversation**, and **never
  silently downgrade the model without telling the owner** (`PRICING_V1.md`
  "Over quota"). *(ND-2: the exact behavior at 100% reply quota with no top-up.)*

**S4.3 — Check the push cap (proactive path only).** Cap =
`bots.monthly_push_quota` (default 200/bot/month, set below LINE's free-plan
ceiling as a safety margin).
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
**Speed matters on LINE** — a smarter-but-slow model is the wrong choice for chat
replies.

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
- *(ND-3: **how** the check is implemented — a deterministic filter (model-name
  denylist + human-claim patterns) versus an extra policy/checker model call that
  also judges "off-topic"; the second option adds cost and latency and needs
  approval under `MODEL_POLICY.md`.)*

**Tables/tools:** pre-send checker (TBD per ND-3); `handoff-to-owner`;
`monitor-log`.

---

## 7. Send reply + outage path

**S7.1 — Send.** The adapter sends the checked answer.
- LINE `reply` uses the reply token: **free and unlimited**. Reply tokens are
  **short-lived** (`adapters/line-oa.md`) — the answer must be produced inside
  that window.
- **Fallback if the reply token has expired:** the answer cannot be sent as a
  reply. Do not silently convert it to a push (that spends the tenant's quota).
  *(ND-5: behavior when the reply token expires before the answer is ready.)*
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
- *(ND-7: a **total** n8n outage means no code path inside n8n can send the
  fallback or the red alert — an edge/watchdog path is required. Not yet defined
  in a source.)*

**Tables/tools:** `line-channel` / `web-chat-channel`; `monitor-log`; the owner
alert transport from the Settings page (T-071: Email or LINE).

---

## 8. Logging (always, after the reply is sent)

Logging must not block the customer's reply once it has been sent — but a
logging failure must raise an alert, because a lost `usage_log` row means the
quota counter drifts and could push a tenant into LINE's paid tier.

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
  protects the tenant's own LINE free tier (`PRICING_V1.md`).

**S9.3 — Compose + check.** Compose the proactive message; it still passes §6
(honesty/scope). It may not name a model, claim to be human, or leave the
tenant's lane.

**S9.4 — Send (push).** Send via the LINE push API (or web chat). This counts
against LINE's plan quota and the platform cap.

**S9.5 — Log.** Increment `push_count` + `model_tokens` + `estimated_cost_thb`
in `usage_log`; append any created conversation turn to `conversations`.

**S9.6 — Reminder/booking specifics.** Secretary bots (`secretary-bot` in
`MCP_TOOLS_V1.md`) use this path for reminders; the booking reply itself is a
free reply, only the proactive reminder is a push.

---

## 10. Stop rules (where the flow must not continue)

| # | Condition | Action |
|---|---|---|
| 1 | LINE signature verification fails | Drop, do not parse, do not answer. **STOP.** |
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
| Ingress, signature, identity, dedup, normalize | adapter (`line-channel` / `web-chat-channel`) | `channels` |
| Scope + context load | `data-access`, `memory-store` | `bots`, `end_customers`, `conversations`, `memory_summaries` |
| PDPA notice | adapter; `data-access` | `end_customers` |
| Quota gate | `usage-tracker`; `data-access` | `bots`, `usage_log` |
| Model call + tools | `chat-bot-core`, `memory-store`, `handoff-to-owner` + `enabled_tools` | — |
| Pre-send check | (TBD per ND-3), `handoff-to-owner`, `monitor-log` | — |
| Send reply / push | `line-channel`, `web-chat-channel`, `secretary-bot` | — |
| Log | `memory-store`, `usage-tracker`, `monitor-log` | `conversations`, `usage_log` |

**Note on table names:** `LITE_SCHEMA_V1.md` lists logical names (`bots`,
`usage_log`, …); the physical Phase A tables are the `lite_*` set with RLS
ENABLE + FORCE (`lite_bots`, `lite_usage_log`, …). The runtime always sets
`app.tenant_id` + `app.bot_id` per transaction.

---

## 12. Open points — NEEDS_DECISION

These are places where the existing source documents do not specify the
behavior. **Not guessed** — each needs an Owner decision before it is built.

| ID | Question | Why it matters | Suggested default (for the Owner to accept or change) |
|---|---|---|---|
| **ND-1** | Where is the de-duplication store for `webhookEventId` / `message_id`? `LITE_SCHEMA_V1.md` defines no table for processed events. | Without it, a platform retry can double-answer (and double-charge a model call). | Add a small `lite_processed_events` table (scoped by `tenant_id`/`bot_id`, keyed by event id, with a short TTL). Fail-closed: if unavailable, drop the message. |
| **ND-2** | At 100% of the reply quota with no top-up, what does the bot do? `PRICING_V1.md` says "never go silent mid-conversation" and "never silently downgrade", but not the actual behavior. | Directly affects tenant cost exposure and the "never silent" guarantee. | Continue answering until the owner is warned and either tops up or explicitly accepts the overage; do not downgrade silently. Needs the Owner's ceiling. |
| **ND-3** | How is the pre-send check implemented — deterministic filter only, or an extra policy/checker model call that also judges "off-topic"? | A checker model adds cost/latency per message and needs approval under `MODEL_POLICY.md`; a deterministic filter is cheap but only catches name/human-claim patterns. | Start deterministic (denylist + human-claim patterns + explicit "unsure → handoff"); add a checker model only if measurements show it is needed. |
| **ND-4** | Is the PDPA first-contact notice a separate message or attached to the first answer? | Affects the first customer experience; both satisfy the notice requirement. | Attach the short notice to the first answer (one message, one reply). |
| **ND-5** | What happens when the LINE reply token expires before the answer is ready? | The answer cannot be sent as a free reply; converting to a push spends the tenant's quota. | Do not auto-push. Log the miss and count it against a quality metric; define a maximum wait budget per reply. |
| **ND-6** | What HTTP status is returned on a failed signature check? | Affects whether the platform retries a rejected request and how attacks are logged. | Acknowledge with a non-2xx that does not trigger a retry storm; log every occurrence. |
| **ND-7** | Who sends the fallback message and the red alert during a **total** n8n outage? | If n8n is fully down, nothing inside n8n can send either one — an edge/watchdog path is required. | Add a thin edge/watchdog path (e.g. Cloudflare Worker) that owns the outage fallback + alert; to be scoped in its own card. |

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