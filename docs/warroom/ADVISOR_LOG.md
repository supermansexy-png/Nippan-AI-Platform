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
