T-030 EXECUTION EVIDENCE — 2026-09-25
INTAKE: TASKS.md (INTAKE T-030)
HR: muse-spark-1.2 + space-bunny-free READY
Builder: z-ai/glm-5.3-flash DELIVERED (plan + config)
DB verify: SQL SELECT rolname FROM pg_roles WHERE rolname='nippan_n8n' → rolcanlogin=true (VERIFIED)
SET ROLE nippan_n8n: blocked (42501 permission denied) — expected, confirms auth gate requires connection with password
Blocker: CLEARED (Owner set password 2026-09-25)
Reviewer: space-bunny-free L1-3 PASS (plan checked; no secret leaked; models correct)
Execution steps completed by builder/PL (no direct source edit):
  - Credential params documented (host/port/user/auth/SSL)
  - RLS test plan defined (tenant A visible / B hidden / rollback)
  - DB role verified
Physical n8n credential creation + connection test result: NEXT (requires n8n UI config per plan)
Status: BUILDER+REVIEW COMPLETE / EXECUTION UNVERIFIED UNTIL CONNECTION TEST RESULT RECEIVED
Evidence files: docs/n8n/T-030-credential-plan.md + this file + SQL result + DEV_ERROR_LOG.md update
NOT FULL DONE — per protocol rule 6 (no DONE without proof)

## EXECUTION — 2026-09-26 (real run through n8n, PL via n8n MCP tools)

Created workflow (MCP `create_workflow_from_code`, PL `deepseek-v4.1-flash`):
- name `T-030 RLS test (tenant A vs B)`, id `CVhNSU5pjpGgzquB`
- folder `Nippan Phase A` (`zClFVASPRDPnaeuQ`), personal project `hmhfL4HtmuUod5jL`
- nodes: Manual Trigger `Start` → Postgres `RLS test (tenant A vs B)` (v2.7 · resource `database` · operation `executeQuery`)
- credential auto-assigned by name: `Postgres account` (id `6anMUYRLDYPduKY7`) — no secret read or written
- no Query Parameters used (multi-statement body sent as one simple query; `queryBatching` default `single`)

Query body: `BEGIN` → `set_config('app.tenant_id', A, true)` → `INSERT public.lite_tenants` (tenant A) → `count(*)`
→ `set_config('app.tenant_id', B, true)` → `count(*)` → `ROLLBACK`

Execution `5842` (mode manual, status **success**, 2026-09-25T17:31:06Z → 17:31:09Z), node output verbatim:
- `set_config` = `11111111-1111-1111-1111-111111111111`
- `visible_as_tenant_a` = **"1"** ← INSERT accepted under RLS and tenant A reads its own row
- `set_config` = `22222222-2222-2222-2222-222222222222`
- `visible_as_tenant_b` = **"0"** ← tenant B cannot see tenant A's row

Non-destructive check (independent of the workflow): `SELECT count(*) FROM public.lite_tenants` on Supabase
`xzxwakvsbdzkdybijbzs` → **0 rows** ⇒ the INSERT was rolled back; nothing persisted.

Meaning: a real connection as `nippan_n8n` through the n8n Postgres credential works, and RLS scopes reads/writes per tenant.

Done-when coverage: (1) credential configured + connection PASS ✔ · (2) A sees own row / B sees 0 ✔ ·
(3) insert+read inside a transaction then rollback ✔ · (4) reviewer verdict on this evidence — **PENDING**
(reviewer `opencode/space-bunny-free`, different model from the author).

Status: EXECUTION VERIFIED / AWAITING REVIEWER VERDICT — not DONE yet.

## REVIEWER PASS 1 — `opencode/space-bunny-free` — 2026-09-26

Verdict: **ACCEPT-WITH-FINDINGS** (card must not close as DONE on pass-1 evidence alone).
- Passed: the pair `A=1` (inside the transaction) + `count(*)=0` (after it) eliminates the two ways the result could be fake —
  if the role bypassed RLS, B would read 1; if the INSERT never ran, A would read 0. Grep of `migrations/20260925120000_lite_rls_v1.sql`
  confirms `FOR ALL TO nippan_runtime` with `USING`/`WITH CHECK tenant_id = current_tenant_id()`, which matches the observed result.
- Passed: no secret in the evidence; no `SET ROLE` / GRANT / BYPASSRLS / policy change / DDL in the query; role is non-BYPASSRLS.
- Finding (ก): the output never records `current_user` → nothing in the file proved the connection was `nippan_n8n` rather than `postgres`.
- Finding (ข): only SELECT isolation was tested — no positive control (tenant B reading/writing its OWN row) and no proof that
  the `WITH CHECK` actually rejects a cross-tenant write.
- Residual risk noted by the reviewer: credential uses `Ignore SSL Issues` (encrypted but no server verification) — acceptable in
  dev-time, must be removed before real use.

## EXECUTION — 2026-09-26 (v2, answers both findings) — PL via n8n MCP

Workflow `T-030 RLS test v2 (role + positive control + cross-tenant)` id `eohtRWY8YEvEuS7n`, folder `Nippan Phase A`,
credential auto-assigned by name `Postgres account`. One Postgres `executeQuery` node, one transaction, `ROLLBACK` at the end.

Execution `5844` (manual, status **success**, 2026-09-25T17:33:28Z → 17:33:29Z), node output verbatim:
- `step: connected_role` = **`nippan_n8n`** ⇒ the session really is the least-privilege role (answers finding ก)
- `step: visible_as_tenant_a` = **1**
- `step: visible_as_tenant_b_before_own_insert` = **0** ⇒ tenant B cannot read tenant A's uncommitted row
- `step: visible_as_tenant_b_after_own_insert` = **1** ⇒ positive control: B can write AND read its own row (answers finding ข, part 1)
- `step: cross_tenant_write` = **`BLOCKED by RLS WITH CHECK (42501)`** ⇒ a cross-tenant INSERT is rejected by the policy
  (raised inside a PL/pgSQL exception block so the rejection is recorded instead of aborting the run) (answers finding ข, part 2)
- `step: visible_as_tenant_a_after_all` = **1**
- (three `set_config` rows are the scope switches for A → B → A)

Non-destructive re-check (independent, after both runs): `lite_tenants = 0` and `lite_bots = 0` on Supabase `xzxwakvsbdzkdybijbzs`.

ENV FINDING (worth recording): `n8n_update_workflow` (setNodeParameter on `/parameters/query`) wrote a new workflow version but
manual execution `5843` still ran the OLD query — i.e. an updated workflow is not what a manual run executes until it is published.
Creating a workflow (`create_workflow_from_code`) IS immediately runnable. For T-030 v2 we therefore created a new workflow instead of
patching the old one.

Status: evidence for both reviewer findings recorded — AWAITING REVIEWER PASS 2. Not DONE.

## REVIEWER PASS 2 — `opencode/space-bunny-free` — 2026-09-26

Verdict: **ACCEPT-WITH-FINDINGS** — both pass-1 findings answered. The reviewer did not take this record on trust: it pulled
workflow `eohtRWY8YEvEuS7n` and execution `5844` raw from n8n, matched all 7 output rows against this document, and confirmed
`createdAt == updatedAt` on the version (`9e6ee7bc`) so the SQL that ran is the SQL stored now.
- (ก) PASS — `current_user = nippan_n8n`; `20260925130000` creates `login inherit` (default NOSUPERUSER / NOBYPASSRLS) as a member of
  `nippan_runtime`; every `lite_*` table is `force row level security`; the query has no `SET ROLE`, so `current_user = session_user`.
- (ข) PASS — the `BLOCKED` string can only be written from the `EXCEPTION WHEN insufficient_privilege` handler, and the only statement in
  that block able to raise 42501 is the cross-tenant INSERT (the other statement could only raise 23505, and both `step` values are a
  PRIMARY KEY so they cannot coexist). Weakest point flagged by the reviewer: "WITH CHECK" is the author's wording — the actual
  SQLSTATE/message was not captured; the rejection argument rests on the elimination above.
- Positive control sound: tenant B reads 1 while tenant A's row is still present in the same transaction (without RLS it would be 2).
- Non-destructive acceptable: one transaction + `ROLLBACK` + temp table `ON COMMIT DROP`; `lite_tenants = 0`, `lite_bots = 0` reported.
- No secret leak. Still open (carried from pass 1): the credential's `Ignore SSL Issues`; every run was `manual`, never published.
- Reviewer's card-hygiene notes were applied afterwards by the PL (card status, v1/v2 + pass 1–2 records, this appendix, CURRENT_STATE
  and handoff lines).

## APPENDIX — the exact v2 SQL that ran (execution `5844`)

```sql
BEGIN;
CREATE TEMP TABLE _t030(step text primary key, val text) ON COMMIT DROP;
INSERT INTO _t030 VALUES ('connected_role', current_user);
SELECT set_config('app.tenant_id','11111111-1111-1111-1111-111111111111', true);
INSERT INTO public.lite_tenants (tenant_id, business_name, owner_contact)
VALUES ('11111111-1111-1111-1111-111111111111','TEST tenant A (rollback)','test@example.invalid');
INSERT INTO _t030 VALUES ('visible_as_tenant_a', (SELECT count(*)::text FROM public.lite_tenants));
SELECT set_config('app.tenant_id','22222222-2222-2222-2222-222222222222', true);
INSERT INTO _t030 VALUES ('visible_as_tenant_b_before_own_insert', (SELECT count(*)::text FROM public.lite_tenants));
INSERT INTO public.lite_tenants (tenant_id, business_name, owner_contact)
VALUES ('22222222-2222-2222-2222-222222222222','TEST tenant B (rollback)','test@example.invalid');
INSERT INTO _t030 VALUES ('visible_as_tenant_b_after_own_insert', (SELECT count(*)::text FROM public.lite_tenants));
DO $do$
BEGIN
  BEGIN
    INSERT INTO public.lite_tenants (tenant_id, business_name, owner_contact)
    VALUES ('11111111-1111-1111-1111-111111111111','CROSS-TENANT attempt (must fail)','test@example.invalid');
    INSERT INTO _t030 VALUES ('cross_tenant_write','ALLOWED - RLS WRITE GAP');
  EXCEPTION WHEN insufficient_privilege THEN
    INSERT INTO _t030 VALUES ('cross_tenant_write','BLOCKED by RLS WITH CHECK (42501)');
  END;
END
$do$;
SELECT set_config('app.tenant_id','11111111-1111-1111-1111-111111111111', true);
INSERT INTO _t030 VALUES ('visible_as_tenant_a_after_all', (SELECT count(*)::text FROM public.lite_tenants));
SELECT step, val FROM _t030 ORDER BY step;
ROLLBACK;
```
