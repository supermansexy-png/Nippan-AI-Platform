# Nippan MCP Hub Roadmap

## Phase 0 — Foundation

Goal: create the shared tool gateway architecture.

Deliverables:
- MCP Hub architecture document
- server registry design
- agent permission model
- audit/event logging design

## Phase 1 — Core Connectors

Priority MCP connectors:

1. GitHub MCP
2. OpenRouter MCP
3. Supabase MCP
4. Nippan internal services MCP

Requirements:
- scoped permissions
- request tracing
- error handling
- usage tracking

## Phase 2 — War Room Integration

Connect MCP Hub with:
- Project Lead agent
- Developer agent
- Auditor agent
- Decision log

## Phase 3 — Production Platform

Add:
- Cloudflare
- Render
- Google Drive
- n8n
- monitoring
- dashboards

All production migration must be incremental and preserve existing systems.
