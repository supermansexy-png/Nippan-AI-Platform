# Nippan AI War Room V1 — Implementation Plan

Status: INCREMENT A AUTHORIZED / INCREMENTS B-F GATED
Date: 2026-09-23
Parent design issue: #19
Governance dependency: Phase 2 Independent Audit #18 — RESOLVED

This plan decomposes the accepted design work into small implementation increments. Audit #18 is resolved. Increment A is authorized because it is deterministic contract work with no network/model calls and no schema migration. Increment B design may proceed, but schema/RLS migration or application requires an immediate Independent Audit. Increments C-F remain gated by their prerequisite increments and normal audit controls.

## Increment A — Contracts and orchestration rules

Deliver:
- typed room modes and room states
- participant role contract
- message/event types
- deterministic turn scheduler contract
- round/budget/owner-decision rules
- auditor independence invariant
- tests for state transitions and loop prevention

Exit:
- no network/model calls required
- deterministic contract tests pass
- no schema migration required

## Increment B — PostgreSQL logical schema + RLS review

Deliver:
- exact tables/columns/constraints derived from proposal
- tenant/application ownership rules
- references to existing request/trace/usage records
- retention/content-reference decision
- RLS policies
- isolation/invariant test plan
- migration rollback plan

Exit:
- schema is independently reviewed before migration is applied
- no duplicate usage/cost source of truth
- missing tenant context fails closed

Important:
This increment is itself an immediate Audit trigger under the project Audit System because it introduces PostgreSQL/schema/RLS changes.

## Increment C — Core War Room orchestrator

Deliver:
- room lifecycle service
- bounded turn scheduler
- participant selection
- OpenRouter adapter usage through existing platform abstraction
- per-room / per-agenda / per-agent budgets
- Pause / Resume / Stop
- NEEDS_OWNER_DECISION gate
- failure/retry behavior
- request/trace correlation

Exit:
- synthetic multi-agent room works without UI
- two-round hard limit is testable
- no agent self-recursion
- owner gate stops automatic turns
- hard budget stop works

## Increment D — Realtime Control Plane UI

Deliver:
- `/war-room`
- participant roster
- live ordered messages
- agenda/findings/decision panel
- Start / Pause / Resume / Stop
- Ask Role / Ask All
- Summarize
- Owner Decision
- token/cost display

Realtime transport must be chosen from measured/simple options before implementation.

Exit:
- one internal owner can operate one room end to end
- reconnect does not lose durable room state
- system-of-record events can replay the UI

## Increment E — Meeting artifacts and GitHub linkage

Deliver:
- durable meeting summary
- decision list
- unresolved owner decisions
- action items
- optional GitHub issue/meeting document creation with owner-authorized write behavior
- formal audit reports remain separate

Exit:
- meeting can close with a reproducible artifact
- discussion is not confused with binding audit outcome

## Increment F — Security / cost / pilot verification

Deliver:
- cross-tenant isolation tests
- participant permission tests
- model/tool permission separation tests
- token/cost budget tests
- timeout/provider-failure tests
- owner pause/stop tests
- protected-system boundary checks
- first internal pilot

Recommended first pilot:
- War Room Meeting #001 — Phase 2 Audit Review

## Implementation ordering

A -> B -> C -> D -> E -> F

Parallel work allowed only where contracts are stable and no dependency is bypassed.

## Audit interaction

War Room work is subject to the same project Audit System.

Examples:
- Schema/RLS work triggers immediate independent audit.
- Security authorization changes trigger immediate independent audit.
- Major topology changes trigger immediate independent audit.
- Normal progress gates continue to apply to the War Room implementation milestone.

## Definition of V1 done

V1 is not DONE until:
- deterministic orchestration contracts pass
- schema/RLS isolation passes
- synthetic multi-agent flow passes
- owner controls work
- budget hard stops work
- meeting artifact can be produced
- no formal audit independence violation exists
- required Audit Gate at V1 completion is PASS
