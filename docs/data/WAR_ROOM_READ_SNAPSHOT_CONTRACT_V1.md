# War Room Snapshot / Read Contract V1

Status: **FROZEN FOR TRACK D CONSUMPTION**  
Date: 2026-09-23  
Parent findings: Audit #41 N-10  
Parent issues: #35, #49

## Purpose

Freeze the read-side contract before Track D implements snapshot/SSE surfaces.
Track D must consume this contract and must not define a competing wire format,
read-authorization rule, or usage aggregate.

## Wire schemas

Normative JSON schemas:

- `schemas/war-room-event-v1.schema.json`
- `schemas/war-room-snapshot-v1.schema.json`

Serialization rules:

- UUID -> lowercase/standard JSON string with UUID format;
- datetime -> RFC3339 JSON string (`date-time`);
- enum -> canonical contract string value;
- Decimal cost -> base-10 JSON **string**, never binary floating point;
- nullable contract fields -> explicit JSON `null`;
- unknown top-level or payload fields are rejected by the schemas.

## Read authorization

`RoomReadAuthorizer` is the only Core read-authorization boundary for snapshot
and SSE reads.

The request scope is `tenant_id + application_id + room_id + read_kind` and a
server-established `TrustedActorContext` is supplied separately. Request/body/
query data is never accepted as actor authority.

V1 authorization semantics for a future concrete implementation are:

1. actor tenant/application must equal the requested tenant/application;
2. the canonical `principal_type + principal_id` must match an **active**
   `project_room_participants` row for the requested room;
3. OWNER role is **not** required for read access; an active non-owner
   participant may read the room but cannot issue owner commands;
4. missing identity, scope mismatch, missing/inactive participant, database
   failure, or indeterminate result fails closed;
5. the default implementation is `DenyAllRoomReadAuthorizer`; no read endpoint
   may bypass the injected authorizer.

This document freezes semantics only. N-10 does not add a granting database
authorizer or endpoint, so it does not expand the currently reachable
authorization surface.

## Snapshot source-of-truth mapping

All reads are scoped by `tenant_id + application_id + room_id`.

| Snapshot field | Source |
|---|---|
| mode, state | `project_rooms` |
| participants | `project_room_participants`, deterministic order by `created_at, participant_id` |
| agenda | `project_room_agenda_items`, order by `sequence` |
| findings | `project_room_findings`, order by `created_at, finding_id` |
| decisions | `project_room_decisions`, order by `created_at, decision_id` |
| last_sequence | `max(project_room_messages.sequence)`, or 0 when no rows |
| recent_events | `project_room_messages`, ordered by sequence, decoded from the ADR-0008 canonical JSON envelope |
| request set for usage | distinct non-null `project_room_messages.request_id` for the room |
| directional input/output token breakdown | `ai_calls.input_tokens/output_tokens` for the room request set |
| billable/aggregate usage and normalized cost | immutable `usage_events` for the same room request set |

No Track D table, browser counter, cache or materialized aggregate is a usage
source of truth.

## Usage query contract

First derive the room request set without duplicating rows:

```sql
with room_requests as (
  select distinct request_id
  from public.project_room_messages
  where tenant_id = :tenant_id
    and application_id = :application_id
    and room_id = :room_id
    and request_id is not null
)
```

Directional token breakdown is read from model-call telemetry:

```sql
select
  sum(input_tokens) as input_tokens,
  sum(output_tokens) as output_tokens,
  count(*) filter (
    where input_tokens is null or output_tokens is null
  ) as incomplete_calls
from public.ai_calls
where tenant_id = :tenant_id
  and application_id = :application_id
  and request_id in (select request_id from room_requests);
```

Rules:

- when there are zero matching AI calls, directional token counts are 0;
- when any matching call has missing input/output metrics, the producer must not
  guess zero for that call; V1 snapshot production fails closed with a typed
  usage-projection error rather than returning incomplete directional totals;
- a later implementation may add an explicit completeness field only through
  the frozen-contract change process.

Aggregate token/cost truth is read from the immutable UsageEvent ledger:

```sql
select
  event_type,
  unit,
  currency,
  sum(quantity) as quantity,
  sum(normalized_cost) as normalized_cost
from public.usage_events
where tenant_id = :tenant_id
  and application_id = :application_id
  and request_id in (select request_id from room_requests)
  and event_type in ('ai_tokens', 'ai_cost')
group by event_type, unit, currency;
```

Rules:

- UsageEvent is authoritative for rebuildable aggregate/billable usage;
- `ai_calls` is used only for directional input/output breakdown that the
  current UsageEvent shape does not encode;
- provider/normalized cost is never estimated by the snapshot producer;
- multiple non-null currencies in one room snapshot are an error, not a
  conversion opportunity;
- missing provider metrics remain unknown under
  `REQUEST_TRACE_USAGE_CONTRACT_V1.md`; they are never guessed;
- no new usage ledger or aggregate table is permitted for Track D.

## Event replay

SSE replay reads `project_room_messages` with:

```sql
where tenant_id = :tenant_id
  and application_id = :application_id
  and room_id = :room_id
  and sequence > :after_sequence
order by sequence asc
```

The SSE `id` is the durable sequence. PostgreSQL remains authoritative after
reconnect; browser state is disposable.

## Change control

Any change to wire field names, enum encodings, Decimal representation, read
authorization semantics, or usage source-of-truth mapping requires integration
review. Schema/RLS/grant changes or a materially different authorization model
remain immediate-audit triggers under `AUDIT_SYSTEM_V1.md`.
