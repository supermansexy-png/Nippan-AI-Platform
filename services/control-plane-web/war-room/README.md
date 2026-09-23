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

By default, development HTTP access remains limited to the loopback client.
Remote preview is a separate, explicit gate and remains disabled unless all of the
following server-side settings are configured:

```text
NIPPAN_WAR_ROOM_PREVIEW_REMOTE_ACCESS_ENABLED=true
NIPPAN_CLOUDFLARE_ACCESS_TEAM_DOMAIN=https://<team>.cloudflareaccess.com
NIPPAN_CLOUDFLARE_ACCESS_AUDIENCE=<Access application AUD tag>
NIPPAN_CLOUDFLARE_ACCESS_OWNER_EMAIL=<exact owner email>
```

For every non-loopback War Room request, Core requires the
`Cf-Access-Jwt-Assertion` header, fetches Cloudflare Access signing keys from
the configured team domain, verifies the RS256 signature plus issuer/audience
and token lifetime claims, requires an Access application token, and requires
an exact owner-email match. A verified remote request is then mapped to the
same server-configured preview principal; tenant/application/principal scope is
never accepted from the browser.

Signing keys are cached briefly and refreshed when the key id/signature requires
it. Missing or invalid remote auth fails closed with HTTP 403. Provider/model
turns remain disabled.

Cloudflare reference:
https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json/

This is still a development/preview authentication path, not production traffic
authorization.


### Seed a complete local room

After applying the repository migrations to a local development PostgreSQL
database, the preview can seed a deterministic room with one Project Owner and
seven AI-role participants (Chair, Architect, Builder, Security, Cost & Ops,
Independent Auditor and Secretary), plus an agenda, finding and proposal.

Run from `services/core`:

```bash
export NIPPAN_ENVIRONMENT=development
export NIPPAN_WAR_ROOM_PREVIEW_ENABLED=true
export NIPPAN_WAR_ROOM_PREVIEW_SEED_ADMIN_DSN='postgresql://...local-admin...'
python scripts/seed_war_room_preview.py
```

The script refuses non-development environments and prints the exact
`NIPPAN_WAR_ROOM_PREVIEW_*` scope plus a loopback URL. The default deterministic
room URL ends with:

```text
/war-room/?room_id=c3333333-3333-4333-8333-333333333333
```

The seed contains no provider credentials and creates no model calls. Pressing
owner controls exercises only durable lifecycle/owner-message paths until a
separately governed turn driver is introduced.


### Render preview database bootstrap

For an isolated development preview database, Core can apply the already-reviewed
repository migrations and seed the deterministic preview room at startup.

Required settings:

```text
NIPPAN_ENVIRONMENT=development
NIPPAN_DATABASE_URL=<isolated preview database URL>
NIPPAN_WAR_ROOM_PREVIEW_ENABLED=true
NIPPAN_WAR_ROOM_PREVIEW_BOOTSTRAP=true
```

Bootstrap behavior is fail-closed:

- a completely empty database receives only the existing reviewed migration files,
  in repository order, after the same Supabase-compatibility role/schema preparation
  used by CI;
- an already-complete database skips migration replay;
- a partially initialized database is rejected instead of being repaired or guessed;
- the deterministic preview room is seeded only when absent, so service restarts do
  not reset durable room state;
- bootstrap refuses any non-development environment.

This does not expose the preview remotely and does not enable provider/model turns.
