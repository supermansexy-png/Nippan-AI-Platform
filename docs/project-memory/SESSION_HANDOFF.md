<!-- AUTO-HANDOFF:START -->
## Handoff ล่าสุด (auto) — 2026-09-27
**หัวข้อ:** T-057 correction: Owner model-selection framework + fix fabricated work

T-057 CORRECTION เสร็จแล้ว:
- เขียน Owner's Model-Selection Framework ลง MODEL_POLICY.md (4 หลักการ, checklist 6 ข้อพอดี, wallet ladder 4 ขั้น, ตารางสมาชิก 5 แถว, กฎปักรุ่น/รอบ2วัน/ตัวอย่าง ops)
- อัปเดต .opencode/agents/model-recruiter.md ให้อ้างอิง framework ใน read-first order
- append CORRECTION ใน decision-log.md (ระบุ 3 ข้อเท็จของ PL: MODEL_POLICY ไม่ได้แก้, 12-item ผิด, protected doc claim ผิด)
- append CORRECTION ORDER ใน ADVISOR_LOG.md (บันทึกคำสั่งครั้งนี้ + ความผิด PL + ความผิดผม: prompt ถูกตัด)
- append false-claim entry ใน ai-scorecard.md (project-lead seat penalty -1 ladder step stage 4→3)
- ผ่าน reviewer (muse spark 1.3 free) ตรวจทุกไฟล์ = PASS
- commit a2c642e + push origin/dev-workspace

สถานะ: T-057 จริงเสร็จสมบูรณ์ — ไม่มี fabrication

งานค้าง (นอก scope T-057): ไฟล์ modified ที่ไม่ได้ commit (project-lead.md, TASKS.md, TASKS_DONE_ARCHIVE.md, SESSION_HANDOFF.md, services/**) — คงมาจากงานก่อนหน้า

Archive 2026-09-27 (PL, ยังไม่ commit): T-041/T-048/T-052/T-057-CORRECTION ย้ายเข้า TASKS_DONE_ARCHIVE แล้ว; ซ่อม corruption 3 จุด (T-018 header, บล็อก T-057 ปลอมแทรกกลาง T-034a, link-test แทรกกลาง T-055 entry); ลบการ์ดปลอม T-057 (12-item) ออกจากบอร์ดแล้ว
ค้าง: T-053 (ขัดคำสั่ง — order ห้ามแก้ ROLES.md แต่ commit af5d9a7 แก้จริง +20/−0 ต้อง Owner ตัดสิน) · T-054/055/056 (งาน commit แล้วแต่การ์ดยัง READY + ไม่มี reviewer verdict) · T-035 (migrate 6 seats commit e6330a1 แล้ว เหลือ per-role evidence) · T-038/T-039/T-042/T-043/T-044 · services/** (T-051 participants-only seed, runtime — รอ builder/reviewer)
<!-- AUTO-HANDOFF:END -->

## งานค้างที่ยังไม่ปิด — บ้านเดียว (ย้ายมาจาก CURRENT_STATE.md, การ์ด T-058, 2026-09-27)

> ย้ายมาไว้ที่นี่เพื่อให้ "งานค้าง" มีที่เดียว ไม่กระจายสองไฟล์ · อัปเดตทุกครั้งที่ปิดงาน

- **T-058 — DONE (2026-09-27):** doc cleanup ครบทุกส่วน (A / B / governance / security re-pin / INDEX) · reviewer `opencode-go/space-bunny-free` = **ACCEPT-WITH-FINDINGS** (findings 1/3/4 แก้แล้ว, 5/6 ยกเป็นการ์ดใหม่) · **ยังไม่ push — รอพี่เชษยืนยัน**
- **T-053** — ขัดคำสั่ง: order ห้ามแก้ `ROLES.md` แต่ commit `af5d9a7` แก้จริง (+20/−0) → **รอ Owner ตัดสิน**
- **T-054 / T-055 / T-056** — งาน commit แล้ว แต่การ์ดยัง READY และไม่มี reviewer verdict บนการ์ด
- **T-035** — ย้าย 6 seats บน Go/free แล้ว (`e6330a1`) เหลือ per-role evidence
- **T-038 / T-039 / T-042 / T-043 / T-044** — ยังไม่ปิด
- **T-051** — participants-only seed: `services/core/**` แก้ไว้ใน working tree แล้ว รอ builder + reviewer (ยังไม่ commit โดยเจตนา)
- **T-032** — ติดคำตอบ Owner 2 ข้อ: branch protection บน `dev-workspace` (ตอนนี้ = false) และค่าฝั่ง Codex 4 ตัว
- **T-007 (D-01)** — ยังไม่ปิดการ์ดอย่างเป็นทางการ; Issues #35/#30 ค้าง
- **T-034b** — War Room server: งาน commit แล้ว ยังไม่ deploy
- **restart opencode** — pin ใหม่ (reviewer / project-lead / advisor) จะมีผลหลังพี่เชษ restart
- **n8n publish** — `n8n_publish_workflow` ปิดอยู่ (`false`); workflow ที่แก้แล้วจะยังรัน query เก่าจนกว่าจะ publish
- **`PROJECT_BRIEF.th.md`** — เคย untracked ใน git ทั้งที่ `AGENTS.md` บังคับให้อ่าน → **commit แล้ว (`74dc21c`)**
- **agent prompt ยังชี้โมเดลผิดตัว (finding จาก reviewer T-058):** `.opencode/agents/project-lead.md:73,76` และ `reviewer.md:57` ยังเขียนว่า builder = `opencode-go/glm-5.3-flash` (ของจริง = `openrouter/poolside/laguna-s-2.1:free`) → ต้องมีการ์ดใหม่ + writer (PL แก้ไฟล์ runtime เองไม่ได้)
- **งบ OpenRouter** — เครดิตต่ำ (~$0.64); งานเสียเงินทุกงานต้องขอพี่เชษก่อน
