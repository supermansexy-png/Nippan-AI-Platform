# Platform Identity & Tenancy Contract v1

Status: **REVIEW**  
Issue: #7  
Date: 2026-09-22

**Normativity:** This Markdown contract is normative for identity/tenancy semantics and invariants. `schemas/platform-identity-v1.schema.json` is normative for the serialized structures it describes and must not conflict with this contract.

## 1. Purpose

Define stable ownership, identity and isolation boundaries for Nippan AI Platform before PostgreSQL tables, dashboard APIs or runtime services are implemented.

This contract supports:
- Nippan internal applications
- websites and messaging bots
- web/mobile/desktop applications
- multiple AI Agents per application
- multiple channels per application
- future external/rental/SaaS tenants
- versioned configuration and usage attribution

## 2. Core rule

**Tenant is the primary security, ownership, quota and future billing boundary.**

No tenant-owned runtime record may exist without a tenant scope.

Cross-tenant access is denied by default.

## 3. Logical model

```text
Platform
  |
  +-- Tenant
       |
       +-- Workspace (optional grouping)
       |
       +-- Application
            |
            +-- Agent
            |
            +-- Channel
            |
            +-- Agent <-> Channel Binding
            |
            +-- Subject
                 |
                 +-- Subject Identity
                 |
                 +-- Conversation
                      |
                      +-- Agent participation / handoff
```

Important refinement from the simplified Foundation diagram:

Agents and Channels are both owned by an Application.
They are connected by explicit bindings instead of forcing one permanent Agent -> Channel hierarchy.

This permits:
- one LINE channel to use support + sales + order Agents
- one Agent to work on LINE + web + app
- agent handoff without recreating the conversation

## 4. Identifier standard

All internal IDs are opaque UUIDs.

Preferred generation:
- UUIDv7 when supported by the application/library
- UUIDv4 is acceptable where UUIDv7 support is unavailable

Rules:
- IDs are never reused
- human-readable names/slugs are not primary keys
- external provider IDs are never used as platform primary keys
- provider/channel IDs are stored separately and scoped
- public APIs may expose internal UUIDs unless a later threat model requires public aliases

Standard identifiers:
- tenant_id
- workspace_id
- application_id
- agent_id
- channel_id
- subject_id
- subject_identity_id
- conversation_id
- config_version_id
- request_id

## 5. Tenant

A Tenant represents an isolated organization/customer/account boundary.

Examples:
- Nippan internal tenant
- Customer A
- Company B

Required fields:
- tenant_id
- slug
- display_name
- status
- tenant_type
- created_at
- updated_at

tenant_type:
- internal
- customer
- partner
- system

status:
- provisioning
- active
- suspended
- disabled
- archived

Rules:
- tenant slug is unique platform-wide
- suspended tenants cannot start new model/tool work
- archived tenants are read-only until retention/deletion policy runs
- tenant deletion is never a direct hard delete from normal dashboard operations

## 6. Workspace

Workspace is an optional organizational container inside a Tenant.

Use cases:
- departments
- brands
- projects
- customer business units

Required:
- workspace_id
- tenant_id
- slug
- display_name
- status
- created_at
- updated_at

Rules:
- an Application may belong to zero or one Workspace
- Workspace never replaces tenant security scope
- workspace slug is unique inside a tenant

For Nippan's initial deployment, Workspace may remain unused.

## 7. Application

Application is a product/use-case boundary running on the platform.

Examples:
- Personal Assistant
- Nippan Website AI
- Customer LINE Bot
- Slip Application
- future mobile app

Required:
- application_id
- tenant_id
- workspace_id nullable
- slug
- display_name
- application_type
- status
- environment_policy
- created_at
- updated_at

application_type examples:
- assistant
- customer_support
- website
- automation
- extraction
- internal_tool
- custom

Rules:
- every Application belongs to exactly one Tenant
- moving an Application between tenants is prohibited; clone/migrate instead
- all Agents, Channels, conversations, usage and application configuration inherit tenant scope
- an Application can contain many Agents and Channels

## 8. Agent

Agent is a configurable AI role/capability, not a channel and not a model.

Examples:
- Customer Support Agent
- Sales Agent
- SEO Agent
- Slip Reader Agent
- Website Admin Agent

Required:
- agent_id
- tenant_id
- application_id
- slug
- display_name
- role
- status
- created_at
- updated_at

Rules:
- Agent belongs to exactly one Application
- Agent cannot be moved between Applications; clone instead
- model/provider IDs are not stored as immutable Agent identity
- Agent behavior comes from versioned configuration/policies
- Agent does not carry a singular active-config pointer; activation is environment-scoped
- disabling an Agent prevents new executions but keeps historical traces intact

### 8.1 Agent Activation

Agent activation/deployment is separate from stable Agent identity.

Required:
- activation_id
- tenant_id
- application_id
- agent_id
- environment
- config_version_id
- activated_at
- activated_by

Rules:
- zero or one current AgentActivation row exists per Agent + environment; the row itself is the current activation pointer, not an activation-history record
- the referenced config version must be PUBLISHED, belong to the same Tenant/Application/Agent, and its target environment must equal the activation environment
- publish/rollback updates the current activation pointer to a previously published immutable config version
- activation history is recorded in audit events rather than retained as multiple competing activation rows
- changing activation is audited; activating does not mutate the Agent or config version

## 9. Channel

Channel represents an ingress/egress integration.

Examples:
- LINE Messaging API channel
- website widget
- REST API client
- mobile app
- internal webhook

Required:
- channel_id
- tenant_id
- application_id
- channel_type
- display_name
- status
- external_ref nullable
- created_at
- updated_at

channel_type examples:
- line
- web
- api
- mobile
- desktop
- webhook
- internal

Rules:
- channel credentials/secrets are references to secret storage, never plain DB/repo values
- non-null `external_ref` is unique within `tenant_id + application_id + channel_type`
- disabling a Channel blocks new ingress but preserves history

## 10. Agent-Channel Binding

Do not permanently attach one Agent to one Channel.

Use an explicit binding:
- binding_id
- tenant_id
- application_id
- agent_id
- channel_id
- environment
- routing_role
- priority
- enabled
- created_at
- updated_at

routing_role examples:
- default
- specialist
- fallback
- reviewer

Rules:
- binding Agent and Channel must belong to the same Tenant and Application
- at most one enabled default Agent per Channel/environment unless a deterministic router policy says otherwise
- specialist/fallback Agents may coexist

## 11. Subject and Subject Identity

Subject is a tenant-global identity anchor for a person/entity that one or more Applications may serve.

Do not confuse Subject with Tenant dashboard members/operators.

Examples:
- LINE user
- website customer
- internal employee
- API service account being assisted

Subject:
- subject_id
- tenant_id
- canonical_display_name nullable
- status
- created_at
- updated_at

Subject Identity:
- subject_identity_id
- tenant_id
- subject_id
- channel_id
- provider
- external_subject_id
- verified_at nullable
- created_at
- updated_at

Rules:
- `SubjectIdentity` is unique by `tenant_id + channel_id + provider + external_subject_id`
- `subject_id` alone never authorizes cross-Application memory, business-data or personal-data access
- Application-scoped records that reference a Subject must also carry/resolve `application_id` and authorize against the current Application
- a dedicated Subject/Application membership table is not required in v1; association may be derived from Application-scoped Channel/Conversation/data records
- cross-Application Subject data/memory sharing is denied unless a future explicit governed capability permits it
- merging two Subjects is an explicit audited operation; production merge remains disabled until survivor/redirect/unmerge semantics are separately defined
- never auto-merge identities across channels using display name alone
- PII belongs in dedicated governed fields/tables, not identity keys

## 12. Tenant Members / Operators

Control Plane users are separate from Subjects.

TenantMember represents people allowed to configure/operate a tenant.

Minimum relationship:
- tenant_member_id
- tenant_id
- principal_id
- role
- status

Initial role examples:
- owner
- admin
- operator
- analyst
- reviewer
- billing

Authorization details will be defined in the Control Plane authorization contract.

## 13. Conversation

Conversation is a runtime interaction thread.

Required:
- conversation_id
- tenant_id
- application_id
- channel_id
- subject_id nullable
- status
- started_at
- last_activity_at
- closed_at nullable

Optional:
- primary_agent_id
- external_thread_ref
- parent_conversation_id

status:
- active
- waiting
- human_handoff
- closed
- archived

Rules:
- Conversation belongs to exactly one Tenant and Application
- Conversation is bound to one Channel for v1
- multiple Agents may participate over time
- agent participation/handoff must be recorded in events/traces
- historical messages never change tenant/application ownership
- anonymous website sessions may have subject_id null initially and be linked later through an audited operation

## 14. Environment model

Use environment as deployment/configuration context, not identity hierarchy.

Initial values:
- development
- staging
- production

Rules:
- environment is explicit on Agent activation/deployment and AgentChannelBinding; config versions retain their target environment
- tenant/application/agent IDs remain stable across environments when representing the same logical object
- secrets and provider credentials are environment-specific
- production configuration cannot be overwritten by an unpublished draft

## 15. Configuration/version relationship

Mutable AI behavior is versioned separately from stable identity.

Examples:
- Agent identity remains `agent_id=A`
- config versions become A:v1, A:v2, A:v3

Required lifecycle:
```text
DRAFT -> TESTING -> PUBLISHED -> SUPERSEDED
```

Rollback means repointing the Agent + environment activation to a previously published immutable version.

Published config versions are immutable.

## 16. Ownership matrix

| Object | Tenant | Workspace | Application |
|---|---|---|---|
| Tenant | self | - | - |
| Workspace | required | self | - |
| Application | required | optional | self |
| Agent | required | inherited/reference | required |
| AgentActivation | required | inherited/reference | required |
| Channel | required | inherited/reference | required |
| AgentChannelBinding | required | inherited/reference | required |
| Subject | required | - | application-independent within tenant |
| SubjectIdentity | required | - | via Channel |
| Conversation | required | - | required |
| ConfigVersion | required | optional | required/target-specific |
| Usage/Audit | required | optional | required when applicable |

Denormalized tenant_id on child tables is intentional to simplify RLS, auditing and safe queries.

## 17. Isolation rules

Database/runtime enforcement:
1. Every tenant-owned table contains tenant_id.
2. PostgreSQL RLS will be used for tenant-sensitive operational tables unless a documented exception exists.
3. Tenant/Application consistency of references must be enforceable by database constraints (for example composite uniqueness/FKs or an equivalent enforceable mechanism), not prose alone.
4. Runtime establishes tenant context before any tenant query using a pool-safe, transaction-scoped mechanism; tenant context from one request must not leak to another pooled connection.
5. Runtime roles for tenant-protected tables must not be superuser, table owner, or have `BYPASSRLS`. Use `FORCE ROW LEVEL SECURITY` only where the selected ownership/access pattern would otherwise allow owner bypass.
6. Application, Agent, Channel, Conversation, Workspace, Subject and policy references must be validated as belonging to the authorized Tenant/Application scope.
7. Vector/semantic searches always filter tenant_id and application scope where applicable before returning candidates.
8. Cache keys, queues, files and telemetry include tenant scope.
9. Tool execution receives authoritative tenant/application/agent scope from Core, not from model-supplied IDs.
10. No model is trusted to enforce tenant isolation.
11. Cross-tenant admin operations require a separate platform-admin capability and audit event.

## 18. Lifecycle rules

Normal lifecycle:
```text
provisioning -> active -> suspended -> disabled -> archived
```

Not every object needs every state, but:
- disable/suspend is preferred to destructive deletion
- archival preserves audit references
- hard deletion is retention/compliance workflow, not routine CRUD
- foreign historical records must not become orphaned

## 19. Usage and future billing attribution

Every billable/measurable request must be attributable to:
- tenant_id
- application_id
- agent_id when AI executed
- channel_id when channel-originated
- request_id

Track independently:
- model/provider
- input/output/cache tokens where available
- model cost
- tool calls
- storage/processing units where useful
- success/failure
- latency

Billing implementation is deferred, attribution is not.

The immutable usage-event ledger and dedupe semantics are defined by `REQUEST_TRACE_USAGE_CONTRACT_V1.md`; identity/tenancy fields here must remain compatible with that contract.

## 20. Migration considerations

### Existing Personal Assistant
Map to:
- Tenant: Nippan
- Application: Personal Assistant
- Agents: role-based configuration
- Channel: current LINE channel

### Existing Ai-Nippan
Remain independent until migration.
Future adapter maps production traffic to:
- Tenant: Nippan
- Application: Nippan Customer Service
- Channel: existing LINE channel
- Subjects: customers
- Agents: support/sales/order roles as adopted

Do not force legacy database IDs to become platform primary IDs.
Store them as external/legacy references.

## 21. Invariants

These rules must be testable:

1. Child tenant_id must match its parent's tenant_id.
2. Agent and Channel binding cannot cross tenants/applications and binding environment is explicit.
3. Agent activation cannot cross Tenant/Application/Agent scope, is unique as the current row per Agent + environment, and may reference only a PUBLISHED config whose target environment matches the activation environment.
4. Conversation channel must belong to same tenant/application.
5. primary_agent_id, when set, must belong to same application.
6. SubjectIdentity uniqueness is `tenant_id + channel_id + provider + external_subject_id`.
7. Non-null Channel external_ref uniqueness is `tenant_id + application_id + channel_type + external_ref`.
8. A tenant-global Subject never implies cross-Application data/memory authorization.
9. Published config versions are immutable.
10. Suspended tenant cannot initiate model/tool execution.
11. Usage/audit events cannot be written without tenant_id and request_id.
12. Semantic search cannot execute without tenant and applicable application filters.
13. Secrets are references, never contract payload values.

## 22. Explicit non-goals for v1

Not defined here:
- pricing plans
- payment collection
- full RBAC/ABAC implementation
- customer self-service signup
- reseller hierarchy
- cross-tenant shared memory
- global identity graph
- production PostgreSQL DDL

Those require separate contracts/decisions.

## 23. Acceptance checklist

- ownership is unambiguous
- supports one operator and future SaaS tenants
- supports many Agents and Channels per Application
- does not require database redesign for website/app/bot use
- tenant isolation can be enforced at database and runtime layers
- configuration is independently versioned
- usage can be attributed for future billing
- legacy systems can migrate without ID replacement
