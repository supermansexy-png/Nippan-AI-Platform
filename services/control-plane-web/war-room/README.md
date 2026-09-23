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
