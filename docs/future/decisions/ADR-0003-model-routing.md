# ADR-0003 — Model Routing and Context Policy

Status: Accepted  
Date: 2026-09-22

## Decision
Use OpenRouter as the primary model gateway with central model policies. Build deterministic context assembly first. Context Compiler is optional and benchmark-gated.

## Context
A model call before every main model call adds latency, cost and information-loss risk.

## Consequences
- Model IDs are configuration, not hard-coded throughout applications.
- Raw user request is always retained.
- Privacy class is enforced before provider/model selection.
- Cloudflare AI Gateway is deferred until a benchmark shows clear value.
