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

Independent Audit through OpenRouter/Claude Opus is currently paused.

Do not restart Independent Audit unless explicitly instructed by Project Owner.

## Governance

Normal CI, testing, review, and security verification continue even while
Independent Audit is paused.

Major architecture changes require evidence and Project Owner decision.
