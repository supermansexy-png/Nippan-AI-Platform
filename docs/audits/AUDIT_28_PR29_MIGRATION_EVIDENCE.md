# Audit #28 - PR #29 Migration Remediation Evidence

Status: READY FOR INDEPENDENT RE-REVIEW
Date: 2026-09-23
Repository: `supermansexy-png/Nippan-AI-Platform`
Pull request: #29

## Review target

- original audited head: `c5bb358ce5ec74e5f056b487fa19ddb373f0b358`
- remediation implementation head: `4e63fe0713fd5f4f21855f93fc81f7857f7b2531`
- approved design base: `43ac9fd077bebf34ff5e8bc237173bbbdf8b4612`
- original blocked audit generation: `gen-1790120199-tFltkAkyujYQOT0D0vZD`
- remediation CI run: `35799894160`
- CI job: `postgres-regression` / `106987600211`
- PostgreSQL image: `postgres:17`

The remediation changes only the migration governance triggers, their ACL
regression coverage, multi-session tests, the existing isolation fixtures and
the PostgreSQL regression workflow. It does not apply a Supabase migration or
change production data.

## Findings addressed

### PR29-F-01 - Builder/Auditor concurrency

Every participant mutation that can affect governance now locks the canonical
`project_rooms` row before evaluating canonical
`principal_type + principal_id` separation. Concurrent opposite-role writes
for one room therefore cannot evaluate from independent snapshots.

### PR29-F-02 - exactly-one Auditor readiness concurrency

Room readiness transitions and participant INSERT/UPDATE/DELETE operations use
the same room row as their serialization point. The readiness assertion runs
only after the governing room lock has been acquired. It checks:

- exactly one active HUMAN OWNER;
- exactly one active INDEPENDENT_AUDITOR;
- no active canonical principal represented as both BUILDER and
  INDEPENDENT_AUDITOR.

### PR29-F-03 - helper EXECUTE scope

Direct EXECUTE grants were removed from all trigger-returning functions. The
read-only readiness assertion remains executable by runtime and control-plane
because their trigger paths call it under `SECURITY INVOKER`.

## Locking strategy

The authoritative lock is a PostgreSQL row-level `FOR UPDATE` lock on the
scoped `project_rooms` row.

- INSERT participant: lock the new room.
- DELETE participant: lock the old room.
- UPDATE participant without a scope move: lock that room once.
- UPDATE participant across rooms: lock old and new rooms ordered by
  `(tenant_id, application_id, room_id)`.
- room readiness UPDATE: PostgreSQL's row UPDATE already owns the same room
  row lock before the readiness trigger evaluates participant state.

There is no advisory lock or global table lock. Mutations for different rooms
can proceed concurrently. The deterministic composite-key order prevents two
cross-room participant moves from taking the room locks in opposite order.

## Multi-session concurrency evidence

`tests/sql/run_war_room_concurrency.py` opens independent `psql` processes and
holds the room row lock in one transaction while the contender runs in another
transaction. Each contender was observed waiting about 1.24 seconds for the
holder before PostgreSQL evaluated the invariant.

| Scenario | Lock order covered | Result |
|---|---|---|
| same canonical principal Builder + Auditor | participant then participant | PASS - contender rejected |
| READY versus second Auditor | READY first | PASS - second Auditor rejected |
| READY versus Auditor deactivation | READY first | PASS - deactivation rejected |
| READY versus Auditor identity collision with Builder | READY first | PASS - identity mutation rejected |
| second Auditor versus READY | participant first | PASS - READY rejected; room remains DRAFT |
| Auditor deactivation versus READY | participant first | PASS - READY rejected; room remains DRAFT |

Committed final-state assertions also passed:

- canonical Builder/Auditor overlap count remains one role;
- READY rooms retain exactly one active Auditor;
- distinct Builder/Auditor identities remain distinct;
- participant-first invalid readiness attempts leave the room DRAFT.

The same concurrency suite passed again after destructive ephemeral rollback
and clean migration reapplication.

## EXECUTE matrix

### Before remediation

| Function | Runtime | Control plane | Analytics | anon/authenticated/service_role/PUBLIC |
|---|---:|---:|---:|---:|
| `validate_project_room_participant_independence()` | yes | yes | no | no |
| `assert_project_room_audit_readiness(uuid,uuid,uuid)` | yes | yes | no | no |
| `enforce_project_room_ready_state()` | yes | yes | no | no |
| `enforce_project_room_participant_post_ready()` | yes | yes | no | no |

### After remediation

| Function | Runtime | Control plane | Analytics | anon/authenticated/service_role/PUBLIC |
|---|---:|---:|---:|---:|
| `validate_project_room_participant_independence()` | no | no | no | no |
| `assert_project_room_audit_readiness(uuid,uuid,uuid)` | yes | yes | no | no |
| `enforce_project_room_ready_state()` | no | no | no | no |
| `enforce_project_room_participant_post_ready()` | no | no | no | no |

The privilege regression suite checks every cell available through the named
database roles. Revoking PUBLIC is transitively verified because an accidental
PUBLIC EXECUTE grant would make the denied named roles executable as well.

## Regression results

GitHub Actions run `35799894160` completed successfully on the exact
remediation head merged ephemerally onto the exact PR base.

- clean ordered migration apply: PASS
- A-001 table and function privilege suite: PASS
- tenant isolation: PASS
- same-tenant application isolation: PASS
- existing Phase 2 invariants: PASS
- War Room isolation and integrity invariants: PASS
- HUMAN OWNER readiness invariant: PASS
- six multi-session race cases and final-state assertions: PASS
- deterministic contract tests: 13 PASS
- forbidden participant UPDATE negative control: expected failure observed
- privilege cleanup and clean rerun: PASS
- destructive ephemeral rollback: PASS
- clean migration reapply: PASS
- post-reapply privilege and isolation suites: PASS
- post-reapply concurrency suite: PASS

An earlier run, `35799763099`, proved all six concurrency scenarios but failed
only because fixture cleanup attempted to delete a HUMAN OWNER while its room
was still READY. Cleanup now transitions test rooms to DRAFT before removing
fixtures; run `35799894160` verifies that correction.

## Rollback and reapply

The existing ephemeral rollback continues to drop the seven War Room tables in
reverse dependency order and then the four War Room helper functions. CI
confirmed that no listed table/function survived. The migration reapplied
cleanly and all privilege, isolation and concurrency checks passed again.

This remains development/CI rollback evidence only. It is not authorization
for destructive production rollback.

## Remaining limitations and gates

- DRAFT Audit Review rooms may temporarily contain zero or multiple Auditors;
  exactly-one is enforced when entering or remaining in READY/active states.
- The direct readiness assertion is intentionally callable by runtime and
  control-plane trigger paths, remains `SECURITY INVOKER`, and does not mutate
  state or bypass RLS.
- The migration has not been applied to Supabase production.
- No production post-deploy ACL/RLS query or Supabase Advisor evidence exists.
- Independent Auditor re-review is still required to close PR29-F-01 through
  PR29-F-03.
- Independent last-push GitHub approval is still required by the active
  repository ruleset. Builder self-approval remains prohibited.
- PR #29 remains unmerged and production remains untouched.

After this blocked-finding re-review, normal project auditing returns to the
25/50/75/90/100 Audit Gates. The next normal gate is 75 percent unless another
major architecture, security or PostgreSQL trigger occurs.
