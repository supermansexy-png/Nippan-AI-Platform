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
