# ADR-0005 — Policy, MCP Tools and Approval

Status: Accepted  
Date: 2026-09-22

## Decision
Enforce tool permissions, risk classes, privacy gates and side-effect controls in deterministic policy/code. Use modular Nippan MCP domains with explicit per-Agent allowlists.

## Context
LLMs must not be allowed to self-classify destructive actions as safe or gain capabilities through prompts.

## Consequences
- Tool/action risk is statically mapped.
- All tool arguments are schema validated.
- Side effects require idempotency and audit records.
- AI reviewer is risk/uncertainty-triggered, not universal.
- Destructive/financial actions can require human approval.
