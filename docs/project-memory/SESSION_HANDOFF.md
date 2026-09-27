<!-- AUTO-HANDOFF:START -->
## Handoff ล่าสุด (auto) — 2026-09-27
**หัวข้อ:** Session 10 handoff — Google 2 models, free-tier policy, Jev tool (T-068 handed to advisor)

## Session 10 — 2026-09-27 (PL, dev-workspace) — Owner consulting session; Jev/Google/provider work

Owner used this session for consultation + a few adopted decisions. All work is **committed locally on `dev-workspace`, NOT pushed** (Owner: "รอทีเดียว" — push the whole batch at once).

### Decisions taken (Owner, 2026-09-27)
1. **Google free tier adopted — exactly 2 models**: `google/gemini-flash-lite-latest` + `google/gemini-3.8-flash` (card T-067). Free tier = $0 but Google trains on + human-reviews submitted content → never repo code/secrets/customer data. Live-probed 200. Not usable for the $0.25/$1.00 price cap debate because it is free.
2. **Free-tier policy (scope resolved, Owner answered "ก")**: free = **backup-only, task-scoped, never a standing primary** — covering **external shared-pool free only** (OpenRouter `:free`, Groq, Google). OpenCode-hosted free (Zen `*-free`, Go `longcat-2.5-preview-free`, `space-bunny-free`) is **not** covered and may stay primary. Compliance VERIFIED: no external `:free` holds a Primary slot in the T-065 table or in `opencode.json` → no pin change needed.
3. **Jev 1.13 Free adopted as a screening TOOL** (not a seat). Pilot: review-tier 5/5, Owner-approval 5/5, auth/tenant flag 4/5, dangerous under-classification 0/5 (n=5). Tool only: Zen-hosted (`/zen/v1/systemone`), emits no text, cannot be a seat. Accepted uses locked in card T-068.

### Open items (the single list)
- **T-068 (HANDED OVER)** — build the Jev gate helper `scripts/jev_gate.mjs`. Two failed attempts today: (a) Task-tool `builder`/`glm-5.3-flash` → **FALSE DONE**, no file created (recorded in `ai-scorecard.md`, commit `64af977`); (b) headless run with backup model `openrouter/poolside/laguna-s-2.1:free` → **opencode rejected `--agent builder`** ("builder is a subagent, not a primary agent. Falling back to default agent") so it ran as the **default agent** and produced nothing. **Correct approach: `--agent worker`.** Owner will **restart opencode**, then the **advisor** follows this card. No runtime file exists; nothing to clean up.
- **T-067** — Google adoption: HR proposed researcher/HR/assistant/advisor as eligible; **PL reservation recorded** (assistant+advisor read/write internal docs → not clean; eligibility is TASK-level, not seat-level). Still needs the real free-tier limits from the AI Studio page (Owner) + Owner approval before any pin.
- **Push deferred** — local commits `9c9b2bf`, `6a997db`, `82c847e`, `f556a48`, `885a8ba`, `42d14db`, `64af977`, `f7c2d70`.
- **Restart opencode** still pending (Owner has another window with work in flight). NOTE: this session still ran on paid `openrouter/deepseek/deepseek-v4.1-flash`; restart puts PL back on the free pin. OpenRouter credit ≈ **$3.38**.
- **Another window's uncommitted change**: `docs/warroom/ADVISOR_LOG.md` (n8n publish entry; the other session's commit `6f07713` exists). **Do not touch it.**

### Findings worth keeping
- `npx add-mcp "https://gemini-api-docs-mcp.dev"` — official Google (documented on ai.google.dev). MCP only or MCP+skills not decided.
- Provider scan (recorded in `MODEL_ROSTER.md`, candidates only NOT adopted): NVIDIA NIM free (kimi-k3 / deepseek-v4-pro-0813 / nemotron-3.5-lightning, function calling, Trial Terms → no confidential data, rate limits UNVERIFIED) · DeepInfra `deepseek-v4-flash-0731` $0.06/$0.18 · Z.ai GLM-4.7-Flash free + Coding Plan $18/mo · Cerebras $5/30-day trial, very fast · Mistral free plan $10/mo credit. Dead: GitHub Models retired 2026-07-30, Hyperbolic/Nebius GPU-only, SambaNova expensive, Chutes no free, Vercel = router.
- `qwen/qwen3.8-27b:free` (coding 68.1) failed twice with upstream 429 → the evidence behind the Owner's free-tier rule. `deepseek/deepseek-v4-flash-0731` probed clean, cost $0.0000238 for a 3-line task.
- Cost levers (not yet acted on): restart/one-card-per-chat, `:batch` for non-urgent paid, heavy reading inside subagents, cached reads (~50× cheaper), verify slug format before declaring a model broken.

### Recommended next step after restart
Read `docs/project-memory/SESSION_HANDOFF.md`, then hand T-068 to the **advisor** with the finding "use `--agent worker`", and ask the Owner for the AI Studio free-tier limits so T-067 can close.
<!-- AUTO-HANDOFF:END -->

## งานค้างที่ยังไม่ปิด — บ้านเดียว

- **T-033** — War Room pilot: ปิดแล้ว 2 ข้อ (fresh room ครั้งละห้อง = ใช่ · Owner จ่าย เพดาน $1/ครั้ง) — **เหลือ "ใครเข้าร่วม" รอ Owner ตัดสิน** (สถานะบนการ์ด: IN_PROGRESS)
- **T-032** — force-push block บน `dev-workspace` (repo setting): แนะนำให้ Owner เปิดใน GitHub UI (process rule มีอยู่แล้ว; นี่คือ repo-level belt-and-braces)
- **T-050** — roadmap draft (`ROADMAP_STUDY_DRAFT_2026-09-26.md`) รอ Owner พิจารณา (DRAFT — NOT APPROVED)
- **restart opencode** — pin ใหม่ (project-lead ฯลฯ) จะมีผลหลังเปิดแชทใหม่ (resumed session ยังใช้โมเดลเก่า)
- **n8n publish** — ✅ RESOLVED 2026-09-27: execution test proved the edited (new) query already runs on manual execution; publish is moot. Workflow `eohtRWY8YEvEuS7n` stays inactive.
- **OpenRouter credit** — ~$0.64 คงเหลือ; งานเสียเงินต้องขอ Owner ก่อน
