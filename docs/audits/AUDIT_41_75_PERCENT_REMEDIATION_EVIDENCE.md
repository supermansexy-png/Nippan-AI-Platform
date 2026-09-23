# Audit #41 — 75% War Room Increment C Remediation Evidence

Status: READY FOR INDEPENDENT RE-REVIEW AFTER FINAL EXACT-HEAD CI  
Date: 2026-09-23  
Parent audit: Issue #41  
Remediation tracker: Issue #42  
Milestone: Issue #30

## Independent audit disposition received

The 75% Independent Audit inspected the GitHub repository rather than relying
on the project summary and returned **BLOCKED**.

Auditor/model reported by the audit run: `claude-opus-5.5` via OpenRouter.
This exact identifier is recorded because it differs from the earlier project
label "Claude Opus 5".

Track D Issue #35 remains blocked until independent re-review permits
advancement.

## F-01 — Required CI did not run Increment C tests

Disposition: REMEDIATED, pending independent closure.

PR #43 changed the required `postgres-regression` check to install the Core
package and execute:

```sh
python -m pytest -q tests/test_war_room_*.py
```

Evidence:
- PR #43 head: `ba3464a95900b30f43fdaa4b0b34939c59db23f1`
- CI run: `35805641049` — SUCCESS
- merge commit: `cb047dffdc0e3701f1d09cba506d5d5896fe3f44`

## F-04 — Owner command authorization / scope binding

Disposition: REMEDIATED, pending independent closure.

PR #44:
- introduced server-established `TrustedActorContext`;
- requires `RoomCommandAuthorizer` before room mutation;
- binds tenant + application + room + canonical principal type/id;
- authorizes only the active OWNER in the existing
  `project_room_participants` table;
- fails closed before state mutation;
- added scope mismatch and non-owner tests;
- added no schema/RLS change.

Evidence:
- PR #44 head: `0301dc2860b4edb9e73c44fe6f6fcaed4af8c930`
- CI run: `35805945927` — SUCCESS
- merge commit: `a61130eb3cc211a62e97cd930355611f5c00383a`

## F-05 — Durable source of truth / atomic state and event persistence

Disposition: REMEDIATED, pending independent closure.

Decision: no new events table. ADR-0008 reuses the existing
`project_room_messages` table as the durable ordered event stream.

PR #45:
- removed in-memory sequence authority;
- locks the scoped `project_rooms` row;
- verifies expected durable state;
- updates room state and inserts the ordered event in one transaction;
- allocates sequence under the room lock and relies on the existing unique
  per-room sequence constraint;
- mutates the in-memory session only after persistence succeeds;
- added durability/conflict/persistence-failure tests;
- reused existing grants and RLS; no schema change.

Evidence:
- PR #45 head: `852aa0618e343dec051b2d05926f01a2d976853d`
- CI run: `35806412270` — SUCCESS
- merge commit: `5e5c4c6c2a5ea0695199d29dc2b3ae69f4bb61a2`

## F-06 — Snapshot and realtime contract missing

Disposition: REMEDIATED, pending independent closure.

ADR-0009 freezes V1 transport as:
- typed `RoomSnapshot`;
- SSE for ordered server-to-browser events;
- durable sequence as SSE replay cursor;
- authenticated HTTP POST for owner commands;
- trusted actor identity supplied separately by server auth;
- no WebSocket/polling requirement for V1.

PR #46 added snapshot types, scope/cursor invariants and contract tests only.
No endpoint/frontend implementation was started.

Evidence:
- PR #46 head: `bdf35acfc209b7920c20785450036fe5380309a2`
- CI run: `35806603488` — SUCCESS
- merge commit: `dac4c31c320fe8cabbd55473f10c91879dbd4b11`

## F-02 — Budget fail-open / retry spend / race

Disposition: REMEDIATED, pending independent closure.

PR #47 makes War Room V1 cost-first and fail-closed:
- one application-level billable OpenRouter request per automatic turn;
- no automatic second model request on timeout/rate-limit/provider failure;
- provider redundancy may remain inside OpenRouter provider routing for the
  configured primary model;
- explicit `max_tokens` is sent, bounded by both model policy and remaining
  room/agenda/participant token allowance;
- successful provider responses must contain prompt tokens, completion tokens
  and cost; missing/invalid usage is an accounting failure, never zero;
- a PostgreSQL transaction-scoped advisory lock serializes each room across
  budget check -> provider request -> usage recording -> event persistence;
- no duplicate reservation/usage ledger and no schema change.

Evidence:
- PR #47 head: `9238a98afb8ccaa725722ccd9a1e1670b50504ac`
- CI run: `35807195835` — SUCCESS
- merge commit: `9ac28336af8e2f71d467df87344841486436948e`

## F-03 — Failed participant retry loop

Disposition: REMEDIATED, pending independent closure.

PR #48:
- adds `PARTICIPANT_FAILURE_LIMIT_REACHED`;
- one failed automatic provider turn exhausts that participant's automatic
  failure allowance for the room;
- failed participants are excluded from later automatic scheduling;
- non-Chair failure enters `NEEDS_OWNER_DECISION`;
- Chair failure pauses the room;
- after owner resume, only healthy participants may continue;
- if every automatic participant is failed, the scheduler halts with no new
  provider call;
- durable TURN_FAILED events record the failure limit and
  `automatic_retry_allowed=false`;
- contract requires failure caps to be restored from durable failure events on
  session reconstruction.

Pre-evidence before this packet commit:
- PR #48 head: `c80f6095f30152849c16d49b20b514acc2b73677`
- CI run: `35807523049` — SUCCESS

A new exact-head CI run is required after this evidence packet commit. The final
PR #48 head and that final CI run are the preferred re-audit verification
target.

## Production boundary

Across F-01/F-04/F-05/F-06/F-02/F-03 remediation:
- no Supabase production application;
- no production deployment;
- no production provider/model call;
- no n8n production change;
- no `supermansexy-png/Ai-Nippan` change;
- no new PostgreSQL schema/RLS migration.

## Re-review request

The Independent Auditor should verify repository evidence and independently
decide whether each F-01/F-02/F-03/F-04/F-05/F-06 finding is closed and whether
Track D Issue #35 may proceed.

Builder self-approval remains prohibited.
