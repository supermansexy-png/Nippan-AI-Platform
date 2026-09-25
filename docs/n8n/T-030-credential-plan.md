T-030 — Builder DELIVERED (z-ai/glm-5.3-flash) — 2026-09-25
INPAke source: TASKS.md (INTAKE T-030)
Blocker (verified): owner must set `nippan_n8n` password before live DB connection

DELIVERY (builder output — not yet executed against DB):
1. n8n Postgres credential params (recommended):
   - Host / Port / DB: from Supabase `xzxw...` (project details)
   - User: nippan_n8n (LOGIN member of nippan_runtime, RLS forced, not bypass)
   - Auth: password (NEEDS_OWNER_DECISION — set via SQL editor, do NOT write secret to file)
   - SSL: required (Supabase)
2. RLS verification test plan:
   a. Connect with tenant A credentials → verify tenants_visible=1, botA_visible=1
   b. Connect with tenant B scope → verify tenantB_visible=0 (isolation)
   c. Write test (non-destructive): INSERT into lite_* with correct tenant key → rollback
3. Evidence required for DONE: screenshot/cli output of connection success + RLS scope results
3b. FINDING 2026-09-25 (both PL SQL tool and Owner Supabase SQL editor): `SET ROLE nippan_n8n` -> ERROR 42501 permission denied to set role. SQL-editor impersonation path is NOT usable; RLS/role proof must come from a real connection authenticated as nippan_n8n (n8n credential test). Interim role evidence still VERIFIED via pg_roles (rolcanlogin=true).
3c. CONNECTION RESULT 2026-09-25 (owner-reported, n8n UI): FAIL direct `db.xzxwakvsbdzkdybijbzs.supabase.co:5432` -> ENETUNREACH to IPv6 2406:...:5432 (direct endpoint is IPv6-only). FAIL then self-signed certificate in certificate chain -> fixed via SSL=require + Ignore SSL Issues. PASS with pooler host `aws-0-ap-northeast-2.pooler.supabase.com:5432`, user `nippan_n8n.xzxwakvsbdzkdybijbzs`, db postgres. Credential usable; RLS read/write test still TODO (card not DONE).
3d. POLICY MAPPING (read-only, VERIFIED via pg_policies/pg_proc): all 7 `lite_*` tables FORCE RLS, policy roles = `nippan_runtime`; scope = `app_private.current_tenant_id()` -> `current_setting('app.tenant_id')` and `current_bot_id()` -> `current_setting('app.bot_id')`; `lite_tenants` keys on tenant only, other 6 key on tenant+bot. `lite_*` currently EMPTY (0 rows) so RLS proof needs insert+read inside a transaction.
Status: BUILDER DELIVERED / BLOCKED (password) / UNVERIFIED execution — will rerun after owner sets password
Model: builder z-ai/glm-5.3-flash; reviewer space-bunny-free (L1-L3) pending
