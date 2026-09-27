# Adapter: Web chat

Kind: Channel · Status: building (T-079a, Phase A Step 3 groundwork) · Risk: L2

- Implementation: `services/core/app/web_chat/` (adapter + tests + e2e proof script)
- Auth: per-channel auth key bound to the tenant's channel row; key stored
  only as a SHA-256 digest and compared constant-time (`hmac.compare_digest`).
  The cleartext key never enters the core. Web chat has no platform-side
  signature scheme like LINE — the bound key is the authenticity gate.
- Identity: the registered key → (`tenant_id`, `bot_id`, `channel_id`) via
  `ChannelMappingRecord`; unmapped requests are rejected, never guessed.
- Reply: web chat has no LINE-style reply token; `reply_handle` = the
  visitor ref, valid for the same open chat session.
- Proactive: in Phase A only in-session replies (`kind: reply`); proactive
  push is not built (card's smallest correct change).
- Duplicates: de-dup on `(tenant_id, channel_id, message_id)` via the
  injectable `DedupeStore` (ND-1); in-memory sliding-window in Phase A preview,
  Postgres-backed `lite_processed_events` swaps in via the same interface
  (card T-077).
- Content supported: text. Other parts are rejected fail-closed inbound and
  degrade to text outbound — the core never learns which.
- Credentials: per-channel key digest lives in the mapping record; no secret
  is stored in the database (`channels.credential_ref` rule respected).
- Cost model: free delivery; cost is the model call only.
- Observability: usage → `usage-tracker` sink; events/errors →
  `monitor-log` JSONL sink (`docs/product/INTEGRATIONS.md` duty 6).
- Known limits: single-instance in-memory dedupe resets on restart; content
  parts beyond `text` arrive in a later card if demanded by real usage.
