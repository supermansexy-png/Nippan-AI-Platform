# Decision log

Append-only. Format: `docs/warroom/DECISION_LOG_FORMAT.md`. Owner: Project Lead.

## 2026-09-24 — model-recruiter/dev-time — Dev-time model roster approved (qwen3.7-flash + 2 free backups)
Context: deepseek-v4-flash-free dropped (no longer free; VERIFIED 404 from
catalog). model-recruiter re-verified live pricing/availability and proposed
a replacement roster.
Decision: Approve dev-time roster: Primary `qwen/qwen3.7-flash`
(OpenRouter, $0.03/$0.13), Backup 1 `thinkingmachines/inkling:free`,
Backup 2 `nvidia/nemotron-3-ultra-550b-a55b:free`. Recorded in
`docs/product/MODEL_ROSTER.md`.
Reason: all pass MODEL_POLICY self-approval thresholds; backups are free and
from different providers than Primary; prices verified from live data.
Task: roster recruitment (model-recruiter DELIVERY MR-DEV-ROSTER-REFRESH);
owner approval in chat 2026-09-24.

## 2026-09-24 — Project Lead — Independent Audit System suspended; War Room resumed
Context: Owner pivoted to Phase A market test, then ordered War Room brought
back for dev-time use and as a runtime backstage ecosystem, with the
Independent Audit System removed from gating first.
Decision: Suspend Independent Audit System progress gates (25/50/75/90/100)
and immediate paid-audit triggers as blocking controls. Normal code review,
tests, CI, security review and evidence verification continue. Historical
audit records under docs/audits/ are preserved, not rewritten. Paid
Independent Auditor remains not invoked unless the owner re-enables it.
War Room V1 work (Track D and onward) may resume under normal task cards.
Reason: Owner decision — audit pauses were blocking War Room completion;
owner wants War Room available for dev workflow and future runtime ecosystem.
Task: T-005 (audit suspension), T-006 (War Room resumption plan).

## 2026-09-24 — Project Lead / Builder — War Room dev-time API key auth documented (fail-closed)
Context: War Room preview endpoint needs a safe remote access path for owner
to use from dev machine without exposing it publicly or relying solely on
loopback. The code already supports Bearer-token API key auth via
`DevApiKeyAuthenticator`; settings exist but were undocumented.
Decision: Documented the existing auth path in `services/dev/WAR_ROOM_AUTH_GUIDE.md`,
added auth-related env vars to `.env.example`. No code changes needed — the
auth chain is: (1) try DevApiKeyAuthenticator with SHA-256 + hmac.compare_digest,
(2) fallback to local-only if remote disabled, (3) Cloudflare JWT if remote enabled.
Unauthenticated requests → HTTP 403. Fail-closed by design.
Reason: Owner requested ability to access War Room from remote dev machine;
existing code already implements this securely — only documentation was missing.
Security properties: constant-time hash comparison, no timing side-channels,
keys never logged, fail-closed when config absent.
Task: T-010 (War Room preview access for dev-time use).

## INCIDENT — 2026-09-24 — Model Mismatch + Evidence Gap

**Severity**: HIGH — anti-redundancy bypass via same-model reviewer
**Affected tasks**: T-010, T-002
**Root cause**: Project Lead did not specify model when invoking reviewer agent; relied on subagent_type routing which does not enforce MODEL_ROSTER.md assignments
**Impact**: No independent verification occurred on two L3 tasks; reviewer used qwen3.7-flash (same as builder) instead of required z-ai/glm-5.3-flash
**Remediation**:
1. All future task invocations MUST include explicit model slug in START_PROMPT
2. DELIVERY reports for L2/L3 tasks involving database changes MUST include live query output as evidence
3. HR to maintain per-role model enforcement tracker
**Owner notified**: Yes — 2026-09-24 immediate escalation
**Scorecard updated**: See ai-scorecard.md entries for reviewer/qwen3.7-flash and builder/qwen3.7-flash

Per Owner directive:如果再发生此类事件，HR将不再被允许调用此模型执行工作。
