<!-- AUTO-HANDOFF:START -->
## Handoff ล่าสุด (auto) — 2026-09-26
**หัวข้อ:** Nippan: team on OpenCode Go + ที่ปรึกษาวางแผน (advisor) + ระบบตรวจสอบ

## งานรอบนี้ (session 4 — 2026-09-26) ทำอะไรเสร็จแล้ว

**ทุกอย่าง commit + push แล้ว · working tree สะอาด**
- `3d92735` feat(skills): advisor skills · `01c8f52` docs(memory): handoff · `a4ce52d` feat(team): Go + advisor
- push ขึ้น `origin/dev-workspace` แล้ว (ไม่มี commit ค้าง)

### 1. ย้ายทีมทั้งชุดไป OpenCode Go (การ์ด T-035 / T-037)
- `opencode-go/<id>` = **คลังหลัก** (พี่จ่าย $10/เดือนแล้ว) · OpenRouter + OpenCode Zen = สำรอง
- pin ปัจจุบัน (ตรงกับไฟล์ agent จริงทั้งหมด):
  - project-lead `openrouter/deepseek/deepseek-v4.1-flash` (**T-042, 2026-09-26 — Owner order** "เปลี่ยน pl เป็น deepseek-v4.1"; ฝั่ง Go ยังติด HTTP 400 "requires Global regions" จึงใช้ endpoint OpenRouter ของโมเดลเดียวกัน) · backup `opencode-go/mimo-v2.6-pro`
  - advisor `opencode-go/mimo-v2.6-pro` · builder `opencode-go/glm-5.3-flash` (Owner lock เดิม **ยกเลิกแล้ว**)
  - reviewer L1–L3 `opencode-go/space-bunny-free` · L4 `anthropic/claude-opus-5.5:batch`
  - ops `opencode-go/mimo-v2.6-flash` · HR `opencode-go/gpt-6-luna`
  - security `openrouter/nex-agi/nex-n2.5-mini:free` (Go ไม่มีตัวแทน) · researcher `opencode/nemotron-3.5-lightning-free` · assistant `opencode/nemotron-3-ultra-free`
- `opencode.json`: global model = `opencode-go/mimo-v2.6-pro`, small_model = `opencode-go/mimo-v2.6-flash`, default_agent = project-lead, subagent_depth = 2 · agent override ของ project-lead = `openrouter/deepseek/deepseek-v4.1-flash` (T-042)
- ทดสอบสดผ่าน: glm-5.3-flash, space-bunny-free, mimo-v2.6-flash, mimo-v2.6-pro, kimi-k3 · ติด region: deepseek-* ทั้งตระกูล
- HR เขียนคำสั่งใหม่แล้วให้สรรหาจากคลัง Go เป็นหลัก

### 1b. แก้ช่องทาง "ที่ปรึกษา → PL" + เปลี่ยนโมเดล PL (การ์ด T-041 / T-042) — 2026-09-26
- **T-041:** ที่ปรึกษาคุยกับ PL ไม่ได้เลย เพราะ Task tool เรียกได้แค่ `subagent` แต่ทั้งคู่เป็น `primary` → แก้ `project-lead` เป็น `mode: all` และเพิ่ม `"subagent_depth": 2` (ค่า default = 1 ทำให้ PL สั่ง builder/reviewer ต่อไม่ได้) · reviewer คนละโมเดล verdict = ACCEPT-WITH-FINDINGS ทั้งสองรอบ
- **T-042:** PL ย้ายไป `openrouter/deepseek/deepseek-v4.1-flash` (backup = `opencode-go/mimo-v2.6-pro`) — เครดิต OpenRouter เหลือ **≈ $4.44** และ **ไม่มี fallback อัตโนมัติ** ถ้าเครดิตหมด PL หยุด
- **ยังไม่พิสูจน์:** `mode: all` ผ่านเงื่อนไข `default_agent` ไหม — ถ้าไม่ผ่าน opencode จะถอยไปใช้ `build` เงียบ ๆ → **ต้องรีสตาร์ทแล้วเช็คว่า agent เริ่มต้นยังเป็น project-lead**
- **T-043 (Owner อนุมัติ + ทดสอบสดผ่าน 2026-09-26):** ล็อกสิทธิ์ PL — ชั้น 1 `edit` allowlist (`TASKS.md`, `docs/**`, `runs/**`, `README*`, `AGENTS.md`, `WORKING_POLICY.md`, `PROJECT_STATE.md`, `ROADMAP.md`; นอกนั้น deny) + ชั้น 2 deny 11 คำสั่ง bash ที่เขียนไฟล์ · **พิสูจน์สดแล้ว:** เขียน `.opencode/**` ถูกปฏิเสธ, เขียน `runs/**` ได้, `Set-Content` ถูกปฏิเสธ · หมายเหตุ: PL ลบไฟล์ด้วย `Remove-Item` ไม่ได้แล้ว (ใช้ `node -e fs.rmSync` แทน) · ย้ำ: กันไม่ได้ 100% (redirect / `git checkout <branch> -- <path>` / `node -e` ยังเขียนได้)

### 2. ตำแหน่งใหม่ "ที่ปรึกษาวางแผน" (advisor) + ระบบตรวจสอบ (การ์ด T-038 / T-039 / T-040)
- ลำดับสั่งงาน: `Owner → advisor → Project Lead → specialist` · สั่ง agent ได้ทุกตัว · อนุมัติ/commit/push แทนพี่ได้ตอนพี่ไม่อยู่
- **แก้ไฟล์เองไม่ได้** (edit deny) · shell ได้แค่ git · **สั่งงานนอกระเบียบไม่ได้** · **ห้ามอนุมัติเอกสาร protected** (conflict of interest)
- ระบบตรวจสอบ: `docs/warroom/ADVISOR_MANDATE.md` (protected) + `docs/warroom/ADVISOR_LOG.md` (append-only)
  - **ผู้รับคำสั่งเป็นคนบันทึก ไม่ใช่ที่ปรึกษา** · audit ทุกการ์ดโดยโมเดลอื่น (≠ mimo-v2.6-pro) · verdict 3 ค่า
  - audit รอบแรกผ่าน: `opencode-go/kimi-k3` → WITHIN-MANDATE-WITH-FINDINGS
  - บันทึกคำสั่งของพี่รอบนี้ = entry T-038 ใน ADVISOR_LOG แล้ว
- สกิล 2 ตัว (`.opencode/skills/`): `advisor-work-order` (แปลงคำสั่งพี่เป็นใบสั่งงาน + เทมเพลตบันทึก) และ `advisor-mandate-audit` (ตรวจ A1–A5)
- กฎซ่อมแล้ว: `AGENTS.md`, `START_PROMPT.md`, `AI_OPERATING_PROTOCOL.md`, `TASK_CONTROL.md`, `DEV_WORKING_GUIDE.md`, `FREE_MODEL_FALLBACK_GUIDE.md`, `MODEL_ROSTER.md`, `CURRENT_STATE.md` — ล้างโมเดลตาย (`big-pickle`, `ling-3.0`, `mimo-v2.6-flash-free`) และ pre-Go facts หมดแล้ว

## พี่ต้องทำ (ค้างอยู่)
1. **ปิดเปิดแอป opencode** → agent "ที่ปรึกษาวางแผน" + สกิลทั้ง 2 จะโผล่ (config commit แล้วแต่ต้องรี)
2. ถ้าต้องการใช้ DeepSeek บน Go → ตั้ง Privacy ของ workspace (https://opencode.ai/auth) เป็น **Global regions** — *ยังยืนยันจากเอกสารสาธารณะไม่ได้ว่าปุ่มชื่ออะไรแน่ (UNVERIFIED)* ไม่ตั้งก็ไม่กระทบงาน
3. หลังรี: ลองเรียก HR อีกที และ **ทดสอบสกิล** (ให้ที่ปรึกษาเรียก `advisor-work-order`) เพื่อยืนยันว่าค้นเจอจริง

## งานเปิดค้าง
- **T-034b เหลือ slice 2b**: แก้วาระ (agenda CRUD) จากหน้าเว็บ War Room — ยัง read-only
- **T-032**: รอพี่ตอบ 4 ข้อฝั่ง Codex + ตัดสินใจเปิด protection ของ `dev-workspace`
- **housekeeping**: T-034a เป็น DONE แล้วยังอยู่บนบอร์ด → ควรย้ายเข้า `docs/archive/TASKS_DONE_ARCHIVE.md` (บอร์ดเกิน cap 5)
- **เครดิต OpenRouter ≈ $1.19** → งานเสียเงินให้ใช้ Go/โมเดลฟรีแทน
- ยังไม่แตะ: `docs/warroom/ROLES.md` (เป็นนิเวศ runtime ไม่ใช่ทีม dev)

## บทเรียนเครื่องมือ (กันเสียเวลารอบหน้า)
- `headless_run.mjs --agent <subagent>` **silently fallback ไป default agent** (ได้ edit permission โดยไม่ตั้งใจ) → ใช้ `--agent worker` เท่านั้นสำหรับงาน headless
- prompt ยาว ๆ ถูกตัดที่ ~600 ตัวอักษรผ่าน powershell wrapper → ใส่ brief ลง `runs/briefs/<card>.md` แล้ว `--prompt` เป็น pointer ประโยคสั้น
- โมเดล reasoning (glm-5.3-flash, mimo, kimi บนงานอ่านเยอะ) **หมดโควตา reasoning แล้วตายกลางทาง** (reason: length) — งานอ่านไฟล์เยอะให้แบ่งเป็นงานเล็ก หรือ PL ทำเองถ้าเป็น dev-process doc
- `git diff -- <paths>` **โดน permission engine ตีความผิด** → ใช้ `git diff <paths>` (ไม่มี `--`)
- ชื่อโมเดลต้องมี prefix เสมอ: `opencode-go/`, `opencode/`, `openrouter/author/` — ไม่ใส่จะขึ้น `Unexpected server error` หลอก ๆ
- demo agent skill: สกิลอยู่ที่ `.opencode/skills/<name>/SKILL.md` (`name` ต้องตรงชื่อโฟลเดอร์, lowercase-hyphen)
<!-- AUTO-HANDOFF:END -->

> ## ▶ สถานะล่าสุด 2026-09-26 (session 4) — ยึดบล็อกนี้ก่อนบล็อกอื่นทั้งหมด
>
> **commit:** `a4ce52d` — "feat(team): move the dev team onto OpenCode Go, add the advisor role and its oversight"
> (24 ไฟล์) · working tree สะอาด
>
> **ทีมย้ายไป OpenCode Go แล้ว (การ์ด T-035/T-037)** — `opencode-go/<id>` = คลังหลัก, OpenRouter/Zen = สำรอง
> - project-lead `opencode-go/mimo-v2.6-pro` (เดิมตั้ง `deepseek-v4.1-flash` แต่ **probe แล้วได้ HTTP 400 "requires Global
>   regions"** จึงสลับ)
> - builder `opencode-go/glm-5.3-flash` (Owner lock เดิม **ถูกยกเลิก** 2026-09-26)
> - reviewer L1–L3 `opencode-go/space-bunny-free` · ops `opencode-go/mimo-v2.6-flash` · HR `opencode-go/gpt-6-luna`
> - security `openrouter/nex-agi/nex-n2.5-mini:free` (Go ไม่มีตัวแทน) · researcher/assistant = Zen ฟรีเดิม
> - `opencode.json`: model = `opencode-go/mimo-v2.6-pro`, small_model = `opencode-go/mimo-v2.6-flash`
>
> **ตำแหน่งใหม่ "ที่ปรึกษาวางแผน" (advisor) — การ์ด T-038/T-039**
> - ลำดับสั่งงาน: `Owner → advisor → Project Lead → specialist` · สั่ง agent ได้ทุกตัว
> - อนุมัติ/commit แทนพี่ได้ตอนพี่ไม่อยู่ · **แก้ไฟล์เองไม่ได้** · สั่งงานนอกระเบียบไม่ได้
> - **ห้ามอนุมัติเอกสาร protected** (เป็น conflict of interest — ตัวมันเองคือสิ่งที่ถูกกำกับ)
> - ระบบตรวจสอบ: `docs/warroom/ADVISOR_MANDATE.md` + `docs/warroom/ADVISOR_LOG.md`
>   (ผู้รับคำสั่งเป็นคนบันทึก ไม่ใช่ที่ปรึกษา · audit โดยโมเดลอื่นทุกการ์ด · verdict 3 ค่า · ออกนอกอำนาจ = หยุด + แจ้งพี่ + ลง scorecard)
> - audit รอบแรก: `opencode-go/kimi-k3` → WITHIN-MANDATE-WITH-FINDINGS (finding แก้แล้ว)
>
> **พี่ต้องทำ:** (1) ตั้งค่า Privacy ของ workspace OpenCode เป็น **Global regions** ถ้าต้องการใช้โมเดลตระกูล DeepSeek บน Go
> (2) **ปิดเปิดแอป opencode** เพื่อให้ agent ใหม่และ config มีผล
>
> **งานเปิดค้าง:** T-034b เหลือ slice 2b (แก้วาระจากหน้าเว็บ) · T-032 รอพี่ตอบ 4 ข้อ · housekeeping: T-034a เป็น DONE แล้วยังอยู่บนบอร์ด
> (ควรย้ายเข้า `docs/archive/TASKS_DONE_ARCHIVE.md`) · เครดิต OpenRouter ≈ $1.19 (งานเสียเงินให้ใช้ Go/ฟรีแทน)

> ## ▶ เริ่มที่แชทใหม่ — สถานะล่าสุด 2026-09-26 (ยึดบล็อกนี้; ทุกอย่างด้านล่างเป็นประวัติก่อนวันนี้)
>
> **บอร์ด:** T-030 = **DONE** (พี่เชษอนุมัติ 2026-09-26) · T-032 = READY รอ INTAKE · T-031 = DROPPED (record รอ move เข้า `TASKS_PARKED.md`)
> **commit ล่าสุด:** `5a93eff` (ปิด T-030 + หลักฐาน + re-pin ทีม + กฎโฟลเดอร์) — **ยังไม่ push** · working tree สะอาด
>
> **T-030 หลักฐาน (รันจริง ไม่ใช่การตั้งค่า):** workflows `CVhNSU5pjpGgzquB` (v1) + `eohtRWY8YEvEuS7n` (v2) ใน folder
> `Nippan Phase A` (`zClFVASPRDPnaeuQ`, project `hmhfL4HtmuUod5jL`) · executions `5842`/`5844` → `current_user = nippan_n8n`,
> tenant A เห็นของตัวเอง = 1, tenant B มองไม่เห็น = 0, tenant B เขียนของตัวเองได้ = 1 (positive control), เขียนข้าม tenant
> ถูก RLS บล็อก (42501) · `lite_tenants`/`lite_bots` = 0 แถวหลัง rollback · reviewer `opencode/space-bunny-free` pass 1 →
> pass 2 = ACCEPT-WITH-FINDINGS (เค้าดึง execution `5844` ดิบจาก n8n มาเทียบเอง) · เอกสาร + SQL จริง: `docs/n8n/T-030-execution-evidence.md`
>
> **กฎที่พี่ตั้ง 2026-09-26 (บันทึกใน `docs/warroom/decision-log.md` entry "2026-09-26"):**
> 1. n8n write/read **เฉพาะในโฟลเดอร์ `Nippan Phase A`** — n8n ไม่รองรับการจำกัดสิทธิ์ MCP ต่อโฟลเดอร์/ต่อ client (ยืนยันจากเอกสาร n8n)
>    จึงบังคับเป็น **process rule**: expose/รันได้เฉพาะ workflow ในโฟลเดอร์นี้, ปิด auto-expose, ตรวจรายการ exposed เป็นระยะ
> 2. **`Ignore SSL Issues` ของ credential `6anMUYRLDYPduKY7` คงไว้ ON (พี่เห็นชอบ 2026-09-26)** — pooler ใช้ CA ของ Supabase เอง
>    (issuer `Supabase Intermediate 2021 CA` → `Supabase Root 2021 CA`); ทดสอบ TLS เองแล้วได้ `SELF_SIGNED_CERT_IN_CHAIN`
>    ⇒ ถ้าปิดจะเชื่อมต่อไม่ได้ · ทางถอดที่ถูก = ใส่ไฟล์ CA ของ Supabase ใน client ที่รองรับ CA (credential ของ n8n ไม่มีช่องนั้น)
> 3. HR: ถ้าโมเดลเสียเงินเรียกใช้ไม่ไหว → PL สลับเป็นโมเดลฟรี + ตั้งเป็น HR ชั่วคราวได้ ไม่ต้องขออนุมัติ
> 4. ช่วงพี่ไม่อยู่ **PL ทำแทนได้** (deploy / production / architecture ยังต้องรอพี่)
>
> **ทีมเปลี่ยน 2026-09-26 (PL ภายใต้อำนาจที่ได้รับ — อัปเดตใน `MODEL_ROSTER.md` แล้ว):** `ops` = `opencode/mimo-v2.6-flash-free` ·
> `researcher` = `opencode/nemotron-3.5-lightning-free` · `model-recruiter` = `opencode/nemotron-3-ultra-free` **ชั่วคราว**
> (ตัวเสียเงินส่ง tool call ผิดซ้ำ ๆ) — ทั้งสามตัว **ทดสอบรันจริงผ่านแล้ว**
>
> **บั๊กค้างสำคัญ:** แอปเก็บ model cache เก่าใน `opencode.global.dat` ซึ่งยังมี id ที่ถูกลบไปแล้ว `opencode/muse-spark-1.2-contributor-free`
> (visibility "show") → **agent ใดก็ตามที่ pin `opencode/muse-spark-*` จะเปิดไม่ได้** (error "Model not found: …muse-spark-1.2-contributor-free"
> ทั้งที่ไฟล์ pin 1.3) · ทางแก้ชั่วคราวที่ใช้อยู่ = pin โมเดลฟรีที่ไม่ใช่ muse-spark · ทางแก้ถาวรที่ควรทำ = เคลียร์/แก้ค่าในแอป
>
> **งานถัดไปตามคำสั่งพี่:** (1) **War Room D-01** — Issues #35/#30 ยัง OPEN, PR #73/#79 merge แล้วแต่ D-01 ยังไม่ถูกปิดอย่างเป็นทางการ → ตรวจแล้วปิด
> (2) **T-032** — รอพี่ตอบ 4 ข้อฝั่ง Codex + ตัดสินใจเปิด protection ของ `dev-workspace` (3) housekeeping: move T-031 เข้า `TASKS_PARKED.md`, ตัดสินใจ push `5a93eff`

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
**T-031 = DROPPED · ยึดแนวทาง Git เป็นช่องจ่ายงาน (Owner 2026-09-25)** — สะพานไม่เปิดเพื่อจ่ายงาน และ **ไม่สร้างระบบ relay/watcher** · เหตุผล: Git เป็นคิวถาวร + มีหลักฐานในตัว (commit/diff/CI/comment) งานจึงเดินได้แม้ไม่มีใครตอบแชท · ฝั่งโน้น (Codex/ChatGPT) มีเมนู Git จริง: prefix `codex/`, draft PR, review handoff, ติดตาม PR จน merge → ทำงานเป็น branch/PR client ได้ · **T-032 = การ์ดใหม่ "จ่ายงานผ่าน Git"** (issue → branch `codex/*` → draft PR → CI → reviewer คนละโมเดล → พี่/PL อนุมัติ → merge) · กฎเหล็ก: ห้าม merge PR ตัวเอง, ห้าม push ตรงเข้า `dev-workspace`/branch แม่, ห้าม force push, **ห้าม secret ลง git**, คนเขียน ≠ คนตรวจ, deploy/architecture รอพี่ · **เช็คแล้ว: `dev-workspace` protected = false** (branch แม่ = true) → ต้องพี่อนุมัติเปิด protection · `T-BRIDGE-01` (watcher) ไม่ต้องทำ ยัง PARKED + ไฟล์ untracked ห้าม commit · T-031 ยังอยู่บนบอร์ดเป็น record รอ move เข้า PARKED ตอน doc-cleanup (จ่ายพนักงานทำ ไม่ทำในแชท)

**ปิดประชุม 2026-09-25 (session 2) — มติครบ 5 วาระ:** (1) **T-001 ปิดแล้ว** (host มีอยู่จริง; n8n→PG = T-030; งานที่ไม่มี card = backup/restore กับ Supabase จริง → ทบทวนตอนเข้า runtime) (2) **T-BRIDGE-01 = ลบ** — `watcher.mjs` + `watcher.test.mjs` ถูกลบออกจาก working tree แล้ว (untracked ไม่เคย commit) · **ค้าง 1 คำสั่ง**: `server.mjs` ยัง modified (watcher wiring) ผม revert ไม่ได้เพราะ sandbox บล็อก → **`git restore .opencode/bridge/server.mjs`** (พี่หรือ builder รัน 1 ครั้ง) (3) **T-032 trigger = พี่เอง** (ไม่ auto-start จากคิว) (4) **การตรวจ PR = 3 ชั้น**: CI อัตโนมัติ → reviewer คนละโมเดลอ่าน diff + เขียน verdict → PL ตรวจสโคป/หลักฐาน · **merge = พี่** (checklist 7 ข้ออยู่ใน T-032) (5) **T-026 residual ไม่เปิดการ์ด** — ความเสี่ยงต่ำช่วง dev, กลางตอนเปิดระบบ (RLS ผูกกับ role `nippan_n8n` ที่ไม่ bypass; ช่องจริงคือ superuser/SECURITY DEFINER) → **เปิดการ์ดก่อนเปิดระบบจริง** · ยังค้างคำตอบพี่ 2 เรื่อง: **protection `dev-workspace`** และ **ค่าฝั่ง Codex 4 ข้อ** (draft PR on / auto-merge off / prefix codex/ / ห้าม force push)
**หมายเหตุ:** roster/agent files อัปเดตเป็น `opencode/muse-spark-1.3-contributor-free` แล้ว (Owner อนุมัติ 2026-09-25; ของเดิมไม่มีในระบบ) · Bridge watcher ยัง **PARKED/UNVERIFIED** (ไฟล์ untracked) ห้าม PL แก้เอง
**บทเรียน:** อย่าใช้ `write` ทับไฟล์บอร์ด/เอกสารที่ใช้ร่วมกัน ให้ `edit`/append และ commit การ์ดในเทิร์นเดียวกัน

# Session Handoff — 2026-09-25 (อัปเดต) — RESET TO PROTOCOL

อ่านไฟล์นี้ก่อนเริ่มงานในแชทใหม่ แล้วอ่านเพิ่มเฉพาะที่จำเป็น อย่าโหลดทั้ง repo

> **RESET 2026-09-25 (Owner)**: ยกเลิกวิธีการทำงานแบบ ad-hoc ทั้งหมด → กลับไปใช้ AI_OPERATING_PROTOCOL + TASK_CONTROL เท่านั้น · PL ห้ามแก้โค้ดเอง · เครดิต ≈ **$1.60** → ห้ามใช้ paid subagent/build

> ~~**กฎเหนือสุด (6 ข้อ)**~~ — **Owner สั่งถอนออกแล้ว 2026-09-25 (session 2)** → ไม่มีผล อย่าอ้างถึง · เนื้อหาเดิมเก็บเป็นประวัติใน `docs/warroom/decision-log.md` (entry "Supreme operating rules") · กติกาที่ใช้แทน = `AGENTS.md` + `docs/warroom/AI_OPERATING_PROTOCOL.md` + `docs/warroom/TASK_CONTROL.md` + กฎ Owner ในไฟล์นี้

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
> กฎชุดนี้คือกติกาที่ใช้อยู่จริง (กฎเหนือสุดถูก Owner ถอนออกแล้ว 2026-09-25)
1. **ทุกอย่างที่เสียเงิน (เรียก agent/โมเดล) ต้องขอ Owner อนุมัติก่อน** — ห้ามทำทันที
2. Owner เป็นผู้ตัดสินใจสุดท้าย (พี่เชษ)
3. รายงานสั้น เน้นเนื้อ ๆ (Owner สั่งลดความยาว ~80%)
4. Anti-redundancy: reviewer/security ต้องคนละโมเดลกับ builder และ reviewer ≠ security
5. ห้ามแตะ production `Ai-bot-Nippan`
6. งาน L2/L3 ต้องมี reviewer ตรวจ + อนุมัติก่อน DONE — **ช่วง dev-time นี้ พี่อนุมัติ หรือถ้าพี่ไม่อยู่ PL อนุมัติแทนได้** (ดูข้อ 12)
7. commit/amend/push เฉพาะเมื่อ Owner สั่ง ("อนุมัติ"/"อนุญาต")
8. งานเสียเงินที่ไม่รีบ → ส่ง Batch API (`:batch`) เสมอ (ถูกกว่า ~40–60%)
9. **งานอ่านเยอะ/ยาว → ส่งเข้า headless queue แล้วห้ามรอในแชท**; 1 งาน = 1 prompt ล็อกสโคป + ระบุ `--agent`/`--model`; งานแก้โค้ดรันบน branch + reviewer คนละโมเดลก่อน merge; ห้ามรันงานที่แตะไฟล์เดียวกันพร้อมกัน; ห้ามใส่ secret เข้าโมเดลฟรี; `runs/` gitignored → สรุปผลลงการ์ดทุกครั้ง (รายละเอียด: `AGENTS.md` + `docs/warroom/DEV_WORKING_GUIDE.md`)
10. **เกณฑ์ "ใครเขียนไฟล์ไหน" แยกตามชนิดไฟล์ (Owner อนุมัติ 2026-09-25)** — ไฟล์ dev-process (`TASKS.md`, `docs/**` ยกเว้น `PRICING_V1`/PDPA, `README*`, `WORKING_POLICY.md`, `AGENTS.md` แบบต้องได้อนุมัติพี่) = **PL เขียนเองได้** · ไฟล์ runtime (`services/**`, `migrations/**`, `tests/**`, `scripts/**`, `.github/**`, `.opencode/**`, `opencode.json`) = **PL ห้ามแตะเอง ต้องผ่าน builder/subagent + reviewer คนละโมเดลเสมอ** — เหตุผลคือคนเขียนต้องไม่ใช่คนตรวจ ไม่ใช่เรื่องงบ · งานหลายไฟล์ห้าม PL ทำในแชทหลัก (ดู `AGENTS.md` §Context Discipline ข้อ 6)
11. **Audit ใหญ่ครั้งเดียวตอนงานเสร็จ (Owner ยืนยัน 2026-09-25)** — **พี่นิยามชัด 2026-09-26: "ตอนปิดโปรเจ็คนี้ก่อนจะนำไปใช้งานจริง"** = ยิงตอนปิดโปรเจ็ค/ก่อนเปิดใช้กับลูกค้าจริง **ไม่ใช่**ตอน track ภายในครบ 100% (เช่น War Room 16/16) และไม่เลื่อนไปหลังเปิดใช้แล้ว · ด่าน audit 25/50/75/90/100 และบทบาท Independent Auditor คนกลาง **ยกเลิก/พักอยู่** ห้ามเรียกจนพี่เปิดใหม่ · **แต่ reviewer L4 (`anthropic/claude-opus-5.5:batch`) อนุมัติให้ใช้ได้** สำหรับงานวิกฤต (security boundary, tenant/bot isolation, data handling) — ไม่นับเป็น Independent Audit · **ต้องผ่าน Batch API เสมอ** · **อนุมัติเป็นรายครั้ง: พี่อนุมัติ หรือถ้าพี่ไม่อยู่ PL อนุมัติแทนได้** · ใช้ sparingly + เช็คเครดิตก่อน (ดู `AGENTS.md` §Independent Audit Status)
12. **Protected docs — แยกตามช่วง (Owner 2026-09-25)** — ไฟล์ protected 9 ไฟล์ (`PRICING_V1`, `CUSTOMER_FACING_RULES`, `PDPA_COMPLIANCE`, `LITE_SCHEMA_V1`, `INTEGRATIONS`, `ROLES`, `AI_OPERATING_PROTOCOL`, `WORKING_POLICY`, `TASK_CONTROL`) แก้เมื่อไร = L3 เสมอ · **ช่วง dev-time (ตอนนี้ ยังไม่มีลูกค้า/ยังไม่เปิดระบบ): พี่อนุมัติ หรือ PL อนุมัติแทนได้ทั้ง 9 ไฟล์** · **ช่วง runtime (เปิดให้ลูกค้าจริง): 3 ไฟล์ `PRICING_V1` / `PDPA_COMPLIANCE` / `CUSTOMER_FACING_RULES` = Owner เท่านั้น PL อนุมัติแทนไม่ได้** อีก 6 ไฟล์ PL อนุมัติแทนได้ · **ไม่ผ่อนทั้งสองช่วง**: การ์ดก่อน + reviewer คนละโมเดล + L3 ต้องมี Decision Log entry พร้อมเหตุผล (PL แทนได้แค่ "อนุมัติ" ไม่ได้แทนการตรวจ) · จุดสลับช่วง = พี่ประกาศว่าเปิดระบบจริง
13. **ชื่อโมเดลเวลาเรียก AI ต้องใส่ prefix ของผู้ให้บริการเสมอ (Owner สั่งจด 2026-09-26)** — โมเดลของ OpenRouter ต้องเขียน `openrouter/<author>/<slug>` เช่น `openrouter/nvidia/nemotron-3.5-lightning:free`, `openrouter/z-ai/glm-5.3-flash` · ของ Zen เขียน `opencode/<slug>` เช่น `opencode/space-bunny-free` · **ถ้าเขียนแบบไม่มี prefix จะล้มด้วย `Unexpected server error` ซึ่งอ่านหลอกว่าเป็นเรื่องสิทธิ์/guardrail ทั้งที่จริงคือชื่อผิดรูปแบบ** → ก่อนสรุปว่าโมเดลใช้ไม่ได้ ให้เช็คชื่อก่อน · กฎนี้ผูกทั้ง PL และ HR (`model-recruiter`) · หลักฐาน: `runs/2026-09-25T19-52-44Z-probe-free-id2` (PROBE OK) เทียบกับ 3 run ที่ล้มด้วยชื่อไม่มี prefix · บันทึกเต็ม: `docs/product/MODEL_ROSTER.md` + `docs/warroom/decision-log.md`

## คำสั่ง Owner ช่วงนี้ (TEMP — 2026-09-25 · ย้อนกลับเมื่อพี่สั่ง "กลับไปกติกาเดิม")
- **ทุกงานที่ได้รับ → ส่งขึ้น headless รันจริงเพื่อทดสอบว่าใช้ได้ และเก็บข้อผิดพลาดที่พบ** (ลงการ์ด + `docs/warroom/DEV_ERROR_LOG.md`)
- **ช่วงนี้ พี่มอบอำนาจให้ PL ตรวจ/อนุมัติแทนทั้งหมด** — ถ้าตัวไหนไม่ผ่าน ให้หา "คนแก้" ให้ผ่านเอง โดยไม่ละเมิด/ไม่เกินขอบเขตงาน
- **PL อนุมัติแทนได้**: ใช้โมเดลตาม roster (ทำงานเฉพาะหน้าที่ + มีหลักฐาน) · ปิดงาน L1/L2/L3 · commit/push · protected docs ฝั่ง dev-process · ใช้ secret ตามงาน
  - ข้อ 1 = ใช้โมเดลที่ roster กำหนดหน้าที่ไว้แล้วได้ตามปกติ (ห้ามงานนอกเรื่อง + ต้องเก็บหลักฐาน)
  - ข้อ 2 = เกินเพดานราคา → ห้ามอนุมัติ ให้หาทางใช้โมเดลฟรีแทน
  - ข้อ 3 = Independent paid Auditor คนกลาง (บทบาทผู้ตรวจภายนอก/ด่าน audit) → รอพี่ · **ไม่รวม reviewer L4** (ดูบรรทัดถัดไป)
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