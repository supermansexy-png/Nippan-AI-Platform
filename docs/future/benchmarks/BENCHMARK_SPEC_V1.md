# Benchmark & Evaluation Specification v1

Status: **DRAFT / REVIEW**
Issue: #11
Date: 2026-09-22

## 1. Goal

Choose models, routing policy and optional optimizations using Nippan's real task shapes rather than benchmark reputation or token price alone.

Primary decision metric:

**cost per successful task**

Supporting metrics:
- task success
- Thai understanding
- structured output validity
- tool correctness
- latency
- reliability/fallback rate
- privacy/policy compliance
- token use
- provider/model cost

## 2. Principles

1. Benchmark roles, not brand popularity.
2. Compare against deterministic baselines where possible.
3. Use redacted/synthetic fixtures; no production secrets or unnecessary PII.
4. Keep the same cases/prompts/policies across candidates.
5. Separate quality failures from provider/runtime failures.
6. Measure p50/p95 latency, not only averages.
7. Never pick a model from one metric alone.
8. Re-run benchmarks when a model/provider/prompt/policy materially changes.
9. Candidate model IDs live in benchmark config/policy, not application code.
10. Human review is used for subjective Thai quality; exact tasks are scored automatically.

## 3. Benchmark suites

### A. Router / Classifier / Decision

Purpose:
- intent classification
- model-tier routing
- tool candidate selection
- escalation/abstain decision
- error classification

Candidates:
- deterministic rules baseline
- Jev candidate through model policy
- low-cost LLM candidate(s)
- other structured decision models as they become available

Test cases:
- Thai colloquial language
- short ambiguous requests
- typos
- mixed Thai/English
- pronouns/reference
- multi-intent requests
- commands with exact IDs/numbers
- irrelevant small talk
- requests that should abstain/escalate

Metrics:
- exact accuracy
- macro F1 by intent
- unsafe false-negative rate
- unnecessary escalation rate
- confidence calibration / abstain quality
- p50/p95 latency
- cost per 1,000 decisions
- valid structured response rate

Important:
Router output is advisory for routing.
Security/risk/tool authorization remains deterministic policy.

### B. Thai Conversational Worker

Purpose:
Normal user-facing conversations.

Cases:
- natural Thai tone
- honorifics and politeness
- concise vs detailed requests
- reference resolution across turns
- corrections: "ไม่ใช่ อันเมื่อกี้"
- follow-up questions
- code-switching Thai/English
- tool-needed vs no-tool conversations
- refusal/degraded response behavior

Metrics:
- task completion
- factual consistency with supplied context
- reference resolution accuracy
- unnecessary verbosity
- hallucination rate
- human preference score
- latency
- tokens
- cost per successful conversation task

Human scoring should be blind to model identity when practical.

### C. Tool / Agent Execution

Purpose:
Select and call allowed tools correctly.

Cases:
- no tool required
- one clear tool
- several possible tools
- invalid arguments
- missing required information
- denied tool
- high-risk action
- repeated request/idempotency
- tool timeout/error
- malicious prompt attempting permission escalation

Metrics:
- correct tool selection
- valid arguments
- schema validity
- unauthorized tool attempt rate
- needless tool-call rate
- recovery after tool failure
- duplicate side-effect rate (target: zero)
- end-to-end task success
- latency and cost

### D. Retrieval

Compare:
1. structured/exact lookup
2. keyword/trigram
3. vector
4. hybrid
5. hybrid + reranking when justified

Cases:
- exact order/reference IDs
- product names
- Thai spelling variants
- transliteration
- synonyms
- date/time references
- old vs current facts
- multiple similar memories
- irrelevant distractors

Metrics:
- Recall@K
- Precision@K
- MRR / first-correct rank
- exact identifier success
- stale fact selection rate
- retrieval latency
- context tokens added

### E. Memory

Cases:
- explicit user-confirmed fact
- inferred preference
- correction of old fact
- conflicting memories
- expired information
- cross-Agent allowed memory
- cross-Agent denied memory
- cross-tenant isolation
- long inactive interval

Metrics:
- correct memory write decision
- correct retrieval
- contradiction resolution
- provenance preservation
- stale memory leakage
- cross-scope leakage (target: zero)
- unnecessary memory write rate

### F. Context Compiler

This suite is run only if the compiler is being considered.

Compare:
- deterministic context only
- conditional compiler

Cases:
- long conversation
- several unresolved references
- mixed relevant/irrelevant history
- conflicting constraints
- short/simple request (compiler should usually be skipped)

Metrics:
- raw intent fidelity
- constraint preservation
- task success delta
- token reduction
- additional latency
- additional cost
- compiler failure rate

Adoption gate:
Compiler is not enabled by default unless it reduces total cost/token pressure without materially reducing task success or user intent fidelity.

### G. Vision / Slip Extraction

Cases:
- clear slip image
- rotated/cropped image
- low contrast
- repeated/duplicate slip
- multiple numbers/amounts
- unsupported/non-slip image
- Thai bank/date/amount fields
- ambiguous extraction requiring review

Metrics:
- field accuracy
- amount accuracy
- reference accuracy
- duplicate detection accuracy
- confidence calibration
- false acceptance rate
- latency/cost

### H. Reliability / Provider Failure

Inject:
- timeout
- HTTP 429
- 5xx
- invalid structured output
- model unavailable
- tool unavailable
- PostgreSQL unavailable in controlled test
- queue retry

Metrics:
- successful fallback rate
- privacy-safe fallback
- bounded retry behavior
- duplicate side effects
- degraded response correctness
- recovery time
- trace completeness

### I. Privacy / Policy

Cases:
- public data
- internal data
- PII
- financial customer data
- secret-like data
- prompt asking model to bypass policy
- cross-tenant access attempt
- Agent trying unavailable tool

Metrics:
- provider/model routing compliance
- redaction compliance
- blocked unauthorized tool calls
- cross-tenant leakage (target: zero)
- sensitive log leakage (target: zero)
- false blocks on legitimate low-risk requests

## 4. Dataset design

Initial v1 should contain a balanced set of real Nippan task patterns.

Sources:
- manually authored canonical cases
- sanitized examples from existing workflows
- synthetic edge cases
- past failure patterns rewritten without private identifiers

Each case includes:
- case_id
- suite
- input/messages
- tenant/application/agent fixture
- expected outcome
- acceptable alternatives
- risk/privacy class
- allowed tools
- grading method
- importance weight
- tags

Do not copy real customer secrets or private identifiers into benchmark fixtures.

## 5. Grading

Use three grading modes.

### Exact / deterministic
For:
- classification
- JSON/schema
- tool selection
- exact extraction
- policy enforcement
- retrieval IDs

### Programmatic semantic
For:
- required facts present
- forbidden claims absent
- constrained outputs

Must be deterministic where possible.

### Human / blinded review
For:
- Thai naturalness
- usefulness
- tone
- ambiguous conversational quality

Avoid using the same candidate model as the sole judge of itself.

## 6. Success score

Do not collapse all tasks into one universal score for every purpose.

For each role create a weighted score with hard gates.

Example router hard gates:
- unsafe routing false-negative below threshold
- structured validity above threshold

Example tool-agent hard gates:
- unauthorized tool execution = disqualifying
- duplicate side effects = disqualifying

Then compare:
- successful task rate
- p95 latency
- total cost

## 7. Cost per successful task

For candidate C:

```text
total model + relevant processing cost
--------------------------------------
number of successful benchmark tasks
```

Track compiler/reviewer/retry costs as part of the same user task.

Cheap model with high retry/failure rate may be more expensive in practice.

## 8. Candidate roles

Initial roles to benchmark:
- structured router/classifier: Jev and low-cost alternatives
- cheap general worker
- reliable tool-calling worker
- Thai conversational worker
- reviewer
- vision specialist
- embedding model
- reranker if needed
- coding/development assistant separately from production runtime

Specific model IDs are benchmark configuration, not architecture.

## 9. Jev evaluation gate

Jev is a high-priority candidate for:
- intent classification
- routing
- scoring
- escalation
- structured decisions

It must be tested against:
- deterministic rules baseline
- at least one inexpensive general LLM candidate

Do not use Jev as:
- conversation model
- authorization engine
- financial/destructive approver
- source of truth

Promotion requires:
- strong Thai intent accuracy
- reliable structured output
- useful confidence/abstention behavior
- lower cost/latency at comparable task success

## 10. Test environments

- local/unit fixtures
- staging platform
- shadow/read-only traffic later

Never run destructive benchmark actions against production resources.

## 11. Benchmark output

Every run produces:
- benchmark_run_id
- code/config revision
- model/provider candidates
- prompt/policy versions
- timestamp
- suite metrics
- failure cases
- token/cost totals
- latency percentiles
- recommendation status

Recommendation statuses:
- PROMOTE
- KEEP_TESTING
- SPECIALIST_ONLY
- REJECT
- RETEST_AFTER_CHANGE

These statuses are benchmark outputs, not permanent model identity.

## 12. Regression suite

Cases that previously caused failures are added permanently to regression fixtures.

Examples from existing systems:
- provider high-demand/503
- malformed function-call ordering
- memory not retrieved because the Agent forgot to call memory
- routing dependent on exact keywords
- duplicate/redelivered events
- bot silently not replying

A fixed regression suite prevents old failures from returning unnoticed.

## 13. First benchmark order

1. Router/classifier including Jev
2. Thai conversational worker
3. structured output + tool calling
4. hybrid retrieval
5. memory retrieval/write policy
6. model fallback/reliability
7. vision/slip
8. Context Compiler only after baseline context metrics exist

## 14. Decision rule

No model receives a permanent platform role merely because it is popular, cheap, new, or strong on public benchmarks.

It earns a role by Nippan benchmark performance and can be replaced through central Model Policy when a better candidate appears.
