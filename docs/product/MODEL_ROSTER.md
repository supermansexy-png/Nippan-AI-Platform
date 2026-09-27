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
| `qwen/qwen3.7-flash` | Alibaba (default) | $0.03 / $0.13 (≥32k→$0.10/$0.40; ≥256k→$0.20/$0.80) | 1M | ✓ | auto + required ✓ | — | **BANNED 2026-09-25 — historical entry, do not use.** (Owner order after a False-DONE incident; see `docs/warroom/ai-scorecard.md`.) Was formerly "Primary for most roles". Fastest + cheapest among high-quality models. Supports structured_outputs + tool_choice. Benchmark pricing consistent at $0.435/$0.87/M tok (source: artificial-analysis conversion). |
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

## แหล่งสรรหาหลัก: OpenCode Go (T-035, 2026-09-26)

**OpenCode Go = คลังสรรหาหลัก (PRIMARY) ของทีม dev** — พี่เชษจ่ายค่าบริการรายเดือนแล้ว (flat $10/mo)
ส่วน OpenRouter และ OpenCode Zen เป็น **คลังสำรอง/ฉุกเฉิน** ใช้เมื่อ Go ไม่มีตัวที่เหมาะ หรือเป็น free ที่ $0 จริง ๆ

- slug ของ Go ต้องเขียน `opencode-go/<model-id>` เสมอ — เขียนเป็น `opencode/<id>` สำหรับโมเดล Go = ผิด
  และจะล้มด้วย `Unexpected server error` ที่อ่านหลอกว่าเป็นเรื่องสิทธิ์ (จริง ๆ คือชื่อผิดรูปแบบ)
- VERIFIED 2026-09-26: `GET https://opencode.ai/zen/go/v1/models` → HTTP 200, **43 ids**
  (first recorded as 35; re-verified at 43 by HR on card T-045)
- งบของ Go คิดเป็น bucket **ต่อโมเดล**: 5 ชั่วโมง = 20%, สัปดาห์ = 50%, เดือน = 100% ของวงเงินโมเดลนั้น
  → โมเดลแพงเก็บไว้ใช้สั้น ๆ กับงานสำคัญ
- retention/training: `muse-spark-1.2-contributor` และ `muse-spark-1.3-contributor` เทรนบน prompt/output
  → ห้ามใช้กับโค้ดใน repo หรือข้อมูลจริง · `grok-4.6`, `grok-4.7`, `gpt-5.6-luna`, `gpt-6-luna` เก็บ log
  30 วัน (abuse monitoring) → ห้ามใช้กับความลับ · ที่เหลือใน Go = no-training / 0-day retention
  · `opencode-go/space-bunny-free` ฟรี + zero-retention

### 43 model ids ใน Go (2026-09-26 — re-verified by HR, card T-045)

`minimax-m3`, `minimax-m2.7`, `minimax-m2.5`, `kimi-k3`, `kimi-k2.7-code`, `kimi-k2.6`,
`longcat-2.0`, `kimi-k2.5`, `glm-5.2`, `glm-5.3-flash`, `glm-5.3`, `glm-5.1`, `glm-5`,
`deepseek-v4-pro`, `deepseek-v4-flash`, `deepseek-flash`, `deepseek-v4.1-flash`,
`deepseek-v4-flash-vision-exp`, `qwen3.7-max`, `qwen3.8-max`, `qwen3.8-flash`, `qwen3.7-plus`,
`qwen3.6-plus`, `qwen3.5-plus`, `mimo-v2-pro`, `mimo-v2-omni`, `mimo-v2.6-pro`, `mimo-v2.6-flash`,
`space-bunny-free`, `longcat-2.5-preview-free`, `mimo-v2.5-pro`, `mimo-v2.5`, `hy4-preview`, `hy3`,
`hy3-preview`, `gpt-5.6-luna`, `grok-4.5`, `grok-4.7`, `grok-4.6`, `muse-spark-1.3-contributor`,
`muse-spark-1.2-contributor`, `omen-alpha`, `gpt-6-luna`

Added after the first 35-id recording (8): `kimi-k2.5`, `glm-5`, `qwen3.5-plus`, `mimo-v2-pro`,
`mimo-v2-omni`, `longcat-2.5-preview-free` (free), `hy3-preview`, `grok-4.5`.

### คู่มือเลือกตามงาน (INFERRED จาก benchmark/index + ราคา + retention — ยังไม่ใช่การแต่งตั้งรายตำแหน่ง)

| งาน | โมเดลที่แนะนำ | เหตุผล |
|---|---|---|
| วางแผน/คิดยาว ๆ (project-lead, advisor) | `opencode-go/mimo-v2.6-pro` | intelligence 46.3 เทียบเท่า Grok-4.7 (46.4) แต่ cached read ถูกกว่า ~138 เท่า ($0.0036 vs $0.50 ต่อ 1M), retention 0 วัน, context 1.05M |
| เขียน/ตรวจโค้ดชิ้นสำคัญ | `opencode-go/kimi-k3` | coding 76.2 / agentic 50.0 — เก่งสุดในกลุ่ม แต่โควตาน้อย (~490 requests/เดือน) → ใช้เฉพาะงานปลายทาง |
| งานประจำ ปริมาณมาก | `opencode-go/deepseek-v4.1-flash` | cached read $0.003, bucket ประมาณ $60 (~130,000 requests/เดือน) |
| ตรวจงาน L1–L3 | `opencode-go/space-bunny-free` | ฟรีไม่จำกัด + zero-retention |
| งานที่แตะข้อมูลอ่อนไหว | `opencode-go/mimo-v2.6-pro` หรือ `opencode-go/space-bunny-free` | retention 0 วัน |
| ตัดออกจากรายการ | `grok-4.7`, `deepseek-v4-pro` | Grok แพงเกินไป + log 30 วัน; deepseek-v4-pro intelligence 30.4 ต่ำสุดในกลุ่ม |

## แหล่งสรรหาเพิ่ม: Google และ Groq (T-064, 2026-09-27)

VERIFIED 2026-09-27 (card T-064) — ทดสอบจริงผ่าน opencode:

- **`google` — provider ใช้ได้จริง.** live probe: `google/gemini-3.5-flash-lite` → `PROBE OK`.
  opencode **ไม่ต้องมี `provider` entry** (provider ที่ authed แล้วถูกเปิดให้อัตโนมัติ) · catalogue (`models.dev`)
  มี 39 โมเดล
  - **ติดเพดานราคา:** โมเดลเดียวที่อยู่ในเพดาน `MODEL_POLICY.md` ($0.25/$1.00) คือ
    `google/gemini-2.5-flash-lite` ($0.10/$0.40) — แต่ **Google แจ้งตรง ๆ ว่าโมเดลนี้ตกรุ่นสำหรับบัญชีใหม่**
    (`no longer available to new users`) จึงใช้ไม่ได้. ตัวที่บัญชีนี้ใช้ได้จริงถูกสุดคือ
    `google/gemini-3.1-flash-lite` $0.25/**$1.50** (output เกินเพดาน 1.5 เท่า); ที่เหลือ
    `google/gemini-3.5-flash-lite` / `google/gemini-2.5-flash` = $0.30/$2.50, ตัวใหญ่ $0.75/$3.75
  - `google/gemma-4-31b-it` และ `google/gemma-4-26b-a4b-it` มี `tool_call` แต่ catalogue
    **ไม่มีข้อมูลราคา (UNKNOWN — อาจฟรี)**
  - → **ยังไม่แต่งตั้งตำแหน่งใด** จน Owner ตัดสินเรื่องเพดานราคา
- **`groq` — PARKED (Owner สั่ง "ปิด", 2026-09-27).** คีย์ถูกต้อง — Groq ตอบกลับโดยระบุ org จริง
   (`org_01m3esvje0e1eveqtdfb3r2fev`) — แต่บัญชีอยู่ขั้นฟรี `on_demand` จำกัด **8,000 tokens/นาที**
   ขณะที่คำขอเดียวของ opencode ≈ **36,900 tokens** (เกิน ~4.6 เท่า) ทุกคำขอจึงล้มด้วย
   `Request too large … Upgrade to Dev Tier`. บัญชีนี้มีเฉพาะ GPT OSS 120B/20B · Qwen 3.8 27B ·
   Safety GPT OSS 20B (**ไม่มี Llama เลย**). จะใช้ได้เมื่อ Owner อัปเกรด Dev Tier เท่านั้น — ยังไม่ทำ

### Google free tier — adopted 2026-09-27 (Owner order: เอา 2 ตัว)

**Adopted (verified HTTP 200 live probe):**
- `google/gemini-flash-lite-latest` — routine / non-sensitive work (alias auto-tracks per policy)
- `google/gemini-3.8-flash` — higher-quality non-sensitive fallback (proven 200)

**Stand-ins (probed 200, not adopted):**
- `google/gemini-3.1-flash-lite`
- `google/gemini-3.5-flash-lite`

**Excluded (unusable):**
- `google/gemini-2.5-flash-lite` → 404 "no longer available to new users"
- `google/gemma-4-31b-it` → 500 INTERNAL

**Cost:** $0 (Google FREE tier, unpaid quota) — the $0.25/$1.00 cost cap does NOT apply while on free tier.

**Limits:** UNKNOWN — Google no longer publishes exact RPM/TPM/RPD for this project; limits are per PROJECT (not per key). RPD resets at midnight Pacific. Preview models are more restricted. Read exact limits at the AI Studio rate-limit page for this key.

**Privacy caveat (Google Gemini API Additional Terms — "Unpaid Services"):** "Do not submit sensitive, confidential, or personal information to the Unpaid Services." Google uses submitted content and generated responses to improve/develop products and ML; human reviewers may read and process API input/output.

**Fail-closed scope (Project Lead):** These two models are a **free fallback for NON-SENSITIVE work ONLY**. They must NOT receive repo code, secrets, customer data, or any confidential material unless the Owner explicitly overrides in writing.

**Slug form:** `google/<model-id>` (no provider entry needed in opencode.json).

**Seat PINNING:** Still requires HR (`model-recruiter`) check + Owner approval — NOT done yet.

### Jev 1.13 Free — correction + role (2026-09-27)

- `opencode/jev-1.13-free` is NOT a chat model. It is a "System One" structured-decision model from TypeSafe AI: you send a `state` plus typed questions and it returns values + probabilities. Question types: `noul` (yes/no), `choice` (multiple choice with criteria), `score` (rubric).
- Endpoint: `https://opencode.ai/zen/v1/systemone` (not chat/completions). Zen only — it is not in the OpenCode Go list.
- Live probes today returned HTTP 200, cost $0. Examples: routing question answered `hr` (p 0.61); "does this change touch tenant isolation" 0.97; "does this delivery need Owner approval" 0.89; risk tier escalated an auth-touching change from L2 to L3 (confidence 0.99). It was also WRONG once: asked who should apply a runtime-config change, it answered "assistant" (0.70) when policy requires builder + different-model review.
- CORRECTION: the earlier roster note that `jev-1.13-free` "failed the T-020 test" judged it as a chat model — the wrong tool for that test, not a defective model.
- It cannot be used as a seat (it produces no text). Candidate use: a cheap pre-screen/gate signal only; never the deciding authority where a written rule applies. Free is limited-time; the paid twin `opencode/jev-1.13` is $0.042 input / free output.
- Evidence: `runs/jev_probe.cjs` (gitignored scratch harness).

### Provider scan 2026-09-27 — candidates only, NOT adopted

One line each, VERIFIED (from the provider's own page) unless marked otherwise:
- NVIDIA NIM (build.nvidia.com): free inference listed for kimi-k3, deepseek-v4-pro-0813, nemotron-3.5-lightning; function calling; NVIDIA API Trial Terms — do not submit confidential data; free-tier rate limits UNVERIFIED.
- DeepInfra: DeepSeek-V4-Flash-0731 at $0.06/$0.18; no free tier (top-up required); retention UNVERIFIED.
- Z.ai (GLM): GLM-4.7-Flash free with function calling; GLM-5.3-Flash $0.15/$0.50; a Coding Plan at $18/month exists; consumer privacy policy permits training; free-tier rate limits UNVERIFIED.
- Cerebras: $5 trial credit, 30 days, card required; very high throughput (~3,000 tok/s) on gpt-oss-120b / qwen-3.8-27b; no permanent free tier.
- Mistral: free plan gives $10/month API credit; card required; retention page not reachable (UNVERIFIED).
- Dead / not applicable: GitHub Models retired 2026-07-30; Hyperbolic and Nebius are GPU clouds only; SambaNova requires a card and is expensive (DeepSeek $3/$4.50); Chutes has no free tier; Vercel AI Gateway is a router, not a provider.
none of these is adopted; every one still needs a live probe plus a retention check before it may touch repo code or confidential data.

> **Free-tier policy (Owner directive 2026-09-27 — scope RESOLVED, answered "ก"):** free models are **backup-only and task-scoped**, never a standing primary. The rule covers **external shared-pool free tiers only** — OpenRouter `:free`, Groq free, Google free. **OpenCode-hosted free models** (Zen `*-free`, Go `longcat-2.5-preview-free`, `space-bunny-free`) are **NOT** covered and may stay in Primary slots. Compliance VERIFIED 2026-09-27: no external `:free` model holds a Primary slot in this table or in `opencode.json` → **no pin change required**. See `docs/project-memory/DECISIONS.md` 2026-09-27.

## Per-role staffing — T-065 re-staff (2026-09-27) — **AUTHORITATIVE: 3 tiers per role**

Owner-approved 2026-09-27 (card T-065). Every seat now has **Primary + Backup 1 + Backup 2** (Owner order: models here die often).
Every row below was **fired live** on 2026-09-27 — none of it is catalogue-only. Cost is the measured per-call cost from the round-1 probe (`runs/*t065-*`).

| # | Role | Primary | Backup 1 | Backup 2 | Measured cost per call | Why |
|---|---|---|---|---|---|---|
| 1 | **project-lead** | `opencode-go/longcat-2.5-preview-free` | `opencode/nemotron-3-ultra-free` | `openrouter/deepseek/deepseek-v4.1-flash` | $0 / $0 / $0.00057–0.00162 | Owner order 2026-09-27: free **and** faster than the Go `mimo-v2.6-pro` (12,977 ms). Free, 1M-token context = satisfies "long context". Backup 1 is the proven ex-primary because `longcat` is still a *preview* with one sample. |
| 2 | **builder** | `opencode-go/glm-5.3-flash` | `openrouter/poolside/laguna-s-2.1:free` | `opencode-go/kimi-k3` | $0.00694 / $0 / $0.1333 | Builder must follow spec exactly. `kimi-k3` is the best coder (76.2) but ~19× the cost and quota-limited → kept as the escalation tier, not the front line. |
| 3 | **reviewer L1–L3** | `opencode/muse-spark-1.3-contributor-free` | `openrouter/nvidia/nemotron-3.5-lightning:free` | `opencode-go/space-bunny-free` | $0 / $0 / $0 | Reviewer must run real tests, not trust the author. RISK: `muse-spark-*` trains on prompts → no secrets. Backup 2 is the only stated zero-retention free seat. |
| 4 | **security L1–L3** | `openrouter/deepseek/deepseek-v4.1-flash` | `opencode-go/qwen3.8-flash` | `openrouter/qwen/qwen3.8-flash` | $0.00057–0.00162 / $0.00705 / $0.00705 | Owner order: the OpenRouter deepseek goes to roles that are **important but context-light** — security reviews a diff, not a whole corpus. |
| 5 | **ops** | `opencode/mimo-v2.6-flash-free` | `opencode-go/mimo-v2.6-flash` | `openrouter/nvidia/nemotron-3.5-lightning:free` | $0 / $0.00664 / $0 | Ops needs fast + cheap + repeatable, not deep. Re-measured 2026-09-27: the Primary is normally 0.7–0.9 s (one 34 s outlier on a cold start — see caveat below). |
| 6 | **researcher** | `opencode-go/longcat-2.5-preview-free` | `openrouter/nvidia/nemotron-3.5-lightning:free` | `openrouter/deepseek/deepseek-v4.1-flash` | $0 / $0 / $0.00057–0.00162 | Researcher must verify and admit ignorance, not dress up an answer. |
| 7 | **model-recruiter (HR)** | `opencode/nemotron-3-ultra-free` | `opencode-go/space-bunny-free` | `openrouter/nvidia/nemotron-3.5-lightning:free` | $0 / $0 / $0 | HR must check facts, never assume "it probably still exists". All three tiers are free. |
| 8 | **assistant** | `opencode/nemotron-3-ultra-free` | `opencode-go/mimo-v2.6-flash` | `openrouter/openrouter/free` | $0 / $0.00664 / $0 | Helper seat. Backup 2 is the Free Models Router — **nested slug required**; it picks a different model per call, which is fine for throwaway helper work only. |
| 9 | **advisor** | `opencode/mimo-v2.6-flash-free` | `openrouter/deepseek/deepseek-v4.1-flash` | `opencode-go/mimo-v2.6-pro` | $0 / $0.00057–0.00162 / $0.02093 | Advisor is called rarely but must think deeply about direction; the expensive deep seat sits at tier 3 where it is only reached if both free/cheap tiers fail. |

**Anti-redundancy (T-023) — PASS:** reviewer and security share no model with builder's Primary or Backup.
`builder = {glm-5.3-flash, laguna-s-2.1:free, kimi-k3}` · `reviewer = {muse-spark-1.3-contributor-free, nemotron-3.5-lightning:free, space-bunny-free}` · `security = {deepseek-v4.1-flash(OR), qwen3.8-flash, qwen3.8-flash(OR)}` → all pairwise intersections with builder = ∅.

**Latency caveat (disclosed):** durations below come from live runs but with **one sample each**, and the short-prompt runs are naturally faster than the 3-line runs — so treat the numbers as indicative, not a benchmark. Free-seat medians measured 2026-09-27: `nemotron-3-ultra-free` 0.68 s · `mimo-v2.6-flash-free` 0.72–0.85 s · `longcat-2.5-preview-free` 1.2–2.1 s · `space-bunny-free` 4.1 s · `nemotron-3.5-lightning:free` (OR) 4.1 s · `inkling-small:free` 4.8 s · `muse-spark-1.3-contributor-free` 7.9 s.

**Do NOT use:** `opencode/nemotron-3.5-lightning-free` (dead endpoint — was pinned to ops/researcher and used as `small_model`) · `opencode-go/ox-alpha-free` (listed free but fails live, 2/2) · `opencode/big-pickle` · `opencode/ling-3.0-flash-fin-free` · `opencode/muse-spark-1.2-contributor-free` · `opencode/deepseek-v4-flash-free` · `openrouter/nex-agi/*` · `qwen/qwen3.7-flash` (BANNED) · all `groq/*` (parked: free tier 8k TPM < 36.9k/request).

**Slug traps (learned the hard way):** `openrouter/free` fails with an opaque server error at all four attempts; the router must be referenced as **`openrouter/openrouter/free`** (the id already contains its provider) — and that form passed 2/2. Always re-check the slug form before declaring a model broken.

## Per-role staffing (T-014 re-staffed — ตารางข้างล่างคือสถานะจริง 2026-09-26) — **SUPERSEDED by the T-065 table above**

Each role has Primary + Backup from a different provider.

Anti-regression rule: all Primary↔Backup pairs use different providers.
Anti-redundancy rule (MODEL_POLICY §): reviewer/security must use DIFFERENT MODEL from builder's Primary AND Backup.

| # | Role | Primary Model | Primary Provider | Backup Model | Backup Provider | Reasoning |
|---|---|---|---|---|---|---|
| 1 | **project-lead** | `opencode/nemotron-3-ultra-free` | OpenCode Zen | `openrouter/deepseek/deepseek-v4.1-flash` | OpenRouter | **CHANGED 2026-09-26 (T-042 re-pin, Owner order: "สลับ pl ไปตัวฟรี").** Free Zen; Backup is paid OpenRouter (effectively unusable at current credit). Anti-redundancy PASS. Takes effect after Owner restarts opencode. |
| 2 | **builder** | `openrouter/poolside/laguna-s-2.1:free` | OpenRouter | `opencode-go/glm-5.3-flash` | OpenCode Go | **CHANGED 2026-09-27 (T-035 free migration):** moved from paid Go to live free OpenRouter. Probe: PROBE OK. Former Go primary becomes Backup. `qwen/qwen3.7-flash` permanently banned. |
| 3 | **reviewer L1–L3** | `opencode/muse-spark-1.3-contributor-free` | OpenCode Zen | `openrouter/nvidia/nemotron-3.5-lightning:free` | OpenRouter | **CHANGED 2026-09-27 (Owner order: space-bunny too slow).** Free Zen. Probe 2026-09-27: PROBE-OK + correct self-id, ~2s, clean stop (`runs/2026-09-26T21-25-34Z-t035-reviewer-probe`). Former primary becomes Backup. RISK disclosed: `muse-spark-*` pins failed 2026-09-26 with a dead cached id (`muse-spark-1.2-contributor-free` in `opencode.global.dat`) on ops/researcher seats — if the reviewer agent fails to open after restart, revert this row to the Backup. Zen may log/train → no secrets/customer data. |
| 3b | **reviewer L4** | `anthropic/claude-opus-5.5:batch` | OpenRouter | — | — | Paid, Batch API only, Owner-approved per use. Not offered in Go. |
| 4 | **security L1–L3** | `opencode-go/kimi-k3` | OpenCode Go | `openrouter/qwen/qwen3.8-flash` | OpenRouter | **BACK ON THE GO PATH 2026-09-27 (Owner order, card T-058).** The 2026-09-27 free migration had left the seat on `opencode/space-bunny-free` — a *different route* from the one with proven results, which the Owner rejected after the check. `opencode-go/kimi-k3` = production, 0-day retention, inside the paid Go pool, and it is the model that actually audited the T-034b advisor run (`ADVISOR_LOG.md`). Pair restored to the T-045 appointment (primary Go + paid OpenRouter backup). Anti-redundancy: ≠ builder (laguna-s-2.1:free, glm-5.3-flash), ≠ reviewer (muse-spark-1.3-contributor-free, nemotron-3.5-lightning:free). |
| 5 | **ops** | `opencode/nemotron-3.5-lightning-free` | OpenCode Zen | `opencode-go/mimo-v2.6-flash` | OpenCode Go | **CHANGED 2026-09-27 (T-035 free migration):** moved from Go to free Zen. Former Go primary becomes Backup. |
| 6 | **researcher** | `opencode/nemotron-3.5-lightning-free` | OpenCode Zen | `openrouter/nvidia/nemotron-3.5-lightning:free` | OpenRouter | Free; unchanged by T-035 free migration (already free Zen). |
| 7 | **model-recruiter (HR)** | `opencode/nemotron-3-ultra-free` | OpenCode Zen | `opencode-go/gpt-6-luna` | OpenCode Go | **CHANGED 2026-09-27 (T-035 free migration):** moved from Go to free Zen. Former Go primary becomes Backup. Note: gpt-6-luna keeps 30-day abuse logs → never for secrets. |
| 8 | **assistant** | `opencode/nemotron-3-ultra-free` | OpenCode Zen | `opencode-go/mimo-v2.6-flash` | OpenCode Go | Free helper; unchanged by T-035. |
| 9 | **advisor (NEW)** | `opencode/mimo-v2.6-flash-free` | OpenCode Zen | `opencode-go/mimo-v2.6-pro` | OpenCode Go | **CHANGED 2026-09-27 (T-035 free migration):** moved from Go to free Zen. Probe: T-042 confirmed 3× live launches. Former Go primary becomes Backup. |

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
- **Model-id format for opencode (verified 2026-09-26)**: an OpenRouter model must be passed to `--model` / agent frontmatter with the
  provider prefix. `openrouter/nvidia/nemotron-3.5-lightning:free` launches (probe: "PROBE OK"), while the bare
  `nvidia/nemotron-3.5-lightning:free` fails with an opaque `Unexpected server error` — which is easy to misread as a free-tier
  guardrail or a broken endpoint. The model itself was reachable through the OpenRouter API at the same time, so when a job fails
  that way, check the slug format first. All `.opencode/agents/*.md` pins were verified to use the prefix on 2026-09-26.
- **HR checklist (mandatory, Owner order 2026-09-26)**: whenever `model-recruiter` reports on, recommends, or is asked to check a
  model, it must (1) write the slug with its provider prefix (`openrouter/<author>/<slug>` or `opencode/<slug>`), and (2) state the
  format check explicitly before declaring a model unavailable — a bare slug fails with an opaque `Unexpected server error` that
  looks like a guardrail/permission problem but is a naming problem.
- **Next recommended scan**: quarterly or upon major model releases (e.g., new GPT/Claude generations, open-source frontier drops).

## Review tiers (T-020 — Owner approved 2026-09-25)

Review/security model is chosen by risk level (TASK_CONTROL §3). Covers L1, L2 and L3.

| Tier | reviewer / security Primary | Backup | Notes |
|---|---|---|---|
| L1/L2 (reversible, non-sensitive) | reviewer: `opencode-go/space-bunny-free` · security: `opencode-go/kimi-k3` | `opencode/nemotron-3-ultra-free` | Caught both planted bugs in the T-020 test. Reviewer model ≠ security model (T-023). **Updated 2026-09-26 (T-045):** the security primary `openrouter/nex-agi/nex-n2.5-mini:free` died (author `nex-agi` has 0 models left) and is replaced by `opencode-go/kimi-k3` (production, 0-day retention, inside the paid Go pool); its Backup is `openrouter/qwen/qwen3.8-flash` (paid). The old L1/L2 stand-ins (`opencode/nemotron-3-ultra-free`, `opencode/big-pickle`) no longer exist / are no longer assigned. |
| L3 (hard to undo / sensitive) | `opencode-go/space-bunny-free` | `opencode/nemotron-3-ultra-free` | `space-bunny-free` = stated zero-retention (runs on OpenCode Go since 2026-09-26). L3 inputs must be redacted. |
| **L4 (critical / high-accuracy verification)** | **`anthropic/claude-opus-5.5:batch`** | — (Owner will appoint if needed) | **Paid, Owner-selected 2026-09-25. Intelligence 57.6 (highest shortlisted); batch $2/$10 per 1M (real-time $4/$20).** Exceeds the normal MODEL_POLICY cap — this is an explicit Owner-approved L4 exception; it is used rarely. E.g. security boundary, tenant/bot isolation, data-handling reviews. **Approval per use (Owner 2026-09-25): the Owner approves, or the PL approves on the Owner's behalf when the Owner is unavailable; Batch API (`:batch`) is required; this is a normal review step, not an Independent Audit — see `AGENTS.md` §Independent Audit Status.** |
| Paid fallback (free endpoint down) | `anthropic/claude-opus-5.5:batch` | — | Batch $2/$10 per 1M. |

Facts / caveats (verified 2026-09-25):
- Zen free tier works ONLY inside opencode (`POST /zen/v1/chat/completions` → 403 `FreeTierError`). Requires the Zen provider connected in opencode auth.
- Most Zen free models log/train on data during the free period (`muse-spark-*` = Meta trains; `nemotron-*` = trial, no confidential data). `space-bunny-free` is the only stated zero-retention one → use it for L3/sensitive.
- Free endpoints can be unstable: `jev-1.13-free`, `deepseek-v4-flash-free`, `mimo-v2.5-free` failed the T-020 test.
- Anti-redundancy: none of these equals builder Primary `z-ai/glm-5.3-flash` or Backup `nvidia/nemotron-3.5-lightning`. `nemotron-3.5-lightning-free` is EXCLUDED (duplicates builder Backup). Reviewer and security free models also differ from each other.
- **Batch rule (Owner 2026-09-25): every non-urgent PAID task must go through the Batch API** (`:batch` variant, ~40–60% cheaper); free-tier work stays synchronous. Batch works at any risk level but needs a `:batch` endpoint — available today include `z-ai/glm-5.3-flash:batch` ($0.06/$0.20), `deepseek/deepseek-v4.1-flash:batch`, and `anthropic/claude-opus-5.5:batch` ($2/$10); the free Zen models have none.
- **L4 is a review tier, not a TASK_CONTROL risk level.** `TASK_CONTROL.md §3` still defines only L1–L3 and is a protected document; formalising L4 as a task risk level would need its own L3 card.

## Enforcement (added 2026-09-24 per Owner incident order)

Triggered by Incident: reviewer used `qwen3.7-flash` instead of required `z-ai/glm-5.3-flash`, violating anti-redundancy cross-checks. Also triggered by lack of live DB query evidence for L3 DELIVERY closeout.

When Project Lead invokes specialist agents:
1. Every task card INTAKE/DELIVERY must explicitly name the model slug being used (e.g., "builder (qwen3.7-flash)")
2. Reviewer/security reviews use the tiered model per "Review tiers" above: L1/L2 → free Zen (`space-bunny-free` etc.); L3/sensitive → `opencode/space-bunny-free`; L4/critical (paid) → `anthropic/claude-opus-5.5:batch`. The builder model is never allowed (anti-redundancy). State the model in the START_PROMPT.
3. Database-related tasks require live query evidence (`supabase_execute_sql` output or `supabase_list_tables` output) in DELIVERY reports. File existence alone is insufficient proof.
4. Any future violation: HR will blacklist the non-compliant model from specialist roles immediately. 如果再发生类似事件 [model name] 将被禁止从 HR 调用执行工作.

## Team update 2026-09-25 (Owner-approved appointments)

> **Superseded 2026-09-26 (T-035):** the "Per-role staffing" table at the top of this file is the
> authoritative one. The rows below are kept as history only — in particular the `ops` and
> `researcher` free pins and the builder lock were replaced when the team moved onto **OpenCode Go**.

Supersedes the earlier builder and L4 assignments in this file. Builder Primary is now GLM (Owner plan); the L4 paid reviewer slot is now filled by `anthropic/claude-opus-5.5:batch` (Owner-selected 2026-09-25).

| Role | Primary | Backup | Why / evidence status |
|---|---|---|---|
| builder | `z-ai/glm-5.3-flash` | `nvidia/nemotron-3.5-lightning` | Primary is Owner-approved, callable per Owner-provided evidence; live catalogue confirms tools + structured_outputs, 1.31M context, coding index 71.5. Nemotron backup kept as directed; live-call readiness **UNKNOWN** (catalogue metadata only). `qwen/qwen3.7-flash` is **PERMANENTLY BANNED** per `docs/warroom/ai-scorecard.md` until Owner reverses. |
| assistant | `opencode/nemotron-3-ultra-free` | `opencode/muse-spark-1.3-contributor-free` | Owner chose option A; completed usage-tracker task that mimo failed silently (57.9s vs 138s no-output). |
| reviewer (L1/L2/L3) | `opencode/muse-spark-1.3-contributor-free` | `openrouter/nvidia/nemotron-3.5-lightning:free` | **CHANGED 2026-09-27 (Owner: space-bunny too slow).** Probe PROBE-OK. Cache-bug revert path: back to the Backup if the agent fails to open after restart. |
| security (L1/L2/L3) | `openrouter/nex-agi/nex-n2.5-mini:free` | `opencode/muse-spark-1.3-contributor-free` | Fallback guide first pick; see free-model evidence and caveats below. |
| ops | `opencode/mimo-v2.6-flash-free` | `opencode/nemotron-3-ultra-free` | **CHANGED 2026-09-26 (PL, delegated authority):** the previous pin `opencode/muse-spark-1.3-contributor-free` failed at runtime with "Model not found: …muse-spark-1.2-contributor-free" (dead id cached app-side in `opencode.global.dat`). New primary verified to launch; free; distinct from reviewer/security/builder/assistant. |
| researcher | `opencode/nemotron-3.5-lightning-free` | `opencode/mimo-v2.6-flash-free` | **CHANGED 2026-09-26 (PL, delegated authority):** same muse-spark runtime failure as `ops`; new primary verified to launch; free; distinct from reviewer/security/builder/assistant. (ling-3.0 failed its probe earlier and is not used.) |
| reviewer L4 (paid) | `anthropic/claude-opus-5.5:batch` | — | **APPOINTED by Owner 2026-09-25** (single model, Owner chose one only). Intelligence 57.6 (highest of the shortlist); batch $2/$10 per 1M (real-time $4/$20) → batch is ~50% cheaper. Used rarely; explicit Owner-approved exception to the normal MODEL_POLICY cap. |

**Live catalogue correction (2026-09-25):** `z-ai/glm-5.3-flash` is currently **$0.045 input / $0.60 output per 1M tokens**, not the roster's stale $0.15/$0.50. `get-model` confirms tools, tool_choice and structured_outputs; context 1,310,720; Artificial Analysis coding 71.5, intelligence 41.8, agentic 50.9. Its `:batch` price is $0.06/$0.20 (not the real-time price).

**L4 paid reviewer — APPOINTED (Owner decision 2026-09-25): `anthropic/claude-opus-5.5:batch`.** Live catalogue (verified 2026-09-25): intelligence 57.6; tools + tool_choice + structured_outputs; context 1,000,000; batch $2/$10 per 1M (real-time $4/$20 → batch ~50% cheaper); illustrative cost for 100k input + 20k output ≈ **$0.40 per review**. This exceeds the normal MODEL_POLICY cap ($0.25/$1.00) by design — an explicit, rare-use Owner exception for critical verification only. No paid inference probe was run; price/capability are catalogue-VERIFIED, live behaviour on a first real review is UNKNOWN.

Superseded shortlist (kept only for the record; Owner chose ONE model — Opus 5.5):

| Candidate | Batch price (input/output per 1M) | `:batch` | Capability / reason |
|---|---:|---|---|
| `openai/gpt-6-luna:batch` | $0.05 / $0.25 | Listed | Live endpoint metadata supports tools, tool_choice and structured_outputs; 1.05M context, intelligence index 37.3. Lowest-cost listed batch candidate; OpenAI family/provider differs from GLM/Z.ai. |
| `deepseek/deepseek-v4.1-flash:batch` | $0.112 / $0.336 | Listed | Live metadata supports tools, tool_choice and structured_outputs; 1.05M context, intelligence index 39.5. Stronger listed intelligence index; DeepSeek family/provider differs from GLM/Z.ai. |

Illustrative cost for 100k input + 20k output tokens: GPT-6 Luna batch ≈ **$0.010**; DeepSeek V4.1 Flash batch ≈ **$0.01792**. Both fit MODEL_POLICY's new-model limits. Candidate catalogue entries are live; no paid inference probe was run, so behavior/readiness beyond metadata is **UNKNOWN**. OpenRouter model detail records the `:batch` variants/prices; recent endpoint performance shown for the realtime listings is not a guarantee of batch completion time.

**Catalogue breadth evidence / limitation (2026-09-25):** the existing T-014 scan above recorded five whole-catalogue slices, ~250+ unique models, on 2026-09-24. This refresh verified live `get-model` details for GLM, GPT-6 Luna, DeepSeek V4.1 Flash, Qwen3.7 Flash and Nemotron 3.5 Lightning, plus both proposed `:batch` variants. Attempts to refresh full-catalogue list slices were rejected by the catalogue tool when category and supported-parameter filters were combined; therefore a new full-catalogue breadth refresh is **UNVERIFIED** and no claim is made that these are the only eligible candidates. No new roster appointment is made until the required breadth scan and Owner review are complete.

**Anti-redundancy proof (model IDs, ignoring `:batch` routing variant):**

```
Builder        = { z-ai/glm-5.3-flash, nvidia/nemotron-3.5-lightning }
Free reviewer  = { opencode/space-bunny-free, thinkingmachines/inkling-small:free }
Security       = { nex-agi/nex-n2.5-mini:free, opencode/muse-spark-1.3-contributor-free }
L4 (paid)      = { anthropic/claude-opus-5.5 }
All pairwise intersections = ∅  (PASS)
```

The free model sets / retention caveats and earlier option-A evidence remain as recorded above in this section's prior roster history and `docs/product/FREE_MODEL_FALLBACK_GUIDE.md`. Changes here are documentation/recruitment records only; no agent config or routing was changed.
