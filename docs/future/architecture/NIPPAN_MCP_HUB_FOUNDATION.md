# Nippan MCP Hub Foundation

Status: Phase 0 — Foundation started

## Objective

Create a single MCP gateway layer for Nippan AI Platform so AI clients and agents can access approved tools through one controlled interface.

## Problem

Current workflow requires opening different environments to access different tools. MCP Hub provides a common connection point.

## Target Architecture

```text
AI Clients
(ChatGPT / OpenCode / Other Agents)
              |
              v
       Nippan MCP Hub
              |
  ---------------------------
  |       |        |         |
GitHub OpenRouter Supabase  Nippan Tools
              |
              v
      Audit + Policy Layer
```

## Initial MCP Servers

### Phase 0

- GitHub MCP
- OpenRouter MCP
- Supabase MCP

### Future

- Cloudflare
- Render
- Google Drive
- n8n
- Analytics
- Internal Nippan services

## Design Principles

- One connection point
- Least privilege access
- Agent-specific scopes
- Auditable actions
- Human approval for destructive operations
- Modular expansion

## Milestones

- [ ] Repository structure finalized
- [ ] MCP registry design
- [ ] Authentication model
- [ ] Tool permission model
- [ ] First MCP adapter
- [ ] War Room integration
