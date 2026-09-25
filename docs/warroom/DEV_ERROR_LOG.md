# Dev error log (dev-time)

Purpose: a durable record of errors/failures found while running dev work, so
every action can be traced back later (Owner order 2026-09-25: record errors
when found and keep every action auditable).

Format: `date | task | what failed | evidence | status`

## Entries

- **2026-09-25 | T-008 fix round 2 | frozen-contract violation** — builder added a new `owner_decision` key to the frozen event payload (`schemas/war-room-event-v1.schema.json`, `additionalProperties:false`). Evidence: reviewer REJECT + L4 batch audit CONFIRM (`anthropic/claude-opus-5.5:batch`, batch-1790297068-g3TQCwDIpy1YJIJ1aO6p). Status: **open** → fix round 3 queued.
- **2026-09-25 | headless runner | foreground wait aborted kills the job** — the queued T-008 job (`runs/2026-09-25T01-39-32Z-t008-fix3`) stopped producing output at 08:44:22, exactly when the foreground `wait.mjs` command was aborted by the Owner. The abort killed the whole process tree, including the detached `opencode run`. Evidence: `owner_decision` still present in `service.py:150` / `persistence.py` (fix not applied); stdout.log frozen at 548,724 bytes. Status: **open** → rule: never run a blocking waiter in the main chat; queue and check later.
- **2026-09-25 | T-009 | live render UNVERIFIED** — no DSN for the preview PostgreSQL, so the live usage_events render cannot be proven. Evidence: card T-009. Status: **open**.
- **2026-09-25 | headless launcher | cosmetic "ChildProcess.kill" message** — the launch command prints `Unknown: ChildProcess.kill (...)` from the shell even though the run dir is created and the job starts. Evidence: observed on both launch attempts. Status: **open (cosmetic)**.
- **2026-09-25 | T-008 fix round 3 | duplicate retry over an ambiguous base** — after the killed run (`01-39-32`), the fix was re-queued as `02-05-41` without first checking whether the killed run had left partial edits, and while the old run dir still existed. Two run dirs for the same task can tempt "two jobs touching the same files". Evidence: `runs/2026-09-25T01-39-32Z-t008-fix3` (killed, no DELIVERY) + `runs/2026-09-25T02-05-41Z-t008-fix3` (running); `git grep` shows `payload["owner_decision"]` still present. Status: **open** → rule: before re-queuing a killed job, delete/rename its run dir and confirm the working tree; judge the result by the **end state** (`git grep` + `pytest`), never by the run's own narration.
