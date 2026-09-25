<!-- AUTO-HANDOFF:START -->
## Handoff ล่าสุด (auto) — 2026-09-25
**หัวข้อ:** War Room เสร็จแล้ว — T-008 + T-009 DONE (owner decision บันทึกได้จริง + live PostgreSQL 152 passed); commit แล้วบน dev-workspace

## เสร็จแล้ว (หลักฐานสั้น)
- **(ข) Headless runner ใช้ได้จริง end-to-end**: `.opencode/agents/worker.md` (primary, ไม่ hardcode model), `scripts/headless_run.mjs` (รัน `opencode run` detached, `--model` REQUIRED, คืน run dir ทันที ~80ms), `scripts/headless_status.mjs` (ดึง "worker answer" + สถานะ). พิสูจน์ E2E ด้วย `opencode/space-bunny-free` → cost $0, ไม่มี fallback warning, ไม่บล็อกแชท. `runs/` gitignored, `.env` gitignored (มี OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true แต่ flag นี้ไม่เปลี่ยน Task tool ของแอป — ใช้ CLI ผ่าน Node แทน)
- **(ค) OpenRouter free ใช้ได้** (พี่ยกเลิก guardrail แล้ว) — ทดสอบ `nex-agi/nex-n2.5-mini:free` ตอบ FREE_OK ($0)
- **ส่งรีวิว T-008 ผ่าน Batch** โมเดล `anthropic/claude-opus-5.5:batch` → batch id `batch-1790297068-g3TQCwDIpy1YJIJ1aO6p` **ยังไม่เช็คผล**
- **(ง) T-027 + T-028 ปิดการ์ดแล้ว (DONE, L1, 2026-09-25)**: T-027 — พิสูจน์ `.cmd/.bat` shell fallback จริง (PATH → shim `.cmd`, args quote ถูก, exit 0), E2E `runs/2026-09-25T01-19-57Z-e2e` (worker, $0); finding: env flag `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS` **ไม่ได้** เปิด background Task tool ในแอป — กลไกจริงคือ Node wrapper. T-028 — ใช้เอกสาร T-024/T-021 ที่มีอยู่ยืนยัน (free call + caveats + จุดใช้งานผ่าน headless). ทั้งสองย้ายเข้า `docs/archive/TASKS_DONE_ARCHIVE.md` แล้ว

## สถานะ/การตัดสินใจล่าสุด
- **แบน `qwen3.7-flash` ทุกแผนกถาวร** (scorecard + decision-log); **builder = `z-ai/glm-5.3-flash`**; **L4 = `anthropic/claude-opus-5.5:batch`**; assistant/ops/researcher = Zen free; reviewer=space-bunny-free, security=nex-n2.5-mini:free
- **Audit gates ยกเลิกทั้งหมด** (Owner: ออดิดใหญ่ครั้งเดียวตอนจบ) — decision-log 2026-09-25
- **Permission deny-by-default** เปิดใช้แล้ว: bash ที่แตะ `.opencode/agents/**` ถูกบล็อก, force-push/rm -rf ฯลฯ บล็อก; reviewer/security ยัง `edit: deny`
- **T-008 (D-02) DONE**: ลบคีย์ `owner_decision` ที่ผิด frozen schema; owner decision ใช้ฟิลด์เดิม (`content_text`/`content_reference` + `message_type=OWNER_DECISION` + top-level `participant_id`=acting owner); persistence เขียน `public.project_room_decisions` ใน transaction เดียว + fail-closed; owner principal ที่ไม่ใช่ UUID (`preview-owner`) ทำงานได้ (messages.participant_id=NULL เฉพาะ owner event); transport `_request_is_loopback` ตรวจ socket peer จริง → 403 `war_room_preview_loopback_only`; reviewer space-bunny ACCEPT + security muse-spark ACCEPT
- **T-009 (D-03) DONE**: live proof — embedded PostgreSQL 16 (pgserver, apply 7 migrations) = **152 passed, 0 skipped** (6 integration tests ที่เคย skip รันผ่านหมด); residual: deployed Supabase preview ไม่ได้รัน (ไม่มี DSN)
- **Team update ใช้เป็นชุดจริงแล้ว**: builder=`z-ai/glm-5.3-flash` (ล็อก ห้ามสลับ), reviewer L1–L3=space-bunny-free, security L1–L3=nex-n2.5-mini:free, ops/researcher=muse-spark, assistant=nemotron-3-ultra-free, L4=claude-opus-5.5:batch
- **commit แล้ว** บน `dev-workspace` (ยังไม่ push)

## ค้างอยู่
- **board archival**: T-008/T-009 ตั้ง Status DONE แล้ว รอย้ายเข้า `docs/archive/TASKS_DONE_ARCHIVE.md`
- **deployed preview** (item 8, Owner เท่านั้น): ยังไม่ได้รัน War Room บน Supabase preview จริง
- T-026 (RLS, L3) DEFERRED; T-029 hardening READY

## ขั้นถัดไปที่แนะนำ
1. ย้าย T-008/T-009 เข้า archive (housekeeping)
2. ถ้าพี่ต้องการเห็น War Room ทำงานจริงบน preview → ต้อง deploy (item 8, รอพี่)
3. กลับ Phase A: T-001 hosting n8n+PostgreSQL (PARKED, ติด Docker)
<!-- AUTO-HANDOFF:END -->

# Session Handoff — 2026-09-25 (อัปเดต)

อ่านไฟล์นี้ก่อนเริ่มงานในแชทใหม่ แล้วอ่านเพิ่มเฉพาะที่จำเป็น อย่าโหลดทั้ง repo

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
| security L1/L2/L3 | `openrouter/nex-agi/nex-n2.5-mini:free` (≠ reviewer) | opencode/muse-spark-1.2-contributor-free |
| ops | `opencode/muse-spark-1.2-contributor-free` | — |
| researcher | `opencode/muse-spark-1.2-contributor-free` | — |
| assistant | `opencode/nemotron-3-ultra-free` | opencode/muse-spark-1.2-contributor-free |
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
- **ทีมโมเดลเปลี่ยน 2026-09-25 (option A, restart แล้วมีผลจริง)**: assistant=`opencode/nemotron-3-ultra-free`; reviewer=`opencode/space-bunny-free`; security=`openrouter/nex-agi/nex-n2.5-mini:free`; ops/researcher=`opencode/muse-spark-1.2-contributor-free`; builder=`z-ai/glm-5.3-flash` (Owner-locked 2026-09-25) — เหตุผล/หลักฐานอยู่ใน `MODEL_ROSTER.md` ส่วน "Team update 2026-09-25"
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