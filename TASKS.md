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
1. Repo settings: **OPEN** — protection on `dev-workspace` not decided yet (checked: `dev-workspace` protected = **false**; `phase2/postgres-logical-schema` = **true**). Owner decision pending.
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

---

### T-033 — War Room in real use: the AI team's meeting room

Status: READY for INTAKE — blocked on the Owner's decisions (access, fresh room, who joins and who pays). No work starts until those are answered.
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
2. **A fresh room per meeting.** The seeded room is terminal `STOPPED`, the state machine permits no exit, and there is no create-room endpoint. Options: (a) add a reviewed create-room/seed path (code change → builder + reviewer); (b) reset the preview room to `DRAFT` before the pilot (one recorded data operation on the isolated preview DB) so the full lifecycle can be driven live; (c) leave it and accept that the first meeting happens on a fresh seed later.
3. **Who joins, and who pays.** Two architectures, and the choice decides the whole pilot:
   (a) **room-driven turns** — enable bounded turns on ONE preview model (`poolside/laguna-s-2.1` by default) so the room itself produces the AI turns. Cheap (the measured 2026-09-23 session cost $0.00027), but the voices are that single model, **not** our real roster agents;
   (b) **team-driven record** — our real AI team (the dev-time agents per `MODEL_ROSTER.md`) does the work and the room is the durable record of the meeting (plan, assignments, reports, problems). Matches the Owner's stated intent, needs a reviewed posting path for non-owner participants;
   (c) no provider calls at all — participants post without room-driven turns.
   Credit ≈ **$1.60**; any paid pilot needs a hard per-meeting ceiling approved by the Owner.

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

Status: BLOCKED behind T-034a — start only after the Owner has used the improved screen.
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

### T-035 — Re-staff the dev team on OpenCode Go (paid primary, free as backup)
Status: IN_PROGRESS (HR re-study queued 2026-09-26 as run `2026-09-26T09-27-58Z-go-restaff-v2`; Owner asked for it in chat)
Owner: Project Lead (plan/record) + Model Recruiter (proposal)
Role: Project Lead + model-recruiter
Risk: L2 — dev-process model routing + cost policy; `MODEL_ROSTER.md` rewrite needs Owner approval
Goal: every dev role is staffed by the best-suited model available in the OpenCode Go
subscription (paid, flat $10/mo with per-model caps); free models drop to backup/fallback
instead of being primary.
Done when:
- HR delivers a role×model proposal built on Go availability + price/limit + privacy + capability
  evidence, with each claim marked VERIFIED / INFERRED / UNKNOWN and a `needs-owner-decision` list
- Owner approves the mapping (all of it, or a subset)
- `opencode.json` + `MODEL_ROSTER.md` updated to the approved mapping; free models kept as backup
- one headless job per migrated role runs end-to-end on the Go provider, evidence under `runs/`
- `SESSION_HANDOFF.md` refreshed and a `decision-log.md` entry written
Budget: HR study = one headless job; implementation = one working session
Links: `docs/product/MODEL_ROSTER.md`, `opencode.json`, `scripts/headless_run.mjs`, `https://opencode.ai/docs/go/`

**Owner directive 2026-09-26 (verbatim intent):** now that we pay for this package, the team must
stop using free models as primary — HR must find the model that best suits each job.

**Owner directive 2026-09-26 (second — supersedes the builder lock):** re-select the WHOLE team; the
new stronger models are already included in the paid monthly package; prefer better coders and
better coordinating agents; HR selects from published reviews/benchmarks only — **no testing**; HR
proposes, and the Owner discusses the report **before** any appointment is approved. → the builder
lock to GLM-5.3-Flash is **lifted**.

**HR run log (T-035):**
- run `2026-09-26T09-21-40Z-go-restaff` — **FAILED, 0 output.** `--agent model-recruiter` is a
  subagent, so the CLI silently fell back to `project-lead` (see `DEV_ERROR_LOG.md`), and the model
  then hit its reasoning-length cap (`step_finish reason "length"`, reasoning 4096, output 0). The
  only artefact is its INTAKE below. Cost ≈ $0.006 of Go usage. Superseded.
- run `2026-09-26T09-27-58Z-go-restaff-v2` — agent `worker` (primary agent, no fallback), model
  `opencode-go/mimo-v2.6-pro`; brief = full re-selection of all 9 roles, benchmark/review-based, no
  testing, proposal only (no appointment). **Result: NEEDS_DECISION — the brief reached the worker truncated
  (~600 chars) so it refused to guess.** Cost ≈ $0.028. Defect recorded in `DEV_ERROR_LOG.md`.
- run `2026-09-26T09-31-09Z-go-restaff-v3` — same agent/model; prompt reduced to a 190-char pointer and the
  full brief moved to `runs/briefs/t035-hr-restaff.md` (repo-local, gitignored). This is the authoritative
  run for the T-035 proposal.
- Already in the tree as input: `docs/product/MODEL_POLICY.md` § "OpenCode Go — approved provider"
  — an uncommitted draft authored by another session. Handed to HR as **input**, not as a decision.

Verified facts 2026-09-26 (PL, evidence class VERIFIED unless noted):
- Provider `opencode-go` is authenticated in this workspace (`auth.json` entry, type `api`) and
  serves inference: `GET /zen/go/v1/models` → HTTP 200, 35 model ids; `glm-5.3-flash` and
  `space-bunny-free` chat completions → HTTP 200 with `served_model` echoed.
- Go catalogue ids returned: deepseek-v4-flash, deepseek-v4-flash-vision-exp, deepseek-flash,
  deepseek-v4.1-flash, deepseek-v4-pro, glm-5.1, glm-5.2, glm-5.3, grok-4.6, grok-4.7,
  muse-spark-1.2-contributor, muse-spark-1.3-contributor, glm-5.3-flash, omen-alpha, gpt-5.6-luna,
  gpt-6-luna, hy3, hy4-preview, kimi-k2.6, kimi-k2.7-code, kimi-k3, mimo-v2.5, mimo-v2.6-flash,
  mimo-v2.5-pro, mimo-v2.6-pro, minimax-m2.5, minimax-m2.7, minimax-m3, space-bunny-free,
  longcat-2.0, qwen3.6-plus, qwen3.7-max, qwen3.8-max, qwen3.8-flash, qwen3.7-plus
- Cost context: OpenRouter balance ≈ **$1.19** left ($45 credits, $43.81 used, checked 2026-09-26);
  PL, builder and HR currently route through OpenRouter → cliff risk.
- Privacy (from the Go doc): most models no-training / 0-day retention; **Muse Spark 1.2 & 1.3
  Contributor train on prompts+outputs and are NOT ZDR**; Grok 4.7/4.6 and GPT Luna keep 30-day
  abuse-monitoring logs.
- Constraint carried over: builder is Owner-locked to GLM-5.3-Flash (2026-09-25) — HR may propose a
  change only as an explicit owner-decision item. Reviewer model ≠ builder model; reviewer model ≠
  security model. No training/non-ZDR model as primary where repo code or config is handled.
- Drift found: `opencode.json` default + `small_model` = `opencode/ling-3.0-flash-fin-free`
  (a model previously recorded unusable/banned for PL+HR) — fix alongside the mapping.
- Policy nuance to record on approval: `DEV_WORKING_GUIDE.md` says "OpenCode Zen = FREE MODELS
  ONLY"; OpenCode Go is a separate Owner-purchased subscription, not a per-call paid Zen model.

INTAKE — T-035 — `opencode-go/gpt-6-luna` — 2026-09-26
Understanding: I will have HR evaluate suitable OpenCode Go models per dev role using verified availability, limits/cost, privacy, capability and probe evidence, then implement only the mapping the Owner approves. Free models may remain as backups; no customer/runtime routing is in scope.
Done when: (1) evidenced role×model proposal with VERIFIED/INFERRED/UNKNOWN + owner decisions; (2) Owner approves mapping; (3) approved `opencode.json` + `MODEL_ROSTER.md` mapping, free backups retained; (4) one end-to-end Go headless job per migrated role, evidence in `runs/`; (5) refreshed handoff + decision-log entry.
Needs: HR (`opencode/nemotron-3-ultra-free`, temporary roster assignment) and Go provider access; later, Owner's mapping approval, builder, independent reviewer, and per-role headless evidence.
Missing: fresh per-candidate limits/privacy/capability/readiness evidence and Owner-approved role mapping; `opencode.json`/roster changes and per-role end-to-end runs are not yet authorized by an approved mapping.
Plan: L2 — 1) HR runs one bounded readiness/recruitment job; 2) report proposal and wait for Owner mapping approval; 3) after approval, delegate only approved config changes; 4) validate, run one headless check per migrated role, obtain different-model review, then record handoff/decision evidence.
Estimate: HR study = one headless job; approved implementation = one working session; within card budget.
Risks: routing/config drift, Go shared usage buckets and privacy restrictions; current repo has unrelated uncommitted changes that must remain untouched. No secrets/customer data go to free models.
Decision: ACCEPT

### T-038 — Advisor mandate + governance rule repair after the OpenCode Go re-staffing

Status: IN_PROGRESS (Owner instruction 2026-09-26 in chat)
Owner: Project Lead (documents) + builder/worker (agent files); Owner approved the mandate in chat
Role: Project Lead (plan/record) + builder (agent config) + reviewer (independent audit)
Risk: L2 for the agent files; **L3 for any change to a protected doc** (`AI_OPERATING_PROTOCOL.md`,
`TASK_CONTROL.md`) — those need a reviewer on a different model + a `decision-log.md` entry

Goal: the Owner-facing `advisor` ("ที่ปรึกษาวางแผน") exists with its full mandate, and the project's
rule set no longer contradicts the new model/provider/role reality.

Owner instruction (intent): the advisor may command every agent, translates the Owner's words into
rigorous AI work orders and issues them to the PL (who distributes); it may approve/commit while the
Owner is away; it may NOT edit files and may NOT order work outside the working protocol. An
oversight system must exist that detects out-of-mandate orders and rule violations. The rules must be
improved and checked for contradictions after the wholesale model/role change.
Record: `docs/warroom/ADVISOR_LOG.md` T-038 (written by the receiver).

Done when:
- [x] `.opencode/agents/advisor.md` carries the final mandate (`task: allow`, git commit/push allowed, `edit: deny`)
- [x] `docs/warroom/ADVISOR_MANDATE.md` defines powers, limits, the instruction record and the per-card audit
- [x] `docs/warroom/ADVISOR_LOG.md` created; record is written **by the receiver**, not the advisor
- [x] advisor agent skills created (T-040): `.opencode/skills/advisor-work-order/SKILL.md` (bounded work
      order + the record format) and `.opencode/skills/advisor-mandate-audit/SKILL.md` (the A1–A5 audit
      with the three verdict values) — discovered by opencode from `.opencode/skills/<name>/SKILL.md`
- [x] `AGENTS.md` recognises the advisor in the order chain `Owner → advisor → Project Lead → specialist`
- [x] `docs/warroom/START_PROMPT.md` no longer assigns dead/old models and carries the Go provider rule
- [x] independent audit of this card's advisor instructions, run on a model ≠ `opencode-go/mimo-v2.6-pro`
      → `opencode-go/kimi-k3`, verdict **WITHIN-MANDATE-WITH-FINDINGS** (recorded in `ADVISOR_LOG.md`)
- [x] protected docs updated on the separate L3 card T-039 with a Decision Log entry —
      `AI_OPERATING_PROTOCOL.md` + `TASK_CONTROL.md` (both) · `ROLES.md` deliberately untouched
      (it describes the runtime role ecosystem, not the dev-time team)
- [ ] `docs/project-memory/CURRENT_STATE.md` refreshed; board housekeeping (T-034a is DONE → archive)

Conflict scan (2026-09-26, PL, grep-based — see the findings reported to the Owner):
1. `docs/warroom/START_PROMPT.md` still assigned `z-ai/glm-5.3-flash` as an Owner-locked builder, plus
   `opencode/nemotron-3-ultra-free` / `opencode/big-pickle` for review tiers → **FIXED** in this card.
2. `AGENTS.md` slug rule listed only `openrouter/` and `opencode/` → **FIXED** (added `opencode-go/`).
3. `.opencode/agents/project-lead.md` slug line lacks `opencode-go/` and does not name the advisor upstream → **OPEN**.
4. `docs/warroom/DEV_WORKING_GUIDE.md` still says "OpenCode Zen = FREE MODELS ONLY" with no Go primary → **OPEN**.
5. `docs/product/FREE_MODEL_FALLBACK_GUIDE.md` still lists dead models as current pins → **OPEN**.
6. `docs/project-memory/CURRENT_STATE.md` still lists the pre-Go models/roles → **OPEN**.
7. No doc previously described the advisor role or any oversight for it → **FIXED** by ADVISOR_MANDATE + AGENTS.md.

Budget: dev-time doc work + free/Go-model headless jobs only; no new paid spend.

Links: `docs/warroom/ADVISOR_MANDATE.md`, `docs/warroom/ADVISOR_LOG.md`, `.opencode/agents/advisor.md`,
`docs/product/MODEL_ROSTER.md`, `docs/warroom/decision-log.md`

### T-041 — Advisor cannot reach the Project Lead: repair the agent-mode mismatch

Status: IN_PROGRESS — Owner approved 2026-09-26; file change done + reviewed; open pending a live test (findings F1/F2)
Owner: Project Lead (diagnose/plan/verify) — Owner instruction 2026-09-26 in chat ("ที่ปรึกษา คุยกับ pl ไม่ได้ แก้ไขให้หน่อย")
Role: Project Lead (diagnose, plan, verify) + builder (one-line agent-config edit) + reviewer on a **different model**
Risk: L1–L2 — dev tooling only (`.opencode/agents/project-lead.md`). No runtime, production, customer or data impact.

Goal: the `advisor` can actually hand a work order to the `project-lead` and read the result, so the chain
`Owner → advisor → PL → specialist` works in practice instead of existing only on paper.

**Root cause (VERIFIED — repo config + opencode agent docs)**
- `.opencode/agents/advisor.md` and `.opencode/agents/project-lead.md` are both `mode: primary`.
- opencode's Task tool invokes **subagents only** (`mode: subagent`); primary→primary is not a channel.
- So `permission: task: allow` on the advisor buys nothing toward the PL — the PL never appears in the Task
  tool's list. Confirmed live in-session: the PL's own Task tool lists exactly the 7 `mode: subagent` agents
  (assistant, builder, model-recruiter, ops, researcher, reviewer, security) and **not** project-lead/advisor.
- Consequence: `ADVISOR_MANDATE.md` §2 ("may command any dev agent (`task` allowed), including PL") is
  currently **unachievable**. The mandate is real; the mechanism was never wired.

**Fix — smallest correct change**
- `.opencode/agents/project-lead.md`: `mode: primary` → `mode: all`. Per opencode docs `all` means the agent
  works as a primary you can Tab into **and** as a subagent the advisor can Task; `all` is also opencode's
  default mode, so risk is low. Blast radius is already contained: every other subagent carries `task: deny`,
  so only the advisor (and the PL itself) would be able to call the PL.

Done when:
- [x] `mode: all` set on `.opencode/agents/project-lead.md` (builder; one line) → `git diff` = one-line pair, PL-verified
- [x] a reviewer on a different model confirms the edit and that no other agent file changed → `opencode-go/space-bunny-free`: ACCEPT-WITH-FINDINGS
- [x] **F2: `subagent_depth: 2` added to `opencode.json`** (Owner approved 2026-09-26) → one-line diff; `node` parse prints `2 project-lead 9`; PL-verified
- [ ] Owner restarts opencode; live test: the advisor's Task tool now offers `project-lead` **and startup does not fall back to `build`** (F1)
- [ ] live round-trip: advisor issues one real work order → PL receives it → the result returns to the advisor
- [ ] PL-as-subagent retains its own permissions (can write dev-process docs) and can still delegate to specialists
- [ ] `ADVISOR_MANDATE.md` §2 re-checked against reality — touch it only if the live test disagrees

Evidence to capture: the agent-file diff · the reviewer's verdict · the live test result.

Team (pins already live-verified under T-035; no fresh HR probe proposed for a one-line change):
builder `opencode-go/glm-5.3-flash` (paid — this is why Owner approval is required) · reviewer `opencode-go/space-bunny-free` (model ≠ author's).

Workaround until the fix lands (needs no config change): the Owner relays — the advisor writes the work order
and the Owner pastes it into the PL chat, or Tabs to the PL agent.

Budget: one small builder call + one review call (both on OpenCode Go) — trivial.
Links: `.opencode/agents/project-lead.md`, `.opencode/agents/advisor.md`, `docs/warroom/ADVISOR_MANDATE.md` §2, `docs/product/MODEL_ROSTER.md`

INTAKE T-041 — 2026-09-26 (Project Lead) — **ACCEPT** (Owner approved in chat 2026-09-26).
Scope: one line in `.opencode/agents/project-lead.md` + a reviewer on a different model + a live test. Nothing else.
Plan: builder edits → reviewer checks → Owner restarts opencode → live round-trip advisor → PL. Builder is paid (Go); Owner approved.
Risk: dev tooling only. The one thing to watch is `default_agent` (finding F1 below).

BUILDER DELIVERY — T-041 — `opencode-go/glm-5.3-flash` — 2026-09-26
Changed: `.opencode/agents/project-lead.md` line 3, `mode: primary` → `mode: all`. One line, nothing else touched; no commit, no push.
Evidence: `git diff .opencode/agents/project-lead.md` = a single `-mode: primary` / `+mode: all` pair.
PL VERIFIED independently: the diff is exactly one line, and `git status --short` lists only that file plus this card.
Not done by the builder (outside the scope lock): live test, review, round-trip.

REVIEWER — T-041 — `opencode-go/space-bunny-free` (model ≠ author's `opencode-go/glm-5.3-flash`) — 2026-09-26
VERDICT: **ACCEPT-WITH-FINDINGS.** Checks 1–3 VERIFIED: the edit is correct and minimal, the rest of the
frontmatter is intact, and after the change **only `advisor`** can invoke `project-lead` (every other agent
carries `task: deny`). `ADVISOR_MANDATE.md` §2 becomes achievable in principle; no permission leak via this path.

Findings — **both CONFIRMED by the PL against the official opencode docs** (`opencode.ai/docs/config/`):
- **F1 — `default_agent` with `mode: all` (should-fix; a blocker if it bites).** `opencode.json` sets
  `default_agent: "project-lead"`. Docs: the default agent "must be a primary agent (not a subagent)" and
  otherwise opencode "will fall back to `build` with a warning". Whether `mode: all` passes that check is
  **UNKNOWN** — only a restart can prove it. If it falls back, the Owner silently gets `build` (full edit +
  bash), which is **less safe**. Test item: on restart the agent must still be `project-lead`, no fallback warning.
- **F2 — `subagent_depth` default is 1 (blocker for the chain).** Docs: default `1` "allows primary agents to
  launch subagents but prevents those subagents from launching additional subagents"; `2` allows one more level.
  So with only the `mode: all` change, advisor → PL works, but **PL-as-subagent cannot launch builder/reviewer** —
  the chain still breaks at the second hop, which is precisely what the mandate requires.
  **Proposed second change (awaiting Owner approval):** add `"subagent_depth": 2` to `opencode.json`.
  Blast radius stays small: every specialist carries `task: deny`, so only advisor and PL can nest at all.
- Minor: `project-lead` now appears in every session's `@` menu, and it can invoke itself. No evidence either causes harm.

F2 CHANGE — T-041 — builder `opencode-go/glm-5.3-flash` + reviewer `opencode-go/space-bunny-free` — 2026-09-26
Changed: `opencode.json` gains ONE top-level line, `"subagent_depth": 2,` (right after `default_agent`). Nothing else.
Evidence: `git diff opencode.json` = `@@ -3,6 +3,7 @@` with a single added line; `node -e "JSON.parse(...)"` prints
`2 project-lead 9`; `git status --short` = only `opencode.json` + `.opencode/agents/project-lead.md` + `TASKS.md`. PL verified independently.
Reviewer verdict: **ACCEPT-WITH-FINDINGS**, 6/6 checks PASS — key name, top-level placement and the value `2` all match the
official docs; the JSON is valid; and the blast radius stays limited to `advisor` + `project-lead` (every other agent carries `task: deny`).
Reviewer minors (deferred, not fixes for this card): `subagent_depth` is global, so if F1 ever falls back to `build`, `build` would
also nest two deep · the PL can self-invoke with no guard yet · F1 still cannot be proven without a real restart.

Card state: **both file changes are DONE and independently reviewed.** The card stays **open** until the Owner restarts and the
live test passes: (1) the startup agent is still `project-lead` — no silent fallback to `build` (F1); (2) the advisor's Task tool
lists `project-lead`; (3) a real work order round-trips advisor → PL → builder.

### T-042 — Project Lead model: switch to `openrouter/deepseek/deepseek-v4.1-flash` (Owner order)

Status: IN_PROGRESS — Owner order 2026-09-26 executed; runtime files changed + reviewed on a different model; docs mirrored; open only pending the Owner's restart check
INTAKE — T-042 — builder `opencode-go/glm-5.3-flash` — 2026-09-26
Understanding: แก้ PL pin 3 จุดตาม scope lock (frontmatter line 4, body line 52, `opencode.json` agent.project-lead.model) ให้เป็น `openrouter/deepseek/deepseek-v4.1-flash` โดยไม่แตะ global fallback / advisor / docs
Done when: diff โชว์ 3 สิ่งพอดี · บรรทัดไทย line 51-56 ครบ · JSON valid parse = `openrouter/deepseek/deepseek-v4.1-flash | opencode-go/mimo-v2.6-pro | 9` · git status = 3 ไฟล์เดิม
Needs: ไฟล์ 2 ไฟล์ + bash (ไม่มี network) — มีครบ
Missing: แค่ reviewer ต่างโมเดล + restart test ของ Owner (อยู่นอกบทบาทผม)
Plan: edit 3 จุด → re-read ยืนยันบรรทัดไทย → run 4 verification commands → DELIVERY
Risks: mangled Thai ระหว่าง encode; diff จะโชว์ T-041 ค้างอยู่ด้วย (baseline ยืนยันแล้ว)
Decision: ACCEPT

DELIVERY — T-042 — builder `opencode-go/glm-5.3-flash` — 2026-09-26
Status claimed: DONE (builder-only runtime edits; card stays open for reviewer + Owner restart test)
Done-when check:
- [x] 2 runtime files carry the new slug + opencode.json parses → `node` prints `openrouter/deepseek/deepseek-v4.1-flash | opencode-go/mimo-v2.6-pro | 9` (global fallback เดิม ✓, 9 keys ✓)
- [ ] reviewer ต่างโมเดลยืนยัน diff scope — อยู่นอกบทบาท builder ยังไม่ทำ
- [ ] docs mirror — อยู่นอก scope lock ของงานนี้ (Owner สั่ง 3 edits/2 files เท่านั้น)
- [ ] Owner restart check — ยังไม่ทำ รอ Owner
Evidence: `git diff` โชว์เฉพาะ model: line, body line 52, JSON value (ส่วน mode:all + subagent_depth เป็น T-041 ค้างจากก่อน) · re-read lines 1-6 และ line 51-56 ไทยครบถ้วน · `git status --short` = 3 ไฟล์เดิม
Changed: `.opencode/agents/project-lead.md` (line 4 + line 52), `opencode.json` (agent.project-lead.model เท่านั้น), TASKS.md (การ์ดนี้เท่านั้น) — ไม่ commit ไม่ push ตาม scope lock
Problems: ไม่มี
Confidence: high — คำสั่ง verify ทั้ง 4 ผ่านจริง
Next: reviewer ต่างโมเดลตรวจ diff scope แล้ว Owner restart ทดสอบว่า PL session เริ่มที่ deepseek-v4.1-flash

REVIEWER — T-042 — `opencode-go/space-bunny-free` (model ≠ author's `opencode-go/glm-5.3-flash`) — 2026-09-26
VERDICT: **ACCEPT-WITH-FINDINGS**, no blockers. Verified: frontmatter carries the new slug with `mode: all` intact; the Thai body
line survived un-mangled; `opencode.json` line 3 (global `model` fallback) and `small_model` are untouched; the JSON parses (9 keys,
`subagent_depth: 2` and `default_agent` intact); `git status --short` limited to the expected three files. The slug was checked
against the **live OpenRouter catalogue** — `deepseek/deepseek-v4.1-flash` exists (1,048,576 ctx, tools + tool_choice, $0.30/$1.20,
cache-read $0.006). Roster rules pass: Primary (OpenRouter) vs Backup (OpenCode Go) = different providers; no anti-redundancy
violation (reviewer/security still differ from both builder models); the "auditor ≠ advisor" rule is unaffected because the
advisor's pin was not touched.
Findings: (should-fix) the doc mirror was still pending at review time — done by the PL in this same card; (should-fix, money)
**there is no provider fallback in `opencode.json`**, so if the OpenRouter credit empties the PL stops until the pin is changed
(remaining ≈ $4.41–4.44); (minor) `MODEL_POLICY.md` marks this model's retention `0 days*` with no explanation of the asterisk →
treat 0-day retention as **unverified** for this model; (minor) the card status lagged its own records.
UNKNOWN (cannot be proven from the repo): whether the restart actually lands the PL session on the new model.

Owner order (verbatim): "เปลี่ยน pl จาก mimo-v2.6-pro เป็น deepseek-v4.1" → then, after being shown the Go blocker, "ให้ไปใช้ที่ OpenRouter".
Owner: Project Lead (docs) + builder (runtime files) + reviewer on a **different model**
Risk: L1–L2 — dev tooling: `.opencode/agents/project-lead.md` + `opencode.json` (both runtime files), plus doc mirroring.
No runtime/production/customer/data impact.

Goal: the Project Lead position runs on `openrouter/deepseek/deepseek-v4.1-flash` — the model the Owner is already
using in his live PL session — with a correct, non-duplicate Backup.

Owner order (verbatim): "เปลี่ยน pl จาก mimo-v2.6-pro เป็น deepseek-v4.1" → then, after being shown the Go blocker,
"ให้ไปใช้ที่ OpenRouter".
Why OpenRouter (recorded): the Go variant `opencode-go/deepseek-v4.1-flash` is probed **blocked** (HTTP 400 "requires
Global regions", T-035/T-037) — it needs the workspace Privacy setting changed to Global regions first. The Owner chose
OpenRouter now; moving to Go later is a one-line change. Neither model arm of the project's policy is violated: OpenRouter
is the sanctioned Backup provider, and the roster already listed this exact slug as the PL's Backup.

Changes:
1. `.opencode/agents/project-lead.md` line 4 — `model:` → `openrouter/deepseek/deepseek-v4.1-flash`
2. `.opencode/agents/project-lead.md` (body, ~line 52) — update the PL pin text so the prompt does not contradict the frontmatter
3. `opencode.json` — `agent.project-lead.model` → the same slug (it currently duplicates the agent file)
4. Docs (PL writes these directly): `docs/product/MODEL_ROSTER.md` row 1 — Primary/Backup **swapped**, reasoning updated;
   `docs/project-memory/CURRENT_STATE.md` pin table; `docs/project-memory/SESSION_HANDOFF.md` current-pin lines.
   New Backup = `opencode-go/mimo-v2.6-pro` → different provider from the new Primary ✓ (anti-regression rule holds).
5. Deliberately NOT touched: the global `opencode.json` `"model"` fallback, the advisor's pin (`opencode-go/mimo-v2.6-pro`,
   unchanged — so the "auditor model ≠ the advisor's model" rule is unaffected), and every historical record
   (`decision-log.md`, `ADVISOR_LOG.md`, `DEV_ERROR_LOG.md`, TASKS.md history) — history is never rewritten.

Done when:
- [x] both runtime files carry the new slug, and `opencode.json` still parses as valid JSON → `node` prints `openrouter/deepseek/deepseek-v4.1-flash | opencode-go/mimo-v2.6-pro | 9`
- [x] reviewer on a different model confirms the diff is exactly scoped and the JSON is valid → `opencode-go/space-bunny-free`: ACCEPT-WITH-FINDINGS, no blockers; slug confirmed in the live OpenRouter catalogue
- [x] docs mirror the change; no historical entry rewritten; PL Backup differs from PL Primary → `MODEL_ROSTER.md` row 1 (swapped), `CURRENT_STATE.md`, `SESSION_HANDOFF.md`, new `decision-log.md` entry
- [ ] Owner restarts and confirms the PL session starts on `deepseek-v4.1-flash`; if it does not, report and revert
- [ ] carry the money finding: **no provider fallback exists** — if the OpenRouter credit empties the PL stops (≈ $4.44 left) → decide with the Owner whether to add one

Evidence to capture: the two diffs · the `node` JSON parse output · the reviewer verdict · the Owner's restart check.
Budget: one small builder call + one review call (both on OpenCode Go) — trivial.
Links: `.opencode/agents/project-lead.md`, `opencode.json`, `docs/product/MODEL_ROSTER.md`, card T-041
**Sequencing note:** T-041 and T-042 both touch `.opencode/agents/project-lead.md` → they are run **sequentially, never concurrently**.

### T-048 — Read-only inventory of all pending work (Owner-facing; nothing started)

Status: IN_PROGRESS — Owner-approved 2026-09-26 ("อนุมัติ").
Owner: Project Lead — 2026-09-26 (Owner intent: "ไปคุยกับ pl สิ รายละเอียดงานทั้งหมดที่รอทำอยู่มีอะไรบ้างเอามาดูแล้วพี่จะสั่งงาน")
Role: Project Lead (compile + verify) + reviewer `opencode-go/space-bunny-free` (different model)
Risk: L1 — read-only documentation; no code/runtime/production/database/credential change, no spend, no execution of any listed item.
Goal: one plain-Thai inventory of every pending item, separating the customer-product launch path from internal tooling/governance, each with goal / status / blocker / dependency / source.
Done when:
- [x] the inventory card exists; the receiver's advisor instruction record is appended to `ADVISOR_LOG.md`
- [x] every remaining open card is covered, plus documented customer-launch prerequisites without cards
- [x] customer-product launch separated from internal tooling; the War Room classified as internal
- [x] statuses from current evidence only; RUNNING claimed only with live process evidence; no percentages
- [x] reviewer `opencode-go/space-bunny-free` verifies coverage + status accuracy → **ACCEPT-WITH-FINDINGS** (A coverage PASS · B status PASS-with-findings · C nothing-started PASS)
Budget: read-only; free model only — no paid spend.
Links: `TASKS.md`, `docs/warroom/STARTUP_PLAYBOOK.md`, `docs/warroom/ADVISOR_LOG.md`

INTAKE T-048 — 2026-09-26 (Project Lead) — ACCEPT (Owner approved). Read-only inventory; creates only this card plus the ADVISOR_LOG record; starts no listed work.

**INVENTORY (Owner-facing; no task IDs; compiled 2026-09-26 from current repo evidence; statuses: READY / IN_PROGRESS / BLOCKED / NEEDS_OWNER_DECISION / CODE-COMPLETE-NOT-DEPLOYED. No item is RUNNING — no live-process evidence exists for any of them.)**

*A. Customer-product launch path (`docs/warroom/STARTUP_PLAYBOOK.md` Steps 0–3)* — **no cards exist for any of these**; the whole customer-facing path is uncarded.

- Market-test foundation (self-hosted n8n + PostgreSQL, HTTPS, daily backups; owner alert channel). Status: **UNKNOWN/partly done** — the hosting card is recorded CLOSED and the lite-schema and tools cards are DONE, but the playbook's Step 0 checklist still shows self-hosted n8n+PostgreSQL and the owner alert channel unchecked, and no current card tracks them. Blocker/Owner decision: confirm what actually exists before building on it. Source: playbook Step 0; `docs/archive/TASKS_PARKED.md`.
- One bot end to end on LINE (LINE channel, bot core, memory, handoff-to-owner, outage fallback, web-fetch, file-reader, onboarding, auditor test). Status: not started; no card. Blocker: the foundation above. Source: playbook Step 1.
- Tenant #1 live and watched (onboard with the Owner, measure real cost per reply, confirm quota, daily monitoring read). Status: not started; no card. Blocker: the LINE bot. Source: playbook Step 2.
- Tenants #2–10 + storefront + web-chat channel + a second bot type + summary/retention jobs + weekly review. Status: not started; no card. Blocker: tenant #1. Source: playbook Step 3.
- Pre-runtime hardening before real customers (data / isolation): the real-tenant RLS residual (superuser / `SECURITY DEFINER`), Supabase backup-and-restore, and the still-unverified retention behaviour of the PL model provider. Status: recorded as residuals; no card. Blocker: needed at the dev→runtime switch. Source: card residuals; `docs/data/LITE_SCHEMA_V1.md`; `docs/product/MODEL_POLICY.md`.
- Customer PDPA / onboarding gates — **no card; required before onboarding real customers.** Status: documented requirements, nothing built or confirmed; completion **UNKNOWN**. (a) an end-customer consent/privacy notice shown automatically on the first message; (b) a tenant agreement stating plainly that the tenant is the data controller and Nippan is the processor, reviewed by a lawyer; (c) an actionable end-customer data-deletion path against the tenant-scoped tables; (d) the exact retention period confirmed with a legal/PDPA advisor before launch (the doc gives only a default, not a confirmed figure). Source: `docs/security/PDPA_COMPLIANCE.md` Layers 1–2; `docs/product/ONBOARDING_FLOW.md`; `docs/product/BUSINESS_OPERATIONS.md` §3.
- Pricing / operational launch decisions — **no card; needed for real onboarding.** Status: documented as decisions to confirm, completion **UNKNOWN**. (a) the starting reply quota (600/month) is explicitly a starting value to confirm/adjust after the first real tenants; (b) onboarding must tell the owner plainly that chat replies are unlimited and reminders are capped (200/month per bot); (c) the manual payment / cancellation process (bank transfer / PromptPay, cancel anytime, 7-day refund, 30-day data retention, a bot paused not deleted 7 days late); (d) re-check LINE's current terms before launch; (e) a lawyer reviews the tenant-agreement wording. Source: `docs/product/PRICING_V1.md`; `docs/product/BUSINESS_OPERATIONS.md` §2/§3/§4/§5; `STARTUP_PLAYBOOK.md` Step 2.

*B. Internal tooling / governance (all eight remaining open cards are here; the War Room is internal dev-time tooling, not a customer-launch prerequisite)*

- Git work channel (issues → branches → draft PRs → CI → review → merge). Status: **READY**, blocked on Owner decisions. What: dispatch work to the external assistant without a chat relay. Blocker/Owner decision: whether to protect the working branch, four external-side settings, and the two pilots. Source: board card.
- War Room — manage a meeting's agenda from the room page. Status: **CODE-COMPLETE-NOT-DEPLOYED**; acceptance/trial pending. What: create/edit/close agenda items in-room, owner-only and fail-closed. Blocker: a deploy decision and the acceptance run; one rate-limit hardening waits for verification. Source: board card; `services/core/app/war_room/`.
- War Room — used as the team's real meeting room. Status: **pilot already run**; remaining Owner decisions. What: plan/assign/report/debate with durable artifacts. Blocker/Owner decision: a fresh room per meeting, and who joins / who pays. Source: board card; `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md`.
- War Room internal residuals (**internal tooling — NOT a customer-launch gate**): an agenda-write rate limit (the card notes it as required before production), the `updated_at` refresh note, and the “durable record” architecture option. Status: recorded as residuals on the War Room cards; no standalone card. Source: War Room card residuals; `services/core/app/war_room/`.
- Dev-team re-staffing on OpenCode Go. Status: **IN_PROGRESS**; roster/config mapping is in the tree but the card's remaining steps are not shown complete. Blocker: the outstanding recruiting/decision items and per-role end-to-end evidence. Source: board card; `docs/product/MODEL_ROSTER.md`.
- Advisor mandate + rule repair. Status: **IN_PROGRESS**. Confirmed remaining item: the card's own close-out box (`CURRENT_STATE.md` refresh + board housekeeping). The card's conflict-scan also lists three stale-rule findings (#3–#5: project-lead prompt naming the advisor/Go provider, the working guide's free-only wording, and the fallback guide's dead-model list). **UNKNOWN which side is authoritative:** the card text says those are OPEN, but a reviewer re-check says the prompt and working guide already reflect the new team/provider and the fallback guide marks its dead-model list as historical — two review runs disagreed, so confirm with a one-line check before closing. Source: board card; `project-lead.md`, `DEV_WORKING_GUIDE.md`, `FREE_MODEL_FALLBACK_GUIDE.md`.
- Advisor→Project-Lead channel. Status: changes done and reviewed; **live test pending**. Blocker/Owner decision: restart opencode, then one real round-trip. Source: board card.
- Project-Lead model switch. Status: changes done and reviewed; **restart check pending**. Blocker/Owner decision: restart to confirm; and a money decision — no provider fallback exists, so if the OpenRouter credit empties the PL stops. Source: board card; `docs/product/MODEL_ROSTER.md`.
- Free writer for the PL's config edits. Status: implemented and reviewed; **close-out boxes not ticked**. What: the PL never writes runtime files itself and never needs a paid builder for a config edit. Blocker: none technical. Source: board card; `.opencode/agents/assistant.md`.

*Owner actions / decisions with no card:* (a) set the workspace Privacy to "Global regions" if DeepSeek models are to run on OpenCode Go; (b) the OpenRouter credit level / whether to add a provider fallback; (c) the one large audit at project close (before real use) — planned, not started.

**Internal coverage map (for the reviewer only — not for the Owner-facing report):** Git channel → T-032 · War Room room-in-use → T-033 · War Room create/agenda → T-034b · Go re-staffing → T-035 · advisor mandate → T-038 · advisor→PL → T-041 · PL model → T-042 · free writer → T-044. Board: **8 pre-existing open cards** (9 including this card T-048), cap 10 (card T-044 sits under the REVIEW heading but its status is IN_PROGRESS).

**Known board drift (recorded, not hidden):** the headers of the archived cards were stale (T-034a/T-039/T-043 showed READY/IN_PROGRESS though their done-when and evidence were complete), and two remaining cards have stale headers — T-034b still says "BLOCKED behind T-034a" although T-034a is now archived DONE, and T-033 still says "READY for INTAKE" although its pilot result is recorded. The evidence confirming the archived cards is in the working tree (not yet committed), so their DONE state is verified from the files, not from git history.

REVIEW — T-048 — `opencode-go/space-bunny-free` (different model from the author) — 2026-09-26 — **ACCEPT-WITH-FINDINGS** (2 runs)
- Run 1 — `runs/2026-09-26T14-58-09Z-t048-inventory-review`: A coverage PASS · B status PASS-with-findings · C nothing-started PASS.
- Run 2 after the revision — `runs/2026-09-26T15-04-25Z-t048-inventory-rereview`: A coverage PASS (8 open cards + playbook Steps 0–3 + the newly added PDPA/onboarding and pricing/ops gates verified against source) · B status PASS-with-findings · C nothing-started PASS.
- Findings actioned on this card: (a) the omitted uncarded customer PDPA/onboarding gates were added; (b) the omitted uncarded pricing/operational decisions were added; (c) the War Room residuals were separated out of customer pre-runtime hardening into internal War Room residuals; (d) the advisor-mandate item was corrected — run 1 claimed the rule conflicts were open, run 2 showed the files already name the advisor/Go provider, so the card now records the conflict as **UNKNOWN** with both sides; (e) the LINE-terms citation corrected to `BUSINESS_OPERATIONS.md` §4.
- Left as-is by design: the internal coverage map contains task IDs but is explicitly marked reviewer-only and is kept out of the Owner-facing report.
- Reviewer could not verify: that no process is actually running (only files/git were inspected); whether the uncommitted working-tree evidence will survive (nothing is committed); and whether the War Room slice-3 acceptance trial started by a concurrent session is finished (the inventory shows it as not deployed).

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

## REVIEW

(none)

### T-044 — A FREE writer that performs the file writes the Project Lead is no longer allowed to do

Status: IN_PROGRESS — **Owner decision 2026-09-26: Option B** ("assistant ใช่ เรามีอยู่แล้ว ใช้ตัวนี้เป็นคนเขียน") — use the existing free `assistant` as the PL's writer; no new role, no new model, no paid spend
Owner: Project Lead (plan/record) + `model-recruiter` (verify the free model) + the writer + a reviewer on a different model
Risk: L2 — the writer holds edit rights on `.opencode/**` and `opencode.json` (runtime/config).
Mitigations: `task: deny` (it cannot command anyone), the PL writes the exact order, a reviewer on a different model checks every
diff, and those files carry only `{env:...}` references — never secret values.

**Why this card exists (the Owner's order, in his words):** the T-043 lock means the Project Lead can no longer write
`.opencode/**` or `opencode.json` itself, and cannot delete files with PowerShell. So a **free** agent must exist whose whole job
is to perform those writes exactly as the PL instructs.

Goal: the PL keeps a free "hands" agent it can order, so no config change ever forces a paid builder call, and the PL still never
writes runtime files itself.

Proposed plan (two options — the Owner picks):
1. **A — new dedicated free writer (`scribe`)** *(recommended)*: a new agent file with a free model, `mode: subagent`, `edit: allow`,
   `task: deny`. Duty: "execute the exact file edit the Project Lead orders — no improvising, no widening the scope, no commit, no
   push". Keeps duties clean (the `assistant` stays a drafting/summarising helper).
2. **B — reuse the existing `assistant`** (free `opencode/nemotron-3-ultra-free`, already `mode: subagent`, `task: deny`, edit
   allowed by the global map): zero new files, zero new hire — only its description and prompt are extended to name the duty.

Steps either way: `model-recruiter` verifies the free model is **live** (free Zen models have died before: `big-pickle`,
`ling-3.0-flash-fin-free`, `mimo-v2.6-flash-free`) and names the best live free substitute if it is dead → Owner approves the pick →
the writer implements its own agent file (it has edit rights, which also proves the pattern) → a reviewer on a different model
checks the file and the permissions → one live round-trip: PL orders a real config edit, the writer performs it, the reviewer checks it.

Constraints:
- **No secrets to a free model.** Free Zen may log or train. `.opencode/**` and `opencode.json` contain `{env:...}` references only,
  so they are safe to share — but the writer must never be handed the `.env` or any credential.
- The writer has **no decision power**: it writes what it is told and nothing more. Detection stays in place (reviewer + scorecard).
- **The chicken-and-egg is real:** the PL cannot create this agent file, so the first implementation of T-044 must itself be performed
  by an existing writer (the free `assistant`, which already has edit rights, or the paid `builder`).

Done when:
- [ ] `model-recruiter` reports the free model's live availability + price ($0) and the substitute if dead
- [ ] the writer's agent definition names the duty and keeps `task: deny`
- [ ] reviewer on a different model verifies the file and the permission block
- [ ] live round-trip proven: the PL orders one real config edit → the writer performs it → the reviewer checks the diff

Evidence to capture: the agent-file diff · the HR availability report · the reviewer verdict · the round-trip diff.
Budget: HR runs on Go (flat monthly) + free models only — **no new paid spend**.
Links: `.opencode/agents/assistant.md`, `.opencode/agents/worker.md` (`edit: allow`, `task: deny`, headless), `docs/product/FREE_MODEL_FALLBACK_GUIDE.md` (historical reference), card T-043

## DONE

(completed cards moved to docs/archive/TASKS_DONE_ARCHIVE.md — T-RLS-01 added 2026-09-25)

- **T-030 — DONE 2026-09-26 (Owner approved).** n8n → Supabase as `nippan_n8n`: connection proven, RLS read isolation proven
  (tenant A = 1 / tenant B = 0), write isolation proven (cross-tenant INSERT rejected, RLS WITH CHECK 42501), positive control for
  tenant B, tables left empty (rollback). Workflows `CVhNSU5pjpGgzquB` + `eohtRWY8YEvEuS7n` in folder `Nippan Phase A`.
  Evidence + the exact SQL: `docs/n8n/T-030-execution-evidence.md`. Reviewer `opencode/space-bunny-free` (different model) pass 2.
  Owner scope condition (2026-09-26): n8n write/read is allowed **only inside the `Nippan Phase A` folder**. Carried residual:
  the credential still has `Ignore SSL Issues`; the card has never been run published/production.
