# Architecture Draft v0

Status: proposal for independent review.

## 1. Logical architecture

```text
LINE / Web / Group / Internal / Future Channels
                    |
             Cloudflare Worker
      verify / normalize / rate-control / identify
                    |
          +---------+---------+
          |                   |
       realtime           background
          |                   |
          |             Cloudflare Queue
          |                   |
          +---------+---------+
                    |
                   n8n
          orchestration / workflows
                    |
            Context Engine
       recent + summary + memory
                    |
       optional Context Compiler
                    |
             OpenRouter Router
        model policy + fallbacks
                    |
      +-------------+--------------+
      |                            |
 Worker/Specialist AI         Reviewer/Arbiter
      |                            |
      +-------------+--------------+
                    |
               Nippan MCP
        controlled tool interface
                    |
       +------------+------------+
       |            |            |
 PostgreSQL      R2/Drive    External APIs
 + pgvector                    Woo/LINE/etc.
```

## 2. Responsibility boundaries

### Cloudflare Worker
Should do cheap deterministic edge work:
- signature/auth verification where appropriate
- rate control
- request IDs
- channel/bot identification
- normalization
- lightweight rejection
- queue handoff

Should not become the primary business workflow engine.

### Cloudflare Queues
For:
- image/slip processing
- background memory processing
- retryable asynchronous tasks
- reporting jobs
- non-realtime telemetry fanout if needed

Realtime conversational responses should not be forced through Queue unless durability requirements justify the latency.

### n8n
Primary orchestration:
- workflow sequencing
- calling Context Engine
- calling AI/model policy
- tools/MCP coordination
- scheduled jobs
- bot-profile execution

Do not embed all domain logic into one giant workflow.

### Context Engine
Owns:
- recent messages
- active state
- rolling summary
- relevant long-term memory retrieval
- relevant business context references
- context/token budget

### Context Compiler
Optional low-cost AI step. Use when ambiguity or context size justifies it.

Required properties:
- original message retained
- structured output
- no authority to perform tools/actions
- no silent loss of constraints
- cost must be lower than the tokens it saves on average

Example output:
```json
{
  "raw_request": "...",
  "intent_hint": "...",
  "entities": {},
  "relevant_context": "...",
  "unresolved_references": [],
  "risk_hint": "low",
  "confidence": 0.92
}
```

### OpenRouter Model Router
Owns:
- model policy
- provider policy
- fallback
- privacy constraints
- central presets/config
- model telemetry metadata

Do not hard-code model IDs throughout n8n/application nodes.

### Reviewer
Triggered by risk/uncertainty, not every message.

Suggested action classes:
- READ
- WRITE_LOW
- WRITE_IMPORTANT
- DESTRUCTIVE
- FINANCIAL

High-risk/destructive work requires independent review and/or explicit human approval according to policy.

### Nippan MCP
Shared controlled capability surface:
- tasks
- expenses
- memory
- files
- orders
- product lookup
- website/WordPress
- Cloudflare
- future domain tools

Each Bot Profile receives only its allowed tools.

## 3. Data architecture

### PostgreSQL as system of record

Suggested logical schemas:

```text
core
  tenants
  bots
  users
  channels
  bot_profiles
  model_policies
  tool_policies
  data_policies
  risk_policies

chat
  conversations
  messages
  conversation_summaries
  active_state

memory
  memories
  memory_embeddings
  memory_feedback
  memory_events

ops
  ai_calls
  tool_calls
  audit_log
  review_queue
  usage_daily

files
  objects
```

Business-specific schemas should be added only when the bot/domain actually enters scope.

### Memory record properties

At minimum:
- memory_id
- tenant_id
- bot_id
- subject_id
- memory_type
- content
- confidence
- importance
- sensitivity
- source reference
- created_at
- last_confirmed_at
- expires_at
- embedding/reference to embedding

Memory must support update/expiration so stale facts do not compete forever.

### R2
Use for machine-oriented blobs:
- images
- slips
- audio
- generated artifacts
- temporary/processing files

### Google Drive
Use for human-facing/shared documents when useful.

### Google Sheets
Use for reports, exports and manual inspection; not primary source of truth.

## 4. Identity / namespace

Every reusable service should be able to scope by:

```text
tenant_id
bot_id
channel_id
user_id
conversation_id
request_id
```

This prevents one bot/customer/context from leaking into another.

## 5. Model policy

Initial candidate classes, subject to benchmark:
- free/ultra-cheap router
- cheap general worker
- reliable tool agent
- vision/multimodal specialist
- coding/reasoning specialist
- independent reviewer
- premium arbiter

Selection criteria:
- task success rate
- tool-call reliability
- structured-output validity
- Thai comprehension
- latency
- retry/fallback rate
- privacy/provider policy
- cost per successful task

The metric is **cost per successful task**, not model price alone.

## 6. Cloudflare proposal

Recommended:
- Workers
- Queues
- R2
- Analytics Engine where beneficial
- Tunnel/VPC for private infrastructure protection where appropriate

Conditional:
- Hyperdrive only if Workers need PostgreSQL directly
- AI Gateway only if benchmark proves observability/cache/rate-control benefit over direct OpenRouter
- Service Bindings only when multiple Workers justify microservice separation
- Durable Objects only for real concurrency/state needs

Avoid duplicate platforms without clear benefit:
- D1 vs PostgreSQL
- Vectorize vs pgvector
- Workflows vs n8n

## 7. Existing Ai-Nippan integration contract

Current bot remains independent.

Prepare future adapters for:
- ModelClient
- ContextProvider
- MemoryStore
- Queue/Delivery
- Telemetry
- Tool/MCP

Do not rewrite commerce/order/LINE behavior merely to fit the new platform.

## 8. Non-functional requirements

- Thai-first natural language quality
- no cross-user/bot memory leakage
- idempotent write/action paths
- durable handling for async work
- explicit retries and dead letters
- measurable cost/latency/success
- safe rollback
- secrets outside source control
- minimum necessary context
- no single-model dependency
- no silent destructive actions
