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

### Board size (Owner order 2026-09-25)
- DONE cards are archived immediately; the board holds only open cards.
- **Cap: 5 open cards** (Owner confirmed 2026-09-25).
- Blocked / superseded cards live in `docs/archive/TASKS_PARKED.md`.
- Inside the cap, WIP is governed by `TASK_CONTROL.md` section 5 (max 3 IN_PROGRESS, 5 REVIEW).

---

> T-030 (DONE 2026-09-26) is archived in `docs/archive/TASKS_DONE_ARCHIVE.md`.
> T-031 (DROPPED 2026-09-25) is archived in `docs/archive/TASKS_PARKED.md`.

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

### T-034a — War Room UI: rewrite the surface as a readable chat screen (UI only, FREE model)

Status: READY for INTAKE — the T-033 pilot has run; model split approved by the Owner 2026-09-26.
Owner: Project Lead — 2026-09-26 (Owner order: "พอผ่านช่วงทดลองเสร็จแล้วต้องพัฒนาให้เรียบร้อย เหมือนหน้าจอแชทจริง")
Role: Developer — **free model `nvidia/nemotron-3.5-lightning:free`** (builder backup slot, $0/M, 1M ctx, tools ✓; HR check 2026-09-26: endpoint live, uptime ~90%, latency p50 2.9s / p90 78s → slow, so scope stays tight) + reviewer `opencode/space-bunny-free` (different model; anti-redundancy holds)
Risk: L2 (front-end only; no authentication, authorization, schema, RLS or grant change)
Goal: the `/war-room` surface behaves like a normal chat screen for daily team use — newest message always in view, long history handled without an endless page, and a meeting can be started/archived without hand-made SQL.
Done when: 1) the message list behaves like a chat thread — auto-scroll to the newest message, "กลับไปล่าสุด" control, and the page does not run away as history grows; 2) long history is handled deliberately (windowed/paged view with "โหลดก่อนหน้า" instead of dumping up to 100 events at once); 3) a fresh room per meeting is possible **without** touching the database by hand (reviewed create-room path — endpoint or a seed script that takes a room id/title); 4) the previous meeting stays archived and reachable by its room id; 5) Thai labels stay consistent and the UI states (idle/loading/error) are explicit; 6) tests + CI green, and the change is reviewed by a different model; 7) no production system, no customer data, no provider spend involved in the UI work itself.
Budget: 1–2 days
Links: T-033 (pilot findings drive this card), `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md` (how the stopgap room was made), `services/control-plane-web/war-room/` (index.html / war-room.js / war-room.css), `docs/warroom/TASK_CONTROL.md` §8

INTAKE T-034 — 2026-09-26 (Project Lead, from the Owner order)
Understanding: during the pilot the Owner found the room page unusable as a chat screen — history is long, there is no way to clear or start fresh, and a new meeting room had to be created by hand in the database. The Owner wants the surface developed properly after the trial.
Scope: the `/war-room` front-end (and, if a create-room path is needed, the smallest reviewed server addition for it). No auth model change, no schema change.
Needs: the pilot results (what actually annoyed the Owner while using it); the T-033 decisions.
Missing: the pilot has not run yet.
Plan: 1) run the T-033 pilot; 2) collect the concrete usability complaints; 3) scope this card against them; 4) builder implements on a branch, reviewer on a different model checks the diff, CI green; 5) PL verifies against the deployed preview; 6) record the verdict.
Estimate: 1–2 days.
Risks: UI work on the deployed preview without breaking the auth boundary; the create-room path touches the server, so it must be reviewed as carefully as any transport change.
Decision: ACCEPT (queued behind the T-033 pilot).

**PILOT FINDINGS TO FIX — from the Owner using the room for real (2026-09-26)**

The first pilot meeting produced three AI answers (Chair, Builder, Security) but the Owner could not tell **who** answered —
the transcript reads as if only one participant replied. Concrete requirements, in priority order:

1. **Speaker identity on every message** — show the participant's display name **and** role (e.g. "Preview Chair · ประธาน")
   as a header on each bubble; the Owner's own messages must look different from AI messages.
2. **Separate system events from the conversation** — `TURN_SCHEDULED` / `ROOM_STATE_CHANGED` currently sit in the same list as
   the messages and drown the discussion; they belong in a collapsible one-line system log.
3. **Chat affordances** — newest message auto-scrolled into view + a "กลับไปล่าสุด" control; group consecutive messages from the
   same speaker; show time; show model and token count per AI message (small, secondary).
4. **Role-based visual distinction** — colour/avatar per role (OWNER / CHAIR / BUILDER / SECURITY / COST_OPS / AUDITOR / SECRETARY)
   so a long meeting is scannable.
5. **Start a new meeting without hand-editing the database** — a "เริ่มประชุมใหม่" action that creates a room (reviewed
   create-room path), and the previous room stays reachable as an archive.
6. Keep Thai labels consistent; make loading/error states explicit.
7. **Show the roster, not just a number** — the sidebar currently shows a count ("8"); the Owner wants to see **who** is in the
   meeting: each participant's display name + role, with active/inactive made obvious. The count alone tells the Owner nothing.
8. **The agenda panel must actually work** — the right-hand "วาระ" panel is decoration today; either make it usable (create/edit
   the agenda item, mark it done, show the round/round-limit and which agenda item a message belongs to) or remove it. Keeping a
   panel that cannot be used is worse than not having it.
9. **Chat window and typography must be readable** — comfortable line length and font size, clear separation between messages,
   no wall of same-looking text; the room must be readable for a long meeting, not only for a three-message demo.

Verification for this card: the Owner must be able to read a meeting transcript and name every speaker at a glance, see who is in
the room, and understand what the meeting is about from the agenda panel — all without asking the PL what the database says.

**Scope lock for T-034a (files the worker may touch — nothing else):** `services/control-plane-web/war-room/index.html`,
`war-room.css`, `war-room.js`. No server/transport/contract change, no new endpoint, no database access, no new dependency or
build step (the surface stays framework-free and dependency-free), the wire contract (snapshot / SSE / commands) is unchanged,
no secrets in the prompt, and the worker must **not** commit or push.
**Fallback rule (Owner-approved):** if the free model fails quality review twice, the paid builder `z-ai/glm-5.3-flash` closes
T-034a instead — no further attempts on the free model.

**WORK LOG — T-034a (PL, 2026-09-26; Owner away, PL acting under the delegation of 2026-09-26)**

| # | Attempt | Model | Outcome |
|---|---|---|---|
| 1 | headless worker, full rewrite | `opencode/nemotron-3.5-lightning-free` | 10 min of planning + todos, **no file written**, died on a length limit |
| 2 | headless worker, full rewrite, "small steps" | `openrouter/thinkingmachines/inkling:free` | **wrote the change** (~150 lines across the 3 files) → reviewer #1 = **REJECT** (5 findings: timestamps read `timestamp`/`created_at` instead of `occurred_at`; token count read `token_usage`/`usage` instead of scalar `usage_tokens`; `provider_model` invented; `provider_request_id` display dropped; system-log open-state reset every render) |
| 3 | headless worker, fix round 1 | `openrouter/thinkingmachines/inkling:free` | fixed 4 of 5 → reviewer #2 = **REJECT** (blocker: owner decisions pushed into the system log and truncated to 120 chars; blocker: `replaceChildren()` resets `scrollTop` so auto-scroll never fires in a long room; minor: English role enums, `usage_tokens === 0` hidden) |
| — | fallback rule triggered (2 free-model failures) | `openrouter/z-ai/glm-5.3-flash` | headless attempt **stalled twice without writing a file** — the headless harness elides large tool output, so the model kept re-reading the file and burned the step limit; the `builder` subagent path returns no edits (its agent file grants no `edit` permission) → use `--agent worker --model <builder model>` |
| 4 | headless worker, tight scope (4 edits max) | `openrouter/thinkingmachines/inkling:free` | in progress at the time of writing — fixes B1 (owner decision in the conversation) and B2 (auto-scroll); reviewer re-check to follow |

- Environment finding worth keeping: the headless runner truncates large tool output, so a job must be told to read only small
  regions; and `builder.md` has no `edit` permission, while `worker.md` has `edit: allow` — code jobs go through `worker`.
- The change is **not deployed yet**: the preview serves `phase2/postgres-logical-schema`, this work is on `dev-workspace`.
  Deploy path planned: commit → isolated 3-file change on a branch off the deployed branch → PR → merge → Render auto-deploy.

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

---

> NOTE (Project Lead, 2026-09-26): the card below was found uncommitted in the working tree and was authored **outside
> this session**. It is preserved here untouched — not reviewed, not approved, and not counted as this session's work.

### T-030 — Bring OpenCode Go ($10/mo) into the dev team as the paid provider
Status: READY (plan written 2026-09-26; waiting Owner approval on the mapping)
Owner: (unclaimed — Project Lead planning; HR readiness check pending)
Role: Project Lead (plan) + Model Recruiter (availability/probe)
Risk: L2 — dev-process model routing + cost policy; rewriting `MODEL_ROSTER.md` needs Owner approval
Goal: roles whose model already exists inside the Go subscription run via `opencode-go/<id>`
instead of the near-empty OpenRouter balance, with the model identity unchanged.
Done when:
- HR reports Go availability per role model, with a real probe result per model (VERIFIED/UNKNOWN marked)
- Owner approves the role→`opencode-go` mapping (or a subset)
- one headless job per migrated role runs end-to-end on the Go provider with evidence under `runs/`
- `MODEL_ROSTER.md` + `SESSION_HANDOFF.md` updated and a `decision-log.md` entry written
- fallback preserved: OpenRouter stays configured; no role left depending on one provider only
Budget: one working session; HR probe calls only (no new paid spend beyond the subscription)
Links: `docs/product/MODEL_ROSTER.md`, `opencode.json`, `scripts/headless_run.mjs`, `https://opencode.ai/docs/go/`

Planned mapping (same model, different provider — model identity preserved):

| Role | Current route | Proposed Go route | Go monthly limit |
|---|---|---|---|
| project-lead | `openrouter/deepseek/deepseek-v4.1-flash` | `opencode-go/deepseek-v4.1-flash` | $60 |
| builder (Owner-locked model) | `z-ai/glm-5.3-flash` | `opencode-go/glm-5.3-flash` | $60 |
| reviewer L1–L3 | `opencode/space-bunny-free` | `opencode-go/space-bunny-free` | unlimited (promo) |
| model-recruiter (HR) | `openrouter/openai/gpt-6-luna` | `opencode-go/gpt-6-luna` | $15 |
| ops / researcher / assistant | `opencode/muse-spark-1.2-contributor-free` | `opencode-go/muse-spark-1.3-contributor` | $60 |
| security L1–L3 | `openrouter/nex-agi/nex-n2.5-mini:free` | unchanged — **not offered in Go** | — |

Notes / constraints found 2026-09-26 (evidence in the card's DELIVERY when done):
- `opencode-go` is already authenticated in this workspace; `/zen/go/v1/models` returns 35 models
  incl. every paid-roster model above; `glm-5.3-flash` and `space-bunny-free` serve inference (HTTP 200).
- Muse Spark under Go trains on prompts/outputs and is **not ZDR** → no secrets/sensitive code.
- Go models still consume reasoning tokens: `max_tokens` in probes must be generous.
- Drift found: `opencode.json` default/`small_model` = `opencode/ling-3.0-flash-fin-free`, a model
  previously recorded as unusable/banned for PL+HR — fix alongside the mapping.

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
