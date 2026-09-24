# MCP tools — Phase A starting set

Status: **ACTIVE — Phase A**

## Principle

Each tool is a small, independent capability. Adding a new one never
requires touching the core n8n routing or another tool's code. This is
what makes "add a new customer segment" cheap: usually it's a new tool or
a new combination of existing ones, not a new system.

## Starting catalog

| Tool | Does | Used by |
|---|---|---|
| `chat-bot-core` | General chat responses for end customers | All bot types |
| `secretary-bot` | Appointment booking, reminders | Secretary-type tenants |
| `web-fetch` | Pulls content from a URL | Onboarding assistant |
| `file-reader` | Reads PDF/Excel/image content | Onboarding assistant |
| `memory-store` | Reads/writes the 4-layer memory (see
  `docs/data/LITE_SCHEMA_V1.md`) | All bot types |
| `usage-tracker` | Logs message count/cost per tenant | Cost Guard |

## Adding a new tool

1. MCP tool builder role builds it, registers name/capability/permission
   scope, and estimates per-call cost
2. Cost Guard reviews the cost estimate
3. Auditor reviews before it reaches a real customer
4. Project Lead approves activation

Removing a tool always goes through Project Lead — a tenant may depend on
it even if usage looks low.
