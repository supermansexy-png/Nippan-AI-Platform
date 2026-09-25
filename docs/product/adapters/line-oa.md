# Adapter: LINE Official Account

Kind: Channel · Status: building (Phase A Step 1) · Risk: L2

- Auth: verify `x-line-signature` = base64(HMAC-SHA256(channel secret, raw body)) before parsing
- Identity: LINE `destination` (bot user id) → `channel_id`; `source.userId` → `end_customer_ref`
- Reply: reply token, short validity; free and unlimited
- Proactive: push API; counts against LINE plan quota; platform cap 200/bot/month
- Duplicates: de-duplicate on `webhookEventId`
- Content supported: text, image, sticker, location, quick replies, flex messages
- Credentials: channel secret + access token in n8n credentials; `channels.credential_ref` only
- Cost model: free delivery for replies; push within tenant's free LINE quota
