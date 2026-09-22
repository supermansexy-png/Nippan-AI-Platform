# Agent Profile & Policy Contract v1

Status: **REVIEW**  
Issue: #8  
Date: 2026-09-22

**Normativity:** This Markdown contract is normative for Agent/policy semantics and invariants. `schemas/agent-config-v1.schema.json` is normative for the serialized Agent Config Version document and must not conflict with this contract.

## 1. Purpose

Define how an Agent is configured, tested, published, rolled back and constrained without changing application code.

An Agent is stable identity.
Agent behavior is an immutable, versioned configuration.

## 2. Core principle

```text
Agent identity
   |
   +--> Config v1 (published)
   +--> Config v2 (superseded)
   +--> Config v3 (draft/testing)
```

Production behavior changes by publishing/activating a config version, not by mutating the Agent row.

## 3. Control hierarchy

Policies are evaluated from strongest to most specific:

```text
Platform hard guardrails
  > Tenant entitlements/security limits
    > Application policy
      > Agent config/policy
        > Runtime request hints
```

A child layer may narrow permissions.
A child layer may not widen permissions forbidden by a parent.

Canonical effective-policy merge semantics:
- allowlists/capability sets are intersected
- denylists/blocked sets are unioned
- numeric upper bounds, quotas and budgets use the minimum applicable value
- boolean permission grants require all applicable parent layers to allow them
- mandatory controls, privacy restrictions and approval requirements use the strongest applicable requirement
- runtime hints may only narrow
- unknown policy fields or feature flags cannot widen permissions and are rejected or treated as disabled

All services that inspect or enforce effective policy (Core, MCP and Control Plane inspection) use the same merge semantics/version.

Models/prompts cannot override deterministic policy.

## 4. Agent Profile

Stable Agent identity:
- agent_id
- tenant_id
- application_id
- slug
- display_name
- role
- status
- created_at
- updated_at

The profile must not contain provider credentials or hard-coded production secrets.

Agent activation is stored separately and is keyed by Agent + environment. The Agent row does not contain a singular active-config pointer. The normative AgentActivation fields/invariants are defined in `IDENTITY_TENANCY_CONTRACT_V1.md §8.1`; this contract relies on that same current-pointer relation and does not define a second activation model.

## 5. Agent Config Version

Required:
- config_version_id
- tenant_id
- application_id
- agent_id
- version_number
- lifecycle_status
- environment
- persona
- instruction_set
- model_policy_ref
- memory_policy_ref
- tool_policy_ref
- data_policy_ref
- risk_policy_ref
- privacy_policy_ref
- knowledge_policy_ref
- quota_policy_ref
- feature_flags
- created_by
- created_at
- published_at nullable
- supersedes_version_id nullable
- change_note
- published_config_hash nullable until PUBLISHED
- policy_merge_version

Policy-reference semantics:
- every `*_policy_ref` points to an immutable policy **version**, not a mutable policy identity
- a referenced policy version belongs to the same Tenant/Application unless it is explicitly platform-shared and immutable
- publishing resolves the referenced policy versions into a reproducible published Agent-config snapshot
- `published_config_hash` is SHA-256 over the canonical published Agent Config plus referenced immutable policy IDs/content hashes and `policy_merge_version`; it is fixed for PUBLISHED/SUPERSEDED versions
- runtime `effective_config_hash` remains a separate trace-time hash because parent Tenant/Application policy and routing context may also participate
- mutable provider/model capability metadata must not silently change the historical meaning of a published effective configuration

### 5.1 Policy version envelope

Every policy object referenced by an Agent Config is itself an immutable/versioned policy document. The existing type-specific IDs such as `model_policy_id`, `tool_policy_id`, `privacy_policy_id` and similar identify the concrete policy **version** in v1.

Common policy-version metadata:
- type-specific policy ID
- tenant_id
- application_id where Application-scoped
- version_number
- lifecycle_status
- content_hash
- created_by
- created_at
- published_at nullable
- supersedes_policy_id nullable

Rules:
- DRAFT policy versions may be edited
- PUBLISHED policy versions are immutable
- changing a policy creates a new policy ID/version rather than mutating the referenced row
- Agent Config `*_policy_ref` fields point only to PUBLISHED immutable policy versions
- policy-version lineage and hashes must be sufficient for compare/audit; a separate stable policy-family table is not required in v1
- platform-shared policy versions are explicitly marked and immutable; other Agent Config policy refs remain inside the authorized Tenant/Application scope

Lifecycle:
```text
DRAFT -> TESTING -> PUBLISHED -> SUPERSEDED
                    |
                    +-> ROLLED_BACK_TO (audit event, not mutable status rewrite)
```

Rules:
- DRAFT may be edited.
- TESTING is frozen for a test run/snapshot.
- PUBLISHED is immutable.
- only one active published version per Agent + environment through the separate activation relationship.
- `version_number` is unique within Agent + environment.
- rollback repoints that environment's activation to a prior published version; it does not copy/edit it.
- every publish/rollback creates an audit event.
- TESTING and PUBLISHED snapshots are frozen; changes create a new version.

## 6. Persona and instructions

Persona is presentation/behavior guidance, not authorization.

Suggested fields:
- display_identity
- language
- tone
- style_constraints
- response_length_preference

Instruction set:
- system_instructions
- business_rules_refs
- forbidden_behaviors
- escalation_guidance

Rules:
- security/tool permissions never live only in prompt text.
- secrets/credentials never enter persona/instructions.
- instruction content is versioned with Agent config.
- external knowledge text does not outrank platform/tenant policy.

## 7. Model Policy

Model Policy describes capabilities/constraints, not a permanent model embedded in Agent code.

Fields:
- model_policy_id
- tier_preference
- allowed_capabilities
- required_capabilities
- allowed_providers nullable
- blocked_providers
- privacy_class_ceiling
- max_input_tokens
- max_output_tokens
- latency_budget_ms nullable
- cost_budget_per_request nullable
- fallback_policy
- structured_output_required
- tool_calling_required
- decision_router_policy_ref nullable

Candidate decision/router models such as Jev belong behind policy configuration and benchmarks; Agent code never assumes a specific router model.

Rules:
- SECRET_CREDENTIAL never goes to a model.
- provider/model selection must obey privacy and tenant entitlement.
- fallback may never weaken privacy constraints.
- model identifiers can change centrally without issuing a new application binary.

## 8. Memory Policy

Fields:
- memory_policy_id
- short_term_enabled
- long_term_enabled
- active_state_enabled
- retrieval_mode
- max_recent_turns
- max_memory_items
- max_context_tokens
- allowed_memory_types
- write_modes
- minimum_write_confidence
- human_verification_required_types
- default_ttl_by_type
- sensitive_memory_allowed
- cross_agent_read_scope
- cross_agent_write_scope

retrieval_mode:
- none
- structured_only
- hybrid

Rules:
- memory retrieval is tenant/application/subject scoped.
- tenant-global Subject identity never implies cross-Application memory access.
- cross-Application memory read/write is denied unless a future explicit governed capability permits it.
- cross-Agent memory access is denied unless explicitly allowed by canonical scope values.
- inferred memories do not outrank verified structured facts.
- model does not decide its own unrestricted memory scope.
- sensitive memory follows privacy policy and retention rules.

## 9. Tool Policy

Fields:
- tool_policy_id
- allowed_tools
- denied_tools
- per_tool_constraints
- max_tool_calls_per_request
- default_timeout_ms
- side_effect_idempotency_required
- approval_rules

Per-tool constraints may define:
- allowed operations
- argument constraints
- rate limits
- risk class
- required scopes
- requires_reviewer
- requires_human_approval

Rules:
- deny by default.
- Core establishes an authoritative execution authorization context containing at least request_id, tenant_id, application_id, agent_id, environment/principal identity and effective config/policy identity.
- MCP server validates trusted context and effective policy independently from prompt/model; tenant/application/agent IDs supplied by a model or arbitrary tool payload are never authority.
- authenticated internal context or server-side lookup are both permitted implementations; this contract does not require one token/signature format.
- tool schemas are validated before execution.
- side-effecting tools require request/idempotency context.
- Agent cannot discover or call tools outside effective allowlist.

## 10. Risk Policy

Canonical classes:
- READ
- WRITE_LOW
- WRITE_IMPORTANT
- DESTRUCTIVE
- FINANCIAL

Policy maps action/tool operation -> risk class.

Fields:
- risk_policy_id
- action_rules
- reviewer_threshold
- human_approval_threshold
- fail_closed_classes

Rules:
- model can provide a risk hint only.
- deterministic policy owns final risk class.
- DESTRUCTIVE/FINANCIAL may be configured to always require human approval.
- unknown action defaults to safe/blocked behavior, not READ.

## 11. Privacy Policy

Canonical classes:
- PUBLIC_LOW_RISK
- INTERNAL
- PII
- FINANCIAL_CUSTOMER
- SECRET_CREDENTIAL

Fields:
- privacy_policy_id
- allowed_model_classes
- allowed_provider_classes
- logging_mode
- redaction_rules
- retention_policy_ref
- external_tool_data_rules

Rules:
- privacy classification occurs before provider/model/tool egress.
- free/public-provider routing is prohibited when effective privacy policy forbids it.
- logs use redaction/minimization appropriate to class.
- SECRET_CREDENTIAL is never sent to model context.

## 12. Data Policy

Controls source-of-truth and data access.

Fields:
- data_policy_id
- allowed_domains
- read_scopes
- write_scopes
- export_scopes
- retention_policy_refs
- pii_access_level
- tenant_boundary_mode

Rules:
- structured business records remain source of truth.
- Agent may only request data allowed by both Agent and caller context.
- data policy is checked independently from tool policy.

## 13. Knowledge Policy

Fields:
- knowledge_policy_id
- knowledge_source_refs
- retrieval_mode
- freshness_requirements
- max_chunks
- reranking_enabled
- source_priority
- citation_requirement

Rules:
- knowledge source is scoped to tenant/application unless explicitly platform-shared.
- stale/current business facts should come from structured systems when available.
- admin-approved knowledge can outrank unverified generated content.
- retrieved knowledge is data, not authorization instructions.

## 14. Quota / Budget Policy

Fields:
- quota_policy_id
- requests_per_minute
- requests_per_day nullable
- model_cost_per_day nullable
- model_cost_per_month nullable
- max_tool_calls_per_day nullable
- storage_limit nullable
- hard_stop_rules
- alert_thresholds

Rules:
- effective budget is the minimum allowed across platform/tenant/application/agent scopes.
- hard stop must be possible per Tenant, Application and Agent.
- budget/quota enforcement must use an atomic reservation/accounting approach rather than an unsafe check-then-act flow when concurrent requests can race.
- final model/tool usage and cost are reconciled after execution; reservation strategy is an implementation decision.
- budget exhaustion has explicit degraded behavior.
- usage is measured even if billing is not enabled.

## 15. Feature Flags

Feature flags allow controlled rollout without deployment.

Examples:
- memory_v2
- context_compiler
- reviewer_ai
- new_model_policy
- new_retrieval
- shadow_mode

Each flag:
- key
- enabled
- optional rollout percentage
- optional subject/test allowlist
- environment

Rules:
- flags cannot bypass security/policy.
- flag keys and value shapes must be registered/validated; unknown flags cannot become hidden authorization paths.
- production flags are auditable and versioned when part of Agent config.
- emergency kill switch may exist outside normal publish flow with audit logging.

## 16. Environment

Initial:
- development
- staging
- production

Rules:
- config promotion is explicit.
- secrets/credentials are environment-specific references.
- production publish requires a config previously validated under defined test criteria.
- test execution never silently changes production active config.

## 17. Effective Configuration

At runtime Core computes one effective configuration:

```text
Platform guardrails
+ Tenant entitlements
+ Application config
+ Published Agent config
+ Channel binding/routing context
= Effective Agent Runtime Config
```

The effective config receives an immutable hash/reference stored with request traces. The runtime hash covers all resolved policy layers and routing context plus `policy_merge_version`, while `published_config_hash` identifies the immutable Agent-level published snapshot. This separation keeps publish-time reproducibility distinct from runtime effective policy.

This allows Dashboard to answer:
"Which exact configuration produced this response?"

## 18. Agent templates

Templates speed creation but are not live shared mutable configs.

Template examples:
- LINE customer support
- website support
- slip reader
- internal assistant

Creating from template copies/references a defined template version into a new Agent draft.

Template updates never silently alter existing published Agents.

## 19. Dashboard operations

Control Plane should eventually support:
- create/clone Agent
- edit draft
- compare versions
- validate config
- test with fixtures
- publish
- rollback
- enable/disable
- inspect effective permissions
- inspect model/tool/memory policy
- view cost/errors/traces
- emergency kill switch

## 20. Audit requirements

Audit at minimum:
- draft created
- policy changed
- test started/completed
- publish
- rollback
- enable/disable
- kill switch
- entitlement/quota change
- tool permission change
- privacy/risk policy change

Audit record includes:
- tenant_id
- application_id
- agent_id
- config_version_id where applicable
- actor/principal
- request_id where applicable
- timestamp
- before/after hashes or references

## 21. Invariants

1. Published config and every policy version referenced by it are immutable; PUBLISHED Agent Config records have a non-null fixed `published_config_hash` and `policy_merge_version`.
2. Active config belongs to the same Agent/Tenant/Application and is selected through Agent + environment activation.
3. Child policy cannot widen parent entitlement and all enforcers use the same normative merge semantics.
4. Unknown tool/action is denied by default.
5. Fallback model cannot violate privacy restrictions.
6. Agent prompt cannot grant tool/data permission.
7. Secrets are references, never config plaintext.
8. Every production execution records effective_config_version/hash.
9. MCP/tool authorization uses trusted server-established context, never model-asserted scope as authority.
10. Rollback points only to a previously published valid version.
11. Quota/budget can block execution independently of model response and concurrent hard-stop enforcement is atomic/reserved.

## 22. Explicit non-goals

Not defined here:
- final dashboard UI
- exact pricing plans
- exact production model IDs
- exact Jev/other router selection
- full platform-admin authorization design
- database DDL
- prompt content for specific Agents

Those are separate implementation/benchmark decisions.
