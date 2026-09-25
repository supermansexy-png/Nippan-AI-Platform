# Free OpenRouter model test — T-024 (reference record)

Status: **RECORD ONLY — no roster change** (Owner order 2026-09-25; record for future use like T-021)

This file is a dev-time reference of how free OpenRouter models
(`<author>/<model>:free`) performed on real role-appropriate work. Use it
when staffing dev roles with free models or when comparing OpenRouter free
options against the Zen free tier (see `FREE_MODEL_ZEN_TEST_T021.md`). It
does NOT change `MODEL_ROSTER.md` by itself.

Raw evidence: `C:\Users\chetgo\AppData\Local\Temp\opencode\T024\results\`
(saved locally on the dev machine; `<model>__<battery>.txt` + coding-line
`*_coding.txt` files).

## When / who / how

- Date: 2026-09-25
- Run by: Project Lead (`opencode/big-pickle`) via `opencode run -m openrouter/<id> --dir <temp> --pure`
- Scope part 1 (all-role batteries): 12 candidate models endpoint-VERIFIED live at $0/M x 5 role batteries.
  Only 4 models returned real answers; 6 were blocked by OpenRouter workspace guardrail
  ("Free model training violation") and 2 (gemma) were rate-limited upstream.
- Scope part 2 (coding line): after Owner opened the guardrail setting, the 6 blocked models
  were tested on 2 coding batteries (builder + reviewer, reviewer = same planted-bug task as T-020).
- Cost: $0 (OpenRouter free tier; no paid model called).
- Data safety: all prompts synthetic (no secrets, no customer data); free tier may log.

## Availability notes (2026-09-25)

- Endpoint-verified live at $0/M: all 12 candidates (openrouter_list-model-endpoints).
- `qwen/qwen3.8-27b:free` was 404 in T-020, but now has a live ModelRun endpoint — included this time.
- 6 models initially blocked by OpenRouter workspace guardrail on `opencode-new`:
  `Free model training violation (guardrail)` — Owner opened the setting, then they ran.
- `google/gemma-4-26b-a4b-it:free` and `google/gemma-4-31b-it:free` (Google AI Studio):
  rate-limited upstream the whole session (all 10 probes errored) → NO SCORE.
- `z-ai/glm-5.2:free` excluded: no tools support (can't do agentic dev work).

## Score table A — full role batteries (4 models that answered; VERIFIED against raw files)

| Model | builder | security | ops | researcher | hr (precision) | latency |
|---|---|---|---|---|---|---|
| `nex-agi/nex-n2.5-mini:free` | PASS | PASS | PASS | PASS | PASS | ~5–7 s |
| `nex-agi/nex-n2.5-pro:free` | PASS | PASS | PASS | PASS | PASS | ~7–28 s (p99 flagged 3 min) |
| `cohere/north-mini-code:free` | PASS | PASS | PASS | PASS | FAIL (Yes ผิด) | ~5 s |
| `qwen/qwen3.8-27b:free` | PASS | PASS | PASS | PASS | FAIL (Yes ผิด + เหตุผลผิด) | ~9–25 s |

## Score table B — coding line (6 guardrail-opened models: builder + reviewer)

| Model | builder | reviewer (2 planted bugs) | Notes |
|---|---|---|---|
| `thinkingmachines/inkling:free` | FAIL (เขียนไฟล์ + รัน shell แทนการตอบโค้ด) | PASS 2/2 (isolation + off-by-one) | verbose agentic; instruction violation |
| `thinkingmachines/inkling-small:free` | PASS | PASS 2/2 | **best of this line**; fast (~8–16 s) |
| `poolside/laguna-s-2.1:free` | PASS | FAIL 1/2 (พลาด isolation) | caught off-by-one only |
| `poolside/laguna-xs-2.1:free` | PASS | FAIL 1/2 (พลาด isolation) | caught off-by-one only |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | FAIL (เขียนไฟล์แล้วอ่านกลับ) | PASS 2/2 | OpenRouter twin of roster reviewer `opencode/nemotron-3-ultra-free` (data point only) |
| `nvidia/nemotron-3-super-120b-a12b:free` | PASS | FAIL 1/2 (พลาด isolation) | caught off-by-one only |

Reviewer battery = T-020 task: `fetch_messages` with missing `tenant_id`/`bot_id`
WHERE filters (tenant/bot isolation leak) + `range(len(rows)+1)` off-by-one.
All models also flagged a "SQL quote syntax error" — same CLI prompt-quoting
artifact as T-020 (caveat b) — treated as unreliable, not scored.

## Findings

- **Full-line stars: `nex-n2.5-mini:free` (5/5, fast, stable)** — best overall this round.
  `nex-n2.5-pro:free` scores equally but had 1d uptime ~90% and p99 latency near 3 min → risky for real use.
- **Precision (hr battery): only the two nex models got the PostgreSQL partial-index
  question right** (`now()` is STABLE → predicate needs IMMUTABLE). `north-mini-code`
  and `qwen3.8-27b` confidently answered "Yes" (wrong), same failure class as
  big-pickle/ling in T-021 → weak for detail-critical roles.
- **Reviewer line: 3/6 caught both planted bugs** (inkling, inkling-small,
  nemotron-ultra) vs 8/11 Zen free in T-020 → the current Zen reviewer set
  (`nemotron-3-ultra-free` / `space-bunny-free`) remains the better reviewer choice.
- **3 coding-agent models (laguna-s, laguna-xs, nemotron-super) missed the
  isolation bug** — the most important bug class for this project (tenant/bot leak). Big red flag for review duty.
- **inkling + nemotron-ultra ignored "answer inline, no file writes"** — wrote
  files / ran shell instead (permission auto-rejected on the first attempt).
  Same instruction-following violation as `nemotron-3.5-lightning-free` in T-021.
- `nvidia/nemotron-3-ultra-550b-a55b:free` ≡ roster reviewer model on OpenRouter
  platform → useful confirmation (2/2) that the current reviewer choice is sound,
  but it is NOT an independent different-model check.

## Suggested use (for future reference — not applied)

- If more free agentic coding capacity is ever needed: `thinkingmachines/inkling-small:free`
  passed both builder and reviewer — best coding-line candidate.
- `nex-agi/nex-n2.5-mini:free` is worth re-probing if a free model is wanted for
  detail-precision support (only one that stayed perfect across all 5 roles here;
  single probe = weak signal, re-verify before long-term assignment).
- Do NOT use laguna-s / laguna-xs / nemotron-super for review/security (missed
  the isolation bug). Free review duty stays on the T-020 set.
- OpenRouter free tier is guardrail-restricted on this workspace by default
  (free-training policy) — budget availability checks for any future free-model
  test must include one live probe, not just catalogue price.

## Role rankings (free models — advisory, record only)

Ranked best → worst per role from probe evidence (T-020/T-021 Zen + T-024 OpenRouter).
Coverage per group: Zen set (T-021) and OpenRouter line-A (nex-n2.5-mini/pro,
north-mini-code, qwen3.8-27b) were tested on all 5 roles; OpenRouter coding
line (inkling ×2, laguna ×2, nemotron ×2) only on builder + reviewer.
Within "all passed" groups, order uses secondary evidence (precision battery,
latency, behaviour). These rankings are reference only — they do NOT change
`MODEL_ROSTER.md`.

### builder (write code to spec, inline, no file writes)
| Rank | Model | Evidence |
|---|---|---|
| 1 | `nex-agi/nex-n2.5-mini:free` | 5/5 all roles, fast (~5–7 s) |
| 2 | `nex-agi/nex-n2.5-pro:free` | 5/5 all roles; slow / uptime 90% p99 ~3min |
| 3 | `thinkingmachines/inkling-small:free` | builder ✅ + reviewer 2/2 (best coding line) |
| 4 | `qwen/qwen3.8-27b:free` | builder ✅; hr precision FAIL |
| 5 | `cohere/north-mini-code:free` | builder ✅; hr precision FAIL |
| 6 | `poolside/laguna-s-2.1:free` | builder ✅; reviewer 1/2 (missed isolation) |
| 7 | `poolside/laguna-xs-2.1:free` | builder ✅; reviewer 1/2 (missed isolation) |
| 8 | `nvidia/nemotron-3-super-120b-a12b:free` | builder ✅; reviewer 1/2 (missed isolation) |
| 9 | Zen set that passed builder 7/8 (mimo-v2.6, muse-spark-1.2/1.3, nemotron-3-ultra, space-bunny, big-pickle, ling-3.0) — all ✅, not cross-ranked vs OpenRouter (different session) | T-021 |
| 10 | `thinkingmachines/inkling:free` | builder FAIL (wrote file + ran shell); reviewer 2/2 |
| 11 | `nvidia/nemotron-3-ultra-550b-a55b:free` | builder FAIL (wrote file + read back); reviewer 2/2 |
| 12 | `opencode/nemotron-3.5-lightning-free` | T-021 builder FAIL (file write) |

### reviewer (planted-bug spot: tenant/bot isolation + off-by-one)
| Rank | Model | Evidence |
|---|---|---|
| 1 | `thinkingmachines/inkling-small:free` | 2/2 both bugs, fast (~8–16 s) |
| 2 | `thinkingmachines/inkling:free` | 2/2 (but weak on instruction-following) |
| 3 | `nvidia/nemotron-3-ultra-550b-a55b:free` | 2/2 (≡ roster reviewer twin on OpenRouter — confirms current choice) |
| 4 | Zen reviewer set that caught both 8/11 (nemotron-3-ultra-free, space-bunny-free, muse-spark-1.2/1.3, mimo-v2.6, …) | T-020 |
| 5 | `poolside/laguna-s-2.1:free` | 1/2 — missed isolation bug |
| 6 | `poolside/laguna-xs-2.1:free` | 1/2 — missed isolation bug |
| 7 | `nvidia/nemotron-3-super-120b-a12b:free` | 1/2 — missed isolation bug |

### security (isolation / SQL review)
All probed models passed (Zen 8/8 T-021; OpenRouter 4/4 T-024). Ranked by
precision secondary signal + zero-retention:
| Rank | Model | Evidence |
|---|---|---|
| 1 | `nex-agi/nex-n2.5-mini:free` | passed all incl. hr precision |
| 2 | `nex-agi/nex-n2.5-pro:free` | passed all incl. hr precision (slower) |
| 3 | `opencode/space-bunny-free` | T-021 pass, zero-retention (best for sensitive) |
| 4 | `opencode/muse-spark-1.2-contributor-free` | T-021 pass, best precision reasoning |
| 5 | `opencode/nemotron-3-ultra-free` / `opencode/mimo-v2.6-flash-free` / `opencode/muse-spark-1.3-contributor-free` | T-021 pass |
| 6 | `cohere/north-mini-code:free` / `qwen/qwen3.8-27b:free` | T-024 pass; hr precision FAIL (detail risk) |
| 7 | `opencode/big-pickle` / `opencode/ling-3.0-flash-fin-free` | T-021 pass incl. security (big-pickle = current security agent) |

### ops / researcher
All probed models passed (Zen 8/8 T-021, OpenRouter 4/4 T-024) — no
discriminating signal on these batteries; use roster defaults.

### hr / precision (detail-critical reasoning — partial index with `now()`, honest UNKNOWN)
| Rank | Model | Evidence |
|---|---|---|
| 1 | `nex-agi/nex-n2.5-mini:free` | PASS — correct IMMUTABLE reasoning |
| 2 | `nex-agi/nex-n2.5-pro:free` | PASS |
| 3 | `opencode/muse-spark-1.2-contributor-free` | PASS — best reasoning (T-021) |
| 4 | `opencode/space-bunny-free` | PASS (T-021) |
| 5 | `opencode/mimo-v2.6-flash-free` | PASS (T-021) |
| 6 | `opencode/muse-spark-1.3-contributor-free` | PASS (T-021) |
| 7 | `opencode/nemotron-3-ultra-free` | PASS, slight "volatile" wording drift (T-021) |
| 8 | `cohere/north-mini-code:free` | FAIL — answered "Yes" (wrong) |
| 9 | `qwen/qwen3.8-27b:free` | FAIL — "Yes" + wrong reason |
| 10 | `opencode/big-pickle` / `opencode/ling-3.0-flash-fin-free` / `opencode/nemotron-3.5-lightning-free` | FAIL — "Yes" (T-021) |

## Caveats

- Single short probe per model per role = weak signal; not a benchmark. Triage only.
- Free tier may log/train on data; only synthetic/redacted content allowed.
- gemma-4-26b / gemma-4-31b: no score this session (rate-limited); re-probe later if needed.
- `nex-n2.5-pro:free` flagged: 1d uptime 90.3%, p99 latency ~187 s at check time.
- Free endpoints change/expire at any time; recheck before relying on one.