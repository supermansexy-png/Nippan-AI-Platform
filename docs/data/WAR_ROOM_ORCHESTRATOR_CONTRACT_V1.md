# War Room Orchestrator Contract V1

Status: FROZEN FOR INCREMENT C
Date: 2026-09-23
Parent: Issue #30
Contract task: Issue #31

## Purpose

This contract is the single interface shared by the Increment C backend,
model/budget, verification and frontend tracks. A track must not introduce a
competing room state, command, event or usage contract.

## Authority boundaries

- PostgreSQL remains the room and message system of record.
- The Core service owns lifecycle transitions and scheduling decisions.
- The browser projects ordered events and sends owner commands; it does not
  schedule agents, authorize participants or enforce budgets.
- Agent configuration resolves `model_policy_ref`; no War Room component
  contains a production model ID.
- `requests`, `ai_calls` and immutable `usage_events` remain the trace and
  token/cost sources of truth. War Room budgets read correlated usage and do
  not create another usage ledger.
- A model may suggest actions but cannot change room state or extend a budget.

## Correlation

Every automatic turn carries the following immutable scope:

- `tenant_id`
- `application_id`
- `room_id`
- `agenda_item_id`
- `request_id`
- W3C-compatible 32-character lowercase hexadecimal `trace_id`

The `request_id` is stored on an automatic room message and joins to platform
request, AI call and usage evidence. Retries retain the room/agenda scope but
receive the request identity defined by the platform request contract.

## Commands

The owner/control plane may submit:

- `PREPARE`, `START`, `PAUSE`, `RESUME`, `STOP`
- `ASK_ROLE`, `ASK_ALL`
- `REQUEST_OWNER_DECISION`, `SUBMIT_OWNER_DECISION`
- `BEGIN_SUMMARY`, `CLOSE`

Commands include `expected_state`. The service rejects a stale command rather
than silently applying it to a different lifecycle state. `ASK_ROLE` requires
a target role. Owner content may be bounded inline text or a durable reference.

Every V1 room command is owner-authorized. The command payload is not authority:
Core supplies a separate trusted actor context containing `tenant_id`,
`application_id`, canonical `principal_type + principal_id`, and the
authorizer binds that actor to the command's tenant/application/room scope.
Authorization succeeds only for the active OWNER participant recorded in
`project_room_participants`; scope mismatch or missing ownership fails closed
before any room-state mutation or owner message append.

## Ordered events

The service emits monotonically ordered room events:

- `ROOM_STATE_CHANGED`
- `TURN_SCHEDULED`
- `SCHEDULER_HALTED`
- `MESSAGE_APPENDED`
- `OWNER_DECISION_REQUIRED`
- `BUDGET_HARD_STOP`
- `TURN_FAILED`

Each event has a positive room sequence and the complete correlation context.
The durable sequence is allocated by the PostgreSQL persistence layer, not by
an in-memory room session. War Room V1 maps the ordered event stream onto the
existing `project_room_messages` table as defined in ADR-0008. State-changing
events update `project_rooms` and append the ordered message/event in one
tenant-scoped transaction. Realtime delivery may reconnect and replay from the
last observed sequence; delivery transport does not become the source of truth.

## Model gateway

`ModelGateway.generate_turn(ModelTurnRequest) -> ModelTurnResult` is the only
Increment C model boundary. Requests identify a `model_policy_ref`, role,
agenda objective and selected context references. Results return displayable
content plus provider usage. Provider/model selection is configuration-owned.

The adapter must support bounded timeout and retry behavior. A formal Auditor
identity must never be silently replaced by fallback routing.

## Budget authority

`BudgetAuthority` authorizes a turn before provider invocation and records its
usage afterward through the platform usage owner. Enforcement covers room,
agenda and participant token/cost limits.

When a hard limit is reached:

1. do not invoke the model;
2. append `BUDGET_HARD_STOP`;
3. halt automatic scheduling;
4. move the room to `NEEDS_OWNER_DECISION` when owner action is required;
5. require an explicit owner/config action to extend a limit.

## Orchestration invariants

- only `RUNNING` rooms schedule automatic turns;
- default and maximum automatic round limit is two for V1;
- no participant can directly trigger itself;
- a completed participant is not scheduled twice in one round;
- pause, stop and owner-decision state halt scheduling before model invocation;
- the Chair failing pauses the room; it does not release uncontrolled turns;
- exactly one state transition is committed for an accepted command;
- Builder/Auditor independence remains enforced by the database and contracts.

## Frontend projection

`/war-room` consumes a room snapshot and ordered events. The minimum projection
contains roster, state, agenda, ordered messages, findings, decisions and
token/cost totals derived from platform usage. Controls map one-to-one to the
commands above. Optimistic UI may show pending intent but authoritative state
comes back from the Core service.

## Failure policy

- timeout and provider errors produce `TURN_FAILED` with a stable failure kind;
- retry count and backoff are configuration, not model decisions;
- retry occurs only while state remains `RUNNING` and budget still authorizes;
- invalid responses are not persisted as successful agent messages;
- database/event persistence failure halts the turn before another agent runs.

## Change control

Downstream tracks may add implementation details behind these interfaces.
Changing state semantics, authorization, schema/RLS, usage ownership or the
public command/event shapes requires integration review. Major architecture,
security/authorization or PostgreSQL/schema/RLS changes trigger immediate
Independent Audit under `AUDIT_SYSTEM_V1`.
