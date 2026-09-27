# P0 Execution Plan — APPROVED 2026-09-27 (Owner: "1 อนุมัติ")

**Date:** 2026-09-27  
**Owner order verbatim:** "ทำไมไม่จำเลย" + "นี้เข้าใจมัียว่าตอนนี้ไม่มีผู้เช่า ไม่มีผู้ใช้ ยังไม่ได้เปิดระบบ เข้าใจใช่มัย" + "เปิดเลย ... อันดับแรกเปิดงาน ทั้ง 2 ใบ และให้ pl ว่างแผนงาน ออกมา เลือกทีมงาน และการกระจายงาน แผนดำเนินการ ให้ทำมาส่งก่อน"

**Owner decisions (verbatim, recorded 2026-09-27):**
1. "1 อนุมัติ" — แผนนี้อนุมัติเริ่มงานได้เลย
2. "อีเมล์ก่อน พอเปิดจริงจะเพิ่มแจ้งทางไลน์ด้วย" — T-071 alert channel = **email first**, add LINE later when live. **Initial email endpoint: supermanexy@gmail.com** (Owner provided 2026-09-27)
3. "ฐานแยก" — T-072 restore target = **separate database/schema** (not the live schema)

**Standing fact (recorded in SESSION_HANDOFF.md + CURRENT_STATE.md):**  
สถานะโครงการ: ยังไม่มีผู้เช่า ไม่มีผู้ใช้ ระบบยังไม่เปิด (pre-G1) — ฐานข้อมูล Supabase เป็นของทดสอบ ไม่มีข้อมูลลูกค้าจริง งานทดสอบ/backup/restore ทำบนฐานจริงได้โดยตรง ไม่ต้องกันข้อมูลผู้เช่า (ที่ยังไม่มี) แต่ยังห้ามแตะระบบ production เก่า Ai-bot-Nippan

---

## 1) ทีมต่อการ์ด (บทบาท + โมเดล provider-prefixed ตาม MODEL_ROSTER.md ตาราง T-065)

| การ์ด | บทบาท | โมเดล Primary (slug) | โมเดล Backup 1 | โมเดล Backup 2 | เหตุผลเลือก |
|------|-------|---------------------|----------------|----------------|-----------|
| **T-071** P0.1 Alert channel | **builder** | `opencode-go/glm-5.3-flash` | `openrouter/poolside/laguna-s-2.1:free` | `opencode-go/kimi-k3` | ต้องเขียน code จริง (emit point + channel wiring) — GLM-5.3-flash เป็น Primary builder ตาม roster |
| | **reviewer L1–L3** | `opencode/muse-spark-1.3-contributor-free` | `openrouter/nvidia/nemotron-3.5-lightning:free` | `opencode-go/space-bunny-free` | ตรวจ diff + evidence คนละโมเดลจาก builder (anti-redundancy PASS) |
| | **ops** | `opencode/mimo-v2.6-flash-free` | `opencode-go/mimo-v2.6-flash` | `openrouter/nvidia/nemotron-3.5-lightning:free` | ดูแล CI/hosting/Render webhook evidence |
| | **PL** | `opencode/nemotron-3-ultra-free` | `opencode-go/longcat-2.5-preview-free` | `openrouter/deepseek/deepseek-v4.1-flash` | วางแผน/ประสาน/verify — ไม่ลงมือ code |
| **T-072** P0.2 Backup/restore proof | **ops** | `opencode/mimo-v2.6-flash-free` | `opencode-go/mimo-v2.6-flash` | `openrouter/nvidia/nemotron-3.5-lightning:free` | รันคำสั่ง dump/restore/verify บน Supabase จริง — ops role ตรงที่สุด |
| | **reviewer L1–L3** | `opencode/muse-spark-1.3-contributor-free` | `openrouter/nvidia/nemotron-3.5-lightning:free` | `opencode-go/space-bunny-free` | ตรวจหลักฐาน dump/restore/verify คนละโมเดลจาก ops |
| | **PL** | `opencode/nemotron-3-ultra-free` | `opencode-go/longcat-2.5-preview-free` | `openrouter/deepseek/deepseek-v4.1-flash` | วางแผน/verify — ไม่รันคำสั่ง DB เอง |

**หมายเหตุ:** ทุกโมเดลจากตาราง T-065 (Per-role staffing) ใช้ได้เลย — ห้ามฮาร์ดโค้ดชื่อโมเดลใหม่ ห้ามใช้โมเดลนอก roster

---

## 2) กระจายงานคู่ขนาน 2 ใบ

```
T-071 (Alert)          T-072 (Backup/restore)
     │                       │
  PL วางแผน              PL วางแผน
     │                       │
  HR เช็คพร้อม           HR เช็คพร้อม
     │                       │
  Owner อนุมัติ           Owner อนุมัติ
     │                       │
  ┌──┴──┐               ┌──┴──┐
  ▼     ▼               ▼     ▼
builder   ops         ops     (reviewer แยกตัว)
  │       │           │       │
  ▼       ▼           ▼       ▼
  PR      PR          PR      PR
  │       │           │       │
  └───────┴───────────┴───────┘
            │
       reviewer ตรวจคนละโมเดล
            │
         merge → ปิดการ์ด
```

- **หนึ่งการ์ด = หนึ่ง branch = หนึ่ง PR** — กันไฟล์ชน
- T-071: branch `t-071-alert-channel` → PR → CI → reviewer → merge
- T-072: branch `t-072-backup-restore-proof` → PR → CI → reviewer → merge
- ทำพร้อมกันได้ เพราะไฟล์ไม่ทับ (T-071 = code/transport; T-072 = docs/scripts/evidence)

---

## 3) ขั้นตอน INTAKE → Issue(ai:ready) → claim → branch → PR → CI → reviewer คนละโมเดล → merge → ปิดการ์ด

ต่อการ์ด **ทุกขั้นตอนบังคับ** (AI_OPERATING_PROTOCOL.md + TASK_CONTROL.md):

1. **INTAKE** — builder/ops เขียน INTAUTE ภายใต้การ์ด (อ่าน TASKS.md บล็อกของตัวเอง) → ACCEPT/DECLINE/NEEDS_DECISION
2. **Issue สร้าง** — PL สร้าง GitHub Issue label `ai:ready` body ครบ (Task/Role/Risk/Scope/Done-when/Stop rules)
3. **Claim** — ผู้รับงาน (builder/ops) ตั้ง label `ai:claimed` เอง (PL ห้ามตั้งแทน)
4. **Branch** — สร้าง branch `t-071-...` / `t-072-...` จาก `dev-workspace`
5. **ทำงาน** — ตาม Done-when บนการ์ด; commits บน branch ตัวเอง
6. **PR** — เปิด Draft PR → CI รันอัตโนมัติ
7. **Reviewer** — PL มอบหมาย reviewer **คนละโมเดลจาก author** (ดูตารางข้างบน) → reviewer เขียน verdict comment บน PR
8. **Merge** — PL verify scope/evidence/verdict → merge (Owner approve หรือ PL แทน Owner ตามกฎ)
9. **ปิดการ์ด** — DELIVERY report + move to DONE (archive ทันที)

---

## 4) หลักฐานปิดงานต่อใบ + Stop rule

| การ์ด | หลักฐาน (Evidence) ที่ต้องมีใน DELIVERY | Stop rule |
|------|----------------------------------------|-----------|
| **T-071** | 1) Alert channel spec doc (endpoint, auth, payload, severity)<br>2) Code diff minimal (emit point + wiring)<br>3) CI green (GitHub Actions)<br>4) Live firing proof: curl/Postman log หรือ Render/Cloudflare log showing alert fired<br>5) Reviewer verdict comment (model name ชัด) | - Budget cap: builder ≤ $2 (OpenCode Go flat pool); reviewer free<br>- หาก alert ไม่ยิงได้ 2 รอบติด → NEEDS_DECISION<br>- หาก CI fail > 15 นาที → BLOCKED |
| **T-072** | 1) `pg_dump` / Supabase CLI command + full output (stdout/stderr)<br>2) Restore command + full output<br>3) Verification queries: row counts per table, FK check, `SELECT * FROM pg_policies WHERE schemaname='public' AND tablename LIKE 'lite_%'`, RLS FORCE check<br>4) Reviewer verdict comment (model name ชัด) | - Budget cap: ops ≤ $1 (OpenCode Go flat pool); reviewer free<br>- หาก restore ไม่ผ่าน FK/RLS → NEEDS_DECISION<br>- หาก Supabase quota limit → BLOCKED (ใช้ project/schmea แยก) |

---

## 5) ความเสี่ยง + อะไรต้องรอ Owner

| เรื่อง | รายละเอียด | สถานะ |
|-------|------------|-------|
| **Alert endpoint** | Owner ระบุ endpoint จริง: **email supermanexy@gmail.com** (initial destination) | **OK — provided** |
| **Supabase restore target** | ใช้ project เดียว schema ใหม่ (`lite_restore_test`) หรือ project แยก — Owner เลือก | **รอ Owner** |
| **Budget approval** | งานทั้งคู่ใช้ OpenCode Go flat pool (ไม่เสียเงินเพิ่ม) — reviewer ฟรี — **ไม่ต้องขอเพดานเพิ่ม** | OK |
| **L4 review** | **ห้าม** ใช้ `anthropic/claude-opus-5.5:batch` (L4) — ไม่ใช่งาน critical boundary | ห้าม |
| **Paid audit** | **ห้าม** เรียก Independent Auditor — paused ตาม AGENTS.md | ห้าม |
| **Tenant data protection** | **ไม่ต้องใส่** — standing fact ชี้ชัดว่า pre-G1 ไม่มีผู้เช่า ทดสอบบนฐานจริงได้ตรง | OK |

---

## 6) จุดที่ advisor คุมงานได้ (ตาม ADVISOR_MANDATE.md)

| จุดควบคุม | Advisor สามารถ... | ไม่สามารถ... |
|-----------|------------------|-------------|
| **สร้างการ์ด** | สั่ง PL สร้างการ์ด (ผ่านแล้ว T-071/072) | แก้ TASKS.md เอง |
| **สั่ง INTAKE** | สั่ง PL ให้ builder/ops เขียน INTAKE | เขียน INTAKE เอง |
| **สร้าง Issue** | สั่ง PL สร้าง `ai:ready` Issue | สร้าง Issue เอง / ตั้ง `ai:claimed` |
| **มอบหมาย reviewer** | สั่ง PL มอบหมาย reviewer คนละโมเดล | เป็น reviewer เอง |
| **อนุมัติ merge** | สั่ง PL merge (แทน Owner ขณะ Owner ไม่อยู่) | merge เอง / push โดยไม่ผ่าน PR |
| **Audit mandate** | ทุกคำสั่งต้องมีบันทึกใน ADVISOR_LOG.md (receiver เขียน) | ลบ/แก้ log |
| **Outside mandate** | **ห้าม** สั่งงานนอก Owner instruction / approved roadmap / existing card | — |

---

## 7) งบประมาณสรุป (ใช้ที่นั่ง OpenCode Go flat pool — ไม่จำกัด free)

| การ์ด | Builder/Ops | Reviewer | รวม | หมายเหตุ |
|------|-------------|----------|-----|---------|
| T-071 | ≤ $2 (GLM-5.3-flash บน Go pool) | $0 (muse-spark free) | ≤ $2 | ไม่ใช้ paid model |
| T-072 | ≤ $1 (mimo-v2.6-flash-free บน Go pool) | $0 (muse-spark free) | ≤ $1 | ไม่ใช้ paid model |
| T-074 | ≤ $3 (GLM-5.3-flash บน Go pool) | $0 (muse-spark free) | ≤ $3 | Code stream structure |
| T-075 | ≤ $2 (mimo-v2.6-flash-free บน Go pool) | $0 (muse-spark free) | ≤ $2 | n8n workflow stubs |
| T-076 | ≤ $2 (GLM-5.3-flash บน Go pool) | $0 (muse-spark free + security free) | ≤ $2 | DB schema via MCP |
| **รวม** | **≤ $10** | **$0** | **≤ $10** | ใน bucket Go pool ที่จ่ายแล้ว |

---

## 9) Tool Survey Results (2026-09-27) — บันทึกไว้ป้องกันการ์ดอ้าง "ไม่มีเครื่องมือ"

| Tool | สถานะ | รายละเอียด |
|------|--------|------------|
| **Supabase MCP** | ✅ Enabled | `supabase_execute_sql`, `supabase_apply_migration`, `supabase_list_tables` พร้อมใช้ — ต้องการ project ref 20-char (รอ Owner ให้) |
| **n8n MCP** | ✅ Enabled | `n8n_create_workflow_from_code`, `n8n_update_workflow`, `n8n_validate_workflow`, `search_nodes`, `get_workflow_sdk_reference` ทำงานได้ |
| **Render MCP** | ✅ Enabled | `list_workspaces` (workspace: `tea-da9ag7psrm7s73bnqf40`), `list_services` — ต้องส่ง `workspaceId` ทุกครั้ง |
| **OpenRouter MCP** | ✅ Enabled | `list_models` (458 models), `get_credits` ($55 total / $52.60 used) |
| **GitHub CLI** | ✅ Enabled | gh v2.101.0, authenticated as `supermansexy-png` |
| **OpenCode Go pool** | ✅ Primary | 43 model ids (verified 2026-09-26) — primary pool for dev team |
| **nippan-gateway** | ❌ Disabled | `"enabled": false` ใน opencode.json line 189 (ตั้งใจให้ปิด) |

**สรุป:** ไม่มี tool ที่ "ใช้ไม่ได้" จริง — ทุกตัวที่จำเป็นมีพร้อมใช้งานแล้ว การ์ดใดก็ตามห้ามอ้าง "ไม่มีเครื่องมือ" โดยไม่ตรวจสอบที่นี่ก่อน

---

## 8) สรุปขั้นตอนถัดไป (รอ Owner อนุมัติ)

1. **Owner อนุมัติแผนนี้** (DRAFT → APPROVED) — **DONE 2026-09-27**
2. **Owner ระบุ alert endpoint จริง** (T-071) + **เลือก restore target** (T-072) — **DONE: email supermanexy@gmail.com provided; restore target = separate schema/project**
3. **PL ส่ง HR (model-recruiter) เช็คความพร้อม** โมเดล Primary/Backup ต่อการ์ด → รายงานกลับ — **DONE 2026-09-27 (all Primary READY per ADVISOR_LOG.md)**
4. **PL แจ้ง Owner ความพร้อม** → รอ Owner อนุมัติเริ่มงานจริง — **DONE 2026-09-27 per ADVISOR_LOG.md**
5. **Owner อนุมัติ** → PL เรียก builder/ops ตามระเบียบ (START_PROMPT → INTAKE → Issue → branch → PR → CI → reviewer → merge → DELIVERY) — **READY TO EXECUTE**
6. **T-071 PR #92**: Adjust to new spec (Settings page + pluggable transports) → CI → Reviewer `opencode/muse-spark-1.3-contributor-free` → Merge
7. **T-072**: Execute via Supabase MCP (dump→restore→verify on schema `t072_restore`) → PR → Reviewer `opencode/muse-spark-1.3-contributor-free` → Merge
8. **T-074, T-075, T-076**: Issues #93, #94, #95 created with `ai:ready` — queued for ChatGPT (external assistant) per two-lane Git channel. Owner triggers when ready.
9. **T-073**: Awaiting Owner approval to start design (Issue creation + design work)

## 9) Reviewer Assignments (ต่อการ์ด ตาม MODEL_ROSTER.md T-065 table)

| การ์ด | Author (Model) | Reviewer L1–L3 (Different Model) | Security (if applicable) |
|-------|----------------|----------------------------------|---------------------------|
| T-071 | builder `opencode-go/glm-5.3-flash` | **Primary: `opencode/muse-spark-1.3-contributor-free`**<br>Backup 1: `openrouter/nvidia/nemotron-3.5-lightning:free`<br>Backup 2: `opencode-go/space-bunny-free` | — |
| T-072 | ops `opencode/mimo-v2.6-flash-free` | **Primary: `opencode/muse-spark-1.3-contributor-free`**<br>Backup 1: `openrouter/nvidia/nemotron-3.5-lightning:free`<br>Backup 2: `opencode-go/space-bunny-free` | — |
| T-074 | builder `opencode-go/glm-5.3-flash` | **Primary: `opencode/muse-spark-1.3-contributor-free`**<br>Backup 1: `openrouter/nvidia/nemotron-3.5-lightning:free`<br>Backup 2: `opencode-go/space-bunny-free` | — |
| T-075 | ops `opencode/mimo-v2.6-flash-free` | **Primary: `opencode/muse-spark-1.3-contributor-free`**<br>Backup 1: `openrouter/nvidia/nemotron-3.5-lightning:free`<br>Backup 2: `opencode-go/space-bunny-free` | — |
| T-076 | builder `opencode-go/glm-5.3-flash` | **Primary: `opencode/muse-spark-1.3-contributor-free`**<br>Backup 1: `openrouter/nvidia/nemotron-3.5-lightning:free`<br>Backup 2: `opencode-go/space-bunny-free` | **Primary: `openrouter/deepseek/deepseek-v4.1-flash`**<br>Backup 1: `opencode-go/qwen3.8-flash`<br>Backup 2: `openrouter/qwen/qwen3.8-flash` |

> Advisor ตรวจทานรอบสุดท้ายกับ PL แล้ว Advisor อนุมัติได้เลย (ไม่หยุดรอ Owner) — ตาม ADVISOR_MANDATE.md §6

---

**ไฟล์นี้เป็น APPROVED 2026-09-27 (Owner: "1 อนุมัติ")**  
Email endpoint provided: **supermanexy@gmail.com** — T-071 ready to execute per step 5  
New cards: **T-074, T-075, T-076** (Issues #93, #94, #95)  
OWNER_ACTION_QUEUE: `docs/warroom/OWNER_ACTION_QUEUE.md`  
Tool survey: All tools enabled (see §9 above)