-- n8n runtime login role (Phase A).
--
-- n8n connects to the lite database as this role. It is a member of
-- nippan_runtime, so the lite_* RLS policies from
-- 20260925120000_lite_rls_v1.sql apply to it, and it is deliberately
-- NOT superuser and NOT BYPASSRLS (unlike the `postgres` role, which
-- bypasses RLS entirely).
--
-- The password is set OUT OF BAND by the operator:
--     alter role nippan_n8n password '<operator secret>';
-- and is never stored in the repository nor in migration history.

begin;

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'nippan_n8n') then
    create role nippan_n8n login inherit;
  end if;
end
$$;

grant nippan_runtime to nippan_n8n;

comment on role nippan_n8n is
  'n8n runtime login role; member of nippan_runtime so lite_* RLS applies. Password set out-of-band.';

commit;
