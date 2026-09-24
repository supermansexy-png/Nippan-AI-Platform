<!-- AUTO-HANDOFF:START -->
## Handoff ล่าสุด (auto)
(ยังไม่มี — จะถูกเขียนทับอัตโนมัติทุกครั้งที่ใช้ `/handoff`)
<!-- AUTO-HANDOFF:END -->

# Session Handoff — 2026-09-25 (อัปเดต)

อ่านไฟล์นี้ก่อนเริ่มงานในแชทใหม่ แล้วอ่านเพิ่มเฉพาะที่จำเป็น อย่าโหลดทั้ง repo

## วิธีเริ่มหน้าใหม่ (Owner ใช้แอป desktop)
- ระหว่างแชท: ใช้ `/compact` เพื่อย่อประวัติ (ลด token) — ทำงานต่อในแชทเดิมได้
- อยากเริ่มหน้าใหม่: กด `/new` แล้วพิมพ์ "อ่าน docs/project-memory/SESSION_HANDOFF.md แล้วทำงานต่อ"
- `/sessions` ใช้ไม่ได้ในแอป desktop (เป็นคำสั่งของ TUI) — อย่าให้ flow พึ่งคำสั่งนี้

## แผนปัจจุบัน (authoritative)
- Phase A Market Test: `docs/warroom/STARTUP_PLAYBOOK.md` — n8n + PostgreSQL lite schema + OpenRouter
- `ROADMAP.md` = archived blueprint (อย่าเอามาทำ)
- War Room = track แยก ACTIVE (T-007/T-008/T-009)

## กฎที่ Owner ตั้งไว้ (บังคับ)
1. **ทุกอย่างที่เสียเงิน (เรียก agent/โมเดล) ต้องขอ Owner อนุมัติก่อน** — ห้ามทำทันที
2. Owner เป็นผู้ตัดสินใจสุดท้าย (พี่เชษ)
3. รายงานสั้น เน้นเนื้อ ๆ (Owner สั่งลดความยาว ~80%)
4. Anti-redundancy: reviewer/security ต้องคนละโมเดลกับ builder และ reviewer ≠ security
5. ห้ามแตะ production `Ai-bot-Nippan`
6. งาน L2/L3 ต้องมี reviewer ตรวจ + Owner อนุมัติก่อน DONE
7. commit/amend/push เฉพาะเมื่อ Owner สั่ง ("อนุมัติ"/"อนุญาต")
8. งานเสียเงินที่ไม่รีบ → ส่ง Batch API (`:batch`) เสมอ (ถูกกว่า ~40–60%)

## ทีมโมเดล (roster ปัจจุบัน — `docs/product/MODEL_ROSTER.md`)
| Role | Primary | Backup |
|------|---------|--------|
| project-lead | `openrouter/deepseek/deepseek-v4.1-flash` (paid, คิด/วางแผนเท่านั้น) | nemotron-3.5-lightning |
| builder | `qwen/qwen3.7-flash` (paid) | nvidia/nemotron-3.5-lightning |
| reviewer L1/L2 | `opencode/nemotron-3-ultra-free` | opencode/space-bunny-free |
| reviewer L3 | `opencode/space-bunny-free` (zero-retention) | — |
| reviewer L4 (ความแม่นสูง) | `z-ai/glm-5.3-flash` (paid) | — |
| security L1/L2 | `opencode/big-pickle` (≠ reviewer) | opencode/ling-3.0-flash-fin-free |
| ops | `opencode/big-pickle` | — |
| researcher | `opencode/ling-3.0-flash-fin-free` | — |
| assistant | `opencode/mimo-v2.6-flash-free` | opencode/big-pickle |
| model-recruiter (HR) | `openai/gpt-6-luna` | tencent/hy3-preview |

- L4 เป็น **review tier** ไม่ใช่ risk level ใน TASK_CONTROL §3 (protected — มีแค่ L1–L3)
- Agent files ผูก `model:` ใน frontmatter แล้ว (ต้อง restart opencode เมื่อแก้)
- โมเดลฟรี Zen ใช้ได้เฉพาะใน opencode (ยิง HTTP ตรงได้ 403); ส่วนใหญ่ log/train → ห้ามใส่ secret

## สถานะงาน (TASKS.md + docs/archive/TASKS_DONE_ARCHIVE.md)
- DONE: T-002, T-005, T-006, T-010, T-011, T-013, T-014, T-015, T-016, T-017
- DONE: T-018 (preamble/report shrink), T-019 (batch rule + smoke test 5/5), T-020 (review tiers), T-022 (paid builder policy), T-023 (team fix)
- DONE (record only): T-021 Zen free-model test (40/40 runs, 8 models × 5 role batteries)
- IN_PROGRESS: T-021 (handoff plugin — เหลือ live test หลัง restart), T-024 (ทดสอบ OpenRouter `:free` — รอ Owner อนุมัติก่อนยิง)
- PARTIAL: T-001 (รอทดสอบ runtime), T-007 (รอ remote access)
- READY: T-003 (3 MCP tools), T-008/T-009 (War Room D-02/D-03 acceptance — โค้ดมีแล้ว)
- T-004 (legal) ถูก Owner ตัดออกจากแผน dev-time; T-012 ถูกแทนที่ด้วย T-014

## ค่าใช้จ่าย (วัดจาก opencode DB)
- 24 ชม.ล่าสุด ≈ $2.71 ; PL session เดียว $1.20 (อ่าน context ซ้ำ) — ตัวเลขก่อนมาตรการลดต้นทุน
- Account OpenRouter: ใช้ $28.18 / $30 (เหลือ $1.82) — **ตัวเลข ณ 2026-09-25 ยังไม่เช็คใหม่**
- มาตรการลดต้นทุนที่ใช้อยู่: `/compact` + เปิดหน้าใหม่ต่อเมื่อจำเป็น / ลด docs ที่อ่านทุก turn / review L1–L2 ใช้โมเดลฟรี / batch / provider sort=price

## Incident ล่าสุดที่ต้องรู้
- qwen3.7-flash ถูกปลดจาก PL + HR (False DONE) — `docs/warroom/ai-scorecard.md` (ภายหลังกลับมาเป็น builder ตาม T-023)
- ระบบเคยไม่ผูก model ใน agent files ทำให้ roster ไม่ถูกบังคับใช้ — แก้แล้ว
- TASKS.md มีเลขการ์ด **T-021 ซ้ำ 2 ใบ** (handoff plugin + Zen test) — รอ renumber