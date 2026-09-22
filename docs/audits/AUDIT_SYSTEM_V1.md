# Nippan AI Platform — Independent Audit System v1

Status: ACTIVE
Date: 2026-09-23
Applies to: all project phases, milestones, architecture work, schema work, security work and implementation work

## Purpose

This Audit System is a project-delivery governance control. It is separate from runtime `audit_events` stored in PostgreSQL.

Its job is to independently verify that the project is still following the accepted plan, that implementation matches the frozen contracts and ADRs, that important work was not omitted, and that errors or unsafe shortcuts are caught before they become the next layer of the platform.

## Core rule

The Builder and the Auditor are separate roles.

- A Builder may implement, test and explain work.
- A Builder must not approve its own milestone.
- The Auditor must independently inspect source material and evidence.
- Audit findings are recorded in the repository.
- A BLOCKER finding stops milestone advancement until remediation is completed and independently re-audited.

## Progress-based Audit Gates

Audits are triggered by milestone progress, not by calendar time.

Mandatory gates:

- 25%
- 50%
- 75%
- 90%
- 100%

The 90% gate is the pre-completion audit.
The 100% gate is the final completion audit and must pass before the milestone can be marked DONE.

### Progress calculation

Each milestone must have an explicit deliverable checklist.

1. Scope and deliverables are recorded before or at milestone start.
2. If explicit weights are defined, progress uses those weights.
3. If no weights are defined, deliverables are equally weighted.
4. A deliverable counts as complete only when its stated acceptance evidence exists.
5. IN_PROGRESS work does not count as completed weight unless a milestone document explicitly defines measurable partial acceptance.
6. Scope changes must be recorded before recalculating the denominator; they must not silently move a gate.
7. Crossing a gate creates an audit obligation even if implementation has already moved beyond that percentage.

Because this system was introduced during Phase 2, Phase 2 requires a catch-up audit against the highest already-crossed gate once its deliverable progress is calculated.

## Immediate Audit Triggers

An independent audit is required immediately, regardless of percentage, for:

- major architecture changes
- major security or authorization changes
- major PostgreSQL/schema/RLS changes

The Project Owner or Architect may also request an ad-hoc audit when evidence is conflicting or a critical assumption changes.

## Primary Independent Auditor

Primary Auditor: Claude Opus 5 through OpenRouter.

This is a governance configuration, not a model ID hard-coded into application runtime logic.

Rules:

- the primary auditor is replaceable by project configuration
- the auditor must not be the Builder that produced the work under audit
- for important work, prefer a different model/model family from the Builder where practical
- a security-specialist or domain-specialist auditor may supplement the primary auditor
- specialist review does not replace the required independent audit gate

## Required Audit Scope

Every gate audit checks, as applicable:

1. Plan alignment
   - work matches ROADMAP, PROJECT_STATE and the assigned milestone
   - no silent scope drift

2. Architecture and contract compliance
   - Foundation and ADRs are followed
   - frozen contracts are not changed accidentally
   - unresolved architecture choices are marked NEEDS_DECISION

3. Correctness
   - implementation matches documented behavior
   - migrations, code, schemas and interfaces agree
   - edge cases and failure paths are considered

4. Security and isolation
   - tenant isolation/RLS remains fail-closed
   - authorization, privacy, secrets and protected-system boundaries are preserved
   - no model is allowed to replace deterministic authorization or risk controls

5. Reliability and data integrity
   - idempotency, retries, state transitions and rollback behavior are coherent
   - immutable/append-only guarantees are preserved where required

6. Observability and evidence
   - tests and verification claimed in docs are actually present
   - request/trace/usage/audit evidence is consistent
   - unsupported claims are identified

7. Cost and complexity
   - unnecessary model calls, token growth, services or duplicated infrastructure are challenged
   - new complexity has measurable justification

8. Documentation consistency
   - README, ROADMAP, PROJECT_STATE, ADRs, schemas and implementation do not contradict one another
   - status claims match repository evidence

9. Protected systems
   - protected production repositories/workflows remain untouched unless a later phase explicitly authorizes migration

## Finding Severity

- BLOCKER — unsafe, incorrect, contract-breaking or missing evidence that prevents milestone advancement
- HIGH — significant issue that must be resolved before the next major gate or release boundary
- MEDIUM — material improvement or risk that requires tracked remediation
- LOW — non-blocking improvement
- NOTE — observation or follow-up with no current defect

## Audit Outcomes

- PASS — no unresolved blocking findings
- PASS_WITH_FINDINGS — no BLOCKER; tracked findings remain
- BLOCKED — one or more BLOCKER findings remain

Only PASS or PASS_WITH_FINDINGS permits normal milestone advancement.
The 100% gate requires PASS for milestone DONE.

## Evidence and Record

Audit reports are stored under `docs/audits/` using `AUDIT_REPORT_TEMPLATE.md`.

Each report records:

- phase/milestone
- gate percentage or immediate trigger
- baseline commit/PR
- Builder identity/model where known
- Auditor identity/model
- progress calculation
- evidence inspected
- findings and severity
- outcome
- remediation owner
- re-audit result when required

Audit records must be durable repository artifacts, not only chat messages.

## Remediation and Re-audit

1. Builder fixes the finding and supplies evidence.
2. BLOCKER findings remain open until the independent Auditor verifies the fix.
3. The Builder cannot close its own BLOCKER.
4. Re-audit records the original finding and the verification evidence.
5. If remediation changes architecture/security/schema materially, that change itself can trigger another immediate audit.

## Relationship to normal reviews

Normal PR reviews, specialist reviews and automated tests remain useful, but they do not replace mandatory progress gates.

The Audit System is the independent project-level control that answers:

- Are we still building the agreed system?
- Is the work actually correct?
- Did anything important get skipped?
- Are documents, code and database still consistent?
- Is the next milestone safe to begin?
