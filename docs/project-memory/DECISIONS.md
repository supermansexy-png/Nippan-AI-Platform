# Nippan AI Platform — Durable Decisions

## Authority

- พี่เชษ is Project Owner and final decision maker.
- ChatGPT is Project Lead / Lead Architect / Project Chair.
- Specialist AI models provide implementation, review, research, or challenge.
- Specialist AI models do not independently redefine architecture.
- Important unresolved decisions use NEEDS_OWNER_DECISION.

## Evidence

Repository/runtime evidence is stronger than summaries or AI claims.

Inspect before changing.

Do not claim success without evidence.

## Architecture

GitHub is the central source of code and project-change history.

Supabase PostgreSQL is used for the platform database.

Do not create duplicate infrastructure before checking what already exists.

## Production Protection

Ai-bot-Nippan production must not be changed without explicit authorization.

## War Room

Remote War Room access must remain fail-closed.

No unauthenticated public bypass is acceptable.

## AI and Cost

Use models/tools according to the task.

Avoid unnecessary paid-model calls.

Independent Audit System (progress gates + paid auditor) is SUSPENDED by
Project Owner (2026-09-24). Historical audit records are preserved.
Do not restart it unless explicitly instructed by Project Owner.

## War Room

War Room V1 work is RESUMED by Project Owner (2026-09-24) for:
1. dev-time use in AI team workflow
2. future runtime backstage ecosystem for AI

Track D and onward proceed under normal task cards; audit gates no longer
block.

## Governance

Normal CI, testing, review, and security verification continue even while
Independent Audit is paused.

Major architecture changes require evidence and Project Owner decision.
