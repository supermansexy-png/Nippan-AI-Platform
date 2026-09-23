# ADR-0008 — War Room Durable Event Persistence

Status: Accepted for Audit #41 remediation  
Date: 2026-09-23  
Parent: Issues #41 and #42

## Decision

War Room V1 will **not** add a separate events table.

The existing `public.project_room_messages` table is the durable ordered event
stream for room replay. Its existing per-room unique `sequence` and message
types `SYSTEM_EVENT`, `BUDGET_WARNING`, and `ERROR` are sufficient to
represent non-chat orchestration events without introducing a duplicate source
of truth.

## Event mapping

- owner/agent/chair display events use their existing message type;
- lifecycle, scheduling and scheduler-halt events persist as `SYSTEM_EVENT`;
- hard budget stops persist as `BUDGET_WARNING`;
- turn failures persist as `ERROR`;
- `content_text` contains a canonical JSON event envelope with event type,
  trace ID, state, halt reason and payload;
- `request_id`, room/agenda scope, participant, sequence and created time use
  the existing typed columns.

The message row's `message_id` is the durable event ID.

## Ordering

The runtime locks the scoped `project_rooms` row before allocating the next
message sequence. While holding that lock it reads
`max(project_room_messages.sequence) + 1`. All Core War Room event writers
must use this persistence path. The database unique constraint on
`tenant_id + application_id + room_id + sequence` remains the final guard.

The in-memory `RoomSession` no longer owns event sequence.

## Atomic state transitions

When an event changes room state, one tenant-scoped database transaction:

1. locks the room row;
2. verifies the durable state matches `expected_state`;
3. updates `project_rooms.state` and lifecycle timestamps;
4. allocates the next durable sequence;
5. inserts the event into `project_room_messages`.

The in-memory session mutates only after this transaction succeeds. A
persistence failure therefore cannot leave the service session advanced while
the durable event is missing.

## Security and privileges

No new schema, role or grant is required. Increment B already grants
`nippan_runtime` UPDATE on `project_rooms`, INSERT on
`project_room_messages`, and tenant/application RLS for both.

## Consequences

- no new migration or RLS surface;
- reconnect/replay can use ordered `project_room_messages`;
- UI transport remains a projection, not a source of truth;
- future high-volume requirements may justify a dedicated event table, but that
  would be a new schema decision and an immediate audit trigger.
