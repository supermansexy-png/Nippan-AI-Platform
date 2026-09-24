# Session Handoff — 2026-09-25

อ่านไฟล์นี้ก่อนเริ่มงานในแชทใหม่ แล้วอ่านเพิ่มเฉพาะที่จำเป็น อย่าโหลดทั้ง repo

## แผนปัจจุบัน (authoritative)
- Phase A Market Test: `docs/warroom/STARTUP_PLAYBOOK.md` — n8n + PostgreSQL lite schema + OpenRouter
- `ROADMAP.md` = archived blueprint (อย่าเอามาทำ)
- War Room = track แยก ACTIVE (T-007/T-008/T-009)

## กฎที่ Owner ตั้งไว้ (บังคับ)
1. **ทุกอย่างที่เสียเงิน (เรียก agent/โมเดล) ต้องขอ Owner อนุมัติก่อน** — ห้ามทำทันที
2. Owner เป็นผู้ตัดสินใจสุดท้าย (พี่เชษ)
3. รายงานสั้น เน้นเนื้อๆ (Owner สั่งลดความยาว ~80%)
4. Anti-redundancy: reviewer/security ต้องคนละโมเดลกับ builder
5. ห้ามแตะ production `Ai-bot-Nippan`
6. งาน L2/L3 ต้องมี reviewer ตรวจ + Owner อนุมัติก่อน DONE

## ทีมโมเดล (roster ปัจจุบัน — `docs/product/MODEL_ROSTER.md`)
| Role | Primary | Backup |
|------|---------|--------|
| project-lead | deepseek/deepseek-v4.1-flash | nemotron-3.5-lightning |
| builder | qwen/qwen3.7-flash | nemotron-3.5-lightning |
| reviewer | z-ai/glm-5.3-flash | inkling:free |
| security | z-ai/glm-5.3-flash | inkling:free |
| model-recruiter (HR) | openai/gpt-6-luna | tencent/hy3-preview |
- Agent files ผูก `model:` ใน frontmatter แล้ว (ต้อง restart opencode เมื่อแก้)

## สถานะงาน (TASKS.md)
- DONE: T-002, T-005, T-006, T-010, T-011, T-013, T-014, T-015, T-016 (ดู `docs/archive/TASKS_DONE_ARCHIVE.md`)
- T-017 (แยกกระดาน) — builder ทำเสร็จ, **รอ reviewer ตรวจ** (ยังไม่ปิด)
- PARTIAL: T-001 (รอทดสอบ runtime), T-007 (รอ remote access)
- READY: T-003 (3 MCP tools), T-008/T-009 (War Room D-02/D-03 acceptance — โค้ดมีแล้ว)
- T-004 (legal) ถูก Owner ตัดออกจากแผน dev-time
- T-012 ยังค้าง READY (ถูกแทนที่ด้วย T-014)

## ค่าใช้จ่าย (วัดจาก opencode DB)
- 24 ชม.ล่าสุด ≈ $2.71 ; PL session เดียว $1.20 (อ่าน context ซ้ำ)
- Account OpenRouter: ใช้ $28.18 / $30 (เหลือ $1.82)
- แผนลดต้นทุน: เปิดแชทใหม่ต่องาน / ลด docs / review L1-L2 ใช้โมเดลฟรี / batch / provider sort=price

## Incident ล่าสุดที่ต้องรู้
- qwen3.7-flash ถูกปลดจาก PL + HR (False DONE) — `docs/warroom/ai-scorecard.md`
- ระบบเคยไม่ผูก model ใน agent files ทำให้ roster ไม่ถูกบังคับใช้ — แก้แล้ว
