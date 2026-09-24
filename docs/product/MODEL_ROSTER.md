# Model roster — dev-time team

Status: **ACTIVE — Owner-approved 2026-09-24**

Current roster for dev-time AI work on this repository (coding, review,
hosting, research sessions). Model-recruiter proposed, Project Owner
(พี่เชษ) approved. Per `MODEL_POLICY.md`: roster models are pre-approved —
do not re-ask the Owner for these entries. This is NOT the runtime
customer-facing roster (runtime models are chosen later per
`MODEL_POLICY.md` tiers, never hardcoded into roles).

| Role | Model | Provider | Price (VERIFIED 2026-09-24) | Notes |
|---|---|---|---|---|
| **Primary** | `qwen/qwen3.7-flash` | OpenRouter (Alibaba) | $0.03 / $0.13 per 1M (in/out); ≥32k prompt $0.10/$0.40; ≥256k $0.20/$0.80 — all under self-approval thresholds | ctx 1M, tools + tool_choice, uptime 99.998% (1d), p50 708ms |
| **Backup 1** | `thinkingmachines/inkling:free` | OpenRouter (Thinking Machines) | $0 / $0 | ctx 1M, tools yes (no `tool_choice` param), coding/agentic strong; provider differs from Primary |
| **Backup 2** | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter (NVIDIA) | $0 / $0 | ctx 1M, tools + tool_choice; uptime 98.3% (1d), p50 2276ms — last resort |

## Failover order (per `MODEL_POLICY.md`)

Primary (retry at most once) → Backup 1 → Backup 2 → STOP and report.
Never loop. Quality failure: one correction, then step down.

## Dropped entries

- `opencode/deepseek-v4-flash-free` — dropped 2026-09-24. Owner reported
  no longer free; Project Lead VERIFIED both it and `opencode/deepseek-v4-flash`
  return 404 from the model catalog (gone, not re-priced).

## Standing caveats

- OpenRouter free-tier data-retention behavior is UNKNOWN — free endpoints
  may log; secrets must never be sent (existing policy already forbids this).
- Zen `opencode/nemotron-3-ultra-free` kept out of roster: tool-calling
  UNVERIFIED (no key to test).
- Swap rules: model-recruiter proposes, Owner approves; never hardcode a
  model into a role definition.
