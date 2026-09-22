# Nippan AI Platform

Status: **Foundation v1 accepted — Phase 2 starting from frozen contracts**

Nippan AI Platform is the shared AI platform for Nippan's bots, website AI, future applications/programs, internal agents and potential external/rental AI services.

## Foundation principles

- easy to operate
- easy to debug end to end
- high-performance realtime path
- cost-efficient by default
- flexible and extensible
- safe multi-tenant/tool isolation
- add complexity only when measured need justifies it

## Product model

```text
Tenant
  -> Workspace
      -> Application
          -> Agent
          -> Channel
          -> AgentChannelBinding
          -> Conversation
```

An Agent is a configurable role, not the same thing as a bot. Agents and Channels are Application-owned peers connected by explicit bindings.

## Foundation v1 architecture

```text
Channels / Website / Apps / Bots
              |
      Cloudflare Worker
   thin edge / request_id
              |
              v
       FastAPI Core AI Service
      /        |         \
 Context     Policy     OpenRouter
 Memory      Engine       Models
      \        |         /
              v
          Nippan MCP
              |
      PostgreSQL + pgvector
              |
       External systems

Background: Cloudflare Queues + n8n
Files: R2
Human docs: Google Drive
Reports/exports: Google Sheets
Control Plane: versioned Dashboard/Admin Center
```

## Key decisions

- PostgreSQL is the operational source of truth.
- pgvector supports semantic memory/RAG; retrieval is hybrid.
- OpenRouter is the primary model gateway.
- FastAPI is the realtime Core runtime.
- n8n handles background, schedules and integrations rather than every realtime chat turn.
- Cloudflare Workers remain a thin deterministic edge gateway.
- Context Compiler is conditional and benchmark-gated, not default.
- risk/privacy/tool permissions are enforced in deterministic policy/code.
- Nippan MCP is modular with per-Agent scopes.
- destructive/financial actions support human approval.
- control plane and runtime data plane are separated.
- existing Ai-Nippan stays independent until adapter-based gradual migration.

## Start here

1. `docs/architecture/FOUNDATION_V1.md`
2. `PROJECT_STATE.md`
3. `ROADMAP.md`
4. `.ai/project.yaml`
5. `AGENTS.md`
6. `docs/decisions/`

## Current work

Phase 2: **PostgreSQL/RLS design and Core Runtime Skeleton**

Phase 1 contracts are frozen at Markdown/JSON Schema level. Current work is translating those contracts into PostgreSQL/RLS design, reproducible migrations, isolation tests and the minimal FastAPI Core runtime skeleton before deploying production infrastructure.

## Protected production systems

- `supermansexy-png/Ai-Nippan`
- existing Personal Assistant / n8n production workflows

Do not migrate or rewrite them during the current phase.
