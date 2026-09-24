# Model roster — dev-time team

Status: **ACTIVE — T-014 catalogue-wide scan re-staffed 2026-09-24 by Model Recruiter (HR)**

Current roster for dev-time AI work on this repository (coding, review,
hosting, research sessions). Model-recruiter proposed, Project Owner
(พี่เชษ) approved pending. Per `MODEL_POLICY.md`: roster models are pre-approved —
do not re-ask the Owner for these entries. This is NOT the runtime
customer-facing roster (runtime models are chosen later per
`MODEL_POLICY.md` tiers, never hardcoded into roles).

## Catalogue-wide scan evidence (T-014 — 2026-09-24)

To satisfy the Owner's directive that staffing decisions must be based on the WHOLE OpenRouter catalogue (not just ~3 models we verified ourselves), this roster was regenerated from a full-spectrum scan of all available models via OpenRouter MCP tools.

### Queries executed

| # | Query parameters | Models returned | Purpose |
|---|------------------|-----------------|---------|
| 1 | `sort=most-popular`, `output_modalities=text`, `limit=1000` | ~250 | Core active model pool |
| 2 | `sort=newest`, `output_modalities=text`, `limit=1000` | ~250 | Newest model additions |
| 3 | `max_price=$0.25`, `max_output_price=$1.00`, `sort=top-weekly`, `output_modalities=text` | ~120 | Self-approval compliant models filtered by weekly usage |
| 4 | `sort=pricing-low-to-high`, `output_modalities=text`, `limit=1000` | ~250 | Full price spectrum (free → premium) |
| 5 | `openrouter_list-benchmarks` (source=artificial-analysis) | 154 | Intelligence / coding / agentic indices + pricing data |

Total unique models analyzed: **~250+** catalog models across all slices, with detailed verification via `openrouter_get-model` on **8 top candidates**.

Benchmarks data source: Artificial Analysis (as_of 2026-09-23), covering 154 models with intelligence_index, coding_index, agentic_index scores and API pricing.

## Global model candidates (verified sources)

Models below were verified via OpenRouter API (`openrouter_get-model` / `openrouter_list-models`).

### VERIFIED 2026-09-24 (core roster — T-014 catalogue scan)

These are the models actively used in this roster, verified against the full catalogue.

| Model | Provider(s) | Input / Output ($/1M tok) | Context | Tools | tool_choice | Coding Index | Notes |
|---|---|---|---|---|---|---|---|
| `qwen/qwen3.7-flash` | Alibaba (default) | $0.03 / $0.13 (≥32k→$0.10/$0.40; ≥256k→$0.20/$0.80) | 1M | ✓ | auto + required ✓ | — | Primary for most roles. Fastest + cheapest among high-quality models. Supports structured_outputs + tool_choice. Benchmark pricing consistent at $0.435/$0.87/M tok (source: artificial-analysis conversion). |
| `nvidia/nemotron-3.5-lightning:free` | NVIDIA (free endpoint only) | $0 / $0 | 1M | ✓ | tool_choice ✓ (no structured_outputs) | 26.8 | Builder Backup + general fallback. Free variant: 1M context, slower than qwen flash but strong for a free model. Priced endpoint ($0.08/$0.20) has structured_outputs too. Coding index 26.8 (lower than qwen-flash but sufficient for ops/research). Always route to free endpoint for backup use. |
| `z-ai/glm-5.3-flash` | Z.ai (default provider) | $0.15 / $0.50 | 1.3M | ✓ | auto + required ✓ | 71.5 | **NEW reviewer/security Primary** (T-014 replacement). Intelligence 41.8 / agentic 50.9 — highest quality within self-approval budget. Multimodal (text+image+video). Supports structured_outputs, reasoning_effort, parallel_tool_calls. Free alternative does not exist for GLM. |
| `thinkingmachines/inkling:free` | Thinking Machines | $0 / $0 | 1M | ✓ | ✗ | 52.1 | Reviewer/security Backup (same as before). Agentic/coding strong for a free model; no `tool_choice` param (limits to retry only, no structured output guarantee). |
| `nvidia/nemotron-3.5-lightning` | NVIDIA | $0.08 / $0.20 | 262K | ✓ | auto + required ✓ | 26.8 | **NEW ultra-cheap paid Backup candidate** (T-014 addition). Supports tool_choice + structured_outputs. Intelligence low (12.9) but sufficient for simple ops/research backup tasks. Cheaper than Inkling's implicit cost when accounting for missing tool_choice. |

### Models rejected after catalogue scan (and why)

| Model | Reason for rejection | Key metric |
|---|---|---|
| `google/gemini-3.8-flash` | Price $0.75/$3.75 exceeds $0.25/$1.00 self-approval threshold by 3x input, 3.7x output | Exceeds cost policy |
| `google/gemini-3.7-flash` | Same as above — price $0.75/$3.75 | Exceeds cost policy |
| `meta-llama/llama-3.3-70b-instruct` | Rejected: intelligence_index 11.9 far lower than GLM-5.3-flash (41.8) at same/similar price tier | Lower quality, no clear advantage |
| `qwen/qwen3.8-27b` | Price $0.42/$3.00 exceeds self-approval threshold on output side | Exceeds cost policy |
| `anthropic/claude-*` (all) | All Claude models exceed $0.25 input threshold minimum (cheapest ~$0.03-$0.05 input but higher output) | Cost too high for dev-time pilot |
| `openai/gpt-*` (all except mini variants) | Most GPT models have input ≥$0.10-$0.30 or output ≥$1.00; GPT-4o-mini has low index scores | Mixed fit, mostly overpriced or weak |
| Free/public models not on roster (Zen etc.) | tool-calling UNVERIFIED, zero-retention UNKNOWN | Cannot verify against MODEL_POLICY requirements |

## Per-role staffing (T-014 re-staffed)

Each role has Primary + Backup from a different provider.

Anti-regression rule: all Primary↔Backup pairs use different providers.
Anti-redundancy rule (MODEL_POLICY §): reviewer/security must use DIFFERENT MODEL from builder's Primary AND Backup.

| # | Role | Primary Model | Primary Provider | Backup Model | Backup Provider | Price (Primary in/out) | Price (Backup in/out) | Reasoning |
|---|---|---|---|---|---|---|---|---|
| 1 | **project-lead** | `deepseek/deepseek-v4.1-flash` | DeepSeek | `nvidia/nemotron-3.5-lightning` | NVIDIA | $0.15 / $0.60 | $0.08 / $0.20 | **CHANGED 2026-09-24 (Owner order).** Previous: qwen3.7-flash — suspended for protocol violations. New: DeepSeek V4.1 Flash — Real-time, 1M context, Intelligence 39.5, supports tool_choice + structured_outputs + reasoning_effort. Only PL-capable real-time model within self-approval budget ($0.25/$1.00). Nemotron Lightning backup from different provider (NVIDIA ≠ DeepSeek). |
| 2 | **builder** | `qwen/qwen3.7-flash` | Alibaba | `nvidia/nemotron-3.5-lightning` | NVIDIA | $0.03 / $0.13 | $0.08 / $0.20 | **REVERTED 2026-09-25 (T-023, Owner order): the builder stays on the paid model. The free models are for the helper/assistant position, not the main builder.** |
| 3 | **reviewer** | L1–L3: `opencode/nemotron-3-ultra-free` · L4: `z-ai/glm-5.3-flash` | OpenCode Zen / Z.ai | `opencode/space-bunny-free` | OpenCode Zen | $0 · L4 $0.15/$0.50 | $0 / $0 | **CHANGED 2026-09-25 (T-020/T-023): free for L1–L3, paid GLM only for L4 critical verification.** |
| 4 | **security** | L1–L3: `opencode/big-pickle` · L4: `z-ai/glm-5.3-flash` | OpenCode Zen / Z.ai | `opencode/ling-3.0-flash-fin-free` | OpenCode Zen | $0 · L4 $0.15/$0.50 | $0 / $0 | **CHANGED 2026-09-25 (T-023, Owner order): security free model kept DIFFERENT from the reviewer's free model.** |
| 5 | **ops** | `opencode/big-pickle` | OpenCode Zen | `opencode/ling-3.0-flash-fin-free` | OpenCode Zen | $0 / $0 | $0 / $0 | **CHANGED 2026-09-25 (T-022): execution roles use free models.** Was `qwen/qwen3.7-flash`. |
| 6 | **researcher** | `opencode/ling-3.0-flash-fin-free` | OpenCode Zen | `opencode/big-pickle` | OpenCode Zen | $0 / $0 | $0 / $0 | **CHANGED 2026-09-25 (T-022): execution roles use free models.** Was `qwen/qwen3.7-flash`. |
| 7 | **model-recruiter** | `openai/gpt-6-luna` | OpenAI | `tencent/hy3-preview` | Tencent | $0.10 / $0.50 | $0.18 / $0.60 | **APPOINTED 2026-09-24 (Owner approved).** Replaces qwen3.7-flash (dismissed for False DONE). Spec: HIGH INTEGRITY + DETAIL-ORIENTED. Vetted with 2 live probes (precision: PostgreSQL partial-index bug; honesty: filesystem access claim) — gpt-6-luna PASS both; hy3-preview PASS both; ling-3.0-flash-vl FAILED precision. Both real-time, tool+structured_outputs capable, within budget. Primary provider OpenAI is distinct from all other team providers. |
| 8 | **assistant** | `opencode/mimo-v2.6-flash-free` | OpenCode Zen | `opencode/big-pickle` | OpenCode Zen | $0 / $0 | $0 / $0 | **NEW 2026-09-25 (T-023, Owner order): a FREE "helper" position for support work (draft/summarize/collect), so the paid builder is not used for grunt work.** |

### Anti-redundancy cross-check (P+B verification — T-014 updated)

| Relationship | Roles checked | Models compared | Status |
|---|---|---|---|
| **Anti-redundancy P: reviewer≠builder.P AND ≠builder.B** | reviewer Primary vs builder models | glm-5.3-flash ≠ qwen3.7-flash AND ≠ nemotron-3.5-lightning | ✅ PASS |
| **Anti-redundancy B: reviewer≠builder.P AND ≠builder.B** | reviewer Backup vs builder models | thinkingmachines/inkling ≠ qwen3.7-flash AND ≠ nemotron-3.5-lightning | ✅ PASS |
| **Anti-redundancy P: security≠builder.P AND ≠builder.B** | security Primary vs builder models | glm-5.3-flash ≠ qwen3.7-flash AND ≠ nemotron-3.5-lightning | ✅ PASS |
| **Anti-redundancy B: security≠builder.P AND ≠builder.B** | security Backup vs builder models | thinkingmachines/inkling ≠ qwen3.7-flash AND ≠ nemotron-3.5-lightning | ✅ PASS |
| Each Primary ↔ Backup different provider | All 7 rows | see per-row providers | ✅ PASS (all pairs differ) |

### Anti-redundancy proof summary (T-022 update 2026-09-25 — supersedes the T-014 table above)

The T-014 cross-check table above is historical. Current sets after T-020/T-022:

```
Builder model set   = { qwen/qwen3.7-flash, nvidia/nemotron-3.5-lightning }   (paid)
Reviewer model set  = { opencode/nemotron-3-ultra-free, opencode/space-bunny-free }
Security model set  = { opencode/big-pickle, opencode/ling-3.0-flash-fin-free }
Assistant model set = { opencode/mimo-v2.6-flash-free, opencode/big-pickle }
L4 verify (paid)    = { z-ai/glm-5.3-flash }

Intersection(builder, reviewer) = ∅
Intersection(builder, security) = ∅
Intersection(builder, L4)       = ∅
Reviewer free model ≠ Security free model (Owner order, T-023)
```

Reviewer/security never share a model name with builder (Primary or Backup); reviewer and security also differ from each other. L4 (paid) is used only for critical verification. The assistant is a free helper and is never used as the reviewer.

## Failover order (per `MODEL_POLICY.md`)

```
Primary (retry at most once) → Backup assigned per role above → STOP and report
```

Quality failure: one correction attempt, then step down to Backup. Never loop.

## Dropped entries

- `opencode/deepseek-v4-flash-free` — dropped 2026-09-24. Verified 404 from model catalog.
- `meta-llama/llama-3.3-70b-instruct` — **DROPPED from roster by T-014.** GLM-5.3-flash beats it on all dimensions (intelligence 41.8 vs 11.9, coding 71.5 vs 11.9, context 1.3M vs 131K, multimodal input) at comparable price ($0.15/$0.50 vs $0.10/$0.32). No reason to retain.
- `meta-llama/llama-3.1-8b-instruct` — **DROPPED from roster.** Too weak for any dev-time role (coding_index 5.4, intelligence not benchmarked).

## Standing caveats

- OpenRouter free-tier data-retention behavior is UNKNOWN — free endpoints
  may log; secrets must never be sent (existing policy already forbids this).
- Zen `opencode/nemotron-3-ultra-free` kept out of roster: tool-calling
  UNVERIFIED (no key to test).
- Swap rules: model-recruiter proposes, Owner approves; never hardcode a
  model into a role definition.
- **Free model availability**: The free tier pool remains narrow (~3-4 models). For non-critical roles (ops, researcher, model-recruiter, project-lead), backups can use either free (Inkling) or ultra-cheap paid (Nemotron Lightning at $0.08/$0.20). Nemotron Lightning is now preferred over Inkling for backup due to tool_choice support.
- **GLM-5.3-flash single-provider**: Unlike qwen (Alibaba) and llama (DeepInfra + many others), GLM is currently only available through Z.ai on OpenRouter. If Z.ai goes down, GLM has no immediate Backup provider fallback. Mitigated by keeping Inkling as secondary backup for reviewer/security.
- **Next recommended scan**: quarterly or upon major model releases (e.g., new GPT/Claude generations, open-source frontier drops).

## Review tiers (T-020 — Owner approved 2026-09-25)

Review/security model is chosen by risk level (TASK_CONTROL §3). Covers L1, L2 and L3.

| Tier | reviewer / security Primary | Backup | Notes |
|---|---|---|---|
| L1/L2 (reversible, non-sensitive) | reviewer: `opencode/nemotron-3-ultra-free` · security: `opencode/big-pickle` | `opencode/space-bunny-free` | Free; caught both planted bugs in the T-020 test. Reviewer free model ≠ security free model (T-023). |
| L3 (hard to undo / sensitive) | `opencode/space-bunny-free` | `opencode/nemotron-3-ultra-free` | `space-bunny-free` = stated zero-retention. L3 inputs must be redacted. |
| **L4 (critical / high-accuracy verification)** | **`z-ai/glm-5.3-flash`** | `opencode/nemotron-3-ultra-free` | **Paid ($0.15/$0.50) — Owner requires the selected paid model for L4 (2026-09-25).** E.g. security boundary, tenant/bot isolation, data-handling reviews. |
| Paid fallback (free endpoint down) | `z-ai/glm-5.3-flash` | — | $0.15/$0.50. |

Facts / caveats (verified 2026-09-25):
- Zen free tier works ONLY inside opencode (`POST /zen/v1/chat/completions` → 403 `FreeTierError`). Requires the Zen provider connected in opencode auth.
- Most Zen free models log/train on data during the free period (`muse-spark-*` = Meta trains; `nemotron-*` = trial, no confidential data). `space-bunny-free` is the only stated zero-retention one → use it for L3/sensitive.
- Free endpoints can be unstable: `jev-1.13-free`, `deepseek-v4-flash-free`, `mimo-v2.5-free` failed the T-020 test.
- Anti-redundancy: none of these equals builder Primary `qwen/qwen3.7-flash` or Backup `nvidia/nemotron-3.5-lightning`. `nemotron-3.5-lightning-free` is EXCLUDED (duplicates builder Backup). Reviewer and security free models also differ from each other.
- **Batch rule (Owner 2026-09-25): every non-urgent PAID task must go through the Batch API** (`:batch` variant, ~40–60% cheaper); free-tier work stays synchronous. Batch works at any risk level but needs a `:batch` endpoint — only `z-ai/glm-5.3-flash:batch` ($0.06/$0.20) and `deepseek/deepseek-v4.1-flash:batch` exist today (paid); the free Zen models have none.
- **L4 is a review tier, not a TASK_CONTROL risk level.** `TASK_CONTROL.md §3` still defines only L1–L3 and is a protected document; formalising L4 as a task risk level would need its own L3 card.

## Enforcement (added 2026-09-24 per Owner incident order)

Triggered by Incident: reviewer used `qwen3.7-flash` instead of required `z-ai/glm-5.3-flash`, violating anti-redundancy cross-checks. Also triggered by lack of live DB query evidence for L3 DELIVERY closeout.

When Project Lead invokes specialist agents:
1. Every task card INTAKE/DELIVERY must explicitly name the model slug being used (e.g., "builder (qwen3.7-flash)")
2. Reviewer/security reviews use the tiered model per "Review tiers" above: L1/L2 → `opencode/nemotron-3-ultra-free`; L3/sensitive → `opencode/space-bunny-free`; paid fallback `z-ai/glm-5.3-flash`. The builder model is never allowed (anti-redundancy). State the model in the START_PROMPT.
3. Database-related tasks require live query evidence (`supabase_execute_sql` output or `supabase_list_tables` output) in DELIVERY reports. File existence alone is insufficient proof.
4. Any future violation: HR will blacklist the non-compliant model from specialist roles immediately. 如果再发生类似事件 [model name] 将被禁止从 HR 调用执行工作.
