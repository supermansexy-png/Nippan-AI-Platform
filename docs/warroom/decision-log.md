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
