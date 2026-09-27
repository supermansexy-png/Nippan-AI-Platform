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

---

> T-030 (DONE 2026-09-26) is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`.
> T-031 (DROPPED 2026-09-25) is archived in `docs/archive/TASKS_PARKED.md`.
> T-049 (DONE 2026-09-26, reviewer ACCEPT-WITH-FINDINGS) is archived in `docs/archive/TASKS_DONE_ARCHIVE.md` (archived 2026-09-26 under card T-050, Owner-authorized).

### T-032 — Dispatch work over Git (issue → branch → draft PR → CI → review → merge)

Status: READY for INTAKE — needs the Owner's decision on repo settings + the external side's settings (see Blockers)
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
3. **Trigger = the Owner (RESOLVED 2026-09-25)** — "พี่เอง": the Owner starts each round; the assistant does not auto-start from a queue. Pilot A therefore tests only whether it can *find* queued work **once started**.
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

**Answer 2 — the four Codex-side values:** the project's required values are confirmed: Draft PR = ON · auto-merge = OFF · branch prefix `codex/` · no force-push — these match the card's hard rules exactly. The external side's ACTUAL current settings cannot be verified from this environment (they live on the Owner's Codex setup) = **UNKNOWN** until the Owner confirms on the Codex side or pilot A verifies them. Recommendation: proceed; pilot B's PR will demonstrate the branch prefix + draft state.

---

### T-033 — War Room in real use: the AI team's meeting room

Status: IN_PROGRESS — Owner answered 2 of 3 open decisions 2026-09-27 (fresh room per meeting = yes; Owner pays, ceiling $1/meeting). "ใครเข้าร่วม" (participants) still open-on-Owner.
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
3. **Who joins, and who pays.** **PARTIALLY RESOLVED 2026-09-27 — Owner answers: bearer = Owner ("พี่จ่าย"); cost ceiling = $1 per meeting ("ไม่เกิน 1 เหรียญต่อครั้ง").** The ceiling replaces the provisional $0.05 stop rule in the meeting plan above. **STILL OPEN: "ใครเข้าร่วม"** — which participants join the room (the architecture choice (a) room-driven turns / (b) team-driven record / (c) no provider calls) is unanswered; the pilot does not start until the Owner picks. Credit ≈ **$1.60** as of 2026-09-27.

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

### T-034b — War Room server: create-room path + usable agenda (paid builder)

Status: **DONE 2026-09-27** — all slices delivered, reviewed and **deployed to the Render preview** (PR #86, merge `da35d60`, deploy `dep-dasdcartqb8s739lmbmg` live). Evidence below.

**Status update 2026-09-27 (batch order):** slices 1–3 delivered and reviewed; slice 2b code committed (`aa36a81`) and pushed to `origin/dev-workspace`. **DEPLOY = BLOCKED on the Owner** — deploying any slice requires separate Owner approval (batch order: "deploy requires separate Owner approval"). No deploy is performed. Card marked blocked-on-Owner.

**DEPLOY DONE — 2026-09-27 (Owner approved, advisor relayed: "1 อนุมั1ิ" = อนุมัติ):**
- The two T-034b commits missing on `phase2/postgres-logical-schema` were cherry-picked (runtime files only): `7ef25f4` (slice 1 seed script — without it the deployed create-room route called `seed(room_id=, title=)` on a script that did not accept those kwargs) and `aa36a81` (slice 2b agenda). Local cherry-picks: `6f7dd15` + `00c0b0e`; content verified identical to the dev-workspace commits (EOL-only diff).
- Direct push to `phase2/postgres-logical-schema` is blocked by repo rules (GH013: PR required + `postgres-regression` status check) — so the Owner-approved merge-on-green path was used: branch `deploy/t-034b-warroom-agenda` → **PR #86** (https://github.com/supermansexy-png/Nippan-AI-Platform/pull/86) → CI **postgres-regression PASS (1m5s)**, remote-auth PASS (28s) → merged as merge commit **`da35d6064ce8eb9c33c831517e825d9b00754335`** (2026-09-27T08:39:06Z).
- Render deploy **`dep-dasdcartqb8s739lmbmg`** (auto-triggered by the merge push) → status **live** at 2026-09-27T08:40:06Z, serving commit `da35d60`.
- Live check: `GET https://chetgo.onrender.com/health` → **200** `{"status":"ok","service":"nippan-core","environment":"development"}`; `GET https://chetgo.onrender.com/war-room/` → **403** `{"detail":"war_room_preview_remote_auth_required"}` (the preview auth gate, fail-closed as designed — the rendered page itself is confirmed by the Owner in his browser, the documented limit of every previous preview deploy).
- No DB migrations, no production system touched, no force push. **Card closed DONE.**
Owner: Project Lead — 2026-09-26 (Owner order: the agenda panel "ถ้าจะมีไว้ต้องใช้งานได้" and a new meeting must not need hand-edited SQL)
Role: Developer — **paid builder `z-ai/glm-5.3-flash` (Owner-locked)** + reviewer `opencode/space-bunny-free` + **security reviewer `openrouter/nex-agi/nex-n2.5-mini:free`** (a new write endpoint on the transport is security-relevant)
Risk: L3 (new write path on the transport: authorization, scope binding, fail-closed behaviour)
Goal: a meeting can be created and its agenda managed from the room itself, without anyone editing the preview database by hand.
Done when: 1) a reviewed create-room path exists (each meeting gets its own room, owner-only, server-established actor, fail-closed); 2) the agenda can be created/edited/closed and a message shows which agenda item it belongs to; 3) previous rooms stay reachable as archives; 4) tests + CI green; 5) reviewer **and** security reviewer verdicts recorded; 6) no schema/RLS/grant change and no production system touched.
Budget: 1–2 days
Links: T-034a, T-033 (blocker 2/3), `services/core/app/war_room/transport.py`, `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md` (the hand-made room that this replaces)

INTAKE T-034b — 2026-09-26 (Project Lead, under the Owner's delegation while he is away; Owner order: the room must be ready to use when he returns)
Understanding: two things stop the room from being usable without the Project Lead: a new meeting cannot be created without hand-written SQL, and the agenda panel shows a meeting item that nobody can create, edit or close. Owner also wants the Project Lead to accept and trial the room before handing it over.
Scope, in slices so each can be reviewed on its own: **slice 1** — a reviewed create-room path that works from the command line (parameterised seed script, no new HTTP surface, no auth change); **slice 2** — the in-room path (create a meeting, manage the agenda) as a reviewed server addition with a security review, then the matching UI; **slice 3** — PL acceptance + a trial meeting, then hand over.
Team: paid builder `openrouter/z-ai/glm-5.3-flash` (server code, Owner-approved for this card) + reviewer `opencode/space-bunny-free` + security reviewer `openrouter/nex-agi/nex-n2.5-mini:free` for slice 2.
Done when (per slice): slice 1 — the script can create an additional room with a chosen id and title, refuses to reset a non-default room without an explicit force flag, scopes every delete to the preview tenant/application, runs deletes plus inserts in one transaction, and a different model has reviewed it; slice 2 — a meeting can be created and its agenda managed from the room with the owner-only, fail-closed, server-established actor rules, tests + CI green, reviewer and security verdicts recorded; slice 3 — the PL opens a fresh room, drives one real meeting, verifies the durable artifacts and the measured cost, and reports the evidence.
Decision: ACCEPT — slices as above.

**WORK LOG — T-034b (PL, 2026-09-26)**
- slice 1 written by the worker (GLM) in `services/core/scripts/seed_war_room_preview.py`: adds `--room-id` (UUID-validated), `--title` and `--force`.
- reviewer round 1 = ACCEPT-WITH-FINDINGS (F1 the seven deletes keyed only on `room_id` with autocommit and no confirmation could silently destroy a live room; F2 child-row ids were room-independent constants so a second room collided on the primary keys after the room row had committed; F3 an empty `--title` fell back silently).
- fix round 1 addressed all three; reviewer round 2 = ACCEPT-WITH-FINDINGS (all three closed) with three follow-ups taken: the connection still used `autocommit=True` so a failed insert after successful deletes would leave the room permanently gone; an empty title failed only at the database constraint after the delete; the confirmation line printed the new title rather than the title of the room about to be destroyed.
- fix round 2 in progress at the time of writing (`t034b-slice1-fix2`); slice 1 is **not** run against the preview database until it passes review, because that database holds the acceptance-evidence room and the live meeting room.
- slice 1 closed and committed: reviewer round 3 confirmed the guard now requires `--force` only for a room that already exists; the hardening (tenant-scoped lookup, row-based guard test) and three tests were added; **full `services/core` suite against an embedded PostgreSQL 16 with all migrations applied = 162 passed, 0 failed**.
- slice 2a (server route `POST /war-room/rooms`) committed: it reuses the seed helper, authorizes first, refuses with 503 when unconfigured, generates the room id itself, runs the seed on a worker thread, maps refusals to 409 with a static detail and database failures to 503. Code reviewer (different model) = ACCEPT-WITH-FINDINGS; its blocker was a bare `RuntimeError` from three seed guards escaping as a 500, now caught. Live suite after the fix = **169 passed, 0 failed**.
- slice 2c/2d (UI: `เริ่มประชุมใหม่` control wired to the new route; conversation windowed to 30 events with `ดูข้อความก่อนหน้า`; system log capped at 50 lines) written; UI reviewer = ACCEPT-WITH-FINDINGS with one must-fix (the top bar had four children in a three-column grid) and one should-fix (the reveal handler's scroll anchor), both sent back for fixing.
- **Security review of slice 2a**: the appointed security model `openrouter/nex-agi/nex-n2.5-mini:free` **no longer resolves** ("Model not found") — a substitute free model (`opencode/nemotron-3-ultra-free`) was used and the substitution is recorded here rather than hidden. Verdict ACCEPT-WITH-FINDINGS: authorization order, scope, fail-closed mapping, injection handling, threading and rollback all pass; **one blocking finding — no rate limit, so an authenticated caller or a leaked dev API key can create unlimited rooms**. A 10-per-hour in-process limiter was added in response, with tests; the deploy waits until it is verified.
- Environment findings worth keeping: the headless runner truncates large tool output, so jobs must be told to read only small regions — after that instruction `z-ai/glm-5.3-flash` completed its server work (it had stalled twice before on whole-file reads); the `builder` subagent grants no `edit` permission, so code jobs run through the `worker` agent with the builder model; and `openrouter/nvidia/nemotron-3.5-lightning:free` only works with the `openrouter/` prefix.

INTAKE T-034b slice 2b — 2026-09-26 (Project Lead, under Owner delegation; ordered by advisor `opencode-go/mimo-v2.6-pro`, record in `docs/warroom/ADVISOR_LOG.md`)
Understanding: the room's agenda panel is read-only — an agenda item ("วาระ") can only appear via the seed script. Slice 2b adds the in-room path so a meeting's agenda can be created/edited/closed from the War Room web page, owner-only, fail-closed, with a server-established actor, and messages keep showing which agenda item they belong to.
Scope: server routes under the existing preview transport (`services/core/app/war_room/transport.py`) + the agenda controls in `services/control-plane-web/war-room/` + tests. No schema/RLS/grant change, no deploy, no production; the pending `SESSION_HANDOFF.md` change is committed as housekeeping.
Team: builder/worker `opencode-go/glm-5.3-flash` (paid, approved for this card) · reviewer `opencode-go/space-bunny-free` · security on a live free model ≠ author ≠ reviewer (the appointed `openrouter/nex-agi/nex-n2.5-mini:free` no longer resolves — substitute recorded on the card). PL does not write code (T-043).
Done when: 1) agenda create/edit/close reachable from the room page, owner-only + fail-closed + server-established actor; 2) a message shows which agenda item it belongs to; 3) `services/core` suite green with counts stated; 4) reviewer + security verdicts recorded; 5) no schema/RLS/grant change and no production touched.
Decision: ACCEPT.

**WORK LOG — T-034b slice 2b (PL, 2026-09-26)** — status: **code complete, reviewed; NOT yet deployed**
- Received as an advisor work order (`opencode-go/mimo-v2.6-pro`); instruction record written by the PL as the receiver in `docs/warroom/ADVISOR_LOG.md`.
- Model finding: the assigned builder `opencode-go/glm-5.3-flash` **failed twice with zero output** (`step_finish reason "length"`, reasoning 4096) on this card, and so did `opencode-go/kimi-k3`; **builder was substituted to `opencode-go/mimo-v2.6-flash`** (same OpenCode Go flat-rate pool, no new spend) with small prescriptive briefs — that model completed every slice-2b step. Substitute is recorded here rather than hidden; the failure is in `DEV_ERROR_LOG.md`.
- Security model: the appointed `openrouter/nex-agi/nex-n2.5-mini:free` still does not resolve (`get-model` → 404, re-checked this session). Substitute used: `opencode/nemotron-3-ultra-free` (Zen free, differs from author and reviewer) — same substitution slice 2a recorded.
- Server (`services/core/app/war_room/`): added `RoomAgendaCreatePayload` + `RoomAgendaUpdatePayload`, a fail-closed `RoomCommandOwnerCheck` in `auth.py`, and two owner-only routes — `POST /war-room/rooms/{room_id}/agenda` (201; server assigns id + `max(sequence)+1`, status OPEN) and `POST /war-room/rooms/{room_id}/agenda/{agenda_item_id}` (200; partial edit, sets `completed_at` with `COMPLETE`/`CANCELLED`). Actor is server-established, authorization runs before any read/write, every statement is inside `tenant_transaction`, errors map 403/404/422/503 (never a 500). No schema/RLS/grant change.
- UI (`services/control-plane-web/war-room/`): agenda create form + per-item close/reopen + inline retitle, Thai notices, `credentials: "same-origin"`, no `innerHTML`; the stale asset cache-buster was bumped to `?v=20260926-agenda`.
- Review round 1 (`opencode-go/space-bunny-free`) = **REJECT** with 2 must-fix: the agenda status domain was wrong (`OPEN/CLOSED` vs the table's `OPEN/RUNNING/NEEDS_OWNER_DECISION/COMPLETE/CANCELLED`, and the completion rule `(status in (COMPLETE,CANCELLED)) = (completed_at is not null)`), plus a test fake that could not catch it. Fix round applied. Review round 2 = **ACCEPT-WITH-FINDINGS, no must-fix** (non-blocking: the UPDATE does not refresh `updated_at`; the fake does not assert the UPDATE's tenant/app/room predicates).
- Security review (`opencode/nemotron-3-ultra-free`) = **ACCEPT-WITH-FINDINGS** (blocking-0): one non-blocking note — no rate limit on agenda writes (room creation has one); acceptable for the dev preview, required before production. Delta re-check after the fix round = **ACCEPT**.
- Tests: `cd services/core && python -m pytest -q` → **176 passed, 9 skipped**; the transport file alone **53 passed**. The 9 skips are the PostgreSQL integration tests (they require `NIPPAN_TEST_POSTGRES_ADMIN_DSN`; no Docker/PostgreSQL is available in this environment, so the live-DB suite of previous slices was **not** re-run here — UNKNOWN). The CI workflow `.github/workflows/war-room-remote-auth.yml` only triggers on a pull request into `phase2/postgres-logical-schema`, so no CI ran for this `dev-workspace` push.
- 2c/2d confirmation (order item): the must-fix (top bar four children in a three-column grid) and the scroll-anchor should-fix are **VERIFIED present** in the committed tree (`services/control-plane-web/war-room/war-room.css:24` now has four columns; the anchor logic is in `war-room.js` commit `ba830ef`, which is an ancestor of `HEAD`).
- Housekeeping (order item 1): the pending `docs/project-memory/SESSION_HANDOFF.md` rewrite was committed as its own commit (`549b0fd`).
- **Commit:** slice 2b = `aa36a81`, pushed to `origin/dev-workspace` (8 files: the two war-room modules, the transport tests, the three web assets, `ADVISOR_LOG.md`, `DEV_ERROR_LOG.md`).
- **Advisor-mandate audit (order requirement):** `opencode-go/kimi-k3`, run `runs/2026-09-26T14-33-23Z-t034b-advisor-audit` → **WITHIN-MANDATE-WITH-FINDINGS**, A1–A5 PASS. Findings recorded: the builder substitution was made without prior approval (disclosed, same pool, no new spend), the security substitute, "CI green" only partially met (the workflow does not trigger on a `dev-workspace` push), and the non-blocking notes above. Verdict written into `ADVISOR_LOG.md`.
- **Not done / carried:** not deployed (per scope — the rate-limiter deploy note still waits); the live PostgreSQL suite was not re-run (no Docker/PostgreSQL in this environment); the board (`TASKS.md`) and `CURRENT_STATE.md` carry another session's concurrent uncommitted edits (card T-045), so this card's work log is present on disk but **left uncommitted** by the PL to avoid committing that session's work.

**WORK LOG — T-034b slice 3 (PL, 2026-09-26)** — status of this slice: **DELIVERED — in REVIEW; awaiting the Owner**. The acceptance trial was driven by an **agent, not the Owner**.
- Order: advisor `opencode-go/mimo-v2.6-pro`; Owner intent verbatim `"หาคนไปเทศ warroom แทนพี่"`. Instruction record written by the PL as the receiver in `docs/warroom/ADVISOR_LOG.md` before the work was queued.
- Execution: headless worker `opencode-go/mimo-v2.6-flash` (OpenCode Go) drove a scripted trial against a **local** stack — the real FastAPI app (`app.main:app`) on `127.0.0.1:8011`, the real routes, the real web assets, and a **throwaway embedded PostgreSQL** with all 9 migrations applied. No deploy, no Supabase/Render/Cloudflare, preview database untouched. **Cost $0.000000** (model turns OFF → 0 provider calls; `usage_events` = 0).
- Done-when covered (all re-verified by the PL against the raw artifacts): fresh room through the tested create path — `POST /war-room/rooms` → **201**, room `941be907-fb1d-4b62-8088-7b9f80b0ba6a`; agenda **create 201 / edit 200 / close 200** (`completed_at` set) confirmed in the database; meeting lifecycle `PREPARE`→READY, `START`→RUNNING, `ASK_ALL` 200 with a durable owner message linked to the agenda item; the UI page + JS/CSS served **200** and the exact routes the page calls exercised over real HTTP — not unit tests.
- Evidence: `runs/2026-09-26T15-06-50Z-t034b-slice3/` (`RESULT.md` + the PL verification addendum, `http-transcript.md`, `db-artifacts.txt`, `trial-checks.json`, `server.log`, `cleanup.txt`).
- Independent evidence review (`opencode-go/space-bunny-free`, ≠ author): `runs/2026-09-26T15-28-53Z-t034b-slice3-review` = **ACCEPT-WITH-FINDINGS**, no blocking. Findings actioned in the addendum: a wrong citation fixed; two discarded rooms from aborted attempts disclosed; the Phase-B skip reason marked UNKNOWN.
- Advisor-mandate audit (`opencode-go/kimi-k3`, ≠ advisor): `runs/2026-09-26T15-36-11Z-t034b-slice3-advisor-audit` → **WITHIN-MANDATE-WITH-FINDINGS**, A1–A5 all PASS. Verdict written into `ADVISOR_LOG.md`.
- **Honest limits — not passes:** (1) **no AI participant turns** — the meeting was driven only through its lifecycle and the owner message; a provider call would be required and the order's budget is Go/free-only, so participant turns are evidenced separately by the T-033 pilot on the deployed preview ($0.000149); (2) browser-only behaviour (DOM, clicks, live SSE in a page) = **UNKNOWN** — no browser in this environment; (3) **new portability finding**: `python -m uvicorn app.main:app` cannot serve the DB routes on Windows (psycopg refuses `ProactorEventLoop`); a selector-loop start works (`run_server.py`); (4) a new room is **not empty** — `POST /war-room/rooms` runs the preview seed, so it arrives with 1 agenda item (`ประชุม #001 — Preview ภาษาไทย`), 8 participants, a finding and a decision.
- **Carried / not done:** the rate-limiter deploy note still waits (no deploy this slice); no commit was made for the trial.

---

> NOTE (Project Lead, 2026-09-26, second session): this card was authored by the Project Lead while the working-tree
> board was in its broken 33-line state (see `DEV_ERROR_LOG.md`); another session then repaired the board and
> preserved the card. It was first written as "T-030" — **renumbered T-035** here because the card number T-030
> belongs to the archived n8n/RLS card. Content is unchanged apart from the number and the intake header.



### T-050 — Whole-project study: convene an existing-role committee and return a detailed draft roadmap

Status: IN_PROGRESS — Owner-ordered 2026-09-26 (verbatim order below); read-only study; deliverables are **DRAFT — NOT APPROVED**
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
- [ ] **finding 1** — a Windows start of the core dev server that reaches a working DB-backed state is documented in `services/core/README.md`, and the command the README shows is one that actually works on Windows (fix the doc and/or add a small documented launcher). Written by builder/worker; the PL does not edit the runtime file.
- [ ] **finding 2** — the pre-seeded new room (1 agenda item + 8 participants + a finding + a decision, from reusing the preview seed inside `POST /war-room/rooms`) is assessed against the T-034b create-room intent; fixed only if clearly unintended, otherwise recorded with options for the Owner. **No code change if it is a product choice.**
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

> **T-064 (DONE 2026-09-27)** is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`. One-line result: the **Google** provider works end to end (live call proven); **Groq** was wired correctly and its key is valid, but the free tier caps it, so the Owner parked it ("ปิด"). **Open follow-up (Owner):** a cost exception for Google (no usable Gemini model fits `MODEL_POLICY`'s $0.25/$1.00 cap), then HR staffing. No commit was made for this card.

### T-067 — Google free tier adoption: 2 models (non-sensitive fallback)

Status: OPEN — created 2026-09-27 from the Owner's direct order ("เคเอา2ตัว"); recording done, seat pinning NOT started
Owner: model-recruiter (HR) — limits check + seat proposal; Project Lead records/verifies
Role: model-recruiter (limits + proposal) + builder (pin apply, only after the Owner approves) + reviewer on a **different model**
Risk: L1–L2 — dev-time roster/model config. No runtime/production/customer/data impact. Standing caveat: the Google **free** tier must never receive repo code, secrets, customer data, or any confidential material.
Goal: adopt exactly two Google free-tier models as a zero-cost fallback for non-sensitive work, and record the real limits.
Adopted: `google/gemini-flash-lite-latest` (routine) · `google/gemini-3.8-flash` (higher-quality fallback) — both live-probed HTTP 200, cost $0.
Stand-ins (probed 200, NOT adopted): `google/gemini-3.1-flash-lite` · `google/gemini-3.5-flash-lite`. Excluded: `google/gemini-2.5-flash-lite` (404, retired) · `google/gemma-4-31b-it` (500 INTERNAL).
Done when:
- [x] `MODEL_ROSTER.md` + `DECISIONS.md` + `CURRENT_STATE.md` updated (2026-09-27)
- [ ] the real free-tier limits (RPM/TPM/RPD) recorded from the AI Studio rate-limit page for this project, or UNKNOWN declared with its source
- [ ] HR proposes which seats may use the 2 Google models as a free fallback (non-sensitive work only), with the anti-redundancy check
- [ ] Owner approves the proposed pins
- [ ] builder applies the pins (`opencode.json` / `.opencode/agents/*.md`); reviewer on a different model verifies; PL keeps no runtime-file edit
Budget: $0 — free-tier probes and free models only; no paid call for this card.
Links: `docs/product/MODEL_ROSTER.md` § "Google free tier — adopted 2026-09-27" · `docs/project-memory/DECISIONS.md` (2026-09-27 entry) · Google Gemini API Additional Terms § "Unpaid Services"
Note: this card changes **no** runtime file; model pins require separate Owner approval before any agent config is touched.

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
