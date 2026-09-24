# Nippan AI Operating System Roadmap v2

## Decision

Adopt a staged foundation-first approach.

The project will not build all AI OS components simultaneously. The priority is to establish a stable core that can support future expansion.

## Phase 0 — MCP Foundation

Goals:
- MCP Gateway foundation
- Tool Registry
- Permission model
- Audit logging
- Project memory foundation

## Phase 1 — Tool + Governance Layer

Goals:
- Connect core tools
- Standardize authentication
- Track usage and events
- Establish security boundaries

Initial tools:
1. GitHub
2. OpenRouter
3. Supabase
4. Cloudflare
5. Render
6. Google Drive
7. n8n

## Phase 2 — Agent System

Goals:
- Agent roles
- Agent scopes
- Tool assignment
- Controlled autonomy

## Phase 3 — War Room

Goals:
- AI team collaboration
- Decision log
- Task tracking
- Audit visibility

## Phase 4 — Full AI Operating System

Goals:
- Complete orchestration
- Memory system
- Policy engine
- Dashboard/control plane

## Architecture Principles

- Keep existing production systems independent during migration.
- Use adapters instead of rewrites.
- Separate runtime data plane and control plane.
- Record major decisions.
- Expand complexity only after foundation is proven.
