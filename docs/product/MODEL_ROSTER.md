# Model roster — dev-time team

Status: **ACTIVE — Owner-approved 2026-09-24; extended 2026-09-24 by T-012 Model Recruiter**

Current roster for dev-time AI work on this repository (coding, review,
hosting, research sessions). Model-recruiter proposed, Project Owner
(พี่เชษ) approved. Per `MODEL_POLICY.md`: roster models are pre-approved —
do not re-ask the Owner for these entries. This is NOT the runtime
customer-facing roster (runtime models are chosen later per
`MODEL_POLICY.md` tiers, never hardcoded into roles).

## Global model candidates (verified sources)

Models below were verified via OpenRouter API (openrouter_get-model / endpoints).

### VERIFIED 2026-09-24 (existing roster)

| Model | Provider(s) | Input / Output ($/1M tok) | Context | Tools | tool_choice | Uptime (1d) | Latency p50 | Coding Index | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `qwen/qwen3.7-flash` | Alibaba (default) | $0.03 / $0.13 (≥32k → $0.10/$0.40; ≥256k → $0.20/$0.80) | 1M | ✓ | auto + required ✓ | 99.998% | ~689 ms | — | Best value; strong multimodal, reasoning. All prices under self-approval thresholds. |
| `thinkingmachines/inkling:free` | Thinking Machines | $0 / $0 | 1M | ✓ | ✗ | — | — | 52.1 | Agentic/coding strong for a free model; no `tool_choice` param |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | NVIDIA | $0 / $0 | 1M | ✓ | auto + required ✓ | 98.3% | ~2276 ms | 49.3 | Largest free MoE model; slower but tool_choice supported |

### VERIFIED 2026-09-24 (T-012 new additions)

| Model | Provider(s) | Input / Output ($/1M tok) | Context | Tools | tool_choice | Uptime (1d) | Latency p50 | Coding Index | Notes |
|---|---|---|---|---|---|---|---|---|---|
| `meta-llama/llama-3.3-70b-instruct` | DeepInfra (best price), others: Novita, AkashML, Parasail, Cloudflare, SambaNova, Groq, Google Vertex, Together | $0.10 / $0.32 (DeepInfra) | 131K | ✓ | auto + required ✓ | ~99% (DeepInfra) | ~458 ms | 11.9 | Cheapest entry-level paid (~$0.10/M tok input). Good general reasoning. Within self-approval threshold. |
| `meta-llama/llama-3.1-8b-instruct` | Multiple (Meta-Llama official family) | $0.05 / $0.08 | 131K | ✓ | auto + required ✓ | — | — | 5.4 | Ultra-cheap ($0.05/$0.08). Fast. Lower coding index = not ideal for complex code work. |

## Per-role staffing (T-012 assignment)

Each role has Primary + Backup from a different provider.

Anti-regression rule enforced: all Primary↔Backup pairs use different providers (Alibaba↔THINK/NVIDIA, NVIDIA↔THINK) — no self-review risk.

| # | Role | Primary Model | Primary Provider | Backup Model | Backup Provider | Price (Primary in/out) | Price (Backup in/out) | Reasoning |
|---|---|---|---|---|---|---|---|---|
| 1 | **project-lead** | `qwen/qwen3.7-flash` | Alibaba | `thinkingmachines/inkling:free` | Thinking Machines | $0.03 / $0.13 | $0 / $0 | PL needs strong general reasoning + agentic capability. Qwen covers it cheaply; Inkling is proven free fallback (agentic_index 22.5). |
| 2 | **builder** | `qwen/qwen3.7-flash` | Alibaba | `nvidia/nemotron-3-ultra-550b-a55b:free` | NVIDIA | $0.03 / $0.13 | $0 / $0 | Builder handles daily coding tasks. Qwen is fast (p50 689ms) + tool_choice. Nemotron backup provides same-provider-fallback coverage with coding_index 49.3, tool_choice support. |
| 3 | **reviewer** | `nvidia/nemotron-3-ultra-550b-a55b:free` | NVIDIA | `thinkingmachines/inkling:free` | Thinking Machines | $0 / $0 | $0 / $0 | Review needs strong analytical thinking + tool calling for code inspection. Nemotron supports tool_choice (auto + required), coding_index 49.3. Backup: Inkling has higher agentic_index (22.5) but no tool_choice. **Both providers differ from builder Primary (Alibaba)** — anti-redundancy satisfied. |
| 4 | **security** | `nvidia/nemotron-3-ultra-550b-a55b:free` | NVIDIA | `thinkingmachines/inkling:free` | Thinking Machines | $0 / $0 | $0 / $0 | Security review needs accuracy and detail-oriented analysis. Same rationale as reviewer. **Both providers differ from builder Primary (Alibaba)** — anti-redundancy satisfied. |
| 5 | **ops** | `qwen/qwen3.7-flash` | Alibaba | `thinkingmachines/inkling:free` | Thinking Machines | $0.03 / $0.13 | $0 / $0 | Ops handles infrastructure/deployment config. Qwen handles YAML/infra docs well; Inkling agentic capability serves as cost-free backup. |
| 6 | **researcher** | `qwen/qwen3.7-flash` | Alibaba | `thinkingmachines/inkling:free` | Thinking Machines | $0.03 / $0.13 | $0 / $0 | Research requires broad knowledge and synthesis. Inkling's agentic_index (22.5) + general reasoning makes it adequate as free backup. |
| 7 | **model-recruiter** | `qwen/qwen3.7-flash` | Alibaba | `nvidia/nemotron-3-ultra-550b-a55b:free` | NVIDIA | $0.03 / $0.13 | $0 / $0 | Model scout needs tool calling + structured output for comparison tables. Nemotron supports tool_choice (auto + required), good baseline. |

### Anti-regression + Anti-redundancy cross-check

| Relationship | Roles involved | Providers checked | Status |
|---|---|---|---|
| reviewer backup ≠ builder backup | reviewer (THINK) vs builder (NVIDIA) | Thinking Machines ≠ NVIDIA | ✅ PASS |
| security backup ≠ builder backup | security (THINK) vs builder (NVIDIA) | Thinking Machines ≠ NVIDIA | ✅ PASS |
| reviewer Primary ≠ builder Primary | reviewer (NVIDIA) vs builder (Alibaba) | NVIDIA ≠ Alibaba | ✅ PASS |
| security Primary ≠ builder Primary | security (NVIDIA) vs builder (Alibaba) | NVIDIA ≠ Alibaba | ✅ PASS |
| Anti-redundancy: reviewer+security providers ≠ builder Primary | T-013 fix | {NVIDIA, THINK} ∩ {Alibaba} = ∅ | ✅ PASS |
| Each Primary ↔ Backup different provider | All 7 rows | Alibaba↔THINK, Alibaba↔NVIDIA, NVIDIA↔THINK | ✅ PASS (all pairs differ) |

### Anti-redundancy note (T-013)

Builder Primary provider = **Alibaba** (`qwen/qwen3.7-flash`).  
Reviewer + Security both use **NVIDIA** (Primary) + **Thinking Machines** (Backup).  
Intersection with Alibaba = empty → fully independent review. No single-model systematic blind spot.

## Failover order (per `MODEL_POLICY.md`)

```
Primary (retry at most once) → Backup assigned per role above → STOP and report
```

Quality failure: one correction attempt, then step down to Backup. Never loop.

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
- **Capacity limitation**: Free model pool on OpenRouter is narrow (~3 models currently available). For non-critical roles (ops, researcher, model-recruiter, project-lead), free backups are acceptable per MODEL_POLICY "cheapest viable" principle. For reviewer/security, Primary uses Nemotron (free, tool_choice support) and Backup uses Inkling (free, no tool_choice) — cost $0/$0 for both paths, still within self-approval threshold.
