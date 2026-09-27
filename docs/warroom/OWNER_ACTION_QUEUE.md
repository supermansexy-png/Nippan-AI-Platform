# Owner Action Queue — จุดแจ้งความต้องการ Owner **ที่เดียว**

> **กฎ:** ไม่ทำไปแจ้งไป — ทุกอย่างที่ต้องรอ Owner รวมไว้ที่นี่ครบ ไม่กระจาย ไม่ซ้ำ อัปเดตทุกครั้งแทนการรายงานทีละเรื่อง
> สถานะ: `OPEN` = รอ Owner ตัดสินใจ/ให้ข้อมูล | `READY` = Owner ให้ข้อมูลแล้ว พร้อมดำเนินการ | `DONE` = ปิดแล้ว

---

## 📋 รายการค้าง (OPEN)

| # | เรื่อง | การ์ดเกี่ยวข้อง | รายละเอียดที่ต้องการจาก Owner | สถานะ | วันที่เปิด |
|---|--------|----------------|-------------------------------|--------|-----------|
| 1 | **GitHub Issue Queue: Trigger ChatGPT (External Assistant)** | T-032 Pilot B, T-074, T-075, T-076 | Owner ต้องเป็นคน trigger ChatGPT อีกตัวผ่าน GitHub Issue (label `ai:ready`) ตามกฎ 2 เลน — PL สร้าง Issue แล้ว Owner กด trigger | OPEN | 2026-09-27 |

---

## ✅ ปิดแล้ว (DONE) — เก็บไว้เพื่ออ้างอิง

| # | เรื่อง | การ์ด | วิธีปิด | วันที่ปิด |
|---|--------|-------|---------|----------|
| 1 | Alert channel = Email first, add LINE later | T-071 | Owner ระบุ: "อีเมล์ก่อน พอเปิดจริงจะเพิ่มแจ้งทางไลน์ด้วย" + endpoint `supermanexy@gmail.com` | 2026-09-27 |
| 2 | Backup/restore target = separate database/schema | T-072 | Owner ระบุ: "ฐานแยก" | 2026-09-27 |
| 3 | P0 Execution Plan approved | T-071, T-072 | Owner: "1 อนุมัติ" | 2026-09-27 |
| 4 | SMTP credential blocker cancelled | T-071 | Owner: "เขียนโครงไว้รอ ไม่ต้องเอา credential จริง" | 2026-09-27 |
| 5 | Use Supabase MCP (cancel pg_dump/CLI blocker) | T-072 | Owner: "เรามี mcp ของ supabase ใช้ทางนั้นได้เลย" | 2026-09-27 |
| 6 | Free-tier policy scope resolved | T-067 | Owner: "ก" (external shared-pool free tiers only) | 2026-09-27 |
| 7 | War Room pilot decisions (3/3) | T-033 | Fresh room = yes; Owner pays $1/meeting; PL chooses participants per agenda | 2026-09-27 |
| 8 | T-034b deploy approved | T-034b | Owner: "1 อนุมั1ิ" → PR #86 merged, deploy live | 2026-09-27 |
| 9 | **SMTP Credentials สำหรับ Email Alert** | T-071 | Owner จะกรอกเองตอนเปิดใช้งานจริง (ตอนนี้เขียน fail-closed stub ไว้รอ) — **ย้ายจาก OPEN มาเป็นหมายเหตุ phase 2** | 2026-09-27 |
| 10 | **LINE Channel Credentials** | T-071 | Owner จะเพิ่มภายหลัง "พอเปิดจริงจะเพิ่มแจ้งทางไลน์ด้วย" — **ย้ายจาก OPEN มาเป็นหมายเหตุ phase 2** | 2026-09-27 |
| 11 | **Supabase Project Ref (20-char) สำหรับ MCP** | T-072, T-076 | Project reference 20 ตัวอักษรของโปรเจกต์ `xzxwakvsbdzkdybijbzs` มีในรีโปแล้ว ใช้ได้เลย — **ย้ายจาก OPEN มาเป็นหมายเหตุ phase 2** | 2026-09-27 |
| 12 | **T-073 Advisor→PL Gate: เริ่มงานออกแบบหรือยัง** | T-073 | Owner สั่งผ่านแล้ว "READY for INTAKE — เริ่มได้เลย ไม่ต้องรออนุมัติ" — **ย้ายจาก OPEN มาเป็นหมายเหตุ phase 2** | 2026-09-27 |

---

## 🔄 วิธีใช้งาน

1. **PL อัปเดตไฟล์นี้** ทุกครั้งที่มีเรื่องใหม่ต้องรอ Owner หรือ Owner ตอบกลับ
2. **Owner ดูที่นี่ครั้งเดียว** ไม่ต้องหาใน chat / handoff / card 散らばり
3. **ปิดรายการ** = ย้ายจาก OPEN → DONE พร้อมบันทึก "วิธีปิด" และ "วันที่ปิด"
4. **ไม่มีรายการซ้ำ** — ถ้ามีเรื่องเก่าเกิดขึ้นอีก ให้อัปเดตรายการเดิม ไม่สร้างใหม่

---

## 📌 หมายเหตุสำคัญ

- **Credential จริง (SMTP, LINE, Supabase tokens)**: Owner จะกรอกเองตอนเปิดใช้งานจริง — ตอนนี้ระบบเขียน **fail-closed stub** ไว้รอ (T-071, T-072, T-076)
- **GitHub Issue trigger**: ตามกฎ 2 เลน (Owner decision 2026-09-27) — งานไม่ด่วน = PL สร้าง Issue `ai:ready` → Owner trigger ChatGPT อีกตัว → Assistant poll ทุก 1 ชม.
- **Advisor oversight**: Advisor ตรวจทานรอบสุดท้ายกับ PL แล้ว Advisor อนุมัติได้เลย ไม่หยุดรอ Owner (ยกเว้น protected docs / architecture / production)