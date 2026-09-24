# ADR-0009 — War Room Realtime Transport and Snapshot Contract

Status: Accepted for Audit #41 remediation  
Date: 2026-09-23  
Parent: Issues #41 and #42

## Decision

War Room V1 uses **Server-Sent Events (SSE)** for server-to-browser live room
events and ordinary authenticated HTTP POST requests for owner commands.

WebSocket is not required for V1.

## Why

- the data plane is naturally server-to-client for ordered room events;
- owner actions are discrete commands and fit normal HTTP requests;
- SSE supports automatic reconnect and a sequence cursor without introducing a
  separate bidirectional connection protocol;
- this keeps infrastructure, operational cost and failure surface smaller;
- durable ordering already exists in `project_room_messages.sequence`.

## Snapshot

The Core/control-plane boundary exposes a typed `RoomSnapshot` containing:

- tenant/application/room scope;
- room mode and authoritative state;
- `last_sequence` replay cursor;
- participant roster;
- agenda;
- findings;
- decisions;
- token/cost usage projection from platform usage evidence;
- a bounded recent ordered-event window for initial rendering.

A snapshot event must belong to the same tenant/application/room scope and must
not exceed `last_sequence`.

## HTTP/SSE contract

### Snapshot

`GET /war-room/rooms/{room_id}/snapshot`

Returns the typed `RoomSnapshot`. Authentication establishes the trusted
tenant/application actor scope; those values are not accepted as authority from
query/body parameters.

### Event stream

`GET /war-room/rooms/{room_id}/events`

Response: `text/event-stream`.

Cursor rules:

- client may send `Last-Event-ID: <sequence>`;
- alternatively `after_sequence=<sequence>` may be used on first connect;
- server replays durable events with `sequence > cursor` before tailing new
  committed events;
- SSE `id` is the durable room sequence;
- SSE event name is the War Room event type;
- payload is the serialized `OrderedRoomEvent`.

Reconnect never changes the source of truth: PostgreSQL replay does.

### Commands

`POST /war-room/rooms/{room_id}/commands`

Body contains the typed `RoomCommand` fields only. Trusted actor identity comes
from server authentication/session context and is passed separately to the
Core authorizer. A client cannot self-assert OWNER identity or tenant/application
scope.

## Authorization

Snapshot, stream and command surfaces all require the same tenant/application/
room authorization boundary. SSE transport itself grants no authorization.

## Consequences

- no WebSocket infrastructure in V1;
- no polling loop for normal live updates;
- reconnect/replay uses the durable sequence from ADR-0008;
- the browser remains a projection and command client, not scheduler/budget/
  authorization authority;
- transport can be revisited later only with measured need.


## N-10 wire/read contract freeze

Track D consumes the normative machine-readable wire contracts:

- `schemas/war-room-event-v1.schema.json`
- `schemas/war-room-snapshot-v1.schema.json`

Read authorization and snapshot source-of-truth mapping are frozen in
`docs/data/WAR_ROOM_READ_SNAPSHOT_CONTRACT_V1.md`. Snapshot/SSE reads must
pass `RoomReadAuthorizer`; the default implementation is deny-all. This ADR
does not authorize a browser or endpoint to infer its own read policy.
