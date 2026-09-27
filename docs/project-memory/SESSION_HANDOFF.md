<!-- AUTO-HANDOFF:START -->
## Handoff ล่าสุด (auto) — 2026-09-27
**หัวข้อ:** Owner redefines T-071 (Settings page Email|LINE), T-072 via Supabase MCP, creates T-074/075/076 structure cards, OWNER_ACTION_QUEUE.md, 3 GitHub Issues for ChatGPT

## Session นี้ — Owner instruction via advisor (8 steps executed)
**Owner verbatim:** "แจ้งเตือนให้ทำเป็นหน้าให้กรอกได้ ให้เลือกกรอกทางเมล์ หรือทางไลน์ ผมจะกรอกเองเมือเปิดใช้งาน ตอนนี้ให้เขียนรอไว้ เรามี mcp ของ supabase ใช้ทางนั้นได้เลย และไม่เห็นจ่ายงานให้ chatgpt ให้เพิ่มงานที่ต้องเขียนโค๊ด งานที่ต้องวางเวิกโฟรใน n8n งานที่ต้องวางระบบฐานข้อมูล ให้ตรงกับดีไซต์ของโปรเจ๊ดที่ออกแบบมา อันไหนต้องเอาข้อมูลผม ยังไม่ต้องเอา ให้ไปจัดการวางโครงสร้างทั้งหมดให้เป็นรูปร่างก่อน ไม่งั้นมาติดอยู่ตรงนี้ ไม่มีเครื่องมืออะไรให้แจ้งที่เดียว ไม่ใช่ทำไปแจ้งไป ให้ลองสำรวจเครื่องมือทั้งหมดของเรา เรามีครบ และให้ ที่ปรึกาษาคุมงานโดยละเอียดทุกขั้นตอน ตรวจทานรอบสุดท้้ายกับ pl เมือผ่านแล้วให้อนุมัติได้เลย งานจะได้เดินต่อเนื่อง"

### 8 Steps executed:
1. **T-071 REWORK** — Settings page with Email|LINE selector, pluggable transports (EmailTransport, LineTransport stubs), config JSONB nullable fail-closed, SMTP credential blocker CANCELLED, PR #92 adjusted on branch `t-071-alert-channel`
2. **T-072 UPDATED** — Backup/restore proof via Supabase MCP (not pg_dump/CLI) to separate schema `t072_restore`
3. **3 New cards created**: T-074 (Code stream), T-075 (n8n workflow stubs), T-076 (DB schema/migrations) — each references design source files, Goal = "วางโครงสร้างให้เป็นรูปร่างก่อน", no Owner data/credentials needed
4. **OWNER_ACTION_QUEUE.md** created at `docs/warroom/OWNER_ACTION_QUEUE.md` — single queue for all Owner-wait items
5. **Tool survey completed** — All tools enabled: Supabase MCP, n8n MCP, Render MCP, OpenRouter MCP, GitHub CLI, OpenCode Go pool (43 models). nippan-gateway = disabled (intentional)
6. **GitHub Issues for ChatGPT**: #93 (T-074), #94 (T-075), #95 (T-076) — all `ai:ready` label, queued for external assistant per two-lane Git channel
7. **Reviewer assignments** per T-065 roster: T-071/T-072/T-074/T-075 reviewer = `opencode/muse-spark-1.3-contributor-free` (Primary); T-076 security = `openrouter/deepseek/deepseek-v4.1-flash` (Primary). Advisor final review with PL then advisor approves merge
8. **ADVISOR_LOG.md** entry appended with full Owner verbatim, receiver=project-lead, auditor=space-bunny-free, verdict=pending

### Board state (VERIFIED on disk this session)
- **T-071** — IN_PROGRESS (rework started on PR #92, branch `t-071-alert-channel`)
- **T-072** — IN_PROGRESS (awaiting Supabase project ref, Supabase MCP ready)
- **T-073** — READY for INTAKE (awaiting Owner approval to start design)
- **T-074** — READY for INTAKE (Issue #93 ai:ready)
- **T-075** — READY for INTAKE (Issue #94 ai:ready)
- **T-076** — READY for INTAKE (Issue #95 ai:ready)
- **T-032** — pilot A DONE, pilot B pending (external assistant)
- **T-033** — War Room pilot ready for next round
- **T-050** — roadmap draft awaiting Owner review (DRAFT — NOT APPROVED)

### Working tree (uncommitted)
`M TASKS.md` · `M docs/project-memory/CURRENT_STATE.md` · `M docs/project-memory/SESSION_HANDOFF.md` · `M docs/warroom/ADVISOR_LOG.md` · `?? docs/warroom/P0_EXECUTION_PLAN_DRAFT_2026-09-27.md` · `?? docs/warroom/OWNER_ACTION_QUEUE.md`

### Next steps (in order)
1. Trigger builder (T-071) to claim Issue #90 and begin INTAKE on PR #92 rework
2. Trigger ops (T-072) to claim Issue #89 and begin INTAKE via Supabase MCP (project ref มีในรีโปแล้ว `xzxwakvsbdzkdybijbzs`)
3. Owner reviews OWNER_ACTION_QUEUE.md — รายการ OPEN เหลือเพียง trigger ChatGPT ที่ Issues #93/#94/#95
4. Owner triggers ChatGPT (external assistant) for Issues #93, #94, #95 when ready
5. Advisor final review with PL on each PR → advisor approves merge

### Rules that mattered this session
- T-071 redefinition: Settings page + pluggable transports + fail-closed + no credential blocker
- T-072: Supabase MCP replaces pg_dump/CLI/Docker blocker
- Three new structure cards: pure scaffolding, no Owner data needed
- Single Owner queue: OWNER_ACTION_QUEUE.md (no scattered reporting)
- Tool survey: no card may claim "no tool" without checking first
- GitHub Issue queue for non-urgent work: Owner triggers ChatGPT per two-lane rule
- Advisor oversight: final review with PL, then advisor approves (per ADVISOR_MANDATE.md §6)
<!-- AUTO-HANDOFF:END -->

## งานค้างที่ยังไม่ปิด — บ้านเดียว

**สถานะโครงการ: ยังไม่มีผู้เช่า ไม่มีผู้ใช้ ระบบยังไม่เปิด (pre-G1) — ฐานข้อมูล Supabase เป็นของทดสอบ ไม่มีข้อมูลลูกค้าจริง งานทดสอบ/backup/restore ทำบนฐานจริงได้โดยตรง ไม่ต้องกันข้อมูลผู้เช่า (ที่ยังไม่มี) แต่ยังห้ามแตะระบบ production เก่า Ai-bot-Nippan**

### ⚙️ กฎถาวร — Git work channel 2 เลน (Owner 2026-09-27; decision-log 2026-09-27)
- **งานด่วน** → PL แจ้งพี่ → **พี่แชทบอก ChatGPT อีกตัวเอง** (Owner = trigger)
- **งานไม่ด่วน** → PL โยน GitHub Issue label `ai:ready` body ครบ (Task/Role/Risk/Scope/Done-when/Stop rules) → **อีกตัว poll ทุก 1 ชม. ดึงเอง**
- **ทุกกรณี** → PL เข้าไป verify: label `ai:ready→ai:claimed→ai:done` + comment INTAKE/DELIVERY + หลักฐานดิบ ก่อนรายงานว่าดี
- อีกตัวเขียนงานบน branch `codex/*` เท่านั้น · ห้าม merge PR ตัวเอง · ห้าม push ตรงเข้า `dev-workspace`/`phase2/postgres-logical-schema` · ห้าม force-push · ห้าม secret ลง git
- กฎนี้ **แทนที่** T-032 blocker 3 เดิม ("assistant ไม่ auto-start จากคิว") — ใช้เฉพาะเลนด่วนเท่านั้น

### การ์ดค้าง
- **T-032** — Git work channel: **pilot A DONE 2026-09-27** (Issue #88, external assistant `GPT-5.6 Sol`, PL verify เอง ruleset 24070054) · force-push block DONE · **เหลือ pilot B (write): 1 real PR + CI + different-model review**
- **T-033** — War Room pilot: ปิด 3/3 ข้อแล้ว (fresh room · Owner จ่าย เพดาน $1/ครั้ง · participants = **PL เลือกตาม agenda ครั้งต่อครั้ง**) — การ์ด IN_PROGRESS พร้อมรอบ pilot ถัดไป
- **T-050** — roadmap draft (`ROADMAP_STUDY_DRAFT_2026-09-26.md`) รอ Owner พิจารณา (DRAFT — NOT APPROVED)
- **T-071** — IN_PROGRESS (rework on PR #92, Settings page Email|LINE, pluggable transports)
- **T-072** — IN_PROGRESS (Supabase MCP, ใช้ project ref ที่มีอยู่จริงในรีโป `xzxwakvsbdzkdybijbzs` ผ่าน Supabase MCP)
- **T-073** — READY for INTAKE (เริ่มได้เลย ไม่ต้องรออนุมัติ)
- **T-074** — READY for INTAKE (Issue #93 ai:ready, Code stream structure)
- **T-075** — READY for INTAKE (Issue #94 ai:ready, n8n workflow stubs)
- **T-076** — READY for INTAKE (Issue #95 ai:ready, DB schema/migrations)
- **restart opencode** — pin ใหม่ (project-lead ฯลฯ) จะมีผลหลังเปิดแชทใหม่
- **OpenRouter credit** — ~$55 total / $52.60 used (re-check before any paid call)

### Working tree / push
- **อยู่บน branch `dev-workspace` แล้ว** — จะ commit เอกสาร 6 ไฟล์ที่นี่ แล้ว push `origin/dev-workspace` (no force)
- Branch การ์ด `t-071-alert-channel` และ `t-072-backup-restore-proof` คืนสู่สะอาด (เหลือเฉพาะไฟล์ที่การ์ดรับผิดชอบ)
- `docs/warroom/ADVISOR_LOG.md` มีงานค้างของ session อื่น — **อย่าเขียนทับ**
- ⚠️ อาจมี session อื่นทำงานอยู่: **อย่าเขียนทับไฟล์ที่ตัวเองไม่ได้แก้**

### ไฟล์สำคัญที่อัปเดต/สร้างใหม่ใน session นี้
- `TASKS.md` — T-071 reworked, T-072 updated, T-074/T-075/T-076 added
- `docs/warroom/P0_EXECUTION_PLAN_DRAFT_2026-09-27.md` — updated with new cards, tool survey, reviewer assignments
- `docs/warroom/OWNER_ACTION_QUEUE.md` — created (single Owner queue)
- `docs/warroom/ADVISOR_LOG.md` — new entry appended (8-step Owner instruction)
- GitHub Issues #93, #94, #95 created with `ai:ready` label