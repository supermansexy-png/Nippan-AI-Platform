# Platform Identity & Tenancy Contract v1

Status: **REVIEW**  
Issue: #7  
Date: 2026-09-22

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
- active_config_version_id nullable
- created_at
- updated_at

Rules:
- Agent belongs to exactly one Application
- Agent cannot be moved between Applications; clone instead
- model/provider IDs are not stored as immutable Agent identity
- Agent behavior comes from versioned configuration/policies
- disabling an Agent prevents new executions but keeps historical traces intact

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
- provider external IDs are unique within their provider/application scope
- disabling a Channel blocks new ingress but preserves history

## 10. Agent-Channel Binding

Do not permanently attach one Agent to one Channel.

Use an explicit binding:
- binding_id
- tenant_id
- application_id
- agent_id
- channel_id
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

Subject is the person/entity that an Application serves.

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
- external IDs are unique within tenant + channel + provider
- merging two Subjects is an explicit audited operation
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
- environment is attached to config versions/deployments/bindings where necessary
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

Rollback means repointing the active config to a previously published immutable version.

Published config versions are immutable.

## 16. Ownership matrix

| Object | Tenant | Workspace | Application |
|---|---|---|---|
| Tenant | self | - | - |
| Workspace | required | self | - |
| Application | required | optional | self |
| Agent | required | inherited/reference | required |
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
3. Runtime establishes tenant context before any tenant query.
4. Application and Agent IDs must be validated as belonging to current tenant.
5. Vector/semantic searches always filter tenant_id before returning candidates.
6. Cache keys, queues, files and telemetry include tenant scope.
7. Tool execution receives tenant/application/agent scope explicitly.
8. No model is trusted to enforce tenant isolation.
9. Cross-tenant admin operations require a separate platform-admin capability and audit event.

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
2. Agent and Channel binding cannot cross tenants/applications.
3. Conversation channel must belong to same tenant/application.
4. primary_agent_id, when set, must belong to same application.
5. SubjectIdentity external ID uniqueness is provider/channel scoped.
6. Published config versions are immutable.
7. Suspended tenant cannot initiate model/tool execution.
8. Usage/audit events cannot be written without tenant_id and request_id.
9. Semantic search cannot execute without tenant filter.
10. Secrets are references, never contract payload values.

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
