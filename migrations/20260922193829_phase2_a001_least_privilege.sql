-- Audit #18 Finding A-001 remediation: least-privilege database role boundaries.
-- Baseline: PR #17 @ 1129bc562a238d338bf2761a49e4170588d52735
--
-- Control Plane owns identity/configuration mutation.
-- Data Plane runtime may mutate only conversation/runtime execution state,
-- telemetry, idempotency, usage and audit records required for execution.
-- Analytics remains read-only.
--
-- Existing tenant RLS policies remain unchanged. No role is granted BYPASSRLS.

-- Reset table privileges first so the broad grants from the Phase 2 foundation
-- cannot survive on any current public table.
revoke all on all tables in schema public
  from nippan_runtime, nippan_control_plane, nippan_analytics;

-- Runtime may read the control-plane state required to route and execute work.
grant select on
  public.tenants,
  public.applications,
  public.agents,
  public.channels,
  public.agent_channel_bindings,
  public.subjects,
  public.subject_identities,
  public.policy_versions,
  public.agent_config_versions,
  public.agent_activations
to nippan_runtime;

-- Conversation state and runtime/request telemetry are Data Plane-owned.
grant select, insert, update on
  public.conversations,
  public.requests,
  public.trace_spans,
  public.trace_span_links,
  public.ai_calls,
  public.tool_calls,
  public.retrieval_events,
  public.idempotency_records
to nippan_runtime;

-- Usage and audit ledgers are append-only at the role boundary as well as by
-- their existing database triggers.
grant select, insert on
  public.usage_events,
  public.audit_events
to nippan_runtime;

-- The Control Plane may inspect current platform/runtime state for dashboard
-- operations but may mutate only identity/configuration state plus the
-- idempotency/audit records needed for governed side effects.
grant select on all tables in schema public
to nippan_control_plane;

grant insert, update on
  public.tenants,
  public.workspaces,
  public.applications,
  public.agents,
  public.channels,
  public.agent_channel_bindings,
  public.subjects,
  public.subject_identities,
  public.policy_versions,
  public.agent_config_versions,
  public.agent_activations,
  public.idempotency_records
to nippan_control_plane;

grant insert on
  public.audit_events
to nippan_control_plane;

-- Analytics is strictly read-only.
grant select on all tables in schema public
to nippan_analytics;
