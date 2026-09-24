# Nippan AI War Room V1 — Product / Architecture Proposal

Status: PROPOSAL ACCEPTED — INCREMENT A AUTHORIZED
Date: 2026-09-23
Implementation status: INCREMENT A STARTING
Current dependency: Audit #18 resolved; A-001 closed and production verified

## 1. Purpose

Nippan AI War Room is a visible multi-agent project chat room where the Project Owner can watch specialist AIs discuss project work, interrupt the discussion, ask one or all participants questions, pause/stop the room, and turn the discussion into durable decisions and action items.

The War Room is intended to become part of the Nippan AI Platform Control Plane, not a separate orchestration platform.

V1 should prove one thing well:

> Multiple independently configured AI roles can discuss one project issue in a controlled, observable and cost-bounded room while a human owner remains in control.

## 2. Non-goals for V1

V1 does NOT attempt to provide:

- autonomous infinite agent loops
- AI majority-rule governance
- autonomous production changes
- autonomous approval of high-risk actions
- full SaaS multi-customer collaboration
- voice/video meetings
- arbitrary external tool execution
- a new message broker or distributed orchestration platform
- a replacement for the Independent Audit System

The War Room may host an Auditor, but the formal Audit outcome remains governed by `docs/audits/AUDIT_SYSTEM_V1.md`.

## 3. Human authority

The Project Owner is the final human decision-maker.

AI participants may:
- propose
- challenge
- compare evidence
- identify conflicts
- request clarification
- recommend actions

AI participants must not:
- silently convert disagreement into a binding decision
- lower deterministic security/risk requirements
- approve their own Builder work as an Independent Auditor
- continue consuming tokens indefinitely
- execute destructive/financial/high-risk actions merely because the room agrees

Important unresolved decisions are surfaced as `NEEDS_OWNER_DECISION`.

## 4. V1 participant roles

Default room roster:

### Chair / Project Lead
Responsibilities:
- opens agenda
- chooses the next speaker
- keeps discussion on topic
- detects repetition
- asks for evidence when claims conflict
- creates a neutral synthesis
- marks unresolved owner decisions

The Chair is not automatically the Independent Auditor.

### Architect
Responsibilities:
- Foundation/ADR consistency
- interfaces and system boundaries
- complexity control
- future extensibility

### Builder
Responsibilities:
- explains implementation intent
- supplies code/test evidence
- proposes remediation
- cannot approve its own milestone

### Security Reviewer
Responsibilities:
- tenant isolation
- authorization/RLS
- privacy/secrets
- destructive-action controls
- trust boundaries

### Cost & Operations Reviewer
Responsibilities:
- token/model cost
- latency
- reliability/retry behavior
- operational complexity
- unnecessary managed services

### Independent Auditor
Responsibilities:
- formal evidence-driven audit when the room is running an Audit agenda
- independent from Builder
- governed by `AUDIT_SYSTEM_V1.md`
- may return findings but cannot be replaced by room consensus

### Project Owner
Human participant with authority to:
- interrupt
- ask questions
- pause/resume/stop
- request another round
- accept/reject a proposed owner decision
- close a discussion

## 5. User experience

Target Control Plane route:

`/war-room`

Suggested V1 layout:

```text
+--------------------------------------------------------------------------------+
| Nippan AI War Room                  [Start] [Pause] [Stop] [Summarize]          |
+----------------------+--------------------------------------+------------------+
| Participants         | Live discussion                      | Agenda / Findings|
|                      |                                      |                  |
| Chair        ACTIVE  | Chair: ...                           | Agenda 1         |
| Architect            | Architect: ...                       | OPEN             |
| Builder              | Security: ...                        |                  |
| Security             | Owner: @all ...                      | Findings         |
| Cost & Ops           | Auditor: ...                         | HIGH A-003       |
| Auditor              |                                      |                  |
| Owner (human)        |                                      | Decisions        |
|                      |                                      | NEEDS_OWNER...   |
+----------------------+--------------------------------------+------------------+
| Message / @Role / @all                                      [Send]             |
+--------------------------------------------------------------------------------+
```

V1 controls:
- Start
- Pause
- Resume
- Stop
- Ask All
- Summarize
- Owner Decision

Optional later controls:
- branch discussion
- replay
- compare two model rosters
- export/share meeting

## 6. Interaction modes

### Free Discussion

Goal:
- exploration and brainstorming
- visible specialist disagreement
- owner can interrupt freely

Rules:
- no formal audit outcome
- Chair limits repetition
- findings may be captured but remain discussion artifacts

### Formal Meeting

Goal:
- bounded agenda
- evidence review
- decisions/action items

Output:
- meeting summary
- decisions
- unresolved decisions
- action items

### Audit Review

Goal:
- discuss evidence relevant to a formal audit

Critical rule:
- War Room conversation does not itself constitute the mandatory Independent Audit
- only the configured independent Auditor may issue the formal audit report
- Builder and other participants may challenge or supply evidence
- final formal audit record remains a durable repository artifact

## 7. Conversation protocol

V1 uses controlled turns rather than an unconstrained model-to-model loop.

Recommended sequence:

1. Owner or Chair creates agenda.
2. Chair selects 2–5 relevant AI roles.
3. Round 1: each selected role gives an independent view without seeing other agents' new answers.
4. Chair extracts:
   - agreements
   - conflicts
   - evidence requests
5. Round 2: selected roles see the summarized conflicting claims and respond.
6. Chair stops automatic turns unless:
   - owner requests another round, or
   - a bounded evidence-resolution turn is justified.
7. Chair produces a neutral synthesis.
8. Owner decides items tagged `NEEDS_OWNER_DECISION`.
9. Secretary behavior writes durable meeting artifacts if requested.

This prevents first-speaker anchoring and reduces token-consuming circular debate.

## 8. Turn and cost guardrails

Default V1 proposal:

- maximum automatic discussion rounds: 2
- default maximum AI participants per agenda item: 5
- one Chair synthesis after each round
- no AI may directly trigger itself
- no agent-to-agent recursion
- owner messages do not count as automatic rounds
- per-room token budget
- per-agent token budget
- per-agenda token budget
- hard stop when budget is reached
- explicit owner action required to extend budget

Model policy:
- model identity comes from Agent configuration
- do not hard-code models in War Room application code
- cheaper specialist models may handle routine analysis
- expensive models are used intentionally for high-value roles/gates

Cost visibility:
- estimated/actual model tokens
- normalized cost when available
- cost by participant
- cost by agenda item
- total room cost

## 9. Proposed room states

Conceptual state machine:

```text
DRAFT
  -> READY
  -> RUNNING
       -> PAUSED
       -> RUNNING
       -> NEEDS_OWNER_DECISION
       -> RUNNING
  -> SUMMARIZING
  -> CLOSED

Any active state -> STOPPED
```

State meanings:

- DRAFT: room exists; agenda/roster editable
- READY: validated and ready to start
- RUNNING: bounded orchestration may schedule turns
- PAUSED: no automatic AI turns
- NEEDS_OWNER_DECISION: orchestration halts for human input
- SUMMARIZING: no new debate; durable summary is being prepared
- CLOSED: normal completed room
- STOPPED: manually terminated

## 10. Proposed message types

Conceptual message/event categories:

- OWNER_MESSAGE
- AGENT_MESSAGE
- CHAIR_PROMPT
- CHAIR_SYNTHESIS
- EVIDENCE_REQUEST
- EVIDENCE_REFERENCE
- FINDING
- DECISION_PROPOSAL
- OWNER_DECISION
- ACTION_ITEM
- SYSTEM_EVENT
- BUDGET_WARNING
- ERROR

The V1 implementation should preserve display-friendly chat while storing enough structure to distinguish discussion from decisions/findings.

## 11. Proposed data model

This is a logical proposal only. Audit #18 no longer blocks advancement, but this proposal does not authorize a schema migration. Increment B schema/RLS work requires immediate Independent Audit before migration/application.

Potential entities:

### project_rooms
- room_id
- tenant_id
- application_id
- project_key
- title
- mode
- state
- created_by
- token_budget
- cost_budget
- created_at
- started_at
- closed_at

### project_room_participants
- participant_id
- room_id
- agent_id nullable for human/system participants
- participant_type
- role
- display_name
- model_policy_ref
- active

### project_room_agenda_items
- agenda_item_id
- room_id
- sequence
- title
- objective
- status
- round_limit
- token_budget

### project_room_messages
- message_id
- room_id
- agenda_item_id
- participant_id
- request_id
- message_type
- content_reference or safe content
- round_number
- created_at

### project_room_findings
- finding_id
- room_id
- agenda_item_id
- raised_by_participant_id
- severity
- status
- summary
- evidence_refs

### project_room_decisions
- decision_id
- room_id
- agenda_item_id
- decision_type
- proposed_by
- owner_decision
- rationale
- decided_at

### project_room_action_items
- action_item_id
- room_id
- agenda_item_id
- title
- owner
- status
- linked_issue_or_pr

Important:
- exact schema, foreign keys, RLS, retention and content storage must be independently reviewed before implementation.
- do not duplicate request/trace/usage/audit data already owned by platform telemetry tables.
- room messages should reference platform request/trace records where possible instead of creating a second observability system.

## 12. Proposed realtime architecture

Preferred direction consistent with Foundation:

```text
Browser / Control Plane
        |
        v
FastAPI Core / War Room service boundary
        |
        +--> deterministic Room Orchestrator
        |       |
        |       +--> Agent config loader
        |       +--> OpenRouter model gateway
        |       +--> policy / budget checks
        |
        +--> PostgreSQL system of record
        |
        +--> realtime delivery mechanism
```

V1 principle:
- reuse the existing platform topology
- do not introduce a new orchestration platform merely for chat-room presentation

Realtime implementation choice remains open until implementation phase.

Candidate approaches may include:
- SSE from FastAPI
- WebSocket
- Supabase Realtime if it provides a measured operational benefit

No candidate is accepted by this proposal.

## 13. Orchestrator requirements

The War Room Orchestrator must be deterministic around:

- who may speak
- maximum rounds
- token/cost budgets
- room state
- pause/stop
- owner-decision gates
- participant permissions
- allowed tool access
- audit-role independence

The model may propose "who should answer next", but deterministic code must enforce the allowed participant set and limits.

## 14. Prompt/context rules

Each AI turn receives only relevant context:

Required:
- agenda objective
- role instructions
- relevant project evidence
- compact prior-round synthesis
- directly relevant messages/evidence

Avoid:
- sending the entire project repository
- sending the full chat history every turn
- repeatedly sending identical Foundation/ADR text
- cross-tenant context leakage

Use references/retrieval where possible.

The raw owner request must be preserved.

## 15. Evidence model

Claims should be distinguishable as:

- VERIFIED_EVIDENCE
- PROVIDED_CLAIM
- INFERENCE
- OPINION
- UNKNOWN

For project/audit discussions, agent messages should cite repository evidence or explicitly state that evidence is unavailable.

This allows the Chair to surface conflicts such as:

- Builder says test passed
- repository contains test code
- CI execution evidence missing

without treating the three statements as equivalent.

## 16. Security / permissions

Minimum V1 principles:

- tenant/application scoped room access
- server-side participant authorization
- Agent tool scopes remain independent
- room membership does not automatically grant tool permission
- no secrets displayed in chat
- privacy gate before model calls
- protected systems remain protected
- destructive/financial actions require existing deterministic policy and approval flow
- Independent Auditor role cannot be impersonated by Builder for a formal audit

## 17. Tool execution

Recommended V1:
- discussion first
- evidence-reading tools may be allowed by explicit role policy
- write/destructive tools disabled by default inside automatic discussion

Later:
- an Agent can propose an action
- Chair turns it into an action proposal
- policy evaluates it
- human approval occurs when required
- separate execution path performs the action
- result returns to room as evidence

This keeps "talking about an action" separate from "executing an action".

## 18. Observability

Every model turn should correlate with:
- room_id
- agenda_item_id
- participant/agent
- request_id
- trace_id
- config version
- model/provider telemetry
- token/cost usage

Room-level dashboard should show:
- total turns
- rounds
- latency
- cost
- errors/retries
- findings count
- owner-decision count

Do not create parallel cost truth if UsageEvent already owns usage/cost accounting.

## 19. Failure behavior

Examples:

Model timeout:
- mark turn failed
- retry only within configured retry policy
- Chair may skip participant
- room remains inspectable

Provider outage:
- use configured model gateway fallback only when policy permits
- record actual provider/model
- do not silently change an Independent Auditor identity when a formal audit requires a configured auditor

Budget exhausted:
- pause automatic discussion
- request owner decision

Chair failure:
- room pauses rather than letting agents continue uncontrolled

Database/realtime delivery failure:
- system of record wins
- client reconnects/replays durable events

## 20. Meeting artifacts

Formal Meeting may produce:

`docs/meetings/MEETING-<id>-<slug>.md`

Suggested contents:
- objective
- participants/models/config versions
- evidence inspected
- agreements
- disagreements
- findings
- owner decisions
- action items
- unresolved items
- cost/turn summary

Formal Audit reports remain under:
- `docs/audits/`

## 21. Initial pilot

Recommended first pilot after implementation is authorized:

**War Room Meeting #001 — Phase 2 Audit Review**

Participants:
- Chair
- Architect
- Builder
- Security Reviewer
- Cost & Ops Reviewer
- Independent Auditor
- Project Owner

Purpose:
- discuss the formal Audit #18 findings
- allow Builder to provide remediation evidence
- let specialists challenge assumptions
- surface decisions for the Project Owner

Important:
- Issue #18's formal Independent Audit should exist first or remain separately governed.
- the War Room is not used to manufacture a PASS by consensus.

## 22. V1 acceptance criteria

War Room V1 is acceptable when:

- owner can create/open one room
- owner can configure/select participants
- owner can send to one role or all
- owner can Start/Pause/Resume/Stop
- controlled Round 1 + Round 2 works
- Chair produces a neutral synthesis
- owner-decision gate halts automation
- token/cost hard limits work
- messages remain ordered and durable
- participant/model/config identity is observable
- tenant isolation is tested
- room does not grant tool permissions implicitly
- meeting summary/action items can be persisted
- formal audit independence remains enforceable
- no autonomous infinite loops

## 23. Rollout plan

### Design Track — allowed now
- proposal
- UX/flow
- role protocol
- logical data model
- acceptance criteria
- issue decomposition

### Implementation Track — Increment A authorized
Audit #18 permits Phase 2 advancement. Increment A deterministic contracts are authorized now. Increment B schema/RLS application requires immediate Independent Audit, and later increments remain gated by prerequisite completion and normal audit controls.

Implementation should be split into reviewed increments rather than one large feature.

## 24. Open decisions before implementation

Mark NEEDS_DECISION during implementation planning:

1. Exact phase placement: Control Plane Phase 5 versus an earlier isolated internal pilot.
2. SSE vs WebSocket vs Supabase Realtime.
3. Storage strategy for full chat content versus content references/retention.
4. Default role roster and per-role model policy.
5. Whether Secretary is a separate model or deterministic synthesis task.
6. Whether GitHub meeting artifact creation is automatic or owner-confirmed.
7. Exact per-room/agenda/participant budget defaults.
8. Which read-only evidence tools are allowed in V1.

Open decisions above do not block deterministic Increment A contract work; each must be resolved before the dependent implementation increment.
