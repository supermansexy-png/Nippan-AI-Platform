# ADVISOR LOG — instruction records for the "ที่ปรึกษาวางแผน"

Status: **ACTIVE — created 2026-09-26 (card T-038).**

Every instruction issued by the `advisor` agent is recorded here **by the receiver of the
instruction (usually the Project Lead) — never by the advisor itself**. Rules are in
`docs/warroom/ADVISOR_MANDATE.md` §4–§5.

**This log is append-only. Never rewrite or delete an entry.** Corrections are added as a new entry
that references the old one.

## Entry format (copy this block, one per instruction)

```
### T-___ — <YYYY-MM-DD HH:MMZ> — <one-line order>
- owner_intent_verbatim: "<the Owner's own words, quoted verbatim, Thai>"
- order (as understood by the receiver): <what the advisor ordered, plainly>
- receiver: <PL | role | model slug>
- scope_in: <what is included>
- scope_out: <what is explicitly excluded>
- prohibitions: <what must not be done>
- auditor: <model slug used for the independent audit — must differ from opencode-go/mimo-v2.6-pro>
- verdict: <WITHIN-MANDATE | WITHIN-MANDATE-WITH-FINDINGS | OUT-OF-MANDATE | pending>
- evidence: <links to card / run dir / commit>
- notes: <anything the receiver wants on the record>
```

## Entries

### T-038 — 2026-09-26 — Upgrade the advisor's mandate and add oversight
- owner_intent_verbatim: "ที่ปรึกษาวางแผน สั่งงาน agent อื่นได้ทุกตัว จะเป็นคนแปลภาษาพี่เป็นภาษาเอไอที่รัดกุมและสั่งงานลงมาที่ pl ได้เลย pl แจกงานไปให้แต่ละฝ่ายทำต่อ ที่ปรึกษา commit อนุมัติได้ ได้กรณีพี่ไม่อยู่ แต่แก้ไฟล์ไม่ได้ และสั่งงานนอกเหนือระเบียบการทำงานไม่ได้ ตรงนี้ช่วยสร้างระบบตรวจสอบที่ปรึกษาด้วยว่ามีการสั่งงานนอกเหนือคำสั่งและละเมิดกฎระเบียบมั้ย — ปรับปรุงกฎให้ด้วยครับ และให้ตรวจสอบกฎว่าตรงไหนขัดแย้งบ้าง เพราะตอนนี้เราเปลี่ยนเอไอและบทบาทกันใหม่ต้องตรวจ"
- order (as understood by the receiver): expand `.opencode/agents/advisor.md` so the advisor may command every agent and may commit/approve while the Owner is away, while still being unable to edit files and unable to order work outside the working protocol; create a written oversight mechanism for the advisor; and run a conflict scan across the project's AI governance rules after the model/role changes.
- receiver: PL (`opencode-go/mimo-v2.6-pro` after T-037 re-pin)
- scope_in: advisor agent definition; `docs/warroom/ADVISOR_MANDATE.md`; this log; the governance conflict scan (T-038a); rule amendments the scan shows are needed.
- scope_out: production `Ai-bot-Nippan`; runtime customer routing; pricing/PDPA documents; any new paid spend.
- prohibitions: advisor must not edit files; no work without a card; no architecture/customer-policy/pricing change; no deploy/force-push; no Independent paid Auditor.
- auditor: `opencode-go/kimi-k3` — run `runs/2026-09-26T10-19-22Z-t039-protected-review` (model differs from the advisor's `opencode-go/mimo-v2.6-pro`)
- verdict: **WITHIN-MANDATE-WITH-FINDINGS** — all six mandate checks PASS; one finding: `TASK_CONTROL.md` §8 named only the Owner / PL as protected-document approvers and was silent on the advisor. Resolved conservatively: `ADVISOR_MANDATE.md` §6 and `TASK_CONTROL.md` §8 now state explicitly that protected-document approval is **outside** the advisor's substitute authority (conflict of interest — it is the subject of that governance).
- evidence: card T-038 / T-039 in `TASKS.md`; run `runs/2026-09-26T10-10-16Z-t038a-rule-scan` (conflict scan; the job itself ran out of budget, findings were taken by direct grep — see T-038); `runs/2026-09-26T10-12-56Z-t038b-advisor-upgrade`; `runs/2026-09-26T10-15-11Z-t038c-stale-rules`; `runs/2026-09-26T10-19-22Z-t039-protected-review`
- notes: the instruction record is written by the receiver, not the advisor — this is the audit property described in `ADVISOR_MANDATE.md` §4.

### T-034b slice 2b — 2026-09-26 — เริ่มงานแก้วาระจากหน้าเว็บ + commit ไฟล์ handoff ที่ค้าง
- owner_intent_verbatim: "อนุมัติ เสร้จแล้วมารอรับคำสั่งต่อไป"
- order (as understood by the receiver): the Owner approved the advisor's proposal to start T-034b slice 2b at once. The Project Lead is to (1) commit the pending working-tree change of `docs/project-memory/SESSION_HANDOFF.md` as a small standalone commit; (2) first read the card's work log and open the changed files to confirm what is actually still missing in slice 2b and that the 2c/2d must-fix + should-fix landed in the tree (not merely reported); (3) deliver slice 2b only — a meeting's agenda ("วาระ") must be creatable/editable/closable from the War Room web page under owner-only, fail-closed, server-established-actor rules, with the message→agenda link shown; (4) write slice 2b code through the builder/worker, never by the PL (T-043 lock); (5) obtain a reviewer verdict on a different model AND a security verdict for slice 2, and record both on the card; (6) write this instruction record into `ADVISOR_LOG.md` as the receiver.
- receiver: project-lead `openrouter/deepseek/deepseek-v4.1-flash` (distributes to builder/worker, reviewer, security)
- scope_in: the pending `SESSION_HANDOFF.md` commit; T-034b slice 2b only (in-room agenda path + its web UI, tests + CI green, reviewer + security verdicts); the instruction record below.
- scope_out: no deploy, no production, no `Ai-bot-Nippan`; no architecture/pricing/PDPA/customer-policy change; no protected-document change; do not re-open or expand closed cards (T-034a, T-030…); no goals beyond the card's slice-2 Done-when; do not run the seed/room script against the preview database carelessly (keep the `--force` + never-reset-a-live-room discipline).
- prohibitions: production · deploy (the rate-limiter deploy note stays "waits until verified") · architecture · pricing/PDPA/protected docs · secrets into any model or prompt · force-push · destructive DB operations · PL editing runtime files itself (T-043 lock — builder/worker or assistant only).
- auditor: `opencode-go/kimi-k3` (must answer the advisor-mandate A1–A5 audit per `ADVISOR_MANDATE.md` / skill `advisor-mandate-audit` before this order's card work is closed)
- verdict: pending
- evidence: card T-034b in `TASKS.md` (slice-2b work log) · housekeeping commit for `SESSION_HANDOFF.md` = `549b0fd` · slice-2b runs `runs/2026-09-26T13-32-18Z-t034b-slice2b-server-A`, `...14-05-…-server-B`, `...-ui-mimo`, `...-fix1a`, `...-fix1b`, `...-fix1c`; reviews `runs/2026-09-26T13-57-04Z-t034b-slice2b-review`, `...13-57-05Z-…-security`, `...14-25-53Z-…-review2`, `...14-25-59Z-…-security-delta` · tests `python -m pytest -q` (services/core) = 176 passed, 9 skipped · slice-2b commit SHA recorded on the card
- notes: OpenRouter credit is low (~$1–4) — checked before any OpenRouter call; the card's approved paid builder `opencode-go/glm-5.3-flash` (flat-rate Go) is the only new spend. The security model `openrouter/nex-agi/nex-n2.5-mini:free` was already recorded on the card as not resolving; per this order a live free substitute that differs from both the author and the reviewer is used and the substitution is recorded on the card (as slice 2a did).
