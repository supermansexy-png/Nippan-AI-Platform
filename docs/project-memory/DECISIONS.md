# Nippan AI Platform — Durable Decisions

## Authority

- พี่เชษ is Project Owner and final decision maker.
- ChatGPT is Project Lead / Lead Architect / Project Chair.
- Specialist AI models provide implementation, review, research, or challenge.
- Specialist AI models do not independently redefine architecture.
- Important unresolved decisions use NEEDS_OWNER_DECISION.

## Evidence

Repository/runtime evidence is stronger than summaries or AI claims.

Inspect before changing.

Do not claim success without evidence.

## Architecture

GitHub is the central source of code and project-change history.

Supabase PostgreSQL is used for the platform database.

Do not create duplicate infrastructure before checking what already exists.

## Production Protection

Ai-bot-Nippan production must not be changed without explicit authorization.

## War Room

Remote War Room access must remain fail-closed.

No unauthenticated public bypass is acceptable.

## AI and Cost

Use models/tools according to the task.

Avoid unnecessary paid-model calls.

Independent Audit System (progress gates + paid auditor) is SUSPENDED by
Project Owner (2026-09-24). Historical audit records are preserved.
Do not restart it unless explicitly instructed by Project Owner.

## War Room

War Room V1 work is RESUMED by Project Owner (2026-09-24) for:
1. dev-time use in AI team workflow
2. future runtime backstage ecosystem for AI

Track D and onward proceed under normal task cards; audit gates no longer
block.

## Governance

Normal CI, testing, review, and security verification continue even while
Independent Audit is paused.

Major architecture changes require evidence and Project Owner decision.

## 2026-09-27 — Adopt 2 Google free models as non-sensitive fallback

Decision: Adopt exactly two Google free-tier models as a zero-cost fallback for non-sensitive work:
- `google/gemini-flash-lite-latest` (routine)
- `google/gemini-3.8-flash` (higher-quality fallback)

Authority: Owner decision 2026-09-27 ("เคเอา2ตัว"). Live probe verified both return HTTP 200.

Caveats:
- Free tier trains on + human-reviews submitted content (Google Gemini API Additional Terms, "Unpaid Services": "Do not submit sensitive, confidential, or personal information to the Unpaid Services.")
- Limits UNKNOWN (per PROJECT, not per key; RPM/TPM/RPD unpublished; RPD resets midnight Pacific; preview models more restricted).
- Not usable for repo code, secrets, customer data, or any confidential material unless Owner explicitly overrides in writing.
- Slug form: `google/<model-id>` (no provider entry needed in opencode.json).

Status: Recorded in MODEL_ROSTER.md and CURRENT_STATE.md. Seat pinning still requires HR check + Owner approval.

## 2026-09-27 — Free-tier models: backup only, task-scoped (Owner directive)

Decision (Owner, 2026-09-27, verbatim): "ของฟรี เค้านิ่งยังไม่โอเค ใช้ได้แปบๆเดียวก็หลุด ให้อยุ่สำรอง ใช้เฉพาะงาน"

Intent: free models are not reliable enough to be a standing primary; they belong in the **backup** tier and should be used only for specific, scoped tasks.

Supporting evidence: `qwen/qwen3.8-27b:free` returned upstream `429` twice within minutes on 2026-09-27; the Groq free tier is capped at 8,000 TPM (parked); earlier free endpoints (`jev-1.13-free`, `deepseek-v4-flash-free`, `mimo-v2.5-free`) failed the T-020 test.

**OPEN CONFLICT — nothing is changed until the Owner clarifies the scope:**
- The authoritative T-065 per-role table has FREE models as **Primary** for **7 of 9 seats** (project-lead, reviewer, ops, researcher, model-recruiter, assistant, advisor). Applying this directive to *all* free models means re-staffing those seats onto paid models — which raises cost, the opposite of our current direction.
- Free models in use fall into two classes: **(a) OpenCode-hosted free** — Zen `*-free`, plus Go `longcat-2.5-preview-free` and `space-bunny-free`; hosted on OpenCode's own infrastructure, inside the paid $10/mo Go subscription / Zen account, and 7 free models passed the T-065 hard suite. **(b) External shared-pool free** — OpenRouter `:free`, Groq free, Google free; these are the ones that actually dropped today.
- If the directive applies only to (b), **today's table already complies**: no external `:free` model holds a Primary slot — they sit in Backup tiers only.

Status: recorded. **No pin was changed.**

**RESOLVED (Owner, 2026-09-27 — answered "ก"):** the rule covers **external shared-pool free tiers only** — OpenRouter `:free`, Groq free, Google free. **OpenCode-hosted free models** (Zen `*-free`, Go `longcat-2.5-preview-free`, `space-bunny-free`) are **not** covered: they run on OpenCode's own infrastructure inside the paid $10/mo Go subscription / Zen account, so they may stay in Primary slots.

**Compliance check (VERIFIED 2026-09-27):** no external `:free` model holds a Primary slot — checked both in the T-065 table and in the live `opencode.json` agent pins. External free models appear only in Backup tiers, which is exactly where this directive puts them. **No pin change is required.** The two adopted Google models are class (b), so they are **backup / task-scoped only — never a seat primary**.

## 2026-09-27 — Jev 1.13 Free adopted as a screening tool (not a seat)

Decision (Owner, 2026-09-27): "ก ทดสอบเลย ถ้าใช้ได้ เอามาเป็นเครื่องมือ" — run the pilot; if it works, adopt it as a tool.

Pilot result (5 real-shaped cases scored against our own L1/L2/L3 and Owner-approval rules): review-tier **5/5** · Owner-approval-needed **5/5** · auth/tenant flag **4/5** (one over-flag on a CI change — conservative) · **dangerous under-classification 0/5**. Harness `runs/jev_pilot.cjs` (gitignored).

Terms of adoption:
- It supplies a **signal only** — never the deciding authority where a written rule applies, and never the sole gate for an L3.
- It is a **tool, not a seat**: it emits no text, so no agent pin exists or will be created for it.
- Runtime class is OpenCode Zen hosted free — **not** an external shared-pool free tier, so the 2026-09-27 free-tier directive does not restrict it. It is not listed among Zen's training exceptions; the free tier is limited-time; the paid twin `opencode/jev-1.13` is $0.042/M input, free output.
- Producing any automation around it is a **separate card (T-068)** that must pass builder + a different-model review.

Status: adopted as a tool; **no agent pin changed, no config touched**.
