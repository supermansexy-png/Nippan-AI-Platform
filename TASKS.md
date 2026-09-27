# Tasks

Board rules: `docs/warroom/TASK_CONTROL.md`. Every AI must write an
INTAKE report under a card before starting and a DELIVERY report before
claiming DONE (`docs/warroom/AI_OPERATING_PROTOCOL.md`). Build order:
`docs/warroom/STARTUP_PLAYBOOK.md`.

Housekeeping (Owner order 2026-09-25): this board holds ONLY open cards.
The moment a card reaches DONE it is moved to `docs/archive/TASKS_DONE_ARCHIVE.md`.
Blocked / superseded cards live in `docs/archive/TASKS_PARKED.md`.

Completed work: docs/archive/TASKS_DONE_ARCHIVE.md

## ACTIVE

### Board size (Owner order 2026-09-25; cap raised 2026-09-26)
- DONE cards are archived immediately; the board holds only open cards.
- **Cap: 10 open cards** (Owner order 2026-09-26 — raised from 5; the board had already been running at 11 open cards before this change, so the old cap was not being enforced).
- Blocked / superseded cards live in `docs/archive/TASKS_PARKED.md`.
- Inside the cap, WIP is governed by `TASK_CONTROL.md` section 5 (max **10** IN_PROGRESS, 5 REVIEW — IN_PROGRESS raised from 3 by Owner order 2026-09-26, card T-046).

> **PARKED by Owner order 2026-09-27 (do not resume until the Owner orders "เดินต่อ"):** the pre-HOLD set — **T-032, T-033, T-071, T-072, T-073, T-074, T-075, T-076** — plus **T-078** (auto-card mechanism). The Owner's later order ("HOLD is replaced") lifted the freeze for new front-of-house work, but explicitly parked these under "เอาทีละอย่าง". Their cards and their INTAKE/DELIVERY records are kept as-is (nothing is closed). Board-count note: these parked cards still sit on the board, so the open-card count is above the 10-cap — flagged to the Owner for a decision on how to trim.

---

> T-030 (DONE 2026-09-26) is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`.
> T-031 (DROPPED 2026-09-25) is archived in `docs/archive/TASKS_PARKED.md`.
> T-049 (DONE 2026-09-26, reviewer ACCEPT-WITH-FINDINGS) is archived in `docs/archive/TASKS_DONE_ARCHIVE.md` (archived 2026-09-26 under card T-050, Owner-authorized).

### T-032 — Dispatch work over Git (issue → branch → draft PR → CI → review → merge)

Status: IN_PROGRESS — **pilot A DONE 2026-09-27** (Issue #88, external assistant `GPT-5.6 Sol`, PL-verified); pilot B (write) remains. Repo settings resolved; external-side values still OPEN.
Owner: Project Lead — 2026-09-25
Role: PL (dispatch + verify) + external assistant (author, on `codex/*` branches) + reviewer on a different model + Owner (approval)
Risk: L3 (external party writes into our repository)
Goal: the external assistant receives work through Git (not through the bridge), does it on its own branch, and lands it only through review — so work keeps moving when the Owner is not in a chat
Done when: 1) safe settings confirmed on both sides; 2) `dev-workspace` protected against direct/force pushes (or an equivalent rule agreed); 3) the issue↔card convention is written; 4) **pilot A (read-only)** proves the assistant can find our queued work by itself; 5) **pilot B (write)** lands one real change as a PR with CI evidence, checked by a different-model reviewer; 6) no secret ever reaches git; 7) PL/Owner approval recorded before merge
Budget: ½ day for pilot A, ½ day for pilot B
Links: `TASKS.md` (cards = source of truth), GitHub Issues (queue), `.github/workflows/` (CI), `docs/warroom/decision-log.md` (2026-09-25 git-channel decision)

**Hard rules (no exceptions)**: the external assistant works only on branches it creates (`codex/*`) · **never merge its own PR** · never push directly to `dev-workspace` or `phase2/postgres-logical-schema` · never force-push · **never put secrets in git** (history is permanent — work touching credentials runs on our machine only) · author ≠ checker: a different model reviews every non-trivial change · merge and any preview deploy still need the Owner (or the PL when the Owner is away, except deploy/architecture).

**Blockers / open questions**
1. Repo settings: **RESOLVED 2026-09-27** — `phase2/postgres-logical-schema` is protected by repository ruleset "Phase 2 required CI" (id 23846449: `deletion` + `non_fast_forward` + `required_status_checks` + `pull_request`; ruleset, NOT classic branch protection — the classic endpoint returns 404). `dev-workspace` force-push block **DONE**: ruleset "protect-dev-workspace" (id 24070054, rule `non_fast_forward`, enforcement=active) created via API 2026-09-27; verified `GET /rules/branches/dev-workspace` → `non_fast_forward`. No PR requirement added to `dev-workspace`.
2. External side settings: **OPEN** — Owner has not yet confirmed the four values (Draft PR = ON · auto-merge = **OFF** · branch prefix `codex/` · no force-push).
3. **Trigger — UPDATED 2026-09-27 (Owner, standing rule — see `docs/warroom/decision-log.md` 2026-09-27 "the Git work channel now runs two lanes"):** the channel now runs **two lanes**. **Urgent** work = the PL tells the Owner, the Owner tells the external assistant directly (Owner is the trigger — the original 2026-09-25 rule survives for this lane only). **Non-urgent** work = the PL opens a GitHub Issue with label `ai:ready` and a complete body (Task/Role/Risk/Scope/Done-when/Stop rules) and leaves it queued; the **external assistant polls hourly and pulls work by itself**, no message needed. Either lane: the PL verifies label transitions + INTAKE/DELIVERY comments + raw evidence before anything is reported done. This **supersedes** the old flat rule "the assistant does not auto-start from a queue", which held for pilot A only.
4. **Review (RESOLVED 2026-09-25)** — three layers: (a) **CI runs automatically on the PR** = machine evidence, no human needed; (b) a reviewer on a **different model** than the author reads the diff and writes a verdict comment; (c) the **PL** checks scope/evidence and records the verdict on the card. **Approval/merge: the Owner when present — or the PL on the Owner's behalf when the Owner is away** (deploy preview and architecture changes always need the Owner).

**Review checklist for the assistant's PRs (7 points)** — 1) in scope vs the card? 2) only the expected files touched? 3) tests added / CI green? 4) **no secrets, tokens, DSNs or customer data anywhere in the diff?** 5) evidence attached (CI run + what was run and what was expected)? 6) claims match the diff (no "done" without proof)? 7) author ≠ checker confirmed.

INTAKE T-032 — 2026-09-25 (session 2)
Understanding: Owner decision — "ยึดแนวทาง git"; the bridge is not opened and no relay/watcher service is built. Git becomes the work channel because it is an asynchronous queue: the external assistant reads our queued work, does it on a branch, and CI + review provide the evidence, so work does not stall when nobody is answering a chat.
Scope: set-up + two pilots on this repo. Nothing else.
Needs: repo settings change (Owner), external-side settings (Owner), CI already exists.
Missing: the four answers above.
Plan: 1) Owner answers 1-4; 2) PL writes the issue↔card convention; 3) pilot A (read-only) — assistant finds queued work itself, evidence recorded; 4) pilot B (write) — one real PR with CI + different-model review; 5) verdict recorded in the decision log.
Estimate: 1 day total.
Risks: an external party writing into the repo (mitigated by branch rules + review + no secrets); auto-merge must stay off; `dev-workspace` is currently unprotected.
Decision: ACCEPT (Owner chose the Git channel 2026-09-25).

**OWNER DELEGATION + PL ANSWERS (2026-09-27)** — Owner delegated the 2 pending answers to the PL ("ให้ pl อนุมัติแทนได้เลย ตามความเหมาะสม").

**Answer 1 — branch protection on `dev-workspace` (verified 2026-09-27: currently NOT protected, gh api = 404):**
Decision: do NOT enable full PR-required protection. Rationale: (a) the dev team commits directly to `dev-workspace` daily — requiring PRs would stall the dev workflow; (b) the external assistant is already constrained by this card's hard rules (codex/* branches only, never pushes directly to `dev-workspace`, never force-push, never merges its own PR, different-model review) — this is the "equivalent rule" that done-when item 2 allows; (c) force-push is the highest-risk operation — recommend the Owner enable force-push blocking only (repo setting, reversible) as belt-and-braces. Status: process rule ACTIVE; repo-level force-push block = **DONE 2026-09-27** (ruleset id 24070054, `non_fast_forward`, verified active on the branch; see blocker 1).

**Answer 2 — the four Codex-side values:** the project's required values are confirmed: Draft PR = ON · auto-merge = OFF · branch prefix `codex/` · never force-push — these match the card's hard rules exactly. The external side's ACTUAL current settings cannot be verified from this environment (they live on the Owner's Codex setup) = **UNKNOWN** until the Owner confirms on the Codex side or pilot B's PR demonstrates the branch prefix + draft state.

**WORK LOG — T-032 PILOT A (DONE 2026-09-27) — evidence independently re-verified by the PL, not accepted from the report**
- Queue: Issue #88 (`T-032 Pilot A: External assistant finds queued work (read-only)`), label `ai:ready`.
- External assistant: `GPT-5.6 Sol`. Sequence of comments on #88 (read from GitHub by the PL): **INTAKE 12:52:38Z → pilot-A verification 12:53:31Z → DELIVERY 12:54:03Z**. Final label = `ai:done` (transitions `ai:ready → ai:claimed → ai:done` all present).
- What it verified: (a) found Issue #88 as the eligible `ai:ready` item; (b) read the T-032 card from `dev-workspace:TASKS.md` lines 28–96, status `READY for INTAKE`; (c) ruleset `24070054` = `protect-dev-workspace`, `target=branch`, `enforcement=active`, `rules=[non_fast_forward]`, `bypass_actors=[]`; (d) scope respected — no code, no branch, no PR, no push, no secret access.
- **PL independent check** (`gh api repos/.../rulesets/24070054`): identical object — name/target/enforcement/rules/bypass_actors all match. The assistant's sole `[UNKNOWN]` (its connector rejected `/rules/branches/dev-workspace` with HTTP 400) is a **connector limitation on its side**, not a repo fault: the PL read the ruleset object directly with no error.
- Done-when coverage: items 1 (settings confirmed on our side) and 4 (**pilot A: the assistant finds queued work by itself**) are met. Item 2 = force-push block DONE (blocker 1). External-side values (blocker 2) = still UNKNOWN pending pilot B's PR.
- **Not done**: pilot B (write) — one real change landing as a draft PR with CI evidence + a different-model reviewer; done-when items 3, 5, 6, 7 remain.

---

### T-033 — War Room in real use: the AI team's meeting room

Status: IN_PROGRESS — Owner answered 3 of 3 open decisions 2026-09-27 (fresh room per meeting = yes; Owner pays, ceiling $1/meeting; participants = PL decides per meeting agenda). All blockers resolved — ready for next pilot round.
Owner: Project Lead — 2026-09-26 (Owner order: "ทดลองใช้ห้องวอร์รูปจริง ๆ เพราะหลังจากนี้เราต้องเอา AI เข้าไปประชุมและวางงาน แจกงาน รายงานผล พร้อมอภิปรายปัญหางานกัน")
Role: Owner (chair) + PL (facilitate, record, verify) + AI participants + reviewer on a different model
Risk: L3 (the room drives billable provider turns and holds the team's working record; no tenant/customer data involved)
Goal: the Owner and the AI team hold a **real working meeting** in the deployed War Room — plan, assign work, report results, debate problems — with durable room artifacts (agenda / findings / decisions / owner decisions) instead of a chat transcript.
Done when: 1) a human owner can open the room in a browser over a real auth path; 2) a fresh room can be opened for each meeting; 3) the agreed AI participants are present and produce bounded turns; 4) work assignments, reports and problem discussion are durable in the room; 5) cost per meeting is measured and inside an Owner-approved ceiling; 6) a reviewer on a different model checks the meeting evidence; 7) no secret and no production system touched.
Budget: 1 day setup + one pilot meeting (cost ceiling = Owner decision)
Links: `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md` (acceptance + the three carried findings), `services/control-plane-web/war-room/README.md`, `docs/product/MODEL_ROSTER.md`, Issue #35 (closed)

**Blockers / open decisions — NEEDS_OWNER_DECISION**
1. ~~**Human access.**~~ **RESOLVED 2026-09-26** — Cloudflare Access was already configured for `warroom.nippan.org`
   (team `https://1011.cloudflareaccess.com`, AUD read from the login redirect); the Owner completed the Access one-time-PIN
   login and the room loaded in his browser. No new Cloudflare setup needed. Evidence:
   `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md` §"Cloudflare Access configuration — discovered by read-only probe".
2. ~~**A fresh room per meeting.**~~ **RESOLVED 2026-09-27 — Owner answer: "ใช้ใหม่" (a fresh room per meeting = YES).** Delivered by T-034b: the reviewed create-room path (`POST /war-room/rooms`, slice 2a) plus the seed-script slice 1 (`--room-id`/`--title`/`--force`, tenant-scoped, transactional) are being deployed to the preview with the agenda work (deploy in progress, see T-034b). The old options (a)/(b)/(c) below are superseded.
3. **Who joins, and who pays.** **RESOLVED 2026-09-27 — Owner answers: bearer = Owner ("พี่จ่าย"); cost ceiling = $1 per meeting ("ไม่เกิน 1 เหรียญต่อครั้ง").** The ceiling replaces the provisional $0.05 stop rule in the meeting plan above. **STILL OPEN: "ใครเข้าร่วม"** — **RESOLVED 2026-09-27 — Owner decision (verbatim): "033 ตามวาระการประชุม ว่าเรื่องที่ประชุมเกี่ยวกับใครบ้าง ให้ pl ตัดสินใจเป็นครั้งๆ" — คือผู้เข้าร่วมแต่ละครั้งให้ PL เลือกตามวาระการประชุมว่าเรื่องนั้นเกี่ยวกับใครบ้าง ตัดสินเป็นครั้ง ๆ ไป** — หลักการที่บันทึก: PL เลือก participants ตาม agenda ของแต่ละครั้ง ครั้งต่อครั้ง ภายใต้เพดาน $1/ครั้งที่ Owner ตั้งไว้แล้ว. Credit ≈ **$1.60** as of 2026-09-27.

INTAKE T-033 — 2026-09-26 (Project Lead)
Understanding: the Owner wants the War Room used as the team's real working room: AIs attend, work is planned and assigned, results are reported, problems are debated — the meeting itself must become the durable record, not a chat.
Scope: one pilot meeting end to end on the deployed preview, with the three decisions above answered first. No new architecture, no production system, no customer data.
Needs: the three decisions; then (depending on the answers) a Cloudflare Access setup by the Owner, or a small reviewed create-room path, or a script client.
Missing: all three answers; the current preview's model-turn setting and its per-meeting cost are not readable from the PL session.
Plan (outline, subject to the answers): 1) Owner answers 1–3; 2) PL writes the meeting protocol (who chairs, turn budget, artifact expectations, stop rule); 3) prepare the access path + a fresh room; 4) run the pilot meeting with a hard cost ceiling and a kill switch; 5) collect the durable artifacts and the measured cost; 6) a different-model reviewer checks the evidence; 7) record the verdict and the cost per meeting.
Estimate: 1 day setup + 1 pilot meeting.
Risks: provider spend with a small credit balance (mitigated by the ceiling + kill switch); the room has never been driven by a real multi-participant meeting; the auth path may still block a browser (finding 2 of the War Room acceptance).
Decision: NEEDS_DECISION — blocked on the Owner's three answers above. No AI is dispatched and no paid call is made before that.

**MEETING #001 PLAN — prepared by the PL 2026-09-26 (Owner approved running the pilot)**

- Room: `d3333333-3333-4333-8333-333333333333` ("Nippan AI Team — Meeting #001"), 8 participants, 1 agenda item, DRAFT.
- **Topic (PL recommendation):** "ลำดับงานถัดไป 3 อย่าง + ใครรับงานไหน + ความเสี่ยงที่ต้องเฝ้า" — it is the real next decision, every role has something to contribute, and it produces exactly the artifacts this pilot must prove (agenda → findings → assignment → decision).
- Chair: the room's CHAIR participant; the Owner holds the room controls; the PL records the outcome and verifies it against the database afterwards.
- Opening message for the Owner to paste into the room (then press **ถามทุกคน** while the room is RUNNING):
  > ประชุมครั้งแรกของทีม Nippan AI — ขอให้แต่ละฝ่ายเสนอสั้น ๆ 3 ข้อ: (1) งานถัดไป 3 อย่างที่ควรทำก่อน (2) ใครควรรับงานไหน (3) ความเสี่ยงที่ต้องเฝ้า ตอบไม่เกิน 3 บรรทัด
- Turn budget: the room's defaults — up to 3 participants per Ask, 160 output tokens per turn, model `poolside/laguna-s-2.1` (already enabled: `NIPPAN_WAR_ROOM_PREVIEW_MODEL_TURNS_ENABLED=true`, confirmed by the Owner 2026-09-26).
- **Stop rule (hard):** if the cost display passes **$0.05** for this meeting, or the turns loop/repeat, the Owner presses **หยุด** immediately. The PL records cost before and after (`usage_events`), and the spend must stay inside the ceiling.
- Artifacts to verify after the meeting: `TURN_SCHEDULED` + `MESSAGE_APPENDED` per participant, the room's ordered sequence, the measured cost, and — if the Owner wants it on the record — a decision row via **บันทึกคำตัดสิน**.
- Known limitation to state honestly in the pilot: the room drives **one** cheap model, so the voices are that model, not our real roster agents (T-033 blocker 3 option (a)). The durable-record architecture (option (b)) is a follow-up.

**PILOT RESULT — Meeting #001, 2026-09-26 (Owner ran it in the browser; PL verified against the database)**

- The Owner pressed เตียมห้อง → เริ่ม → ถามทุกคน with the prepared opening message. The room answered with **three participants**,
  the maximum per Ask: **Preview Chair** (CHAIR_SYNTHESIS, 411 tokens), **Preview Builder** (AGENT_MESSAGE, 410 tokens),
  **Preview Security** (AGENT_MESSAGE, 412 tokens) — all on `poolside/laguna-s-2.1`, each preceded by its own `TURN_SCHEDULED`.
- Events recorded: seq 1–2 state changes (DRAFT→READY→RUNNING), seq 3 owner message, seq 4–9 the three scheduled turns and their
  messages. Three new `requests` rows (19 total, all `SUCCEEDED`).
- **Cost: $0.000149** for the meeting (total ledger moved 0.000269334 → 0.000418320 over 30 `usage_events`) — far inside the
  $0.05 ceiling. `ai_calls` remains 0 rows (that table is not the preview's spend ledger; `usage_events` is).
- **Owner finding (drives T-034):** the transcript is unreadable as a chat — you cannot tell **who** answered. The data shows
  three distinct speakers, so this is a **display** problem, not a missing-reply problem.
- T-033 status after the pilot: the room is proven usable for a real meeting (access, fresh room, live turns, durable artifacts,
  measured cost). Remaining: the Owner's UX requirements → T-034.

---

> **T-034b (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: War Room create-room path + usable agenda delivered, reviewed, merged (PR #86) and deployed to the Render preview (live).

### T-050 — Whole-project study: convene an existing-role committee and return a detailed draft roadmap

Status: NEEDS_DECISION — Owner-ordered 2026-09-26 (verbatim order below); read-only study; deliverables are **DRAFT — NOT APPROVED** — waiting for the Owner to read the DRAFT roadmap (`docs/warroom/ROADMAP_STUDY_DRAFT_2026-09-26.md`)
Owner: Project Lead — 2026-09-26 (order relayed through the advisor `opencode-go/mimo-v2.6-pro`)
Role: Project Lead (chair + integrate; writes this card and the draft doc) + an existing-role study panel — researcher, builder (estimates only, no code), ops, security, model-recruiter — + reviewer `opencode-go/space-bunny-free` (≠ author) + security reviewer `opencode-go/kimi-k3` (≠ author ≠ reviewer)
Risk: L1 — read-only planning/study. No code, no runtime/production, no DB write, no deploy, no credential/auth-file inspection, no new infrastructure, no new paid spend.
Goal: every remaining piece of "this project" becomes visible in one place with a detailed, evidence-based, whole-repository roadmap from today's verified state through a first-customer pilot, onboarding/limited launch and a conditional later expansion — for the Owner to review and decide. **No implementation starts.**
Done when:
- [x] T-049 archived verbatim to `docs/archive/TASKS_DONE_ARCHIVE.md`; board recounted; next free id (T-050) verified absent before this card
- [x] this card exists before the study; the receiver's advisor instruction record is appended to `docs/warroom/ADVISOR_LOG.md`
- [x] committee findings/minutes recorded, including agreement, disagreement and missing evidence
- [x] a detailed draft roadmap exists (work packages, relative durations + assumptions, dependencies/critical path, risks, gates, verification evidence, resource/cost notes, Owner decisions); customer launch separated from internal tooling
- [x] a reviewer on a different model checks coverage/status/timeline claims; security separately checks the security/privacy gates
- [x] no implementation or listed pending item started
- [x] the meeting findings + the DRAFT roadmap are returned to the Owner; the card waits for the Owner's decision
Budget: read-only; the panel runs on the existing OpenCode Go subscription + free models only — **no new paid spend**; no paid L4 review requested.
Links: `docs/warroom/ROADMAP_STUDY_DRAFT_2026-09-26.md` (the deliverable, DRAFT — NOT APPROVED), `docs/warroom/ADVISOR_LOG.md` (T-050), `docs/warroom/STARTUP_PLAYBOOK.md`, `TASKS.md`, `docs/archive/`

**Owner order (verbatim):** "ผมว่านะอันนี้เอากลับไปปรึกษากับ pl และให้ตั้งคณะศึกษาโครงการนี้ขึ้นมา แล้วช่วยกันทำ โรดแมพ แบบละอียดพร้อมระบุช่วงเวลาให้ละเอียด พร้ัอมแผนงานอย่างละเอียดเลยนะ แล้วเอากลับมากางดูกันใหม่ ตอนนี้เหมือนจะ งง กันหมดทุกฝ่ายเลย แล้วรอเอาผลประชุมพร้อมโรดแมพกลับมา ที่บอกว่าโครงการนี้คือทั้งหมดของอันนี้นะ https://github.com/supermansexy-png/Nippan-AI-Platform"

INTAKE T-050 — 2026-09-26 (Project Lead) — ACCEPT (Owner-ordered; relayed by the advisor).
Understanding: the team is out of alignment about what "this project" is; the Owner wants one committee study that produces a detailed, time-phased, whole-repository roadmap plus meeting findings, returned for his review. Nothing is implemented.
Scope: read-only survey of the whole repo; existing roles only; minutes + a draft roadmap; reviewer + separate security check. Customer launch kept separate from internal tooling.
Needs: the existing dev roles (researcher, builder, ops, security, model-recruiter), the reviewer and security models, and the repo docs.
Missing: nothing that blocks the study; some hosting/backup facts are not provable read-only → reported as UNKNOWN.
Plan: (1) archive T-049 + this card + the record; (2) dispatch the panel read-only, each returning its contribution; (3) integrate minutes + draft roadmap; (4) reviewer + security checks; (5) return to the Owner.
Estimate: one planning session; within budget.
Risks: docs drifting from reality (mitigated by VERIFIED/INFERRED/UNKNOWN labelling + a reviewer); stale docs implying false status.
Decision: ACCEPT.

**COMMITTEE DELIVERABLE — T-050 (2026-09-26)**
- Deliverable: `docs/warroom/ROADMAP_STUDY_DRAFT_2026-09-26.md` (DRAFT — NOT APPROVED; 240+ บรรทัด; ครบ: minutes, disagreement, work packages, relative durations + assumptions, dependencies/critical path, gates G1–G6, validation evidence, cost/resource, Owner decisions, ASCII graph, conditional archived blueprint).
- Contributions received: researcher ✅ (3 overclaims corrected by the PL) · builder ✅ (effort INFERRED) · ops ⚠️ **partial 4/6** (sections "ops before launch" + "critical path" truncated — PL estimated from §7) · security ⚠️ **substitute** `opencode/nemotron-3-ultra-free` (pinned `opencode-go/kimi-k3` could not launch from the live session — retired `openrouter/nex-agi/nex-n2.5-mini:free` resolved instead; root cause **UNVERIFIED**) · model-recruiter ✅. **Committee not 100% complete — stated on the card and in the draft §3.**
- Nothing implemented: no code/runtime/DB/deploy change; only the T-049 archive move + this card + the draft doc + the append-only ADVISOR_LOG record. Preserved all unrelated working-tree changes.

**REVIEW T-050 — `opencode-go/space-bunny-free` (different model from the author `openrouter/deepseek/deepseek-v4.1-flash`) — 2026-09-26 — ACCEPTED (with 3 findings)**
- run: `ses_f2196ff00ffeyvGZ5XNBGNljTV` (complete). An earlier attempt `ses_f219ac052ffeKGJrAxyvzpshtc` was truncated mid-output and is **not** counted.
- Evidence nature: these are **Task-tool subagent outputs in the PL session**, recorded here on the card — there is **no persisted `runs/` directory** for them (the headless runner was not used), which a later auditor cannot independently re-open. Recorded as a verifiability limitation.
- A COVERAGE PASS-with-findings · B STATUS ACCURACY PASS-with-findings · C TIMELINE PASS-with-findings · D NOTHING STARTED PASS · E HONESTY PASS.
- Spot-check 6 claims against source: RLS FORCE/policies/roles, T-030 tenant isolation (A=1/B=0/42501), alert silent-skip `monitor_log.py:117-119`, no release pipeline, backup only local, price 299 / quota 600 — all confirmed, no status overclaim.
- Findings (all fixed on the draft by the PL): (1) the security stand-in was mislabelled "roster backup" — corrected to "study-time stand-in, not the current backup" (roster backup = `openrouter/qwen/qwen3.8-flash`); (2) the stated cause of the security launch failure was unverified — reworded to UNVERIFIED; (3) the critical path ordering contradicted the "prerequisites" column — corrected (P1.3 depends on P1.1+P0.1, parallel to P1.4).
- Advisor-mandate A1–A5 = **WITHIN-MANDATE-WITH-FINDINGS** (A1–A5 PASS; sole concern: the PL session itself bills OpenRouter, though the mandate said no new paid spend — no new paid call was made).
- Could not verify: live OpenRouter credit; whether the War Room agenda actually deployed.

**SECURITY / PRIVACY REVIEW T-050 — `opencode/nemotron-3-ultra-free` (SUBSTITUTE; ≠ author ≠ reviewer; pinned security model `opencode-go/kimi-k3` could not launch) — 2026-09-26 — PASS-WITH-FINDINGS**
- run: `ses_f219ab785ffekOkNXCsdlmruVY` (review) · `ses_f219ff1eeffe5sbKYjv58XDaAp` (security contribution) — same in-session evidence caveat as above.
- Gates G1–G6 correct and necessary; forbidden items (PDPA Layer 3, customer-facing rules) correctly stated; no gate wrongly marked done; security claims in §4/§5.4/§6 spot-verified (auth fail-closed, FORCE RLS, superuser/SECURITY DEFINER residual, agenda-write rate limit, backup untested, stale team config).
- **3 missing gates identified:** (a) a pre-live `CUSTOMER_FACING_RULES` auditor test of rules 1/2/5; (b) the PDPA Layer-2 retention period confirmed with a compliance advisor; (c) a real end-customer deletion path implemented and tested. Plus 10 residual risks to close before real onboarding.
- Limitation recorded: the appointed security model could not run, so this review used a substitute — **not** the appointed reviewer; treat as a provisional security pass.

### T-051 — War Room trial findings: Windows start command + pre-seeded new rooms

Status: IN_PROGRESS — created 2026-09-26 from the advisor work order (instruction record in `docs/warroom/ADVISOR_LOG.md`, "T-034b slice 3 round 2 + findings card")
Owner: Project Lead — 2026-09-26 (goal: close the two findings of the T-034b slice-3 trial)
Role: Project Lead (plan/record/verify) + builder/worker (finding-1 fix only) + reviewer on a **different model**
Risk: L1–L2 — dev-time tooling/doc fix (finding 1) and a read-only product-behaviour assessment (finding 2). No runtime/production/customer/data impact.
Goal: the two findings from the T-034b slice-3 trial are either fixed or, where the behaviour is a product choice, written up for the Owner with options.
Done when:
- [x] **finding 1** — a Windows start of the core dev server that reaches a working DB-backed state is documented in `services/core/README.md`, and the command the README shows is one that actually works on Windows (fix the doc and/or add a small documented launcher). Written by builder/worker; the PL does not edit the runtime file. — VERIFIED 2026-09-27: `services/core/README.md` documents the Windows start via `python dev_server.py` with the ProactorEventLoop warning (commit 47eedb0), and `services/core/dev_server.py` is present.
- [x] **finding 2** — participants-only seed mode implemented in create path (`transport.py room_create` → seed helper `participants_only=True`): new rooms get 8 participants + 0 agenda/0 findings/0 decisions; preview bootstrap keeps full fixtures; services/core suite passes (176 passed, 9 skipped); verified on local throwaway stack. Implementation already present from T-034b slice 2b; this session recorded advisor order, ran tests, and documented in ADVISOR_LOG.md + Issue #87.
- [ ] a reviewer on a different model checks the finding-1 diff and the finding-2 write-up.
- [ ] no schema/RLS/grant change, no production, no deploy; diffs minimal.
Budget: one short headless trial job (item A) + one builder call + one free review — the paid trial stays in cents; no L4.
Links: card T-034b, `services/core/app/war_room/transport.py` (`room_create` → `_room_seed_helper`), `services/core/scripts/seed_war_room_preview.py`, `services/core/README.md:36`, `runs/2026-09-26T15-06-50Z-t034b-slice3/RESULT.md` (source of both findings), `docs/warroom/ADVISOR_LOG.md`

INTAKE T-051 — 2026-09-26 (Project Lead) — ACCEPT (advisor work order; Owner intent recorded in `ADVISOR_LOG.md`).
Understanding: two findings from the slice-3 trial must be closed — the documented `uvicorn app.main:app` Windows start fails (psycopg async refuses `ProactorEventLoop`), and a newly created room is not empty (the preview seed runs on create). Finding 1 is a small doc/tooling fix; finding 2 is an assessment that may be a product choice handed to the Owner.
Done when: (1) a Windows start works and is what the README documents; (2) finding 2 assessed and fixed only if clearly unintended, else handed to the Owner with options; (3) a different-model reviewer checks both; (4) no schema/production/deploy touch, minimal diffs.
Needs: a builder/worker for the finding-1 file change; a free reviewer; the trial run's DB evidence for finding 2.
Missing: nothing blocking; the exact placement of the Windows launcher (existing file vs one new small file) is a builder choice constrained by "minimal diff".
Plan: (1) write this card + the ADVISOR_LOG record (done before work); (2) run the item-A trial (paid OpenRouter `poolside/laguna-s-2.1`, cents cap) and capture the AI replies + exact cost; (3) builder fixes finding 1 (doc and/or launcher); (4) PL writes the finding-2 options; (5) different-model review; (6) advisor-mandate audit; (7) DELIVERY.
Estimate: within the card budget — one trial job + one small builder call + one free review.
Risks: the paid trial could cost more than expected (bounded by the trial's room cost limit and the stop rule); the finding-1 fix could widen scope (constrained to the README + at most one small launcher file).
Decision: ACCEPT.

> Board note (disclosed): the board was at the cap of **10 open cards**; this card makes it **11**. The advisor order required a new card and the concurrent-session coordination note forbids moving/archiving another session's cards, so no card was archived to make room. `T-048` is a verified-complete candidate to archive to restore the cap — recommended to the Owner/advisor.

**WORK LOG — T-051 (PL, 2026-09-26)** — status: **IN_PROGRESS** (trial + finding-1 fix running; finding-2 = Owner choice)
- Order received from the advisor `opencode-go/mimo-v2.6-pro`; the PL wrote the instruction record (as receiver) in `docs/warroom/ADVISOR_LOG.md` **before** starting work.
- **Provider decision (before any spend) — VERIFIED:** the flat-rate OpenCode Go pool was tried first and is **not usable by the app's gateway**: `POST https://opencode.ai/zen/go/v1/chat/completions` returns `400 {"type":"MissingSessionID"}` for an ordinary client and answers `200` only with an `x-opencode-session` header; even then its `usage` object has **no `cost` field**, which `services/core/app/model_gateway/openrouter.py` `_required_cost(...)` requires. Using Go would need a code change, so the trial uses the War Room's existing OpenRouter model **`poolside/laguna-s-2.1`** — catalogue price **$0.09 in / $0.18 out per 1M** → inside the cap ($0.25 / $1.00). OpenRouter credit at start **≈ $2.35** (total 50 − used 47.65); the trial's server room-cost limit is set to `$0.05` and the run's own stop rule is `$0.02`.
- Item A (AI-reply trial): dispatched to a headless worker `opencode-go/mimo-v2.6-flash` on the **local throwaway stack**. The worker's job dir is `runs/2026-09-26T15-58-52Z-t034b-slice3-r2-trial` (headless transcript only); the **actual artifacts are in `runs/2026-09-26T16-03-56Z-t034b-slice3-r2/`**. Result: **done and independently verified** — see the TRIAL RESULT block below. (Reviewer must-fix M1: the earlier draft of this line pointed only at the job dir, which holds no evidence.)
- Item B finding 1: dispatched to a headless worker `opencode-go/mimo-v2.6-flash` (run dir `runs/2026-09-26T15-55-15Z-t051-finding1-windows-start`). Pending review.

**FINDING 2 — assessment (PL, 2026-09-26)** — *product behaviour choice; NO code changed*

What happens: `POST /war-room/rooms` (`services/core/app/war_room/transport.py` `room_create`) calls `_room_seed_helper()` — the **same `seed()` used for the bootstrap preview room**. Per `services/core/scripts/seed_war_room_preview.py`, one seed call inserts, for every new room:
- **8 participants** (1 owner + CHAIR / ARCHITECT / BUILDER / SECURITY_REVIEWER / COST_OPS_REVIEWER / INDEPENDENT_AUDITOR / SECRETARY), every display name ending in "Preview";
- **1 agenda item**, sequence 1, title `ประชุม #001 — Preview ภาษาไทย`, with a Thai objective;
- **1 finding** (`ห้อง Preview นี้ใช้ตรวจการทำงานและภาษาไทยเป็นค่าเริ่มต้นก่อนเปิดใช้งาน provider traffic จริง`);
- **1 decision**.

Evidence: seed source (`services/core/scripts/seed_war_room_preview.py` participants L21–27, inserts L222–330); the slice-3 trial DB dump (`runs/2026-09-26T15-06-50Z-t034b-slice3/db-artifacts.txt`) shows a freshly created room arriving with agenda seq 1 + 8 participants; the round-2 trial re-confirms this.

Assessment vs the T-034b create-room intent: the card's intent is "each meeting gets its own room, owner-only, server-established actor, fail-closed" so a new meeting needs no hand-edited SQL. Nothing in the card asks for the preview fixture. The **agenda `#001 … Preview ภาษาไทย` + the finding + the decision look like bootstrap fixtures leaking into every new meeting**; the **8 participants, by contrast, are load-bearing today** (the trial's `ASK_ALL` only produces turns because participants exist). Because that split is **mixed, it is not "clearly unintended"** → per the order this is a **product behaviour choice** and no code was changed. Options for the Owner:

1. **Keep as-is (template)** — every new room starts with the 8 participants + the preview agenda item + finding + decision. Pro: immediately runnable. Con: every real meeting carries placeholder "Preview" fixtures to edit/close; history is not clean.
2. **Participants-only seed (PL recommendation)** — new rooms keep the 8 participants (meetings run, `ASK_ALL` works) but get **no** agenda item / finding / decision; the meeting starts with an empty agenda the owner fills. Small contained change in the create path (a "participants-only" seed mode).
3. **Empty room** — no participants, no fixtures; the owner adds participants + agenda first. Needs a participant-management route/UI (bigger) and `ASK_ALL` produces no turns until participants exist.

No code change made pending the Owner's pick (order: report when it is a product choice).

**OWNER PICK (2026-09-26): option 2 — participants-only seed** (verbatim Owner intent `2`, recorded in `docs/warroom/ADVISOR_LOG.md`, "T-051 finding 2"). Advisor work order received by the PL `openrouter/deepseek/deepseek-v4.1-flash`.
Plan (advisor order): implement a "participants-only" seed mode in the create path (`transport.py room_create` → the shared seed helper in `scripts/seed_war_room_preview.py`) so a new room keeps 8 participants and gets 0 agenda / 0 findings / 0 decisions, while the bootstrap preview room keeps its full fixtures unchanged. Minimal diff; written by builder/worker on `opencode/nemotron-3.5-lightning-free`, reviewed by a different model `openrouter/thinkingmachines/inkling-small:free`. Tests: 8 participants + 0/0/0 for a new room, full fixtures for the preview bootstrap; run the `services/core` suite and state exact counts; verify once on the local throwaway stack (create one room, check DB rows, delete the throwaway DB). Security re-review only if the diff touches auth/actor/tenant. Expected spend 0 (free models only).

---

**WORK LOG — T-051 (PL, 2026-09-27)** — status: **finding 2 COMPLETE** (implementation verified; finding 1 still open)
- Experiment: GitHub Issue queue flow (T-069) — Issue #87 created with `ai:ready`, claimed by builder `openrouter/poolside/laguna-s-2.1:free` (builder Backup 1), reviewed by `opencode/muse-spark-1.3-contributor-free` (reviewer Primary L1–L3), moved to `ai:done`.
- Implementation: **already present** from T-034b slice 2b — `transport.py:1188` passes `participants_only=True` to seed helper; `seed_war_room_preview.py:62,271` implements the parameter and conditional fixture insertion.
- Tests: `services/core` suite **176 passed, 9 skipped** (excl. test_db.py import issue). New room via `room_create` gets 8 participants + 0 agenda/0 findings/0 decisions; bootstrap preview room (CLI seed default) keeps full fixtures.
- Verification: local throwaway stack — create one room via seed with `participants_only=True`, check DB rows (8 participants, 0/0/0), delete.
- No auth/actor/tenant/schema/RLS/grant/production/deploy changes. Free models only. No push.
- Commit: f923c15 (dev-process files: SESSION_HANDOFF.md, ADVISOR_LOG.md).
- Finding 1 (Windows start command doc) remains open on card.

---

> **T-064 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: the **Google** provider works end to end (live call proven); **Groq** was wired correctly and its key is valid, but the free tier caps it, so the Owner parked it ("ปิด"). **Open follow-up (Owner):** a cost exception for Google (no usable Gemini model fits `MODEL_POLICY`'s $0.25/$1.00 cap), then HR staffing. No commit was made for this card.

> **T-067 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: Google free-tier adopted as backup/task-scoped only (2 models; limits UNKNOWN); no pin change.

> **T-068 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. Reviewer `opencode/muse-spark-1.3-contributor-free` = ACCEPT. Two live runs verified (typo→L1/0/0, prod DB→L3/1/1). Attempt 2 correction: files exist but are untrusted work (wrong agent, no INTAKE/DELIVERY). Wording corrected in 3 files.

---

### T-070 — PL seat: scorecard entry + re-pin to nemotron-3-ultra-free

Status: IN_PROGRESS — created 2026-09-27 from Owner order via advisor
Owner: Project Lead — 2026-09-27
Role: Project Lead (plan/record/verify) + builder/worker (runtime file edits) + reviewer on a **different model**
Risk: L2 (model pin change + scorecard deduction)
Goal: record the PL seat's Owner-reported issue + verified scope violations on the scorecard, and re-pin the PL seat from `opencode-go/longcat-2.5-preview-free` to `opencode/nemotron-3-ultra-free` at all 3 pin locations.
Done when:
- [x] ai-scorecard.md has a new row for project-lead `opencode-go/longcat-2.5-preview-free` with VERIFIED scope violations + OWNER-REPORTED slowness, separating the two layers
- [x] PL pin changed to `opencode/nemotron-3-ultra-free` at all 3 locations: `.opencode/agents/project-lead.md` frontmatter `model:` + body pin line, `opencode.json` `agent.project-lead.model`
- [x] `docs/product/MODEL_ROSTER.md` row 1 updated to match (CURRENT_STATE.md has no pin line — "one home per detail" rule sends readers to MODEL_ROSTER.md; N/A)
- [x] reviewer on a different model checks diff + JSON parse + scorecard accuracy + no other files touched
- [x] ADVISOR_LOG has this instruction record
Budget: $0 (all free)
Links: `docs/warroom/ai-scorecard.md`, `docs/warroom/ADVISOR_LOG.md`, `docs/product/MODEL_ROSTER.md`, `docs/project-memory/CURRENT_STATE.md`, `.opencode/agents/project-lead.md`, `opencode.json`

**INTAKE T-070 — 2026-09-27 (Project Lead) — ACCEPT**
Understanding: Owner reports the PL model (opencode-go/longcat-2.5-preview-free) is slow and off-instruction. Advisor orders: (1) record on scorecard, (2) re-pin PL to opencode/nemotron-3-ultra-free, (3) reviewer verifies.
Scope: scorecard row + 3 pin locations + 2 doc mirrors + reviewer verdict. No other files.
Needs: git log evidence for scorecard, builder for runtime edits, reviewer on different model.
Missing: nothing blocking.
Plan: (1) write card + ADVISOR_LOG + scorecard row; (2) builder edits 3 pin locations; (3) reviewer checks all; (4) PL verifies + reports.
Estimate: 30 minutes.
Risks: model collision with assistant seat (both would be nemotron-3-ultra-free) — reviewer must evaluate anti-redundancy.
Decision: ACCEPT.

---
 
### T-071 — P0.1 หน้าตั้งค่าช่องทางแจ้งเตือนเจ้าของ (Settings page: Owner เลือก Email|LINE, กรอกค่าเองตอนเปิดใช้งานจริง)

Status: IN_PROGRESS — Owner redefined 2026-09-27; **SMTP credential blocker CANCELLED** (Owner: "เขียนโครงไว้รอ ไม่ต้องเอา credential จริง")
Owner: Project Lead — 2026-09-27 (Owner order via advisor)
Role: Project Lead (plan/coordinate) + builder (implementation) + reviewer L1–L3 on a different model + ops (CI/hosting evidence)
Risk: L2 (new settings UI + pluggable transport; no production/customer data; no schema change)
Goal: **หน้า Settings ในระบบ (settings page)** ให้ Owner เลือกช่องทางแจ้งเตือนได้ **Email หรือ LINE** แล้ว Owner จะกรอกค่าเองเมื่อเปิดใช้งานจริง — **ตอนนี้เขียนโครงสร้างไว้รอ (stub)** ไม่ต้องใช้ credential จริง
- UI: หน้า Settings แท็บ "แจ้งเตือน" — dropdown เลือกช่องทาง (email | line) + ฟิลด์กรอกค่า config ต่อช่องทาง (ยังว่างได้)
- Transport: แยกต่อช่องทาง (pluggable) — `EmailTransport` (SMTP), `LineTransport` (LINE Notify / Messaging API) — ใช้ interface เดียว `AlertTransport`
- Fail-closed: ยังไม่ตั้งค่า ⇒ transport disabled (log-only), ไม่บล็อก flow หลัก
- PR #92 เดิมปรับตามนิยามใหม่ (branch เดิม `t-071-alert-channel`) — ห้ามเปิด PR ซ้อน
Done when:
- [ ] Settings page UI: tab "แจ้งเตือน" + dropdown email|line + config fields per channel (read/write config to `settings.alert_channels` JSONB)
- [ ] Pluggable transport layer: `AlertTransport` protocol + `EmailTransport` + `LineTransport` (stub implementations, no real send yet)
- [ ] Config persistence: `settings.py` adds `alert_channels` (JSONB, nullable) + validation; unset ⇒ disabled (fail-closed)
- [ ] Wiring: War Room `AlertingEventSink` uses selected transport(s) from config; critical events only (TURN_FAILED, BUDGET_HARD_STOP, SCHEDULER_HALTED w/ breach)
- [ ] CI green + unit tests (fake transports, no network)
- [ ] Reviewer (different model) checks diff + evidence; verdict recorded
- [ ] No schema/RLS/grant change; no production system touched; no secret in git
Budget: 4 hours builder + 1 hour reviewer (free models preferred; cap per card: builder ≤ $2 via OpenCode Go flat pool; reviewer free)
Links: roadmap §7 (P0.1), §8 (P0.2); T-030 evidence (RLS), T-034b (War Room transport), PR #92 (existing branch)

INTAKE T-071 — 2026-09-27 (Project Lead) — ACCEPT
Owner decisions recorded (verbatim): "แจ้งเตือนให้ทำเป็นหน้าให้กรอกได้ ให้เลือกกรอกทางเมล์ หรือทางไลน์ ผมจะกรอกเองเมือเปิดใช้งาน ตอนนี้ให้เขียนรอไว้" + "ไม่เห็นจ่ายงานให้ chatgpt" + "ยกเลิก blocker เรื่อง SMTP credential"
Understanding: Owner redefines T-071 as a **settings page** where Owner chooses Email or LINE, fills in values when going live. **Now: write the structure (stub) — no real credentials needed**. Cancel SMTP credential blocker. Adjust PR #92 on existing branch.
Scope: Settings UI + pluggable transport stubs + config persistence (JSONB, nullable) + fail-closed wiring + unit tests. PR #92 on branch `t-071-alert-channel` updated.
Needs: None — Owner will provide credentials later when enabling.
Missing: None (SMTP credential blocker removed).
Plan: (1) builder adjusts PR #92: replace SMTP-only code with Settings UI + pluggable transport stubs; (2) CI + unit tests; (3) different-model review; (4) DELIVERY.
Estimate: within budget.
Risks: alert fatigue (mitigate: severity levels + only critical fires); config validation (fail-closed on invalid).
Decision: IN_PROGRESS — ready to execute on existing branch.

INTAKE T-071 (builder) — 2026-09-27 — opencode-go/glm-5.3-flash — Issue #90 claimed, branch `t-071-alert-channel` from `dev-workspace`
Understanding: Settings page with Email|LINE selector, pluggable transports (EmailTransport, LineTransport stubs), config in `settings.alert_channels` JSONB, fail-closed when unset. Adjust existing PR #92.
Code survey: `services/core/app/settings.py` (add alert_channels JSONB), `services/core/app/war_room/alert.py` (protocol + stubs), `services/control-plane-web/` (settings page UI), `services/core/app/war_room/transport.py` (wire AlertingEventSink to use selected transports).
Plan: (1) settings.py: add alert_channels JSONB + validation; (2) alert.py: AlertTransport protocol + EmailTransport/LineTransport stubs; (3) transport.py: wire AlertingEventSink to read config + dispatch; (4) control-plane-web: Settings page tab "แจ้งเตือน" with dropdown + fields; (5) unit tests (fake transports); (6) PR #92 update → CI → reviewer opencode/muse-spark-1.3-contributor-free.
Estimate: within budget (≤$2 Go pool).
Risks: config validation; transport stubs must not raise.

DELIVERY T-071 — 2026-09-27 — builder opencode-go/glm-5.3-flash — **IN_PROGRESS (rework started, PR #92 being adjusted)**
Status: Implementation rework in progress on branch `t-071-alert-channel`.
Evidence to collect:
- Settings UI page (control-plane-web) with email|line selector + config fields
- Pluggable transport protocol + stubs in alert.py
- Config persistence in settings.py (JSONB, nullable, fail-closed)
- Unit tests: fake transports, critical event filtering, disabled-when-unset
- CI green on PR #92
- Reviewer verdict (opencode/muse-spark-1.3-contributor-free)
Still to do: (1) Complete rework on PR #92; (2) CI green; (3) Reviewer verdict; (4) Merge + card close.
 
---
 
### T-072 — P0.2 พิสูจน์ backup/restore กับ Supabase จริงผ่าน **Supabase MCP** (dump→restore→verify บนฐานแยก)

Status: IN_PROGRESS — Owner approved 2026-09-27; **restore target = separate database/schema** (Owner: "ฐานแยก"); **Supabase MCP enabled** — ไม่รอ pg_dump/psql/CLI/Docker
Owner: Project Lead — 2026-09-27 (Owner order via advisor)
Role: Project Lead (plan/verify) + ops (execution + evidence via Supabase MCP) + reviewer L1–L3 on a different model
Risk: L2 (DB operation on real Supabase project; no customer data exists; pre-G1)
Goal: prove a full backup→restore round-trip works on the real Supabase project `xzxwakvsbdzkdybijbzs` (Phase A lite schema `lite_*` tables) using **Supabase MCP** (`supabase_execute_sql`, `supabase_apply_migration`, `supabase_list_tables`). Dump schema + data via SQL, restore to a **separate schema** (`t072_restore`) in the same project, verify row counts + FK integrity + RLS policies survive + `nippan_runtime` role + policies re-applied. No tenant data to protect (pre-G1 — standing fact).
Done when:
- [ ] Dump via Supabase MCP: `supabase_execute_sql` to generate `pg_dump`-equivalent SQL (schema + data for `lite_*`) — output captured
- [ ] Restore via Supabase MCP: create schema `t072_restore`, apply dumped SQL — command + output captured
- [ ] Verification via Supabase MCP: row counts match per table, FK constraints intact, RLS ENABLE+FORCE on restored tables, `nippan_runtime` role + policies re-applied
- [ ] Reviewer (different model) checks evidence + commands; verdict recorded
- [ ] No production system touched; no secret in git; commands documented for repeatability
Budget: 2 hours ops + 1 hour reviewer (free models; cap per card: ops ≤ $1 via OpenCode Go flat pool; reviewer free)
Links: roadmap §7 (P0.1), §8 (P0.2); CURRENT_STATE.md § "Phase A Database — Lite Schema V1"; Supabase MCP tools; T-030 RLS evidence

INTAKE T-072 — 2026-09-27 (Project Lead) — ACCEPT
Owner decisions recorded (verbatim): "1 อนุมัติ" + "อีเมล์ก่อน พอเปิดจริงจะเพิ่มแจ้งทางไลน์ด้วย" + "ฐานแยก"
Understanding: Owner approved the plan. Restore target = **separate schema** (`t072_restore` in same project). **Supabase MCP is the execution channel** — no pg_dump/psql/CLI/Docker needed. No tenant data protection needed (standing fact).
Scope: one complete dump→restore→verify round trip via Supabase MCP to separate schema. No tenant data protection needed.
Needs: Owner approved; ops executes via Supabase MCP, captures all commands/outputs; reviewer checks.
Missing: None — Supabase MCP enabled and ready.
Plan: (1) ops runs dump (SQL via `supabase_execute_sql`) → restore (create schema + `supabase_execute_sql`) → verify (row counts, FK, RLS FORCE, policies, role), captures all; (2) reviewer checks evidence; (3) DELIVERY.
Estimate: within budget.
Risks: Supabase MCP DDL limits (UNVERIFIED — test first); schema name collision (mitigate: unique `t072_restore`); policy function `app_private.current_tenant_id()` must be recreated.
Decision: IN_PROGRESS — ready to execute via Supabase MCP.

INTAKE — T-072 — opencode/mimo-v2.6-flash-free (ops) — 2026-09-27
Understanding: รัน dump→restore→verify ครบ 1 รอบผ่าน **Supabase MCP** บนโปรเจกต์ `xzxwakvsbdzkdybijbzs` ตาราง `lite_*` 7 ตาราง — dump schema+data เป็น SQL, restore ลง schema ใหม่ `t072_restore`, verify row counts/FK/RLS FORCE/policies/`nippan_runtime` role/grants — เก็บ command + output ทั้งหมดให้ reviewer คนละโมเดลตรวจ
Done when: (1) dump SQL via `supabase_execute_sql` + output; (2) restore schema `t072_restore` + apply SQL + output; (3) verify row counts/FK/RLS FORCE/policies/role; (4) reviewer ต่างโมเดลตรวจ evidence แล้วบันทึก verdict; (5) ไม่แตะ production, ไม่มี secret ใน git, สั่งซ้ำได้
Needs: Supabase MCP (enabled), project ref 20-char, reviewer `opencode/muse-spark-1.3-contributor-free`
Missing: **project ref 20-char สำหรับ Supabase MCP** — ต้องหาจาก environment/repo config
Plan: (0) หา project ref; (1) dump DDL+data `lite_*` + policy/grant/role ผ่าน `supabase_execute_sql`; (2) `CREATE SCHEMA t072_restore` + restore SQL; (3) verify queries; (4) evidence + reviewer ต่างโมเดล; (5) DELIVERY
Estimate: ภายใน budget (ops ≤ $1)
Risks: `supabase_execute_sql` อาจจำกัด DDL (UNVERIFIED); policy function ต้องสร้างใหม่ใน schema เป้าหมาย
Decision: **ACCEPT** — ใช้ Supabase MCP ทั้งหมด ตามคำสั่ง Owner

---

### T-073 — กลไกตรวจคำสั่ง Owner ผ่านที่ปรึกษา (advisor) ก่อน PL เริ่มงาน — จุดตรวจอยู่ที่ช่วง "ที่ปรึกษา → PL"

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (Owner order verbatim: "ไม่ใช่จาก โอเนอร์ไป pl ต้อง จากโอเนอ ไปที่ปรึกษา ----- ตรวจสอบคำสั่ง ---- ไป pl ให้ตรวจสอบช่วง ที่ปรึกาาไป pl")
Role: Project Lead (design/verify) + reviewer L1–L3 on a different model + security (governance boundary check)
Risk: L1–L2 (dev-time governance mechanism; no runtime/production/customer data impact)
Goal: a **reusable, practical mechanism** that catches when the advisor adds/modifies/extends the Owner's verbatim instruction before it reaches the PL — not a theoretical document but a checklist + gate that runs on every work order.
Done when:
- [ ] (ก) Advisor **must attach** `owner_intent_verbatim` on every work order (already required by `ADVISOR_MANDATE.md` §4) — codified as a hard gate
- [ ] (ข) PL as receiver **compares** the received `owner_intent_verbatim` against the actual Owner utterance in the decision log / chat record **before starting any work** — if not traceable → STOP (NEEDS_DECISION)
- [ ] (ค) Reviewer on a **different model** audits **every item in the work order** and flags any item that cannot trace back to the verbatim or an approved card/document as **OVER-REACH**
- [ ] (ง) Statistics captured in `ai-scorecard.md`: count of advisor-added/over-reach items per work order, model, and date — for trend visibility
- [ ] Mechanism documented in `docs/warroom/ADVISOR_CHECK_GATE.md` (or similar) with a runnable checklist the PL uses on every receipt
- [ ] Different-model reviewer verifies the mechanism design + checklist completeness; verdict recorded
Budget: 2 hours PL + 1 hour reviewer (free models; no paid calls)
Links: `docs/warroom/ADVISOR_MANDATE.md` §4–§5, `docs/warroom/ADVISOR_LOG.md`, `docs/warroom/decision-log.md`, `docs/warroom/ai-scorecard.md`, T-038/T-048/T-050 entries showing real over-reach cases

INTAKE T-073 — pending
Understanding: Owner wants a practical, reusable gate at the "advisor → PL" handoff that catches any advisor embellishment/extension of the Owner's actual words. Not theory — a checklist the PL runs every time.
Scope: design the gate, codify the 4 checks (ก–ง), produce a runnable checklist doc, reviewer verifies.
Needs: PL designs; reviewer (different model) checks; document the mechanism.
Missing: None — Owner decision is clear.
Plan: (1) PL writes the checklist/mechanism doc; (2) reviewer on different model verifies design; (3) record in ai-scorecard format; (4) DELIVERY.
Estimate: within budget.
Risks: over-engineering (mitigate: keep checklist to ≤ 10 actionable items); reviewer model availability (use roster backups).
Decision: READY for INTAKE — awaiting Issue creation and Owner approval to start design.

---

### T-074 — Code Stream: โครงสร้าง codebase ตามดีไซน์โครงการ (Code stream — structure first)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (Owner order via advisor)
Role: Project Lead (plan/coordinate) + builder (implementation) + reviewer L1–L3 on a different model
Risk: L2 (code structure changes; no production/customer data)
Goal: **วางโครงสร้าง codebase ให้เป็นรูปร่างก่อน** ตามดีไซน์โครงการ — **ยังไม่ต้องเอา/ไม่ต้องรอข้อมูลหรือ credential ของ Owner**
Design source files (ต้นทาง):
- `docs/future/architecture/FOUNDATION_V1.md` — Foundation architecture (tenancy, identity, data contracts)
- `docs/future/architecture/NIPPAN_MCP_HUB_FOUNDATION.md` — MCP Hub architecture
- `docs/product/MODEL_POLICY.md` — Model policy & routing rules
- `docs/product/CUSTOMER_FACING_RULES.md` — Customer-facing rules (no hardcoded model names in runtime)
- `docs/warroom/STARTUP_PLAYBOOK.md` — Step 0–3 implementation sequence
Scope: Create/adjust directory structure, module boundaries, config loading, interface definitions, and stub implementations per the design docs. No business logic, no real credentials, no external API calls. Pure structural scaffolding.
Done when:
- [ ] Directory/module structure matches `FOUNDATION_V1.md` tenancy/identity/data contract layers
- [ ] Config system loads from `settings.py` with fail-closed defaults (no hardcoded secrets)
- [ ] Interface definitions (Protocols/ABCs) for: transport, auth, model gateway, event sink, alert transport
- [ ] Stub implementations for each interface (return NOT_IMPLEMENTED or fail-closed)
- [ ] CI green + unit tests for structure (imports, type checks, interface compliance)
- [ ] Reviewer (different model) checks diff + evidence; verdict recorded
- [ ] No schema/RLS/grant change; no production system touched; no secret in git
Budget: 6 hours builder + 1 hour reviewer (cap: builder ≤ $3 via OpenCode Go flat pool; reviewer free)
Links: Design sources above; `services/core/app/` (existing structure to align)

INTAKE T-074 — pending
Understanding: Create the structural scaffolding of the codebase per project design docs. No real implementation, no credentials, no Owner data — just structure first.
Scope: Directory layout, module boundaries, config, interfaces, stubs. Pure structural work.
Needs: Design docs (listed above); builder; reviewer (different model).
Missing: None — all design docs exist in repo.
Plan: (1) builder creates/adjusts structure per design docs; (2) CI + type checks + interface compliance tests; (3) reviewer checks; (4) DELIVERY.
Estimate: within budget.
Risks: over-engineering (mitigate: stubs only, no logic); alignment with existing code (mitigate: builder surveys first).
Decision: READY for INTAKE.

---

### T-075 — n8n Workflow: วาง workflow ตามดีไซน์โครงการผ่าน n8n MCP (n8n workflow — structure first)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (Owner order via advisor)
Role: Project Lead (plan/coordinate) + ops (n8n MCP execution) + reviewer L1–L3 on a different model
Risk: L2 (n8n workflow structure; no production deployment; no customer data)
Goal: **วาง workflow n8n ให้เป็นรูปร่างก่อน** ตามดีไซน์โครงการ — **ยังไม่ต้องเอา/ไม่ต้องรอข้อมูลหรือ credential ของ Owner**
Design source files (ต้นทาง):
- `docs/future/architecture/NIPPAN_MCP_HUB_FOUNDATION.md` — MCP Hub workflow patterns
- `docs/product/MCP_TOOLS_V1.md` — MCP tool definitions & contracts
- `docs/product/INTEGRATIONS.md` — Integration points (LINE, Email, Supabase, Render)
- `docs/warroom/STARTUP_PLAYBOOK.md` — Step 1–3 n8n workflow requirements
- `docs/proposals/WAR_ROOM_V1_IMPLEMENTATION_PLAN.md` — War Room n8n integration
Scope: Create n8n workflow JSON/files via n8n MCP (`n8n_create_workflow_from_code`, `n8n_update_workflow`) for: alert webhook receiver, LINE webhook handler, Supabase sync, Render deploy trigger, War Room event forwarder. Workflows are **structural stubs** — nodes wired, credentials referenced via n8n credential references (not real values), no active triggers. Stored in repo under `n8n/workflows/` for version control.
Done when:
- [ ] 5 workflow stubs created via n8n MCP: alert-webhook, line-webhook, supabase-sync, render-deploy, warroom-forwarder
- [ ] Each workflow: nodes wired, credential refs (placeholders), no hardcoded secrets, disabled by default
- [ ] Workflow files committed to `n8n/workflows/` (version controlled)
- [ ] CI validates workflow JSON syntax + n8n MCP `validate_workflow` passes
- [ ] Reviewer (different model) checks structure + evidence; verdict recorded
- [ ] No production n8n deployment; no real credentials; no customer data
Budget: 4 hours ops + 1 hour reviewer (cap: ops ≤ $2 via OpenCode Go flat pool; reviewer free)
Links: Design sources above; n8n MCP tools (enabled per tool survey)

INTAKE T-075 — pending
Understanding: Create structural n8n workflow stubs per design docs via n8n MCP. No real credentials, no production deploy — structure first.
Scope: 5 workflow stubs with proper node wiring, credential references, disabled state. Committed to repo.
Needs: n8n MCP (verified enabled); design docs; ops; reviewer (different model).
Missing: None — n8n MCP enabled, design docs exist.
Plan: (1) ops creates workflows via n8n MCP; (2) validate + commit to repo; (3) CI + reviewer checks; (4) DELIVERY.
Estimate: within budget.
Risks: n8n MCP rate limits (UNVERIFIED); credential ref format (mitigate: use n8n standard pattern).
Decision: READY for INTAKE.

---

### T-076 — Database System: Schema/migrations ตามดีไซน์โครงการ (Database — structure first)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (Owner order via advisor)
Role: Project Lead (plan/coordinate) + builder (migrations via Supabase MCP) + reviewer L1–L3 on a different model + security (RLS/tenant isolation review)
Risk: L2 (schema changes on real Supabase via MCP; no customer data; pre-G1)
Goal: **วาง schema + migrations ให้เป็นรูปร่างก่อน** ตามดีไซน์โครงการ — **ยังไม่ต้องเอา/ไม่ต้องรอข้อมูลหรือ credential ของ Owner**
Design source files (ต้นทาง):
- `docs/future/architecture/FOUNDATION_V1.md` — Data contracts, tenancy, RLS policies
- `docs/proposals/WAR_ROOM_V1_SCHEMA_RLS_DESIGN.md` — War Room schema + RLS design
- `docs/product/CUSTOMER_FACING_RULES.md` — Data handling rules
- `docs/warroom/STARTUP_PLAYBOOK.md` — Step 0 database requirements
- `docs/product/PRICING_V1.md` — Pricing/quota tables
Scope: Create migration files via Supabase MCP (`supabase_apply_migration`) for: tenancy tables, identity tables, data contracts, War Room tables (rooms, agenda, participants, findings, decisions), pricing/quota tables, audit/log tables. Migrations are **structural** — tables, indexes, FK, RLS policies (FORCE RLS), roles/grants. No seed data, no real credentials, no production apply until Owner approves. Migration files committed to `migrations/` for version control.
Done when:
- [ ] Migration files created for all design-specified tables (via `supabase_apply_migration` on dev schema)
- [ ] Each migration: tables + indexes + FK + RLS ENABLE+FORCE + policies + role grants
- [ ] Migration files committed to `migrations/` (version controlled, ordered)
- [ ] Supabase MCP `supabase_list_tables` + `supabase_execute_sql` verification on dev schema
- [ ] Reviewer (different model) + security (RLS/tenant) check structure + evidence; verdicts recorded
- [ ] No production apply; no real credentials; no customer data
Budget: 4 hours builder + 1 hour reviewer + 1 hour security (cap: builder ≤ $2 Go pool; reviewer/security free)
Links: Design sources above; Supabase MCP (enabled per tool survey); T-072 (backup/restore proof on same project)

INTAKE T-076 — pending
Understanding: Create structural schema/migrations per design docs via Supabase MCP. No seed data, no production apply, no Owner credentials — structure first.
Scope: Full migration set for tenancy, identity, data contracts, War Room, pricing, audit. RLS FORCE throughout.
Needs: Supabase MCP (enabled); design docs; builder; reviewer + security (different models).
Missing: None — Supabase MCP enabled, design docs exist.
Plan: (1) builder creates migrations via Supabase MCP on dev schema; (2) verify via MCP; (3) commit migration files; (4) reviewer + security check; (5) DELIVERY.
Estimate: within budget.
Risks: Supabase MCP DDL limits (UNVERIFIED — T-072 will test first); RLS policy complexity (mitigate: security review per migration).
Decision: READY for INTAKE.

### T-078 — Auto-card signal mechanism: extend `monitor-log` to open task cards on 4 conditions (card-opening ONLY)

Status: **PARKED** — Owner order 2026-09-27: park, do not retry, do not change model. Reason recorded: three consecutive builder failures with three *different* symptoms (Primary `opencode-go/glm-5.3-flash` = empty output; Backup1 `openrouter/poolside/laguna-s-2.1:free` = upstream rate-limit; Backup2 `opencode-go/kimi-k3` = `reason: length`) point at the **task brief being too long/complex for the model**, not model luck. Revisit later with a smaller, split brief. Not closed.
Owner: Project Lead — 2026-09-27 (Owner order via this session; design source `docs/architecture/MESSAGE_FLOW_V1.md` + Track A → War Room linkage)
Role: Project Lead (plan/verify) + builder (extend `services/dev/tools/monitor_log.py`) + reviewer L1–L3 on a **different model**
Risk: L2 (extends an existing dev tool; writes to `TASKS.md`; **no** runtime/customer/production impact)
Goal: `monitor-log` can **open a new task card** in `TASKS.md` when one of four conditions is observed — and can do **nothing else**. It is a signal into the normal queue, never an actor.
Triggers (thresholds in the card, changeable by config):
1. the same role's model fails **≥ 3 consecutive times** → open a card to **Model Scout**: "ตรวจสอบ/เสนอสลับโมเดลตำแหน่ง X"
2. the bot cannot answer / hands off to the owner on the **same subject ≥ 3 times** → open a card to **Marketing**: "คำถามซ้ำที่ตอบไม่ได้: [content] — เจอ N ครั้ง"
3. one shop is **near/over quota for several consecutive months** → open a card to **Cost Guard**: "ตรวจสอบการใช้งานร้าน X"
4. a **red event unhandled for > 30 minutes** → open a card to **Project Lead** at status **NEEDS_DECISION**
**Hard safety rule (the core of this card):** the mechanism may ONLY open a card. It must **never** swap a model, change config, send a customer message, deploy, or take any other action. Every opened card enters the normal process (INTAKE → accept/decline → do → review) exactly like a human-opened card.
Done when:
- [ ] the four triggers are implemented with explicit, configurable thresholds
- [ ] opening a card appends a well-formed card block to `TASKS.md` (unique next `T-0XX` id, `Status: READY`, `Owner:` = the addressed role, `Risk:`, `Goal:`, the evidence that triggered it)
- [ ] **idempotent:** one ongoing condition opens exactly one card (dedup key per trigger+subject); re-observation does not create duplicates
- [ ] no code path in the mechanism performs any action other than writing the card (verified by reviewer reading the diff)
- [ ] simulation test with **fake events** proves each of the 4 triggers opens exactly one correct card (and the dedup holds); test artifact recorded
- [ ] reviewer on a **different model** checks the diff + the simulation evidence; verdict recorded
- [ ] no runtime/customer/production file touched; no secret in git
Budget: 3h builder + 1h reviewer (OpenCode Go pool / free; builder ≤ $2)
Links: `services/dev/tools/monitor_log.py` (T-003), `docs/product/MCP_TOOLS_V1.md` (`monitor-log`), `docs/warroom/ROLES.md` (Model Scout, Marketing, Cost Guard, Project Lead), `docs/warroom/MONITORING.md`, `docs/warroom/TASK_CONTROL.md` (board cap — see note)
Note (cap interaction): auto-opened cards count against the board's 10-open-card cap. The mechanism only signals; **triaging the board stays with the PL.** Flagged to the Owner as a follow-up decision.

INTAKE T-078 — pending

---

### T-077 — Lite schema change: `lite_processed_events` + `bots.business_info` fallback contact (protected doc — L3)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (Owner order: ND-1 resolved 2026-09-27, **option (ข)** — a dedicated L3 card; `docs/warroom/decision-log.md` 2026-09-27)
Role: Project Lead (plan/verify) + builder (migration + schema-doc edits) + reviewer L1–L3 on a **different model** + security (tenant isolation / RLS on the new table)
Risk: **L3** — `docs/data/LITE_SCHEMA_V1.md` is a **protected document** (`TASK_CONTROL.md` §8); adding a table also means a real migration + RLS policy + grants
Goal: the de-duplication store for inbound platform events exists as `lite_processed_events`, is tenant/bot-scoped with FORCE RLS, and is documented in `LITE_SCHEMA_V1.md`; `bots.business_info` is required to carry a fallback contact for the over-quota message (ND-2)
Done when:
- [ ] `LITE_SCHEMA_V1.md` documents `processed_events` / `lite_processed_events` (purpose, columns, scope rule, TTL) and the `business_info` fallback-contact requirement — **spec edit written 2026-09-27; checkbox flips only when the different-model reviewer confirms it**
- [ ] migration creates `lite_processed_events` with `tenant_id` + `bot_id` + `channel_id`, unique key (`tenant_id`, `bot_id`, `platform_event_id`), `ENABLE` + `FORCE ROW LEVEL SECURITY`, policy `tenant_id = app_private.current_tenant_id() AND bot_id = app_private.current_bot_id()`, `nippan_runtime` grants (pattern: `migrations/20260925120000_lite_rls_v1.sql`)
- [ ] tests: cross-tenant read/write rejected (fail-closed); duplicate insert is a no-op (not an error, not a second answer)
- [ ] reviewer (different model) + security verdicts recorded
- [ ] `decision-log.md` entry recorded (L3 requirement)
- [ ] no production apply; no real customer data; migration committed under `migrations/`
Budget: 2h builder + 1h reviewer + 1h security (OpenCode Go pool / free; builder ≤ $2)
Links: ND-1 + ND-2 (`docs/architecture/MESSAGE_FLOW_V1.md` §1.3, §4.2; `docs/warroom/decision-log.md` 2026-09-27), `docs/data/LITE_SCHEMA_V1.md`, `migrations/20260925120000_lite_rls_v1.sql`, T-002 (created the other `lite_*` tables), T-026/T-RLS-01 (RLS), T-076 (foundation schema — a separate card)

INTAKE T-077 — pending

---

### T-004 — Legal review: tenant agreement + end-customer privacy notice (PARKED — hard gate for Step 2)

Status: **PARKED** — cut from the dev-time plan by the Owner on 2026-09-25 ("อันนี้ต้องตัดออก เพราะตอนนี้อยู่ในช่วงทำระบบ งานนี้ไม่เกี่ยวข้องเลย"); **reopened as a tracked card 2026-09-27** so it lives on the board, not only in git history
Owner: Project Owner — must engage a lawyer / PDPA compliance advisor (this is **not** an AI seat)
Role: legal — an external human professional
Risk: L3 (the tenant agreement and the privacy notice are what customers actually agree to)
Goal: the tenant agreement and the end-customer privacy notice have been reviewed by a lawyer before the platform serves any real customer
Done when:
- [ ] Tenant agreement reviewed by a lawyer — the data-controller (tenant) / data-processor (platform) split is stated per `PDPA_COMPLIANCE.md` Layer 1, and the bot-is-an-assistant / owner-is-responsible wording per `BUSINESS_OPERATIONS.md` §2
- [ ] End-customer privacy notice wording reviewed (the short notice the bot shows on first contact, `PDPA_COMPLIANCE.md` Layer 1)
- [ ] The reviewed texts (or a reference to them) are recorded with the reviewer's identity and date
- [ ] No AI closes this card on its own — it closes only on a real legal review
Budget: one-off legal fee (the Owner sets the amount). No AI/model spend.
Links: `docs/security/PDPA_COMPLIANCE.md`, `docs/product/BUSINESS_OPERATIONS.md` §2–§3, `docs/product/ONBOARDING_FLOW.md`, `docs/warroom/STARTUP_PLAYBOOK.md` (hard gate in Step 2), `docs/warroom/decision-log.md` 2026-09-25 ("Legal work (T-004) cut from the dev-time plan")
Note: opening the first-customer onboarding card (Step 2) is blocked until this card is DONE — see the hard gate in `STARTUP_PLAYBOOK.md`.

INTAKE T-004 — pending (PARKED; no AI work is started)

---

### T-079 — Front-of-house: customer onboarding + config (setup via web-chat, confirmation summary, later-edit path)

Status: IN_PROGRESS — split into the child cards **T-079a…T-079f** below; **awaiting the Owner's review before any build starts**
Owner: Project Lead — 2026-09-27 (Owner order: "แตก ONBOARDING_FLOW.md + STOREFRONT.md เป็นงานสร้างจริง")
Role: Project Lead (plan/split) + builder (web UI + transport) + reviewer L1–L3 on a **different model** + security (customer-facing data path + PDPA notice)
Risk: L2–L3 (first customer-facing surface that processes a customer's uploaded business data; no tenant data exists yet — pre-G1)
Goal: the two design docs become **buildable work**, not just prose — a real page where a prospective customer onboards by talking to the assistant over the `web-chat` channel, approves a short confirmation summary before the bot goes live, and has a defined path to change their business info later.
Design sources: `docs/product/ONBOARDING_FLOW.md` · `docs/product/STOREFRONT.md` · `docs/product/CUSTOMER_FACING_RULES.md` §3 ("summary for the customer to confirm"; fixed menus only) · `docs/product/INTEGRATIONS.md` (web-chat adapter) · `docs/product/MCP_TOOLS_V1.md` (`web-chat-channel`, `web-fetch`, `file-reader`)
Build items (the card must split these into their own build cards with estimates):
1. **Setup page** — a visitor talks to the Onboarding assistant over `web-chat`; supports the three input kinds in `ONBOARDING_FLOW.md` (plain conversation / website link via `web-fetch` / uploaded file via `file-reader`).
2. **Confirmation summary** — before go-live, show the extracted **fixed-menu** config + a short sample conversation for the customer to confirm or adjust (ONBOARDING_FLOW steps 4–5).
3. **Later-edit path** — how a customer changes their business info after go-live. **DECIDED 2026-09-27 (Owner): option (ก) — talk to a Support agent.** No separate form in Phase A: build nothing ahead of a proven need (small shops / older owners are more comfortable typing a chat than filling a form); if edit requests later become frequent, a separate form becomes a Phase B card. → child card **T-079e**.
Done when:
- [ ] the three build items are split into child build cards with estimates and dependencies
- [x] the later-edit path is decided by the Owner: **(ก) Support agent** (2026-09-27) — written into child card T-079e
- [ ] reviewer on a different model checks the split is complete against both design docs
- [ ] **no implementation** starts inside this card (this card only produces the build cards)
Budget: planning/split only (no build spend)
Links: `docs/product/ONBOARDING_FLOW.md`, `docs/product/STOREFRONT.md`, `docs/warroom/STARTUP_PLAYBOOK.md` (Step 1 onboarding assistant; Step 3 storefront + web-chat), T-004 (hard gate — no real customer onboarding until legal review is DONE)

INTAKE T-079 — pending

---

> **T-080 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: Phase A uses the log + LINE alert already designed in `MONITORING.md`; **no admin web page in Phase A** — a real dashboard stays a Phase B/C trigger (25+ tenants / digest >15 min / a second person).

### T-079a — `web-chat` channel adapter (front-of-house foundation)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder (adapter + tests) + reviewer L1–L3 on a **different model**
Risk: L2 (new customer-facing channel; pre-G1, no customer data yet)
Goal: a visitor's message sent from a web page reaches the core and a reply comes back — the channel that the storefront demo, the onboarding assistant and the Support agent all run on. No LINE dependency anywhere in it.
Design source: `docs/product/INTEGRATIONS.md` (channel-adapter contract + normalized inbound/outbound), `docs/product/adapters/line-oa.md` (the pattern to follow), `docs/product/MCP_TOOLS_V1.md` (`web-chat-channel`, Step 3), `docs/architecture/MESSAGE_FLOW_V1.md` §1/§7/§14
Done when (each provable by running):
- [ ] adapter does the 4 adapter duties per `INTEGRATIONS.md` (authenticity, identity mapping, normalize, de-dup) and reports usage/errors to `usage-tracker` / `monitor-log`
- [ ] inbound/outbound use the normalized format exactly (`tenant_id, bot_id, channel_id, end_customer_ref, message_id, content[], reply_handle`) — no platform field name leaks into the core
- [ ] runnable proof: a local end-to-end run — post a message as a web visitor → the core answers → the reply returns; transcript saved
- [ ] scope enforced: a request that cannot be mapped to `tenant_id` + `bot_id` is rejected (never guessed)
- [ ] reviewer (different model) verdict recorded
Budget: 4h builder + 1h reviewer (Go pool / free; builder ≤ $2)
Links: `docs/product/INTEGRATIONS.md`, `docs/product/MCP_TOOLS_V1.md`, `docs/architecture/MESSAGE_FLOW_V1.md` §14, `docs/product/adapters/line-oa.md`
Depends on: nothing (foundation). Note: T-075 (n8n workflow stubs) is PARKED — this card does not wait for it.

---

### T-079b — Onboarding assistant: conversation / URL / file → fixed-menu config

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model**
Risk: L2 (processes a prospect's uploaded business data; no real customers yet)
Goal: the assistant reads what the prospect gives it (plain conversation / a website link / an uploaded menu-price file) and produces **fixed-menu config values** — never a raw prompt built from the customer's words.
Design source: `docs/product/ONBOARDING_FLOW.md`, `docs/product/CUSTOMER_FACING_RULES.md` §3, `docs/data/LITE_SCHEMA_V1.md` (`bots.business_info`, `tone`, `enabled_tools`, quotas), `docs/product/MCP_TOOLS_V1.md` (`web-fetch`, `file-reader`, `chat-bot-core`)
Done when (each provable by running):
- [ ] run against a sample shop (one website URL + one sample menu/price file) and show the produced config rows
- [ ] asks only for what is still missing; tone comes from the fixed list; output is fixed-menu values only (no raw customer text stored as instructions)
- [ ] ingestion cost bounds applied (`ONBOARDING_FLOW.md` "Cost controls"): page/file size cap, own-site pages only, no full crawl
- [ ] honesty rule 2 holds with the prospect (never names the model)
- [ ] reviewer (different model) verdict recorded
Budget: 6h builder + 1h reviewer (builder ≤ $3)
Links: `docs/product/ONBOARDING_FLOW.md`, `docs/product/CUSTOMER_FACING_RULES.md` §3, T-079a
Depends on: T-079a (transport for the conversation).

---

### T-079c — Customer setup page (chat with the Onboarding assistant over web-chat)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model** + security (customer-facing surface)
Risk: L2 (customer-facing UI; no payments, no tenant data yet)
Goal: a real page where a prospect onboards by chatting — accepts the three input kinds (conversation / website link / uploaded file) and shows progress.
Design source: `docs/product/ONBOARDING_FLOW.md`, `docs/product/STOREFRONT.md` item 5 ("Set up my bot"), `docs/product/CUSTOMER_FACING_RULES.md`
Done when (provable by running):
- [ ] open the page locally and complete an onboarding conversation end to end; transcript + saved run artifacts
- [ ] all three input kinds work on the page (typed answer, URL, file upload)
- [ ] the page never shows a model/vendor name and shows the short PDPA notice where it collects anything
- [ ] reviewer (different model) + security verdict recorded
Budget: 6h builder + 1h reviewer + 1h security
Links: `docs/product/ONBOARDING_FLOW.md`, `docs/product/STOREFRONT.md`, T-079a, T-079b
Depends on: T-079a, T-079b.

---

### T-079d — Confirmation summary + go-live gate

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079)
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model**
Risk: L2 (the gate that decides when a bot becomes active — fail-closed matters)
Goal: before the bot goes live, show the extracted **fixed-menu** config + a short sample conversation ("your bot will say things like…"); the customer confirms or asks for changes; **only on confirmation does the bot become active**.
Design source: `docs/product/ONBOARDING_FLOW.md` steps 4–5, `docs/product/CUSTOMER_FACING_RULES.md` §3, `docs/data/LITE_SCHEMA_V1.md` (`bots.status`)
Done when (provable by running):
- [ ] run through onboarding → the summary renders the extracted config + a sample conversation
- [ ] if the customer edits or declines, the config changes and the bot **does not** go live (fail-closed)
- [ ] on confirm, `bots.status` flips to active and the config rows are persisted — shown in the run
- [ ] reviewer (different model) verdict recorded
Budget: 4h builder + 1h reviewer
Links: `docs/product/ONBOARDING_FLOW.md`, `docs/data/LITE_SCHEMA_V1.md`, T-079c
Depends on: T-079c.

---

### T-079e — Later-edit path via Support agent (Owner decided (ก))

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079; Owner decision 2026-09-27: option (ก))
Role: Project Lead (plan) + builder + reviewer L1–L3 on a **different model**
Risk: L2 (a live tenant's own config changes; fixed menus only)
Goal: an existing customer asks in chat to change their business info; the Support agent (`ROLES.md`) applies the change **within fixed menus only**, and flags anything that could raise cost to Cost Guard first.
Design source: `docs/warroom/ROLES.md` (Support agent), `docs/product/CUSTOMER_FACING_RULES.md` §3, `docs/data/LITE_SCHEMA_V1.md` (`bots`)
Done when (provable by running):
- [ ] a chat change request updates the config row and the change is logged — shown in the run
- [ ] only fixed-menu fields can change; an attempt to set free-form instructions is refused
- [ ] a change that could raise cost (e.g. quota) is flagged to Cost Guard, not applied silently
- [ ] reviewer (different model) verdict recorded
Budget: 4h builder + 1h reviewer
Links: `docs/warroom/ROLES.md`, `docs/product/CUSTOMER_FACING_RULES.md` §3, T-079b
Depends on: T-079b.

---

### T-079f — Storefront page (public, one page: headline, live demo, price, one button)

Status: READY for INTAKE
Owner: Project Lead — 2026-09-27 (child of T-079; `STOREFRONT.md`, playbook Step 3)
Role: Project Lead (plan) + builder + reviewer on a **different model**
Risk: L1–L2 (public marketing page + live demo bot; the demo must have its own daily cap)
Goal: a prospect understands the offer in under a minute and tries a real bot before paying.
Design source: `docs/product/STOREFRONT.md`
Done when (provable by running):
- [ ] the one page runs locally with all 6 sections of `STOREFRONT.md` (headline, live demo, what it does, price 299, one button, small print)
- [ ] the live demo bot answers over `web-chat` on the cheapest tier with a working daily cap — shown by a run that hits the cap and stops
- [ ] no model name anywhere on the page; the demo shows the same consent notice as tenant bots
- [ ] reviewer (different model) verdict recorded
Budget: 4h builder + 1h reviewer
Links: `docs/product/STOREFRONT.md`, T-079a
Depends on: T-079a.

---

## REVIEW

(none)

## DONE

(completed cards moved to docs/archive/TASKS_DONE_ARCHIVE.md — T-RLS-01 added 2026-09-25)

- **T-030 — DONE 2026-09-26 (Owner approved).** n8n → Supabase as `nippan_n8n`: connection proven, RLS read isolation proven
  (tenant A = 1 / tenant B = 0), write isolation proven (cross-tenant INSERT rejected, RLS WITH CHECK 42501), positive control for
  tenant B, tables left empty (rollback). Workflows `CVhNSU5pjpGgzquB` + `eohtRWY8YEvEuS7n` in folder `Nippan Phase A`.
  Evidence + the exact SQL: `docs/n8n/T-030-execution-evidence.md`. Reviewer `opencode/space-bunny-free` (different model) pass 2.
  Owner scope condition (2026-09-26): n8n write/read is allowed **only inside the `Nippan Phase A` folder**. Carried residual:
  the credential still has `Ignore SSL Issues`; the card has never been run published/production.
