# War Room V1 — Dual-Use Positioning

Status: **ACTIVE**
Date: 2026-09-24
Related: `docs/proposals/WAR_ROOM_V1_PROPOSAL.md`, Issue #30, T-011

## What is the War Room?

The Nippan AI War Room is a controlled multi-agent discussion environment where
specialist AIs collaborate on tasks while a human owner remains in charge.

It uses bounded turns (no infinite loops), token/cost hard limits, and
owner-interruptible sessions. Formal independent audits remain separate and
cannot be replaced by War Room consensus.

## Use Case ① — Dev-Time (NOW)

The War Room is used by the internal AI development team for project work:

- **Project discussions**: Owner watches specialist AIs (Architect, Builder,
  Security, Cost & Ops, Auditor) discuss technical decisions, present evidence,
  surface conflicts, and produce actionable outcomes.
- **Owner control**: Owner can interrupt at any time, ask all/one role, pause/stop
  the room, or make direct decisions. Unresolved items become `NEEDS_OWNER_DECISION`.
- **Action tracking**: Discussions produce durable decisions, findings, and
  action items recorded in the repository.
- **Learning mechanism**: Disagreements between specialists are visible and
  tracked — builder claims get challenged by security/architect — improving
  quality without hidden biases.

**Why it matters:** The War Room lets multiple AI models work together on the
project without any single model being the sole authority. The owner retains
full control while benefiting from parallel specialist analysis.

## Use Case ② — Runtime Backstage Ecosystem (FUTURE)

When tenants' bots are live on the platform, the War Room will serve as a
backstage collaboration layer:

- **Tenant agent teams**: A tenant's agents can discuss and coordinate on complex
  tasks within their own tenant-scoped room (tenant isolation enforced).
- **Platform governance**: Platform-level agents (Auditor, Cost Guard, Router)
  can observe cross-tenant patterns without accessing individual tenant data.
- **Escalation path**: When an agent encounters ambiguity, it can "ask" the
  War Room for multi-agent analysis rather than guessing or overclaiming.
- **Audit trail**: Every collaboration session produces durable records that
  survive beyond the conversation itself.

**Design constraint:** Tenant rooms are fully isolated — no cross-tenant data
leakage. Platform-wide rooms operate at aggregation/summary level only. The
War Room must never expose raw customer conversation content outside the
tenant's scope.

## Non-Goals (unchanged from original proposal)

The War Room does NOT provide:

- Autonomous infinite agent loops
- AI majority-rule governance
- Autonomous production changes
- Independent approval of high-risk actions
- Full SaaS multi-customer collaboration
- Voice/video meetings
- Arbitrary external tool execution
- A replacement for the formal Independent Audit System

These non-goals remain fixed regardless of which use case is active.

## Current State

Increment C progress: 13/16 (81.25%) audit-accepted. Track D (D-01/D-02/D-03)
remains for final acceptance. Independent Audit gates are suspended per owner
decision (2026-09-24) but the architectural design constraints above remain.
