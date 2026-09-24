# ADR-0006 — Infrastructure Simplicity

Status: Accepted  
Date: 2026-09-22

## Decision
Start with Workers, Queues, R2, FastAPI, PostgreSQL+pgvector, OpenRouter, Nippan MCP and n8n. Defer infrastructure that does not solve a measured problem.

## Deferred
- Cloudflare AI Gateway
- Hyperdrive
- Durable Objects
- Analytics Engine
- Redis
- D1
- Vectorize
- Cloudflare Workflows
- Kubernetes
- unnecessary microservices

## Consequences
The v1 system stays understandable and inexpensive while retaining adapter points for future technology.
