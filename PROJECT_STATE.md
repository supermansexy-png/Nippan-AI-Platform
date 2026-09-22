# Project State

Updated: 2026-09-22

## Phase

FOUNDATION / ARCHITECTURE REVIEW

## Current objective

Agree on a stable platform foundation before implementation.

## Completed in planning

- Chosen OpenRouter as the intended model gateway.
- Chosen n8n as the main orchestration layer.
- Chosen PostgreSQL + pgvector as the preferred initial data/memory foundation.
- Identified Cloudflare Workers, Queues, R2, Analytics Engine as likely useful infrastructure.
- Identified Context Compiler as an optimization layer for long/ambiguous context.
- Defined the need for model tiers, fallbacks and reviewer escalation.
- Inspected current private repository `supermansexy-png/Ai-Nippan`.
- Confirmed the existing customer bot must remain independent until the new core is stable.

## In review

- Exact responsibility boundaries between Worker, n8n, Nippan MCP and application services.
- Exact model policy and benchmark methodology.
- Memory v2 schema and retrieval policy.
- Cloudflare component selection and cost/complexity tradeoffs.
- Observability schema.
- Migration adapter contract for Ai-Nippan.
- Multi-agent development workflow.

## Not started

- Production database deployment
- OpenRouter production presets
- Context Compiler implementation
- Cloudflare gateway implementation
- Memory migration
- Personal assistant migration
- Slip bot implementation
- Nippan customer bot migration

## Protected systems

- `supermansexy-png/Ai-Nippan` production code: DO NOT MODIFY from this proposal.
- Existing LINE personal assistant/n8n workflows: do not migrate until Foundation v1 is accepted.

## Immediate next step

Collect two independent AI architecture reviews using `AI_REVIEW_BRIEF.md`, then consolidate disagreements into Foundation v1 decisions.
