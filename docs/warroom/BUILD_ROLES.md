# Dev-Time Roles — Nippan AI Platform

ตำแหน่งชุดนี้ใช้เฉพาะช่วงสร้างระบบ (ก่อนมีลูกค้ารายแรก) เมื่อถึง Step 2 ในแผนงาน ตำแหน่งเหล่านี้จะทยอยเปลี่ยนไปเป็นตำแหน่งใน ROLES.md แทน ตามตารางจับคู่ด้านล่าง

---

## Table 1: Dev-Time Roles & Duties

| Role | Dev-Time Duty |
|------|---------------|
| **Project Lead** | คิด วางแผน สั่งงาน จัดการบอร์ด TASKS.md รายงาน Owner ตาม AI_OPERATING_PROTOCOL + TASK_CONTROL ไม่เขียนโค้ด runtime เอง (file-type rule) |
| **advisor (ที่ปรึกษาวางแผน)** | แปลคำสั่ง Owner เป็น work order รัดกุม สั่ง agent ทุกตัวได้ อนุมัติ/commit แทน Owner ได้ตอน Owner ไม่อยู่ **ห้ามแก้ไฟล์เอง** ห้ามสั่งงานนอกระเบียบ (ADVISOR_MANDATE.md) |
| **builder** | เขียนโค้ด tests implementation ตามการ์ด ใช้โมเดล paid `opencode-go/glm-5.3-flash` (Owner lock lifted 2026-09-26) |
| **reviewer** | ตรวจงาน L1–L3 โดยโมเดลคนละตัวกับ builder (`opencode-go/space-bunny-free`) ให้ verdict ACCEPT/RETURN |
| **security** | ตรวจ authentication authorization secrets tenant/bot isolation attack surface security boundary แบบ read-only (`openrouter/nex-agi/nex-n2.5-mini:free` primary, `opencode-go/kimi-k3` backup) |
| **ops** | ดูแล GitHub CI Render Cloudflare Supabase hosting deployment evidence ตามการ์ด |
| **researcher** | ค้นข้อมูล เอกสาร เปรียบเทียบทางเลือก ให้ PL โดยไม่แก้ project |
| **model-recruiter (HR)** | คัดเลือกโมเดล/AI ให้ตรงงาน dev ตรวจ availability capability ราคา ตามนโยบายราคา (`opencode-go/gpt-6-luna`) |

---

## Table 2: Dev → Runtime Mapping Table

| ห้องสร้างระบบ | ห้องระบบรันจริง (ROLES.md) | ความสัมพันธ์ |
|---|---|---|
| Project Lead | Project Lead | ตำแหน่งเดียวกัน อยู่ทั้งสองห้องตลอด |
| builder | Developer + MCP tool builder | ย้ายห้องตรงๆ |
| security | Auditor (ส่วนความปลอดภัย) | ย้ายห้องบางส่วน รวมกับ reviewer |
| reviewer | Auditor (ส่วนตรวจซ้ำ) | ย้ายห้องบางส่วน รวมกับ security |
| model-recruiter (HR) | Model Scout | ย้ายห้องตรงๆ |
| ops | Cost Guard (ส่วนคุมทุน) | ย้ายห้องบางส่วน งาน hosting/CI ไม่มีตำแหน่งถาวรฝั่งรันจริง |
| researcher | ไม่มีคู่ | เลิกใช้เมื่อสร้างเสร็จ |
| advisor | advisor (เพิ่มใหม่ใน ROLES.md แล้ว) | อยู่ทั้งสองห้อง ไม่หายไปตอนเปลี่ยนห้อง |
| — | Onboarding, Support, Marketing | เกิดใหม่ตอนรันจริงเท่านั้น |