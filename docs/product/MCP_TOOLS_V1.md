# MCP tools — Phase A starting set

Status: **ACTIVE — Phase A**

## Principle

Each tool is a small, independent capability. Adding one never requires
changing the core n8n routing or another tool. A new customer segment is
usually a new tool, or a new combination of existing ones — not a new system.

In Phase A a "tool" may be an n8n sub-workflow exposed through n8n's MCP
support, or a plain n8n sub-workflow called directly. What matters is the
contract (name, input, output, permission scope, cost), not the transport.

## Starting catalog

| Tool | Does | Used by | Build step |
|---|---|---|---|
| `data-access` | The only path to the database; every call requires `tenant_id` + `bot_id` | Every other tool | Step 0 |
| `usage-tracker` | Logs reply/push counts, tokens, cost per bot; enforces the 200/month push cap | Cost Guard | Step 0 |
| `monitor-log` | Writes events to the monitoring log; sends red alerts | All workflows | Step 0 |
| `line-channel` | Receives + replies to LINE OA messages (free, uses reply token) using the tenant's own channel credentials | Bots on LINE | Step 1 |
| `chat-bot-core` | Answers end customers from business info + memory | All bot types | Step 1 |
| `memory-store` | Reads/writes the 4 memory layers | All bot types | Step 1 |
| `web-fetch` | Reads the tenant's own website pages | Onboarding | Step 1 |
| `file-reader` | Reads PDF/Excel/image menus and price lists | Onboarding | Step 1 |
| `handoff-to-owner` | Notifies the business owner when the bot should not answer alone | All bot types | Step 1 |
| `secretary-bot` | Bookings + reminders. Reminders are LINE push messages against `bots.monthly_push_quota` (200/month cap) — booking replies themselves are free reply messages | Secretary bots | Step 3 |
| `web-chat-channel` | Chat widget for the storefront demo and tenant websites | Storefront, tenants | Step 3 |

## Adding a new tool

1. Task card created (`docs/warroom/TASK_CONTROL.md`)
2. MCP tool builder builds it with name, scope, per-call cost estimate
3. Cost Guard checks the cost estimate
4. Auditor checks isolation, honesty rules, quality
5. Project Lead approves go-live; Decision Log entry

Removing a tool goes through Project Lead — a tenant may depend on it.
