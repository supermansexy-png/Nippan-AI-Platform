# Independent AI Review Brief

You are reviewing a proposed architecture for **Nippan AI Platform**.

Do not merely agree with the proposal. Treat this as a pre-implementation architecture review.

## Read first

1. `README.md`
2. `docs/architecture/FOUNDATION_DRAFT.md`
3. `ROADMAP.md`
4. `PROJECT_STATE.md`
5. `AGENTS.md`
6. `.ai/project.yaml`

The current production repository `supermansexy-png/Ai-Nippan` exists and has already been inspected by the primary architect. It must not be modified during this review.

## Review objectives

Analyze whether the proposal is a good long-term foundation for:
- multiple AI bots
- multiple model providers through OpenRouter
- Thai conversational continuity
- long/short-term memory
- tool/MCP execution
- low cost
- easy maintenance
- future bot additions
- safe integration of the existing Nippan customer bot

## Challenge these specific assumptions

1. Is PostgreSQL + pgvector the right initial combined data/memory store?
2. Is n8n the correct orchestration boundary, or is too much/too little placed there?
3. Is a cheap Context Compiler likely to reduce total cost without harming intent fidelity?
4. Are Worker + Queues + R2 the right Cloudflare components?
5. Is Cloudflare AI Gateway redundant in front of OpenRouter, or is there enough value to justify it?
6. Are we duplicating functionality unnecessarily between Cloudflare/OpenRouter/n8n/PostgreSQL?
7. Is the Maker/Reviewer escalation policy efficient enough?
8. How should memory consistency, expiration, contradiction and provenance work?
9. What is missing for multi-bot isolation/security/privacy?
10. What migration risks exist for `Ai-Nippan`?
11. What would become a bottleneck at 10x message volume?
12. What parts are over-engineered for current scale?
13. What should be changed before implementation begins?

## Required response format

### 1. Executive assessment
Short summary of the architecture quality and the biggest concern.

### 2. Keep
What should remain unchanged and why.

### 3. Change
Concrete architecture changes, with reasons.

### 4. Remove / defer
Anything over-engineered, duplicated or premature.

### 5. Missing
Important components not currently addressed.

### 6. Cost review
Where unnecessary AI/model/cloud cost may occur and how to reduce it.

### 7. Data & memory review
Correctness, consistency, privacy, retention and retrieval concerns.

### 8. Reliability review
Queueing, retries, idempotency, fallback, degraded modes and recovery.

### 9. Security review
Isolation, credentials, sensitive data, tool permissions and audit requirements.

### 10. Existing bot migration review
How to integrate Ai-Nippan with minimum risk.

### 11. Proposed revised architecture
Provide a concise architecture if you recommend changes.

### 12. Top 10 decisions before coding
Rank the ten architecture decisions that should be resolved first.

### 13. Confidence and uncertainties
State which conclusions depend on missing measurements or code details.

Do not implement anything. This round is analysis only.
