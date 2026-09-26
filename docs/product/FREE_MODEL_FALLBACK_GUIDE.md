> **HISTORICAL REFERENCE — superseded 2026-09-26 (T-035/T-038).** The dev team moved onto the paid
> **OpenCode Go** provider; the current Primary/Backup pins live in `docs/product/MODEL_ROSTER.md`
> § "แหล่งสรรหาหลัก: OpenCode Go". Models named in this file such as `opencode/big-pickle`,
> `opencode/ling-3.0-flash-fin-free` and `opencode/mimo-v2.6-flash-free` **no longer exist / are no
> longer assigned**. Keep this file for the historical cross-run evidence only.

# Free model fallback guide (dev-time)

Status: **RECORD ONLY — reference guide** (Owner order 2026-09-25: เก็บไว้ใช้
เมื่อตำแหน่งต่าง ๆ ขาด จะได้หยิบตัวฟรีมาใช้ทดแทนได้). Does NOT change
`MODEL_ROSTER.md`.

Purpose: when a staffed dev role's Primary/Backup is unavailable (or to avoid
paid spend), pick a free substitute from THIS list. Every candidate here was
probe-tested on real role batteries — Zen set (T-021: 8 models × 5 roles,
reviewer-ACCEPTED) and OpenRouter set (T-024: 10 scored models, reviewer-ACCEPTED).

Source records:
- `docs/product/FREE_MODEL_ZEN_TEST_T021.md` (Zen `opencode/*-free`)
- `docs/product/FREE_MODEL_OPENROUTER_TEST_T024.md` (OpenRouter `<author>/<model>:free`)

## Ranked per role (best → worst, from probe evidence)

### builder — write code to spec inline, no file writes
1. `nex-agi/nex-n2.5-mini:free` (5/5 all roles, fast)
2. `nex-agi/nex-n2.5-pro:free` (5/5; slow / uptime-flagged)
3. `thinkingmachines/inkling-small:free` (builder ✅ + reviewer 2/2 — best coding-line)
4. `qwen/qwen3.8-27b:free` (builder ✅ ; precision FAIL)
5. `cohere/north-mini-code:free` (builder ✅ ; precision FAIL)
6. `poolside/laguna-s-2.1:free` / `laguna-xs-2.1:free` (builder ✅ ; reviewer 1/2)
7. `nvidia/nemotron-3-super-120b-a12b:free` (builder ✅ ; reviewer 1/2)
8. Zen set that passed builder 7/8: `opencode/mimo-v2.6-flash-free`, `muse-spark-1.2/1.3-contributor-free`, `nemotron-3-ultra-free`, `space-bunny-free`, `big-pickle`, `ling-3.0-flash-fin-free`
9. AVOID (wrote files instead of inline code): `thinkingmachines/inkling:free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `opencode/nemotron-3.5-lightning-free`

### reviewer — planted-bug spot (tenant/bot isolation + off-by-one)
1. `thinkingmachines/inkling-small:free` (2/2, fast)
2. `thinkingmachines/inkling:free` (2/2; weak on instruction-following)
3. `nvidia/nemotron-3-ultra-550b-a55b:free` (2/2; ≡ roster reviewer twin on OpenRouter — confirms current choice)
4. Zen set caught both 8/11 (T-020): `opencode/nemotron-3-ultra-free`, `space-bunny-free`, `muse-spark-1.2/1.3-contributor-free`, `mimo-v2.6-flash-free`, …
5. AVOID (missed the isolation bug — never for review/security):
   `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `nvidia/nemotron-3-super-120b-a12b:free`

### security — isolation / SQL review (all probed passed; ranked by precision + zero-retention)
1. `nex-agi/nex-n2.5-mini:free` (passed all incl. precision)
2. `nex-agi/nex-n2.5-pro:free` (passed all incl. precision; slower)
3. `opencode/space-bunny-free` (zero-retention — best for sensitive/L3)
4. `opencode/muse-spark-1.2-contributor-free` (best precision reasoning, Zen)
5. `opencode/nemotron-3-ultra-free` / `opencode/mimo-v2.6-flash-free` / `opencode/muse-spark-1.3-contributor-free`
6. OK but detail-risky: `cohere/north-mini-code:free`, `qwen/qwen3.8-27b:free`

### ops / researcher
All probed models passed (Zen 8/8, OpenRouter 4/4) — no discriminating signal.
Grab order: `nex-agi/nex-n2.5-mini:free` → `opencode/muse-spark-1.2-contributor-free`
→ `opencode/mimo-v2.6-flash-free` → any roster free model.

### hr / precision (detail-critical, honest-UNKNOWN behaviour)
1. `nex-agi/nex-n2.5-mini:free` / `nex-agi/nex-n2.5-pro:free` (correct IMMUTABLE reasoning)
2. `opencode/muse-spark-1.2-contributor-free` (best reasoning, Zen)
3. `opencode/space-bunny-free`, `opencode/mimo-v2.6-flash-free`, `opencode/muse-spark-1.3-contributor-free`
4. `opencode/nemotron-3-ultra-free` (slight wording drift)
5. AVOID (answered "Yes" wrong on SQL partial-index): `cohere/north-mini-code:free`,
   `qwen/qwen3.8-27b:free`, `opencode/big-pickle`, `opencode/ling-3.0-flash-fin-free`,
   `opencode/nemotron-3.5-lightning-free`

## Per-role substitute table (1st / 2nd / 3rd pick when roster model unavailable)

| Role (roster Primary) | Free substitute 1st | 2nd | 3rd |
|---|---|---|---|
| builder (paid `z-ai/glm-5.3-flash`) | `nex-agi/nex-n2.5-mini:free` | `nex-agi/nex-n2.5-pro:free` | `thinkingmachines/inkling-small:free` |
| reviewer L1/L2 (`opencode/nemotron-3-ultra-free`) | `thinkingmachines/inkling-small:free` | `thinkingmachines/inkling:free` | `opencode/space-bunny-free` |
| reviewer L3 (`opencode/space-bunny-free`) | `thinkingmachines/inkling-small:free` | `nvidia/nemotron-3-ultra-550b-a55b:free` | `opencode/muse-spark-1.2-contributor-free` (L3 inputs must stay redacted) |
| security (`opencode/big-pickle`) | `nex-agi/nex-n2.5-mini:free` | `opencode/space-bunny-free` (zero-retention) | `opencode/muse-spark-1.2-contributor-free` |
| ops (`opencode/big-pickle`) | `opencode/muse-spark-1.2-contributor-free` | `opencode/mimo-v2.6-flash-free` | `opencode/space-bunny-free` |
| researcher (`opencode/ling-3.0-flash-fin-free`) | `opencode/muse-spark-1.2-contributor-free` | `opencode/mimo-v2.6-flash-free` | `opencode/space-bunny-free` |
| assistant (`opencode/mimo-v2.6-flash-free`) | `opencode/muse-spark-1.2-contributor-free` | `opencode/big-pickle` | `opencode/space-bunny-free` |
| model-recruiter (paid `openai/gpt-6-luna`) | `nex-agi/nex-n2.5-mini:free` (precision-proven) | `opencode/muse-spark-1.2-contributor-free` | `opencode/space-bunny-free` |
| L4 verify (paid `anthropic/claude-opus-5.5:batch`) — Owner-selected; free fallback ONLY if Owner approves | `nex-agi/nex-n2.5-mini:free` | `opencode/space-bunny-free` (zero-retention) | `opencode/muse-spark-1.2-contributor-free` |

**The four rows directly above are historical pins (2026-09-25); see MODEL_ROSTER.md for the current ones.**

Anti-redundancy check for the substitutes above: none of the free picks equals
builder Primary `z-ai/glm-5.3-flash` or Backup `nvidia/nemotron-3.5-lightning`;
reviewer pick ≠ security pick at 1st/2nd (inkling-small/inkling vs nex-n2.5-mini/
space-bunny). If staffing multiple roles at once with these, keep the same
anti-redundancy discipline as `MODEL_ROSTER.md`.

## Hard rules when substituting

1. Free tier (Zen AND OpenRouter) may log/train → synthetic/redacted data only, no secrets.
2. Zen free works ONLY inside opencode (raw HTTP → 403); OpenRouter `:free` needs
   the workspace guardrail open (T-024: "Free model training violation" block —
   Owner opened it once; re-check before relying).
3. One probe per model per role = weak signal. Re-probe before a long-term assignment.
4. L4 remains paid-GLM by Owner policy — free fallback only with explicit Owner approval.
5. When a substitute is used in a real task, name the model slug in the card INTAKE/DELIVERY (enforcement rule).

## Coverages & gaps

- Covered roles: builder, reviewer (L1–L3), security, ops, researcher, assistant,
  HR precision, L4 fallback suggestion.
- No score: `google/gemma-4-26b-a4b-it:free`, `google/gemma-4-31b-it:free`
  (rate-limited whole T-024 session) — re-probe before any use.
- Every ranked entry = VERIFIED against raw probe files (reviewer-ACCEPTED records).