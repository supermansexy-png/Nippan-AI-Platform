# Project memory & document index

อ่านไฟล์นี้เพื่อรู้ว่าไฟล์ไหนอยู่ชั้นไหนและ **เปิดตอนไหน** · ทุกชื่อในตารางนี้ยืนยันแล้วว่ามีไฟล์จริง
(ตรวจ 2026-09-27, การ์ด T-058) — **ถ้ามีลิงก์ตายในไฟล์นี้ ถือว่าไฟล์นี้ผิด ต้องซ่อมทันที**
ไม่มีแถวไหนชี้ไปไฟล์ที่ไม่มีอยู่ (เดิมมี 3 แถวชี้ไฟล์ผี — ตัดออกแล้ว)

คอลัมน์ "เจ้าของไฟล์ (dev)" = ห้องสร้างระบบ ตาม `docs/warroom/BUILD_ROLES.md` Table 2 ·
คอลัมน์ "ปลายทาง (runtime)" = ตำแหน่งในห้องรันจริงที่จะรับช่วงไฟล์/ความรับผิดชอบนั้นต่อ

---

## ชั้น 1 — อ่านทุกครั้งที่เปิดแชทใหม่ (5 ไฟล์ + เช็ค git)

| ไฟล์ | อ่านแค่ไหน | เจ้าของไฟล์ (dev) | ปลายทาง (runtime) |
|---|---|---|---|
| `AGENTS.md` | ทั้งไฟล์ — และเป็น**ฉบับหลักของรายการอ่าน** | Project Lead (แก้ต้องอนุมัติจาก Project Owner) | Project Lead |
| `docs/project-memory/PROJECT_BRIEF.th.md` | ทั้งไฟล์ (ภาพรวม+ขอบเขต+กฎเหล็ก) | **Project Owner เท่านั้น** | Project Owner |
| `docs/project-memory/SESSION_HANDOFF.md` | ทั้งไฟล์ — มี**รายการงานค้างที่เดียว** | Project Lead | Project Lead |
| `docs/project-memory/CURRENT_STATE.md` | ทั้งไฟล์ (ตัดแล้ว ~115 บรรทัด) | Project Lead | Project Lead |
| `docs/project-memory/DECISIONS.md` | ทั้งไฟล์ (เล็ก) | Project Lead | Project Lead |

บวกคำสั่งเดียว: เช็ค `git status` + branch ปัจจุบัน

## ชั้น 2 — อ่านตามบทบาท

| ไฟล์ | เปิดตอนไหน | เจ้าของไฟล์ (dev) | ปลายทาง (runtime) |
|---|---|---|---|
| `.opencode/agents/<บทบาท>.md` | ไฟล์ของตัวเอง (โหลดอัตโนมัติอยู่แล้ว) — การจับคู่ตำแหน่งดู `BUILD_ROLES.md` Table 2 | Project Lead | reviewer/security → Auditor · researcher → ไม่มีคู่ |
| `docs/warroom/BUILD_ROLES.md` | งานเกี่ยวกับบทบาท/การส่งมอบตำแหน่ง | Project Lead | — (สะพานไป `ROLES.md`) |
| `docs/warroom/ROLES.md` | งานที่ต้องอ้างตำแหน่งฝั่งรันจริง | Project Lead (protected — L3) | ทุกตำแหน่งในห้องรันจริง |
| `docs/warroom/ADVISOR_MANDATE.md` | งานที่ **advisor** สั่ง (advisor ถูกตรวจด้วยไฟล์นี้) | Project Lead (protected — L3) | advisor |
| `docs/warroom/MONITORING.md` | งาน ops / การเฝ้าระวัง | ops | Cost Guard (ส่วนคุมทุน) |

## ชั้น 3 — อ่านตามประเภทงาน

| ไฟล์ | เปิดตอนไหน | เจ้าของไฟล์ (dev) | ปลายทาง (runtime) |
|---|---|---|---|
| `docs/warroom/AI_OPERATING_PROTOCOL.md` | รับงาน / ปิดงาน (INTAKE–DELIVERY–ตรวจรับ) | Project Lead (protected — L3) | Project Lead |
| `docs/warroom/AI_OPERATING_PROTOCOL.th.md` | เมื่ออธิบายกฎให้พี่เชษฟัง (กระจกอ่านอย่างเดียว) | Project Lead | — |
| `docs/warroom/TASK_CONTROL.md` | งานเกี่ยวกับการ์ด/ความเสี่ยง/WIP/DONE | Project Lead (protected — L3) | Project Lead |
| `TASKS.md` | **เฉพาะการ์ดที่ตัวเองทำอยู่** ไม่ต้องอ่านทั้งบอร์ด | Project Lead | Project Lead |
| `docs/product/MODEL_ROSTER.md` | งานเลือก/ตรวจโมเดล — อ่านแค่ตาราง Per-role staffing | model-recruiter (HR) | Model Scout |
| `docs/product/MODEL_POLICY.md` | งานเลือก/ตรวจโมเดล (กฎ ไม่ใช่รายชื่อ) | model-recruiter (HR) | Model Scout |
| `docs/warroom/START_PROMPT.md` | ตอนก๊อปคำสั่งให้ AI ตัวอื่น | Project Lead | — |
| `docs/warroom/DEV_WORKING_GUIDE.md` | ตอนกระจายงาน/กำหนดหลักฐาน/รายงาน | Project Lead | Developer + MCP tool builder |
| `docs/warroom/STARTUP_PLAYBOOK.md` | ตอนวางลำดับการสร้างเฟส A | Project Lead | — |
| `docs/product/PRICING_V1.md` | งานที่แตะราคา/ต้นทุนต่อบอท | **Project Owner** | — |
| `docs/warroom/ADVISOR_LOG.md` | ทุกครั้งที่ advisor สั่งงาน (append-only) | **ผู้รับคำสั่งเป็นคนเขียน — advisor ห้ามเขียน** | advisor |
| `docs/n8n/T-030-execution-evidence.md` | งาน n8n ↔ PostgreSQL (หลักฐาน RLS) | ops | — (งาน hosting/CI ไม่มีตำแหน่งถาวรฝั่งรันจริง) |

## ชั้น 4 — เปิดเฉพาะกิจ (มีเงื่อนไขกำกับ ไม่ต้องอ่านประจำ)

| ไฟล์ | เปิดเมื่อไหร่ | เจ้าของไฟล์ (dev) |
|---|---|---|
| `docs/warroom/decision-log.md` | อยากรู้ว่าเรื่องนี้เคยตัดสินไว้ว่าอย่างไร (append-only ค้นเฉพาะเรื่อง) | Project Lead |
| `docs/warroom/ai-scorecard.md` | มีเหตุโมเดลทำผิด/ถูก return หรือตอนทบทวนรายสัปดาห์ | Project Lead |
| `docs/warroom/ROADMAP_STUDY_DRAFT_2026-09-26.md` | พี่เชษสั่งรื้อเรื่องแผนเท่านั้น — **ยังเป็นร่างที่ไม่อนุมัติ** | Project Lead |
| `docs/product/FREE_MODEL_FALLBACK_GUIDE.md` | ตำแหน่งขาดคนแล้วต้องหาตัวฟรีแทน (historical — superseded) | model-recruiter (HR) |
| `docs/archive/TASKS_DONE_ARCHIVE.md` | ต้องดูหลักฐาน/ประวัติของงานที่ปิดแล้ว | Project Lead |
| `docs/archive/TASKS_PARKED.md` | ต้องดูงานที่พัก/ถูกทิ้งไว้ | Project Lead |
| `docs/warroom/DEV_ERROR_LOG.md` | เกิด incident หรือมีข้อผิดพลาดที่ต้องบันทึก | Project Lead |
| `docs/warroom/DECISION_LOG_FORMAT.md` | จะเขียน entry ใหม่ใน `decision-log.md` | Project Lead |
| `docs/warroom/SYSTEM_CONSTRAINTS.md` | งานที่ต้องเช็คข้อจำกัดระบบ | Project Lead |
| `docs/audits/WAR_ROOM_PREVIEW_DEPLOYMENT_EVIDENCE.md` | งาน War Room / deploy preview | ops |

## ไฟล์ที่ยังใช้ แต่มีปัญหาค้าง (ต้องมีการ์ดแก้ — L3)

| ไฟล์ | ปัญหา |
|---|---|
| `WORKING_POLICY.md` | ยังใช้ (รูปแบบ handoff + กฎห้ามขัด hard rule) แต่ **Rule 1 ยังมีรายการอ่านของตัวเอง** ขัดกับ `AGENTS.md` ที่เป็นฉบับหลัก — protected doc ต้องเปิดการ์ด L3 แก้ทีหลัง |
| `PROJECT_STATE.md` (root) | ไม่ได้อยู่ในรายการอ่านแล้ว (ถูกแทนด้วย `CURRENT_STATE.md`) แต่ยังถูก `WORKING_POLICY.md` Rule 1 อ้าง |
| `ROADMAP.md` (root) | เช่นเดียวกัน — แผนปัจจุบันอยู่ที่ `STARTUP_PLAYBOOK.md` + ร่าง roadmap |

## กฎเหล็กของไฟล์บันทึก

- **หนึ่งข้อเท็จจริง มีบ้านเดียว:** pin โมเดล → `MODEL_ROSTER.md` · งานค้าง → `SESSION_HANDOFF.md` ·
  รายการอ่าน → `AGENTS.md` · นิยามกฎ → `TASK_CONTROL.md` + `AI_OPERATING_PROTOCOL.md`
  · กลุ่มงานรายสัปดาห์/ความผิดของโมเดล → `ai-scorecard.md`
- **แผนกหนึ่งเขียนได้แค่ไฟล์บันทึกของตัวเอง** ห้ามแก้ไฟล์บันทึกของแผนกอื่น — เรื่องข้ามแผนกให้เขียนลง
  `decision-log.md` แทน (บทเรียนจากเหตุการณ์ไฟล์ `project-lead.md` ชนกัน 2026-09-26)
- ไฟล์ที่อยู่ใน `TASK_CONTROL.md` §8 (protected) แก้ได้เฉพาะการ์ด L3 + คนละโมเดลตรวจ + เจ้าของอนุมัติ
- ห้ามเก็บรหัสผ่าน/กุญแจ/token/ข้อมูลลูกค้าจริงในไฟล์บันทึกเหล่านี้
