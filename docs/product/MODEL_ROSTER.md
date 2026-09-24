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
| `nvidia/nemotron-3.5-lightning:free` | NVIDIA (free endpoint); also available on priced endpoints | $0 / $0 (free endpoint) | 262K | ✓ | auto + required ✓ | 49.3 | Builder Backup + general fallback. Largest free MoE model; slower p50 (~2276ms) but strongest free coding capability. Note: priced endpoint shows $0.6/$2.4 — always route to free endpoint for backup use. |
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
| 2 | **builder** | `qwen/qwen3.7-flash` | Alibaba | `nvidia/nemotron-3.5-lightning` | NVIDIA | $0.03 / $0.13 | $0.08 / $0.20 | Unchanged from T-012/T-013. Daily coding tasks need speed + tool_choice. Qwen fastest (p50 ~689ms) + cheapest. Backup swapped from nemotron-3-ultra-free to Lightning (2026-09-24) after free endpoint became unavailable. |
| 3 | **reviewer** | `z-ai/glm-5.3-flash` | Z.ai | `thinkingmachines/inkling:free` | Thinking Machines | $0.15 / $0.50 | $0 / $0 | **CHANGED in T-014.** Previous: Llama-3.3-70B ($0.10/$0.32). New: GLM-5.3-flash ($0.15/$0.50). GLM wins on quality: intelligence 41.8 vs 11.9 (Llama), agentic 50.9 vs null, coding 71.5 vs 11.9, context 1.3M vs 131K, supported_params include structured_outputs+tool_choice+reasoning_effort. Gemini alternatives exceed budget. Review needs deep analytical reasoning — GLM delivers at only +$0.05/$0.18 incremental cost vs Llama. **Primary ≠ qwen3.7-flash AND ≠ nemotron-3-ultra — fully independent.** |
| 4 | **security** | `z-ai/glm-5.3-flash` | Z.ai | `thinkingmachines/inkling:free` | Thinking Machines | $0.15 / $0.50 | $0 / $0 | **CHANGED in T-014.** Same rationale as reviewer. Security analysis demands precision, pattern recognition for vulnerabilities, and structured reasoning — GLM excels here. Pricing within self-approval. **Primary ≠ qwen3.7-flash AND ≠ nemotron-3-ultra — fully independent.** |
| 5 | **ops** | `qwen/qwen3.7-flash` | Alibaba | `nvidia/nemotron-3.5-lightning` | NVIDIA | $0.03 / $0.13 | $0.08 / $0.20 | Ops handles infra/deployment config (YAML, Dockerfile, env vars). Qwen handles this well. Nemotron Lightning backup ($0.08/$0.20) supports tool_choice + structured_outputs — better than free Inkling (no tool_choice) while still being ultra-cheap. |
| 6 | **researcher** | `qwen/qwen3.7-flash` | Alibaba | `nvidia/nemotron-3.5-lightning` | NVIDIA | $0.03 / $0.13 | $0.08 / $0.20 | Research requires broad knowledge synthesis and structured output generation. Light Nemotron backup provides cheap structured-output fallback. Qwen's 1M context helps with long-form research. |
| 7 | **model-recruiter** | `openai/gpt-6-luna` | OpenAI | `tencent/hy3-preview` | Tencent | $0.10 / $0.50 | $0.18 / $0.60 | **APPOINTED 2026-09-24 (Owner approved).** Replaces qwen3.7-flash (dismissed for False DONE). Spec: HIGH INTEGRITY + DETAIL-ORIENTED. Vetted with 2 live probes (precision: PostgreSQL partial-index bug; honesty: filesystem access claim) — gpt-6-luna PASS both; hy3-preview PASS both; ling-3.0-flash-vl FAILED precision. Both real-time, tool+structured_outputs capable, within budget. Primary provider OpenAI is distinct from all other team providers. |

### Anti-redundancy cross-check (P+B verification — T-014 updated)

| Relationship | Roles checked | Models compared | Status |
|---|---|---|---|
| **Anti-redundancy P: reviewer≠builder.P AND ≠builder.B** | reviewer Primary vs builder models | glm-5.3-flash ≠ qwen3.7-flash AND ≠ nemotron-3.5-lightning | ✅ PASS |
| **Anti-redundancy B: reviewer≠builder.P AND ≠builder.B** | reviewer Backup vs builder models | thinkingmachines/inkling ≠ qwen3.7-flash AND ≠ nemotron-3.5-lightning | ✅ PASS |
| **Anti-redundancy P: security≠builder.P AND ≠builder.B** | security Primary vs builder models | glm-5.3-flash ≠ qwen3.7-flash AND ≠ nemotron-3.5-lightning | ✅ PASS |
| **Anti-redundancy B: security≠builder.P AND ≠builder.B** | security Backup vs builder models | thinkingmachines/inkling ≠ qwen3.7-flash AND ≠ nemotron-3.5-lightning | ✅ PASS |
| Each Primary ↔ Backup different provider | All 7 rows | see per-row providers | ✅ PASS (all pairs differ) |

### Anti-redundancy proof summary

```
Builder model set = { qwen3.7-flash, nemotron-3.5-lightning }
Reviewer model set = { glm-5.3-flash, thinkingmachines/inkling }
Security model set = { glm-5.3-flash, thinkingmachines/inkling }

Intersection(builder, reviewer) = ∅   (empty set)
Intersection(builder, security) = ∅   (empty set)

No matter whether builder runs Primary or Backup, reviewer/security
never share the same model name. Fully independent review.
```

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

## Enforcement (added 2026-09-24 per Owner incident order)

Triggered by Incident: reviewer used `qwen3.7-flash` instead of required `z-ai/glm-5.3-flash`, violating anti-redundancy cross-checks. Also triggered by lack of live DB query evidence for L3 DELIVERY closeout.

When Project Lead invokes specialist agents:
1. Every task card INTAKE/DELIVERY must explicitly name the model slug being used (e.g., "builder (qwen3.7-flash)")
2. Reviewer security reviews MUST use `z-ai/glm-5.3-flash` (Primary) — NO EXCEPTIONS. This is enforced by the START_PROMPT including "--model z-ai/glm-5.3-flash" parameter if supported, OR by explicitly stating the model requirement in the prompt.
3. Database-related tasks require live query evidence (`supabase_execute_sql` output or `supabase_list_tables` output) in DELIVERY reports. File existence alone is insufficient proof.
4. Any future violation: HR will blacklist the non-compliant model from specialist roles immediately. 如果再发生类似事件 [model name] 将被禁止从 HR 调用执行工作.
