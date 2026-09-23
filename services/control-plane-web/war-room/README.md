# War Room Control Plane Surface

This directory contains the dependency-free Track D browser surface for
`/war-room`.

## Boundary

The browser is a projection and command client only. It:

- reads the frozen `RoomSnapshot` JSON shape;
- consumes ordered SSE events using the durable room sequence;
- posts owner/lifecycle `RoomCommand` values;
- renders roster, messages, agenda, findings, decisions and usage.

It does **not** schedule agents, invoke `run_next_turn`, select models, enforce
authorization, enforce budgets, or hold OpenRouter credentials.

Authentication/actor identity remains server-established. The browser uses
same-origin credentials and never sends a principal identity as authority.

## Hosting

This is intentionally framework-free V1 surface code. The repository has not
yet frozen a dashboard framework or production hosting topology. A future
Control Plane host may mount these assets at `/war-room` without changing the
wire contract.

No production deployment is authorized by this directory.


## Local development preview

The Core service can mount the War Room UI plus snapshot/SSE/owner-command
transport for local development only. It is disabled by default and is never
mounted when `NIPPAN_ENVIRONMENT=production`.

Required server-side settings:

```text
NIPPAN_WAR_ROOM_PREVIEW_ENABLED=true
NIPPAN_WAR_ROOM_PREVIEW_LOCAL_ONLY=true
NIPPAN_WAR_ROOM_PREVIEW_TENANT_ID=<tenant UUID>
NIPPAN_WAR_ROOM_PREVIEW_APPLICATION_ID=<application UUID>
NIPPAN_WAR_ROOM_PREVIEW_PRINCIPAL_ID=<active HUMAN OWNER principal_id>
```

The configured principal is server-established; the browser cannot supply or
override tenant/application/principal authority. Database-backed room
authorization still requires that principal to be an active room participant,
and owner commands still require the active OWNER row.

The preview exposes only:

- `GET /war-room/` for the UI;
- `GET /war-room/rooms/{room_id}/snapshot`;
- `GET /war-room/rooms/{room_id}/events` using SSE replay/tail;
- `POST /war-room/rooms/{room_id}/commands` for owner/lifecycle commands.

There is deliberately no turn/tick/auto-advance endpoint. The transport's model
and budget dependencies are disabled sentinels, so the preview command surface
cannot invoke a provider. Owner commands register their request trace in the
existing `requests` table and persist through the existing War Room event sink;
no new ledger, migration, schema, RLS or grant is introduced.

With `NIPPAN_WAR_ROOM_PREVIEW_LOCAL_ONLY=true`, HTTP access is limited to the
loopback client. This preview is not a production authentication mechanism.
