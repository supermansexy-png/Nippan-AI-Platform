# Nippan AI Platform — Foundation Proposal

Status: **DRAFT FOR MULTI-AI REVIEW**  
Date: 2026-09-22  
Purpose: define the shared foundation before implementation. This proposal must not modify the current production bot.

## Why this project exists

Nippan is moving from several independent bots/workflows toward a shared AI platform that can support:
- Personal LINE assistant
- Existing Nippan customer-service bot (future migration only after the core is stable)
- Slip collector/report bot
- Future business bots and internal agents without redesigning the core each time

The platform must prioritize:
1. Natural Thai conversation and continuity
2. Low operating cost
3. Safe model/tool routing
4. Durable memory and data ownership
5. Easy addition of new bots
6. Clear observability and auditability
7. Multi-AI development with explicit handoffs and review

## Core design direction

```text
Channels / Bots
      |
Cloudflare Edge Gateway
      |
n8n Orchestration
      |
Context + Memory Retrieval
      |
Context Compiler (only when useful)
      |
OpenRouter Model Router
      |
Worker / Specialist AI
      |
Reviewer for risky or uncertain work
      |
Nippan MCP / Tools
      |
PostgreSQL + pgvector / R2 / External Systems
```

## Strong current decisions

- OpenRouter is the primary model gateway.
- n8n remains the primary orchestration layer.
- PostgreSQL is planned as the main system-of-record database for the new platform.
- pgvector is planned for semantic memory/RAG so transactional and vector data can coexist initially.
- Cloudflare Workers is planned as the external gateway layer.
- Cloudflare Queues is planned for durable/background workloads.
- Cloudflare R2 is planned for machine-oriented file storage.
- Google Drive remains useful for human-facing/shared documents.
- Google Sheets becomes a reporting/export surface, not the primary database.
- Existing production bot `supermansexy-png/Ai-Nippan` must not be rewritten during foundation work.
- Existing bot migration will be via adapters after the new core is stable.

## Important design principle: cheap intelligence before expensive intelligence

The platform should not send full conversation history and all memory to a strong model by default.

Preferred path:

```text
Raw message
  -> deterministic prechecks
  -> targeted memory retrieval
  -> optional cheap Context Compiler
  -> compact Task Packet
  -> task-appropriate model
  -> tool execution
  -> reviewer only when risk/uncertainty requires it
```

The original user message must remain available to the main worker so a compiler cannot silently change intent.

## Model policy direction

Model names are **candidates, not permanent architecture**. They must be benchmarked on Nippan's own Thai tasks.

Target tiers:
- T0: free / ultra-cheap routing for low-risk data
- T1: cheap daily model for chat, extraction, summaries, memory processing
- T2: reliable tool-capable model for actions
- T3: specialist model for vision, coding, multimodal, research
- T4: premium reasoner/reviewer only when escalation is justified

Model identifiers should live in central policy/presets, never be hard-coded throughout workflows.

## Data classification

At minimum:
- PUBLIC / LOW RISK
- INTERNAL
- PII
- FINANCIAL / CUSTOMER
- SECRET / CREDENTIAL

Free-provider routing must not receive sensitive customer/financial data by default.

## Current production system relationship

The current Nippan customer bot already has useful components:
- FastAPI + LINE
- Gemini integration
- Cloudflare AI Gateway support
- intent routing
- WooCommerce product/order logic
- Firestore chat/admin memory
- lexical retrieval
- per-user in-process dispatching
- dead-letter metadata
- Control Center
- tests

This proposal treats that bot as an existing application to integrate later, not code to replace now.

## Review status

This document is intentionally architectural rather than implementation-complete.
Two independent AI reviewers should analyze this proposal before the team freezes Foundation v1.

See:
- `ARCHITECTURE_DRAFT.md`
- `ROADMAP.md`
- `AGENTS.md`
- `AI_REVIEW_BRIEF.md`
- `.ai/project.yaml`
