begin;

create index agent_activations_config_fk_idx
  on public.agent_activations (tenant_id, application_id, agent_id, environment, config_version_id);

create index agent_config_versions_supersedes_idx
  on public.agent_config_versions (supersedes_version_id)
  where supersedes_version_id is not null;

create index applications_workspace_fk_idx
  on public.applications (tenant_id, workspace_id)
  where workspace_id is not null;

create index conversations_parent_fk_idx
  on public.conversations (tenant_id, application_id, parent_conversation_id)
  where parent_conversation_id is not null;

create index conversations_primary_agent_fk_idx
  on public.conversations (tenant_id, application_id, primary_agent_id)
  where primary_agent_id is not null;

create index conversations_subject_fk_idx
  on public.conversations (tenant_id, subject_id)
  where subject_id is not null;

create index policy_versions_supersedes_idx
  on public.policy_versions (supersedes_policy_id)
  where supersedes_policy_id is not null;

commit;

