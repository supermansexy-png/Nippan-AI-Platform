<!-- AUTO-HANDOFF:START -->
## Handoff ล่าสุด (auto) — 2026-09-25
**หัวข้อ:** Nippan PL — Protocol Reset 2026-09-25 (Bridge PARKED, RLS DONE, T-030/T-031 held)

Nippan PL reset to protocol (2026-09-25). DONE with evidence: PR #83 merged; RLS+role nippan_n8n live on Supabase (project xzxw...); migration efe21c7 committed (watcher excluded); cards T-RLS-01 (DONE retro) + T-BRIDGE-01 (PARKED/UNVERIFIED) + T-030 (READY) + T-031 (INTAKE) written in TASKS.md. Supreme rules 6 items recorded in SESSION_HANDOFF + decision-log; DEV_ERROR_LOG created; credit ~$1.76 — no paid subagent/build used. Pending: push 2 commits (approved), T-030 credential/test (blocked by Owner), T-031 bridge-AI goal/session/PAUSE/restart (missing), Bridge v1 choice (c) confirmed but not executed. Next: Owner picks 1 pending card → INTAKE → free HR (muse-spark + space-bunny) → approval → build/test with evidence → DELIVERY. Stop until card + approval.
<!-- AUTO-HANDOFF:END -->

## ▶ เริ่มต่อทันที (อัปเดต session 2 — 2026-09-25, ตรวจกับ repo/DB จริงแล้ว)
> ⚠️ handoff auto block ด้านล่าง **ล้าสมัยบางส่วน** — ใช้บล็อกนี้เป็นหลัก (session 2 ตรวจซ้ำทุกข้อ)

**สถานะที่ VERIFIED (session 2, read-only):**
- บอร์ด `TASKS.md` **ถูกเขียนทับ** จนการ์ด T-RLS-01/T-BRIDGE-01/T-031 หาย (ไม่เคย commit) → **ซ่อมแล้ว**: บอร์ดเหลือ 2 การ์ดเปิด (T-030 READY · T-031 BLOCKED/NEEDS_OWNER_INPUT) + ย้าย T-RLS-01 → `docs/archive/TASKS_DONE_ARCHIVE.md`, T-BRIDGE-01 → `docs/archive/TASKS_PARKED.md`
- **ไม่ต้อง push อะไรแล้ว** — `git log origin/dev-workspace..HEAD` ว่าง (HEAD = `973bc05`, PR #83 MERGED 2026-09-25T14:06:40Z)
- Supabase `xzxwakvsbdzkdybijbzs`: `nippan_n8n` rolcanlogin=true · `nippan_runtime` false · 7 ตาราง `lite_*` `rls=true force=true` (ยืนยันสด session 2)
- n8n: folder `Nippan Phase A` (`zClFVASPRDPnaeuQ`) มีอยู่และ **ว่าง** (0 workflow) · credential `6anMUYRLDYPduKY7` ("Postgres account") มีอยู่ · host `aws-0-ap-northeast-2.pooler.supabase.com:5432` · user `nippan_n8n.xzxwakvsbdzkdybijbzs` · db `postgres` · SSL=require + Ignore SSL Issues
- **credit ≈ $1.60** (session 2: 40 / 38.4023) → งานเสียเงินแทบทำไม่ได้

**ตัวบล็อกจริงของ T-030 (ไม่ใช่พี่แล้ว):**
- `n8n_create_workflow_from_code` / `n8n_update_workflow` / `n8n_execute_workflow` = `true` ใน `opencode.json` แล้ว แต่ **ยังไม่ขึ้นเป็น tool ในเซสชันที่รันอยู่** → สร้าง/รัน workflow ทดสอบไม่ได้ · ต้อง **ปิด-เปิดแอป opencode ใหม่ทั้งตัว** (กด `/new` ไม่พอ) · subagent ในเซสชันเดียวกันได้ tool ชุดเดียวกัน → ไม่ช่วย

**งานที่เหลือของ T-030 (หลัง restart):** สร้าง workflow ทดสอบใน Phase A → รัน 2 ชุด (scoped → คาด 1/1 · tenant อื่น → คาด 0) → insert+read แล้ว rollback → reviewer `space-bunny-free` ตรวจ → ปิด T-030 (ยังไม่ DONE จนมีผล)
**T-031 ต้องการจากพี่:** (1) เป้าหมาย bridge AI (2) session ที่อนุญาต (3) อนุมัติถอด `PAUSE` + restart · ยังไม่มี → ห้ามเรียก builder
**หมายเหตุ:** roster/agent files อัปเดตเป็น `opencode/muse-spark-1.3-contributor-free` แล้ว (Owner อนุมัติ 2026-09-25; ของเดิมไม่มีในระบบ) · Bridge watcher ยัง **PARKED/UNVERIFIED** (ไฟล์ untracked) ห้าม PL แก้เอง
**บทเรียน:** อย่าใช้ `write` ทับไฟล์บอร์ด/เอกสารที่ใช้ร่วมกัน ให้ `edit`/append และ commit การ์ดในเทิร์นเดียวกัน

# Session Handoff — 2026-09-25 (อัปเดต) — RESET TO PROTOCOL

อ่านไฟล์นี้ก่อนเริ่มงานในแชทใหม่ แล้วอ่านเพิ่มเฉพาะที่จำเป็น อย่าโหลดทั้ง repo

> **RESET 2026-09-25 (Owner)**: ยกเลิกวิธีการทำงานแบบ ad-hoc ทั้งหมด → กลับไปใช้ AI_OPERATING_PROTOCOL + TASK_CONTROL + กฎเหนือสุด (6 ข้อ) เท่านั้น · PL ห้ามแก้โค้ดเอง · เครดิต ~$1.76 → ห้ามใช้ paid subagent/build

## ⚖️ กฎเหนือสุด (Owner 2026-09-25) — ยึดเหนือเอกสาร/นโยบายอื่นทั้งหมด · ห้ามตีความเอง
> ถ้าพบว่ากฎอื่นขัดกับชุดนี้ → **หยุด และรายงานพี่** ห้ามเลือกเอง
> บันทึกเต็มอยู่ใน `docs/warroom/decision-log.md` (entry 2026-09-25 "Supreme operating rules")

1. **งานใหม่ทุกงาน**: การ์ดก่อน → INTAKE → ฝ่ายบุคคล (model-recruiter) เช็คความพร้อม → รายงานพี่ → **รออนุมัติ** → จึงเรียก builder
2. **PL ทำได้แค่ คิด/วางแผน/สั่ง/รายงาน** — ห้าม `write`/`edit` โค้ด (source/tests/migrations/config) ด้วยมือตัวเอง → งานลงมือต้องผ่าน builder/subagent เท่านั้น (เอกสาร dev-process PL แก้ได้)
3. **เรียก AI ตัวอื่นทุกครั้ง** ต้องใช้ template จาก `docs/warroom/START_PROMPT.md` (INTAKE ก่อน / DELIVERY พร้อมหลักฐานหลัง)
4. **ก่อนเริ่มงานที่เสียเงินทุกครั้ง** ต้องเช็คเครดิตก่อน + แจ้งพี่ทุกครั้ง (ล่าสุด 2026-09-25: OpenRouter เหลือ ≈ **$1.76** → งานเสียเงินแทบทำไม่ได้)
5. **1 repo = 1 แชทที่เขียนไฟล์ได้** — ห้ามเปิดแชทอื่นเขียนทับกัน (subagent/worker = เครื่องมือของแชทนี้, รันทีละงาน ห้ามทับไฟล์)
6. **ห้ามอ้าง DONE ถ้าไม่มีหลักฐานที่รันซ้ำได้** — ถ้าพิสูจน์ไม่ได้ให้เขียน **UNVERIFIED**

## วิธีเริ่มหน้าใหม่ (Owner ใช้แอป desktop)
- ระหว่างแชท: ใช้ `/compact` เพื่อย่อประวัติ (ลด token) — ทำงานต่อในแชทเดิมได้
- อยากเริ่มหน้าใหม่: กด `/new` แล้วพิมพ์ "อ่าน docs/project-memory/SESSION_HANDOFF.md แล้วทำงานต่อ"
- `/sessions` ใช้ไม่ได้ในแอป desktop (เป็นคำสั่งของ TUI) — อย่าให้ flow พึ่งคำสั่งนี้

## ✅ สมุดงานคำสั่ง Owner (canonical — ห้ามลบ · อัปเดต 2026-09-25)
> **กฎเหล็กสำหรับแชทใหม่**: (1) อ่านสมุดนี้ก่อนตอบ (2) รายงานสถานะทุกข้อพร้อมหลักฐานที่ "รันซ้ำได้" (3) ห้ามอ้าง DONE ถ้ารันคำสั่ง verify ไม่ผ่าน (4) ถ้าพิสูจน์ไม่ได้ ให้เขียน UNVERIFIED ห้ามเดา
> วิธีตรวจเองเร็วสุด: `git status --short` · `git grep -n owner_decision -- services/core/app` · `node scripts/headless_status.mjs runs/<dir>`

| # | คำสั่งพี่ | สถานะ | หลักฐาน / วิธีตรวจเอง |
|---|-----------|--------|------------------------|
| 1 | ทุกงานที่สั่ง → ส่ง headless รันจริง + เก็บข้อผิดพลาด | DONE (กลไก) | `AGENTS.md` §Background, `docs/warroom/DEV_ERROR_LOG.md`, `scripts/headless_run.mjs` + `headless_status.mjs` |
| 2 | ช่วงนี้ PL อนุมัติแทน (ข้อ 1,2,4,5,6,7,ค) — ข้อ 8/9 รอพี่ | ACTIVE | `docs/warroom/decision-log.md` entry 2026-09-25 |
| 3 | T-008 ให้ผ่าน frozen schema (เลิกเพิ่มคีย์ใหม่) | DONE | fix round 5 · verify: `git grep -n "payload\[.owner_decision.\]" -- services/core/app` = ว่าง · fast 146 passed · live PG 152 passed |
| 4 | T-009 พิสูจน์กับ DB จริง | DONE (local) | embedded PostgreSQL 16 = 152 passed/0 skipped; deployed Supabase preview ยังไม่รัน |
| 5 | T-029 hardening (schema-conformance test / zero-trace guard / metadata) | READY | การ์ดใน `TASKS.md` ยังไม่เริ่ม |
| 6 | T-026 RLS | DEFERRED | playbook ระบุ RLS จริงอยู่นอก Phase A → ต้อง NEEDS_OWNER_DECISION |
| 7 | commit เก็บงานทั้งหมด | DONE | commit บน `dev-workspace` (ยังไม่ push) |
| 8 | headless ใช้ได้จริง end-to-end + ปิด T-027/T-028 | DONE | run `runs/2026-09-25T01-19-57Z-e2e` · `python -m pytest -q` (services/core) = 138 passed, 6 skipped |
| 9 | L4 audit T-008 (ยืนยันช่องโหว่) | DONE | batch `batch-1790297068-g3TQCwDIpy1YJIJ1aO6p` ($0.03) |
| 10 | recon 2 งาน (contract-sweep / deploy-recon) | DONE | runs `...01-48-49Z-contract-sweep`, `...01-48-50Z-deploy-recon` (findings สรุปใน TASKS.md) |
| 11 | หลัง War Room → กลับ Phase A: T-001 hosting n8n+PostgreSQL | PARKED | ติด Docker — รอเรียกขึ้นมาทำ |

## แผนปัจจุบัน (authoritative)
- Phase A Market Test: `docs/warroom/STARTUP_PLAYBOOK.md` — n8n + PostgreSQL lite schema + OpenRouter
- `ROADMAP.md` = archived blueprint (อย่าเอามาทำ)
- War Room = track แยก ACTIVE (T-007/T-008/T-009)

## กฎที่ Owner ตั้งไว้ (บังคับ)
> ⚠️ กฎชุดนี้อยู่ **ใต้** "กฎเหนือสุด" ด้านบน — ถ้าขัดกันให้ใช้กฎเหนือสุด
1. **ทุกอย่างที่เสียเงิน (เรียก agent/โมเดล) ต้องขอ Owner อนุมัติก่อน** — ห้ามทำทันที
2. Owner เป็นผู้ตัดสินใจสุดท้าย (พี่เชษ)
3. รายงานสั้น เน้นเนื้อ ๆ (Owner สั่งลดความยาว ~80%)
4. Anti-redundancy: reviewer/security ต้องคนละโมเดลกับ builder และ reviewer ≠ security
5. ห้ามแตะ production `Ai-bot-Nippan`
6. งาน L2/L3 ต้องมี reviewer ตรวจ + Owner อนุมัติก่อน DONE
7. commit/amend/push เฉพาะเมื่อ Owner สั่ง ("อนุมัติ"/"อนุญาต")
8. งานเสียเงินที่ไม่รีบ → ส่ง Batch API (`:batch`) เสมอ (ถูกกว่า ~40–60%)
9. **งานอ่านเยอะ/ยาว → ส่งเข้า headless queue แล้วห้ามรอในแชท**; 1 งาน = 1 prompt ล็อกสโคป + ระบุ `--agent`/`--model`; งานแก้โค้ดรันบน branch + reviewer คนละโมเดลก่อน merge; ห้ามรันงานที่แตะไฟล์เดียวกันพร้อมกัน; ห้ามใส่ secret เข้าโมเดลฟรี; `runs/` gitignored → สรุปผลลงการ์ดทุกครั้ง (รายละเอียด: `AGENTS.md` + `docs/warroom/DEV_WORKING_GUIDE.md`)

## คำสั่ง Owner ช่วงนี้ (TEMP — 2026-09-25 · ย้อนกลับเมื่อพี่สั่ง "กลับไปกติกาเดิม")
- **ทุกงานที่ได้รับ → ส่งขึ้น headless รันจริงเพื่อทดสอบว่าใช้ได้ และเก็บข้อผิดพลาดที่พบ** (ลงการ์ด + `docs/warroom/DEV_ERROR_LOG.md`)
- **ช่วงนี้ พี่มอบอำนาจให้ PL ตรวจ/อนุมัติแทนทั้งหมด** — ถ้าตัวไหนไม่ผ่าน ให้หา "คนแก้" ให้ผ่านเอง โดยไม่ละเมิด/ไม่เกินขอบเขตงาน
- **PL อนุมัติแทนได้**: ใช้โมเดลตาม roster (ทำงานเฉพาะหน้าที่ + มีหลักฐาน) · ปิดงาน L1/L2/L3 · commit/push · protected docs ฝั่ง dev-process · ใช้ secret ตามงาน
  - ข้อ 1 = ใช้โมเดลที่ roster กำหนดหน้าที่ไว้แล้วได้ตามปกติ (ห้ามงานนอกเรื่อง + ต้องเก็บหลักฐาน)
  - ข้อ 2 = เกินเพดานราคา → ห้ามอนุมัติ ให้หาทางใช้โมเดลฟรีแทน
  - ข้อ 3 = Independent paid Auditor → รอพี่
  - ข้อ 4 = ราคา/นโยบายต้นทุน → ห้ามแก้เอง
  - ข้อ 5/6 = ปิดงาน L2/L3 → PL อนุมัติได้
  - ข้อ 7 = commit/push → PL อนุมัติได้
  - **ข้อ 8 (merge/deploy ขึ้น preview) → รอพี่** · **ข้อ 9 (architecture) → รอพี่**
  - ข้อ ค = protected docs ฝั่ง dev-process → PL อนุมัติได้ (ยกเว้น `PRICING_V1` / `PDPA_COMPLIANCE`)
  - ข้อ ง = production/security → ใช้ตอนระบบรันแล้ว ไม่เกี่ยวช่วงนี้ · ข้อ จ = ห้ามเปลี่ยนวิธีการทำงาน ทำตามระเบียบเดิม
- **ทุกการกระทำต้องค้นย้อนกลับได้** (การ์ด + หลักฐาน + `decision-log.md` + `DEV_ERROR_LOG.md`)

## ทีมโมเดล (roster ปัจจุบัน — `docs/product/MODEL_ROSTER.md`)
| Role | Primary | Backup |
|------|---------|--------|
| project-lead | `openrouter/deepseek/deepseek-v4.1-flash` (paid, คิด/วางแผนเท่านั้น) | nemotron-3.5-lightning |
| builder | `z-ai/glm-5.3-flash` (paid, Owner-locked — ห้ามสลับ) | nvidia/nemotron-3.5-lightning |
| reviewer L1/L2/L3 | `opencode/space-bunny-free` (zero-retention) | thinkingmachines/inkling-small:free |
| reviewer L4 (ความแม่นสูง) | `anthropic/claude-opus-5.5:batch` (paid, Owner-selected) | — |
| security L1/L2/L3 | `openrouter/nex-agi/nex-n2.5-mini:free` (≠ reviewer) | opencode/muse-spark-1.3-contributor-free |
| ops | `opencode/muse-spark-1.3-contributor-free` | — |
| researcher | `opencode/muse-spark-1.3-contributor-free` | — |
| assistant | `opencode/nemotron-3-ultra-free` | opencode/muse-spark-1.3-contributor-free |
| model-recruiter (HR) | `openai/gpt-6-luna` | tencent/hy3-preview |

- L4 เป็น **review tier** ไม่ใช่ risk level ใน TASK_CONTROL §3 (protected — มีแค่ L1–L3)
- Agent files ผูก `model:` ใน frontmatter แล้ว (ต้อง restart opencode เมื่อแก้)
- โมเดลฟรี Zen ใช้ได้เฉพาะใน opencode (ยิง HTTP ตรงได้ 403); ส่วนใหญ่ log/train → ห้ามใส่ secret

## สถานะงาน (TASKS.md + docs/archive/TASKS_DONE_ARCHIVE.md)
- **บอร์ด 2026-09-25 (ทำความสะอาดรอบสอง)**: เหลือ **3 การ์ดเปิด** — T-008, T-009, T-026 (ใต้เพดาน 5); T-024/T-025/T-003 ย้ายเข้า `TASKS_DONE_ARCHIVE.md`; T-012/T-001/T-007 ย้ายไป `TASKS_PARKED.md`
- **T-025 เสร็จ 2026-09-25**: สรุป "ฟรีโมเดลทดแทน" รวมสองเจ้า (Zen T-021 + OpenRouter T-024) → `docs/product/FREE_MODEL_FALLBACK_GUIDE.md` — จัดอันดับรายตำแหน่ง (best→worst) + ตารางตัวสำรอง 1st/2nd/3rd ต่อ role + รายชื่อห้ามใช้ (พลาด isolation bug / ตอบแม่นยำผิด) — record only ไม่แตะ roster
- เปิดอยู่บนบอร์ด: T-008, T-009 (รอพี่เลือก revision ตรวจรับ), T-026 (RLS follow-up จาก T-003)
- **T-003 = DONE (2026-09-25, Owner อนุมัติปิดด้วย option ก)**: 3 tools ทำโดยโมเดลฟรีใน `services/dev/tools/` (data_access, usage_tracker, monitor_log) + 37 เทสต์ผ่าน; named-query registry ปิดช่องส่ง SQL ดิบ; residual (การเช็คตอน register เป็น text) ยอมรับสำหรับ Phase A → ตามเก็บด้วย T-026
- **T-026 = READY**: เปิด PostgreSQL RLS จริง (L3, แตะ protected doc `docs/data/LITE_SCHEMA_V1.md`) — รอ Owner จัดคิว
- **T-024 เสร็จ 2026-09-25 (เซสชันนี้)**: ตรวจฟรีโมเดล OpenRouter `:free` 12 ตัว (ทุกตัว endpoint-VERIFIED $0/M) → ได้คะแนน 10 ตัว: nex-n2.5-mini 5/5 + nex-n2.5-pro 5/5 ดีสุด (แต่ n2.5-pro uptime 90% / p99 ~3นาที), north-mini-code + qwen3.8-27b 4/5 (พลาด hr precision), สายโค้ด: inkling-small เก่งสุด (builder ✅ + reviewer 2/2), laguna-s/xs + nemotron-3-super พลาด isolation bug; gemma ×2 rate-limited ไม่มีคะแนน; 6 ตัวแรกโดน guardrail ฟรีโมเดลของ OpenRouter (พี่เปิดให้) — **RECORD ONLY ไม่เปลี่ยน roster**; reviewer (space-bunny-free) ตรวจตารางคะแนน ACCEPTED
- **ระวัง**: OpenRouter workspace `opencode-new` มี guardrail บล็อก free models ("Free model training violation") — ถ้าจะทดสอบ `:free` อีก ต้องเช็คการตั้งค่า workspace ก่อน (รอบนี้พี่เปิดให้ชั่วคราว)
- **T-008/T-009 = BLOCKED NEEDS_OWNER_DECISION**: ตรวจโค้ดแล้ว เจอ (ก) โค้ดปัจจุบันมี route เรียก `run_next_turn` แล้ว (ขัดกับหลักฐาน deploy เดิม) (ข) เพดาน audit 90% — รับ D ได้ทีละ 1 ตัว; รับ 2 ตัวต้องเปิด Independent Audit (ซึ่งพี่พักไว้)
- DONE ล่าสุด: T-021 (handoff plugin — พี่ยืนยัน), T-017..T-023 (ย้ายเข้า archive แล้ว)
- PARTIAL: T-001 (ติด Docker), T-007 (รอ remote access)
- T-004 (legal) ถูก Owner ตัดออกจากแผน dev-time
- **ค้างรอพี่**: revision ที่จะใช้ตรวจรับ D-02/D-03 (เพดาน audit 90% — รับได้ทีละ 1 ตัว)
- **ทีมโมเดลเปลี่ยน 2026-09-25 (option A, restart แล้วมีผลจริง)**: assistant=`opencode/nemotron-3-ultra-free`; reviewer=`opencode/space-bunny-free`; security=`openrouter/nex-agi/nex-n2.5-mini:free`; ops/researcher=`opencode/muse-spark-1.3-contributor-free`; builder=`z-ai/glm-5.3-flash` (Owner-locked 2026-09-25) — เหตุผล/หลักฐานอยู่ใน `MODEL_ROSTER.md` ส่วน "Team update 2026-09-25"
- **config**: `opencode.json` pin explore/general เป็นฟรี + ให้ assistant/ops/researcher `edit: allow`; `small_model` = muse-spark-1.2
- **บทเรียนโมเดลฟรี**: `big-pickle` รายงาน False DONE (T-003 WS2 → ai-scorecard); `ling-3.0` เชื่อมต่อไม่ได้; โมเดลใหม่ (space-bunny, nex-n2.5-mini) กินสเต็ปจนไม่สรุป → ต้องล็อกสโคปใน prompt

## ค่าใช้จ่าย (วัดจาก opencode DB)
- 24 ชม.ล่าสุด ≈ $2.71 ; PL session เดียว $1.20 (อ่าน context ซ้ำ) — ตัวเลขก่อนมาตรการลดต้นทุน
- Account OpenRouter: ใช้ $28.18 / $30 (เหลือ $1.82) — **ตัวเลข ณ 2026-09-25 ยังไม่เช็คใหม่**
- มาตรการลดต้นทุนที่ใช้อยู่: `/compact` + เปิดหน้าใหม่ต่อเมื่อจำเป็น / ลด docs ที่อ่านทุก turn / review L1–L2 ใช้โมเดลฟรี / batch / provider sort=price

## Incident ล่าสุดที่ต้องรู้
- **กฎ Context Discipline (Owner อนุมัติ 2026-09-25)** อยู่ใน `AGENTS.md` — สิ่งที่เข้าแชทหลักต้องเล็ก, งานอ่านเยอะให้ทำใน subagent แล้วรับกลับแค่สรุป ≤15 บรรทัด, ห้ามดึง output ดิบก้อนใหญ่เข้าแชท, ใช้ `/compact` หรือเปิดแชทใหม่เมื่องานจบ, ล็อกสโคป prompt ของ subagent ให้แคบ
- qwen3.7-flash ถูกปลดจาก PL + HR (False DONE) — `docs/warroom/ai-scorecard.md` (ภายหลังกลับมาเป็น builder ตาม T-023)
- ระบบเคยไม่ผูก model ใน agent files ทำให้ roster ไม่ถูกบังคับใช้ — แก้แล้ว
- TASKS.md มีเลขการ์ด **T-021 ซ้ำ 2 ใบ** (handoff plugin + Zen test) — รอ renumber