# Dev Error Log — 2026-09-25

## Errors / Unverified recorded by PL (per AI_OPERATING_PROTOCOL)

### Bridge Watcher v1 — PARKED (UNVERIFIED)
- Code written (`watcher.mjs`, `watcher.test.mjs`, `server.mjs`) but never tested; no evidence of `node --check` pass or test run.
- Bridge not restarted; runs old code; `.opencode/bridge/PAUSE` not removed.
- Previous external session (`ses_f27b323c8ffeO8M97njUFANf67`) stale (OAuth discovery failed; session terminated 32600).
- Verdict: NOT DONE. Do not claim DONE. Keep PARKED until Owner approves restart + review.

### T-030 — INTAKE only (no test executed)
- Card written; team proposed (free ops + reviewer) but HR check not completed; Owner has not created n8n Postgres credential.
- Connection to `nippan_n8n` via direct connection UNVERIFIED (password set by Owner, never exposed; credential not created yet).
- Verdict: READY (not DONE). Need Owner action (credential + approval) before proof.

### T-008 / T-009 — audit gate removed
- Per `decision-log.md` 2026-09-25: "Audit gates cancelled outright". No per-milestone audit required now; one large audit at completion.
- Status in archive; not reopened until Owner decides.

### Cost / Credit stop
- OpenRouter credit ≈ $1.76 (2026-09-25). No paid subagent / builder / worker called in this session.
- All proposed work uses free models (`opencode/muse-spark-1.2-contributor-free`, `opencode/space-bunny-free`) per MODEL_ROSTER.

---

## Session 2 — 2026-09-25 (protocol re-entry, read-only)

### INCIDENT — `TASKS.md` board overwritten; four cards lost (UNVERIFIED → repaired)
- `TASKS.md` in the working tree contained ONLY a 9-line "INTAKE T-030" block: the board header, the board-size rules and the cards `T-RLS-01`, `T-BRIDGE-01`, `T-031` were gone.
- Root cause: the file was written with `write` (full replace) instead of `edit`/append, after the previous content had been added but **never committed**. `git show HEAD:TASKS.md` = "(no open cards)" — so the loss is real, not a display artefact. `SESSION_HANDOFF.md` and `decision-log.md` both claim the cards existed → those claims were **stale/over-claimed** at the time they were written.
- Repair (session 2): board restored with header + rules + `T-030` (READY, with PL verify note) + `T-031` (BLOCKED/NEEDS_OWNER_INPUT); `T-RLS-01` archived to `docs/archive/TASKS_DONE_ARCHIVE.md`; `T-BRIDGE-01` archived to `docs/archive/TASKS_PARKED.md`. Reconstructed card text is labelled as reconstructed.
- Lesson: never `write` a shared board file; append/edit it. Commit card writes in the same turn.

### BLOCKED — n8n mutating tools not registered in the running session
- `opencode.json` sets `n8n_create_workflow_from_code`, `n8n_update_workflow`, `n8n_execute_workflow` = `true` (uncommitted working-tree change), but none of the three is exposed as a tool in the current session → the T-030 test workflow cannot be created or run.
- `n8n_create_folder` and all read-only n8n tools ARE exposed, so the MCP server itself is connected; this is a config-reload issue (the running process started before the edit). A new chat is not enough — the app must be restarted.
- Impact: T-030 stays READY/UNVERIFIED. Do not report it as done.

### Corrected stale claims (handoff)
- "Pending: push 2 commits (approved)" → **not** pending: `git log origin/dev-workspace..HEAD` is empty (HEAD = `973bc05`, PR #83 merged). Nothing to push.
- Credit check (session 2, `openrouter_get-credits`): total 40 / used 38.4023 → remaining ≈ **$1.60** (was reported as $1.76 in the previous session). Still effectively no paid work.

### Verified in session 2 (read-only, for the record)
- n8n folder `Nippan Phase A` (`zClFVASPRDPnaeuQ`) exists and is empty (0 workflows).
- n8n credential `6anMUYRLDYPduKY7` ("Postgres account", type `postgres`) exists; secret values not read.
- Live Supabase `xzxwakvsbdzkdybijbzs`: `nippan_n8n` rolcanlogin=true, `nippan_runtime` false; 7 `lite_*` tables `rls=true force=true`.
- `gh pr view 83` = MERGED (2026-09-25T14:06:40Z).
- No paid model and no subagent was called in session 2.

---

## Session 3 — 2026-09-26 (OpenCode Go onboarding; read-only + headless)

### DEFECT — `headless_run.mjs --agent <subagent>` silently falls back to the default agent
- Command: `node scripts/headless_run.mjs --agent model-recruiter --model opencode-go/gpt-6-luna --label go-restaff --prompt ...`
  → run dir `runs/2026-09-26T09-21-40Z-go-restaff` (pid 12928).
- `stderr.log` line 1: `! agent "model-recruiter" is a subagent, not a primary agent. Falling back to default agent`.
- Impact: the job (card T-035) runs as **`project-lead`** — a primary agent that HAS `edit` permission — although the
  worker was scoped as a read-only HR proposal and the prompt explicitly said "do not edit any file". The worker did
  write to `TASKS.md` (it appended its INTAKE under T-035) and used `todowrite`. Model was still `opencode-go/gpt-6-luna`
  as explicitly passed; only the agent identity/permission set was wrong.
- Also observed: the command wrapper reported `Unknown: ChildProcess.kill` while the detached child kept running — the
  run is fine, the wrapper's exit status is misleading. Always verify a queued job with `headless_status.mjs`.
- Not yet fixed: `headless_run.mjs` should reject a non-primary `--agent` (or resolve the subagent's own permission set)
  instead of falling back silently. Fix belongs to a builder card, not to this session.
- Safety rule until fixed: never pass `--agent <subagent>` to a job that must not edit files; the fallback agent grants edit.

### INCIDENT (again) — `TASKS.md` was in a broken 33-line state when this session started
- At session start `TASKS.md` held only the header + board-size rules + "(no open cards)": cards T-032, T-033, T-034,
  T-034a/b and the archived T-030/T-031 pointers were missing from the working tree (same failure mode as session 2).
  A `read` at that moment returned 33 lines / "(no open cards)".
- The PL then appended a new card using **`edit`** (append-style, not `write`). A second session repaired the board
  afterwards and preserved that card with an "authored outside this session" note. Current file = 294 lines and holds
  T-032, T-033, T-034, T-034a, T-035.
- Numbering collision: the new card was written as `T-030`, but T-030 is the archived n8n/RLS card → **renumbered T-035**
  on 2026-09-26. Next free number after that is T-036 (T-034a/b sub-cards exist).
- Lesson repeated: two sessions can be live on this repo at once; always re-read `TASKS.md` before editing, edit (never
  write) the board, and re-check the number you are about to use against `docs/archive/`.

### VERIFIED — OpenCode Go provider is live in this workspace (2026-09-26)
- `auth.json` holds an `opencode-go` entry (`type: api`); `GET https://opencode.ai/zen/go/v1/models` → HTTP 200, 35 ids.
- Chat completions through Go: `glm-5.3-flash` HTTP 200 (1.2s, `served_model` echoed) and `space-bunny-free` HTTP 200
  (1.4s, prompt cache hit 149 tokens). Note: these are reasoning models — with `max_tokens` too small the visible
  `content` came back empty because all 8 tokens were spent on `reasoning_tokens`.
- `openrouter_get-credits` = total 45 / used 43.8119 → **remaining ≈ $1.19**. PL, builder and HR still route through
  OpenRouter → the Go provider is now the cheaper path (card T-035).

### FAILED — first HR job (T-035) produced zero output
- Run `runs/2026-09-26T09-21-40Z-go-restaff`, model `opencode-go/gpt-6-luna`, 37 stdout events, **0 text parts**,
  exit without an answer. Final step: `step_finish reason:"length"` with `reasoning: 4096, output: 0` — the model spent
  its whole reasoning budget on one step and the run ended with nothing usable.
- Consequence: the assistant-session summary for T-035 is still missing; HR has to be re-run. Cost ≈ 120k tokens
  (~$0.006 of Go usage, mostly cached read) — cheap, but a wasted round.
- Second attempt queued as `runs/2026-09-26T09-27-58Z-go-restaff-v2`, agent `worker` (a real primary agent → no
  fallback warning; `stderr.log` empty), model `opencode-go/mimo-v2.6-pro`, brief rewritten to demand a compact
  one-pass answer. Lesson: give a reasoning model a tight output budget and an explicit "do not narrate" instruction.

### FOUND — a second session is writing this repo, and it already drafted the Go policy
- `git diff --stat` at 2026-09-26 showed three modified files with work this session did not author: `TASKS.md`
  (board repaired + cards T-032/T-033/T-034/T-034a restored), `docs/product/MODEL_POLICY.md` (+84 lines) and this log.
- The `MODEL_POLICY.md` addition is titled "OpenCode Go — approved provider (Owner decision 2026-09-26)" and contains
  Artificial Analysis numbers per Go model, a long-conversation cost rule, a privacy/retention table and per-job picks
  (e.g. `mimo-v2.6-pro` for long planning, `kimi-k3` for final code, `deepseek-v4.1-flash` for volume, `grok-4.7` and
  `deepseek-v4-pro` rejected).
- Status: **uncommitted, not reviewed by this session, and not yet a decision**. It was handed to HR as input. The two
  sessions must be reconciled by the Owner (see the report): two Project-Lead chats on one worktree can clobber the
  board — this is the third board incident recorded in this log.

### DEFECT — a long `--prompt` is silently truncated before the worker sees it
- Run `runs/2026-09-26T09-27-58Z-go-restaff-v2` (agent `worker`, model `opencode-go/mimo-v2.6-pro`) came back
  **NEEDS_DECISION**: it said the assignment text "ถูกตัดจบ ที่ section OpenCode" — i.e. it received only the first
  ~600 characters of a ~5.5 KB brief — and correctly refused to guess. Cost ≈ $0.028.
- Cause: `headless_run.mjs` does **not** truncate (it writes `prompt` verbatim into `status.json`); the loss happens in
  the `powershell -Command ... --prompt (Get-Content -Raw <file>)` wrapper that passes a long multi-line argument.
- Verified good pattern: keep `--prompt` to one short pointer sentence and put the real brief in a file inside the repo —
  `runs/briefs/<card>-<name>.md` (`runs/` is gitignored) — then tell the worker to read that file in full. Run
  `runs/2026-09-26T09-31-09Z-go-restaff-v3` used this: `status.json.prompt` = 190 chars, complete.
- Blast radius: every earlier headless job with a brief longer than ~600-700 characters lost the tail of its instructions
  (including HR run v1). This is a real defect in how the PL queues work, not a model failure — fix belongs to a builder card.

### DEFECT — `opencode-go/glm-5.3-flash` hits the reasoning-length cap and produces zero output on slice-2b jobs
- Two T-034b slice-2b headless jobs (agent `worker`, model `opencode-go/glm-5.3-flash`) both ended with
  `step_finish reason "length"`, `reasoning 4096`, `output 0` **without writing a single file**:
  - `runs/2026-09-26T13-01-30Z-t034b-slice2b-server` — 54 tool calls, all grep/read, no `edit` call; last
    step `reason:"length"` after ~19 min.
  - `runs/2026-09-26T13-05-45Z-t034b-slice2b-ui` — 4 reads (brief + the three UI files), then
    `reason:"length"`, output 0.
- Cause: the model's reasoning budget (4096) is consumed while designing the change; it never reaches the
  output/edit step. Not a permission problem and not prompt truncation (`status.json.prompt` was complete).
- Recovery used here: builder substituted to `opencode-go/kimi-k3` (same OpenCode Go flat-rate pool, no new
  spend; probe `runs/2026-09-26T13-19-54Z-t034b-probe-kimi` = PROBE-OK) and the work split into a small
  spec file plus a one-line pointer prompt. The substitution is recorded on card T-034b.
- Guideline for future cards: a `*-flash` builder should get short, prescriptive briefs and a small file
  set; if it returns `reason:"length"` with zero output twice, switch to a stronger Go model and record it.

### FINDING — a second session is editing the same worktree concurrently (board + agents + roster)
- During the T-034b slice-2b session (2026-09-26, ~13:00–14:40), files this order never touched appeared
  modified in `git status` while the slice-2b jobs ran: `docs/project-memory/CURRENT_STATE.md`,
  `.opencode/agents/security.md`, `.opencode/agents/assistant.md`, `docs/product/MODEL_ROSTER.md`, and an
  added card **T-045** inside `TASKS.md`.
- None of the slice-2b headless workers referenced those files (checked: `Select-String CURRENT_STATE` in
  both run logs = 0 matches), so the edits came from another actor on the same single worktree — the same
  class of hazard the handoff logged before ("two Project-Lead chats on one worktree can clobber the board").
- Mitigation used: the slice-2b commit `aa36a81` staged **only** its own 8 files; `TASKS.md`,
  `CURRENT_STATE.md`, `MODEL_ROSTER.md` and the two agent files were deliberately left unstaged, so the
  other session's work was not committed or overwritten. The T-034b work-log entry therefore sits
  uncommitted on disk until that session (or the Owner) commits the board.
- Guideline: with one worktree, only one writing session at a time; a second session must wait or use a
  separate branch/worktree. The PL cannot detect this from inside a single chat — `git status` is the only signal.



