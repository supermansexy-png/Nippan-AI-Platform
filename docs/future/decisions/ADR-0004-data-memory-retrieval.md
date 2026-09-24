# ADR-0004 — Data, Memory and Retrieval

Status: Accepted  
Date: 2026-09-22

## Decision
Use PostgreSQL as operational source of truth and pgvector for semantic retrieval. Use hybrid retrieval rather than vector-only search.

## Context
The platform needs transactional business data, conversational state and semantic memory while remaining simple to operate.

## Consequences
- Structured/exact facts outrank semantic memory.
- Memory stores provenance, confidence, verification, expiry and conflict/supersession metadata.
- Keyword/trigram and structured lookup complement vector similarity.
- D1, Vectorize and a dedicated vector database are deferred.
