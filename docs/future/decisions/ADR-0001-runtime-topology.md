# ADR-0001 — Runtime Topology

Status: Accepted  
Date: 2026-09-22

## Decision
Use a thin Cloudflare Worker at ingress and a FastAPI Core AI Service for realtime application logic. Keep n8n outside the default synchronous chat hot path.

## Context
The original draft placed too many layers in the normal message path. Independent reviews consistently identified latency, failure-surface and debugging risks.

## Consequences
- Worker remains simple and deterministic.
- Core runtime is normal code with tests/version control.
- n8n remains available for automation/background workflows.
- One additional service must be deployed and monitored.
