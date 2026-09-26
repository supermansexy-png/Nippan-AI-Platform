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

**NEEDS_OWNER_DECISION: ตารางจับคู่ยังไม่ได้รับจากเจ้าของ**

> Owner ระบุว่า "เอาตารางที่ผมส่งให้ไปใส่ได้เลย" แต่ค้นหาใน repo ทั้งหมด (รวม PROJECT_BRIEF.th.md) **ไม่พบตารางจับคู่ dev-time ↔ runtime roles** จึงสร้าง placeholder นี้ไว้ รอ Owner ส่งมาหรือสั่งให้สร้างใหม่

| Dev-Time Role | Runtime Role (ROLES.md) | Notes |
|---------------|-------------------------|-------|
| Project Lead | Project Lead (Phase A: Owner) | dev-time PL = AI; runtime PL = Owner |
| advisor | — | dev-time only; not in runtime ecosystem |
| builder | Developer / MCP tool builder | |
| reviewer | Auditor | reviewer ≠ builder (anti-redundancy) |
| security | (part of Auditor / separate gate) | |
| ops | Onboarding / Support / Cost Guard | |
| researcher | — | dev-time only |
| model-recruiter | Model Scout | |

*หมายเหตุ: ตารางนี้เป็น placeholder จะต้องได้รับจาก Owner หรือสร้างใหม่เมื่อถึงขั้นตอนการจับคู่อย่างเป็นทางการ*