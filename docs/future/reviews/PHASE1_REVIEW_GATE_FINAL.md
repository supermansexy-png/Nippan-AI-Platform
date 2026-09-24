# Phase 1 Review Gate — Final Project Lead Decisions

Status: **PASSED — FROZEN V1**  
Date: 2026-09-22  
Scope: Issues #12, #13, #14, #15

## Review basis

The Project Lead compared:
- the existing Project Lead reviews on #12, #13 and #14,
- an independent Claude Opus 5 advisor pass through OpenRouter,
- a targeted Google Gemini second opinion on disputed prescriptions,
- the Foundation, ADRs, Markdown contracts and JSON Schemas.

Model output is advisory evidence only. The decisions below are the Project Lead synthesis.

The accepted Foundation Architecture remains in force. No Foundation rewrite and no PostgreSQL DDL/runtime implementation is authorized until this gate is re-reviewed.

## Final gate decisions

### 1. Environment-aware Agent activation and binding

**Decision: CONFIRMED.**

- Stable Agent identity is environment-independent.
- Remove the singular `Agent.active_config_version_id`.
- Add an explicit activation/deployment relationship keyed by Agent + environment.
- An activation may point only to an immutable published config for the same Tenant/Application/Agent and compatible environment.
- Exactly one active config exists per Agent + environment.
- Rollback repoints that environment's activation; it does not mutate/copy the old config.
- `AgentChannelBinding` gains an explicit environment because its default-Agent invariant is environment-qualified.
- At most one enabled default binding exists per Channel + environment unless a separately defined deterministic router policy owns selection.

### 2. Immutable/versioned policy references

**Decision: CONFIRMED.**

- Every policy reference inside a published Agent Config resolves to an immutable policy version, never a mutable policy identity.
- Policy versions are same-Tenant/Application unless explicitly marked platform-shared and immutable.
- Publish resolves a reproducible effective policy/config snapshot and hash.
- Mutable provider/model capability metadata cannot silently change the historical meaning of a published effective configuration; runtime traces still record the actual provider/model used.

### 3. Deterministic policy merge and budget enforcement

**Decision: CONFIRMED, expanded with the missing concurrency rule.**

Canonical merge semantics:
- allowlists/capability sets -> intersection,
- denylists/blocks -> union,
- upper bounds/quotas/budgets -> minimum,
- boolean permission grants -> logical AND across applicable parents,
- mandatory controls/approval requirements -> strongest applicable requirement,
- runtime hints may only narrow,
- unknown policy fields/flags cannot widen permissions.

Hard budgets/quotas must not use an unsafe check-then-act flow. Runtime must use an atomic reservation/accounting approach (implementation is deferred) and reconcile final usage/cost after execution.

### 4. Database-enforceable scope integrity and RLS execution model

**Decision: CONFIRMED with precision.**

- Tenant/Application consistency of references must be DB-enforceable with composite constraints/FKs or an equivalent enforceable mechanism.
- Runtime DB roles must not be superuser, table owner for protected tenant tables, or have `BYPASSRLS`.
- `FORCE ROW LEVEL SECURITY` is required only where the selected ownership/access pattern would otherwise let an owner bypass RLS; it is not a universal requirement.
- Tenant context must be transaction/pool safe and cannot persist accidentally across pooled requests.
- RLS is defense in depth; application authorization remains required.

### 5. Subject scope

**Decision: TENANT-GLOBAL SUBJECT, application-scoped data access.**

- `Subject` remains a tenant-global identity anchor.
- `subject_id` alone never grants cross-Application data/memory access.
- Conversations, memories, business data, usage and other Application-owned records must carry/resolve `application_id` and authorize against the current Application.
- Subject/Application association may be inferred from Application-scoped records in v1; a mandatory `subject_application_link` table is not required by this contract.
- Cross-Application data/memory sharing requires a future explicit governed capability.
- Subject merge remains explicit/audited; until survivor/redirect/unmerge semantics are separately defined, production merge functionality must remain disabled.

### 6. Trusted authorization context for MCP/tools

**Decision: CONFIRMED.**

Core establishes authoritative execution context containing at least request, Tenant, Application, Agent, environment/principal and effective config/policy identity. MCP/tools independently verify that context and effective permissions. IDs supplied by the model, prompt, or arbitrary request payload are never accepted as authority.

Transport may use authenticated internal context or a server-side lookup; a specific token/signature mechanism is an implementation decision.

### 7. W3C/OpenTelemetry trace format and request-envelope scope

**Decision: CONFIRMED.**

- `request_id` remains platform UUID.
- `trace_id` is 32 lowercase hex characters representing 16 bytes and is not all-zero.
- `span_id` is 16 lowercase hex characters representing 8 bytes and is not all-zero.
- Async/queue work supports causal trace links in addition to parent-child relationships.
- Retries create separate attempts/spans while preserving the logical request/trace where appropriate.
- `application_id` and `channel_id` are conditionally required by request kind; fake IDs are forbidden.
- The transport envelope carries a status snapshot (`status_at_emit`); mutable current request status belongs to the operational request record.

### 8. Durable idempotency and provider-event dedupe

**Decision: CONFIRMED with transport-neutral semantics.**

- Side-effect uniqueness scope is Tenant + scope + operation + idempotency key.
- Reservation/check is atomic before the side effect.
- A duplicate in-flight request must not execute the side effect again.
- A completed duplicate reuses/references the prior successful result where supported.
- Same key with materially different operation/request identity is a conflict.
- Expiry and safe retry rules are explicit.
- Provider `event_id` dedupe is ingress-event dedupe and is separate from side-effect `idempotency_key`.
- HTTP 409 is not mandated; transport-specific duplicate responses are implementation policy.

### 9. Immutable usage-event ledger

**Decision: CONFIRMED.**

Define immutable `UsageEvent` records with:
- `usage_event_id`, `occurred_at`,
- Tenant/Application/request attribution,
- Agent/Channel/Subject/Conversation when applicable,
- event type, quantity, unit,
- source/call reference,
- provider/model/tool metadata when applicable,
- provider-reported and normalized cost kept separate,
- currency and pricing/rate version for calculated cost,
- dedupe key/semantics.

Billing aggregates are rebuildable from immutable events and do not double count retry/replay attempts.

### 10. Markdown / JSON Schema normativity and alignment

**Decision: CONFIRMED.**

- Markdown contracts are normative for domain semantics/invariants.
- JSON Schemas are normative for the serialized structures they describe.
- A conflict is a contract defect and must be resolved before freeze.
- Schemas must include the lifecycle/audit/scope fields they claim to validate and conditional requirements where request kind changes scope.

### 11. Privacy-safe telemetry fingerprinting/minimization

**Decision: CONFIRMED WITH MODIFICATION.**

- Plain unsalted/unkeyed hashes are not treated as redaction for low-entropy sensitive data.
- `SECRET_CREDENTIAL` values are never logged, hashed or included in telemetry fingerprints.
- Sensitive values are omitted/redacted by default.
- Where correlation is justified and policy allows it, use canonicalized HMAC-SHA-256 with a platform-managed rotating secret, domain separation including Tenant/field purpose, and `hash_key_id`.
- A separate per-Tenant HMAC key is not required in v1.
- Telemetry minimization is driven by privacy class.

## False positives / over-prescriptions removed

The final gate does **not** require:
- HTTP 409 for every in-flight idempotency collision,
- `FORCE RLS` on every protected table when runtime is already a non-owner/no-BYPASSRLS role,
- a dedicated `subject_application_link` table,
- a separate HMAC key per Tenant.

The prior concern about Channel external-ref uniqueness vs SubjectIdentity uniqueness is clarified as two different object constraints rather than a direct contradiction.

## Important items folded into the gates

The following were valid but do not need separate gates:
- exact Channel and SubjectIdentity external-reference uniqueness keys,
- frozen TESTING/PUBLISHED config snapshots,
- version uniqueness within Agent/environment,
- canonical memory cross-Agent scope,
- atomic quota reservation/reconciliation,
- registered feature-flag validation,
- async trace links and retry attempt semantics,
- pricing/rate version on normalized cost,
- telemetry retention/minimization classes,
- canonical source/service/operation naming.

## Safe to defer

- invoice/payment implementation,
- customer self-service onboarding,
- public ID aliases,
- dedicated observability vendor,
- Redis/Kubernetes/extra microservices,
- exact Dashboard visuals,
- exact retention durations if retention classes/hooks exist,
- advanced cross-tenant/global identity graph,
- dedicated Subject/Application membership table unless a later feature requires it,
- exact internal cryptographic transport for trusted MCP context.

## Gate exit criteria

Phase 1 can freeze only after:
1. the three Markdown contracts and related JSON Schemas are updated,
2. schemas validate as JSON Schema documents and example invariants are internally consistent,
3. an independent re-review checks the revised artifacts,
4. Project Lead resolves remaining findings and records the final acceptance.

No PostgreSQL DDL/runtime implementation before those conditions pass.

## Independent re-review result

Claude Opus 5 was re-run through OpenRouter against the revised artifacts:

- Identity/Tenancy contract + schema: **PASS**, no blockers. Generation `gen-1790094428-sZGxccA0kUCwcGWkZwqS`.
- Agent Policy contract + schema (with Identity activation cross-check): **PASS**, no blockers. Generation `gen-1790094463-4XcPDabfPtZz5ayG5cex`.
- Request/Trace/Usage contract + request/usage schemas: **PASS**, no blockers. Generation `gen-1790094484-dWSv2Zwc2XHrZvHRFdRc`.

Targeted Google Gemini 3.1 Pro review was used earlier to distinguish objective requirements from implementation choices for W3C trace IDs, RLS/FORCE RLS, idempotency response semantics, telemetry HMAC keying and Subject/Application association.

Structural checks on all four JSON Schemas after revision found:
- valid JSON parsing,
- Draft 2020-12 declarations,
- no unresolved local `$ref` targets,
- no `required` names missing from their local `properties`,
- expected top-level conditional/oneOf structure.

A full external JSON-Schema metaschema validator could not be run from the local container because that runtime could not resolve GitHub; the independent advisor re-review found no schema blocker.

## Freeze decision

The 11 Phase 1 review gates are satisfied at contract/schema level. The three contracts are marked **ACCEPTED / FROZEN V1** on the review branch.

Freeze does **not** authorize bypassing the next implementation boundary: PostgreSQL DDL and RLS must still be designed together from these frozen contracts, and any implementation-discovered contradiction must reopen the relevant contract rather than silently changing semantics.
