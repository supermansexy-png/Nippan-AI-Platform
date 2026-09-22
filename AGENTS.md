# AI Collaboration Protocol

This file defines how any AI working on Nippan AI Platform must behave.

## Required reading order

Before proposing or changing anything:
1. `README.md`
2. `.ai/project.yaml`
3. `PROJECT_STATE.md`
4. `ROADMAP.md`
5. `docs/audits/AUDIT_SYSTEM_V1.md`
6. Relevant architecture/decision documents
7. Assigned task or review brief

## Work rules

- Do not modify the production Nippan customer bot while reviewing this proposal.
- Do not put secrets, API keys, tokens, passwords, customer PII, or production credentials in the repository.
- Do not hard-code model names in distributed application logic. Use model policy/presets/config.
- Prefer a single source of truth for each data domain.
- Separate conversation memory, long-term semantic memory, structured business records, and files.
- Preserve the original user request when a Context Compiler is used.
- Do not send full history/catalog/data sets to a model when retrieval can select only relevant context.
- Expensive/reliable models should be escalation paths, not the default for all tasks.
- A worker model must not be the sole approver of high-risk/destructive actions.
- High-risk architecture/security/data changes require independent review.
- Project milestones are subject to mandatory independent Audit Gates at 25%, 50%, 75%, 90% and 100% progress.
- Major architecture, security/authorization or PostgreSQL/schema/RLS changes trigger an immediate independent audit regardless of progress percentage.
- A Builder must not approve its own milestone or close its own BLOCKER audit finding.
- BLOCKER audit findings halt milestone advancement until independently re-audited.
- The 100% Audit Gate must PASS before a milestone is marked DONE.
- Any new managed service must justify operational benefit versus added complexity and recurring cost.
- Avoid duplicating capabilities across Cloudflare, OpenRouter, n8n, and PostgreSQL without a measurable reason.
- Design every reusable component to be scoped by bot/tenant/user/channel where appropriate.

## Audit protocol

The authoritative project-level audit rules are in `docs/audits/AUDIT_SYSTEM_V1.md`.

- Audit progress is based on explicit milestone deliverables, not elapsed calendar time.
- If deliverable weights are not defined, use equal weights.
- Crossing a gate creates an audit obligation even if implementation has already progressed beyond it.
- Primary Independent Auditor: Claude Opus 5 via OpenRouter, replaceable through project configuration.
- Prefer an auditor model/model family different from the Builder where practical.
- Specialist security/domain auditors may supplement, but do not replace, the mandatory independent gate.
- Audit reports are durable repository artifacts under `docs/audits/`.

## Status protocol

Allowed task states:
- BACKLOG
- READY
- IN_PROGRESS
- REVIEW
- BLOCKED
- NEEDS_DECISION
- DONE

If a major architectural decision is unresolved, mark it NEEDS_DECISION rather than silently choosing.

## Handoff format

Every AI contribution should end with:

### Progress / Audit
Current milestone progress, highest crossed Audit Gate, and whether an audit is due.

### Findings
Facts verified from code/docs/data.

### Recommendation
What should change and why.

### Risks
Failure modes, security/privacy/cost/complexity concerns.

### Decisions needed
Items requiring owner/architect choice.

### Next task
The concrete next piece of work, including dependencies.

## Review principle

AI reviewers should challenge assumptions. Agreement is not required.
A review is more useful when it finds:
- duplicated infrastructure
- unnecessary model calls
- hidden token growth
- failure recovery gaps
- data ownership ambiguity
- privacy leaks
- vendor lock-in
- missing idempotency
- concurrency/state issues
- migration risks
- operational complexity
