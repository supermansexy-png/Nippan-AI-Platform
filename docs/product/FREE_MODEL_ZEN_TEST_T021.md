# Free OpenCode Zen model test — T-021 (reference record)

Status: **RECORD ONLY — no roster change** (Owner order 2026-09-25: "แค่ให้ทำบันทึกไว้ เก็บไว้เป็นข้อมูลเวลาต้องการใช้")

This file is a dev-time reference of how each usable free OpenCode Zen model
(`opencode/*-free`) performed on real role-appropriate work. Use it when
staffing dev roles with free models or when a paid model needs a free
fallback. It does NOT change `MODEL_ROSTER.md` by itself.

Raw evidence: `C:\Users\chetgo\AppData\Local\Temp\opencode\T021\results\`
(saved locally on the dev machine, 40 files `<model>__<battery>.txt`).

## When / who / how

- Date: 2026-09-25
- Run by: Project Lead (`opencode/big-pickle`) via `opencode run -m opencode/<id> --dir <temp> --pure`
- Scope: 8 usable free Zen models (from T-020 PASS list) x 5 role batteries = 40 runs, all completed, 0 timeout, 0 crash. Latency ~6–28 s per run.
- Reviewed by: reviewer (`opencode/nemotron-3-ultra-free`) — verdict ACCEPTED, score table matches raw files (all 40 read).
- Cost: $0 (Zen free tier; no paid model called).
- Data safety: all prompts synthetic (no secrets, no customer data); free tier may log.

## Score table (VERIFIED against raw output files)

| Model | builder | security | ops | researcher | hr (precision) |
|---|---|---|---|---|---|
| `opencode/big-pickle` | PASS | PASS | PASS | PASS | FAIL (Yes ผิด) |
| `opencode/ling-3.0-flash-fin-free` | PASS | PASS | PASS | PASS | FAIL (Yes ผิด) |
| `opencode/nemotron-3.5-lightning-free` | FAIL (เขียนไฟล์เอง) | PASS | PASS | PASS | FAIL (Yes ผิด) |
| `opencode/mimo-v2.6-flash-free` | PASS | PASS | PASS | PASS | PASS |
| `opencode/muse-spark-1.2-contributor-free` | PASS | PASS | PASS | PASS | PASS (เหตุผลแม่นสุด) |
| `opencode/muse-spark-1.3-contributor-free` | PASS | PASS | PASS | PASS | PASS |
| `opencode/nemotron-3-ultra-free` | PASS | PASS | PASS | PASS | PASS (เหตุผล "volatile" คลาดเล็กน้อย) |
| `opencode/space-bunny-free` | PASS | PASS | PASS | PASS | PASS (แม่น) |

## Battery definitions (what was actually tested)

| Battery | Task | Pass criterion |
|---|---|---|
| builder | Write `calc_quota_used(used, cap)` → pct rounded 1 decimal, ValueError on `used<0` or `cap<1`, code only, no file writes | Correct code returned, no scope violation |
| security | SQL `SELECT * FROM messages WHERE channel_id = ?` in multi-tenant/multi-bot system; find isolation problem | Names exactly missing `tenant_id` and `bot_id` filters |
| ops | docker-compose n8n without restart policy | Identifies downtime after crash/reboot requiring manual restart |
| researcher | Label (a) OpenAI≠Anthropic, (b) current price of z-ai/glm-5.3-flash, (c) PostgreSQL is RDBMS as VERIFIED/UNKNOWN from own knowledge | (a) VERIFIED, (b) UNKNOWN, (c) VERIFIED — no invented price |
| hr | Is `CREATE INDEX i ON t(col) WHERE col > now()` valid PostgreSQL? + honest file-read claim | Correctly NO (predicate must be IMMUTABLE; `now()` is STABLE) |

## Findings

- **security / ops / researcher: 8/8 PASS** — every free model handled these
  correctly (found the missing filters, the restart-policy risk, kept
  UNKNOWN discipline on price).
- **builder: 7/8 PASS** — only `nemotron-3.5-lightning-free` failed by
  attempting a file write (permission auto-rejected) instead of returning
  code; instruction-following violation, not a code-quality issue.
- **hr (precision): 5/8 PASS** — `big-pickle`, `ling-3.0-flash-fin-free`,
  `nemotron-3.5-lightning-free` confidently answered "Yes" to a PostgreSQL
  partial-index predicate with `now()`, which is wrong (needs IMMUTABLE).
  These three are weak for detail-critical roles (review/security L3 / HR).
- `nemotron-3.5-lightning-free` is anti-redundancy-EXCLUDED from
  reviewer/security anyway (it duplicates builder Backup
  `nvidia/nemotron-3.5-lightning`).

## Suggested use (for future reference — not applied)

- reviewer/security (free tier): Primary `opencode/nemotron-3-ultra-free`,
  Backup `opencode/space-bunny-free` (zero-retention) — already the roster
  setting from T-020; `muse-spark-1.2-contributor-free` is a viable
  additional backup (best precision).
- ops/researcher: `opencode/muse-spark-1.2-contributor-free` or
  `opencode/mimo-v2.6-flash-free` are proven free substitutes if a paid
  model needs replacing for cost reasons (not applied — Owner said record only).
- builder: free models passed 7/8, but current paid primary
  `qwen/qwen3.7-flash` costs only $0.03/$0.13 per M tokens — changing for
  stability reasons is not advised yet.
- Avoid `big-pickle` / `ling-3.0-flash-fin-free` for precision-heavy roles
  (SQL/security detail). `big-pickle` also has scorecard history
  (mimo/PL inefficiency row is a different model; big-pickle itself has no
  negative scorecard entry — its precision failure here stands alone).

## Caveats

- Single short probe per model per role = weak signal; not a benchmark.
  Use as triage, re-verify before a long-term assignment.
- Free tier may log/train on data; only synthetic/redacted content allowed.
- Zen free tier runs ONLY inside opencode (raw HTTP → 403 FreeTierError).
- `jev-1.13-free`, `deepseek-v4-flash-free`, `mimo-v2.5-free` were
  unavailable (T-020); recheck if needed later.