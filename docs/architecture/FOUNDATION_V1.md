# Nippan AI Platform — Foundation Architecture v1

Status: **ACCEPTED FOUNDATION**  
Date: 2026-09-22

## 1. Product definition

Nippan AI Platform is a shared AI platform for:
- LINE and messaging bots
- Nippan website AI features
- future web/mobile/desktop applications
- internal AI assistants and specialist agents
- future customer/rental bots and SaaS-style AI services

The platform is not designed around "one bot". It is designed around **Tenants, Applications and Agents**.

## 2. Design principles

1. Easy to operate and understand.
2. Easy to trace and debug.
3. Fast realtime path.
4. Cost-efficient by default.
5. Flexible without unnecessary infrastructure.
6. Easy to extend with new models, tools, channels and products.
7. Security/policy enforced by code, not by model opinion.
8. One source of truth for operational data.
9. Incremental migration and rollback, never big-bang rewrites.
10. Add complexity only when measurements justify it.

## 3. Topology

```text
Channels / Websites / Apps / Bots
              |
      Cloudflare Worker
 verify / rate-limit / normalize
 request_id / idempotency
              |
              v
       Core AI Service
          FastAPI
  +-----------+-----------+
  |           |           |
Context     Policy     Model Gateway
Memory      Engine      OpenRouter
  |           |           |
  +-----------+-----------+
              |
              v
          Nippan MCP
    scoped tools/capabilities
              |
      +-------+--------+
      |                |
PostgreSQL+pgvector   External systems
      |
      +--> R2 / Drive / reporting surfaces

Background / long-running:
Cloudflare Queues + n8n
```

## 4. Control Plane vs Data Plane

### Control Plane
A dashboard/admin center used to configure and inspect:
- tenants/workspaces
- applications
- agents
- channels
- prompts/personas
- model policies
- memory policies
- tool/MCP permissions
- knowledge sources
- risk/privacy policies
- budgets/quotas
- feature flags
- versions and rollback
- requests/traces/errors
- usage/cost
- queues and approvals

Configuration follows:

```text
Edit -> Draft -> Test -> Publish -> Version -> Rollback
```

### Data Plane
The runtime that handles actual requests, context, models, tools, storage and replies.

The dashboard must not become the realtime execution engine.

## 5. Core hierarchy

```text
Tenant
  -> Workspace (optional grouping)
      -> Application
          -> Agent
              -> Channel
                  -> Conversation
```

An Agent is a role/configuration, not a bot.

An Application may contain multiple Agents.
One Agent may be exposed through multiple Channels where policy permits.

## 6. Core configuration objects

Foundation objects:
- Tenant
- Workspace
- Application
- Agent
- Channel
- Agent Template
- Model Policy
- Memory Policy
- Tool Policy
- Data Policy
- Risk Policy
- Privacy Policy
- Feature Flags
- Entitlements
- Quota/Budget
- Configuration Version
- Environment

## 7. Realtime path

Realtime requests should stay short:

```text
Channel -> Thin Worker -> FastAPI Core -> Context/Policy -> OpenRouter -> Tool if needed -> Reply
```

Do not route ordinary chat through Queue or large n8n workflows by default.

## 8. n8n responsibility

n8n remains important, but primarily for:
- scheduled work
- integrations
- reports
- Google Drive/Sheets/email
- long-running automation
- admin workflows
- background orchestration
- maintenance jobs

n8n is not the default synchronous chat runtime.

## 9. Cloudflare responsibility

Use initially:
- Workers: thin edge gateway
- Queues: durable/background jobs
- R2: machine-facing files

Evaluate later only when metrics justify:
- AI Gateway
- Hyperdrive
- Analytics Engine
- Durable Objects
- Service Bindings

Do not use initially:
- D1 as duplicate source of truth
- Vectorize as duplicate of pgvector
- Cloudflare Workflows as duplicate of n8n

## 10. AI/model architecture

OpenRouter is the primary model gateway.

Central model policy chooses by:
- task
- privacy class
- risk
- tool reliability
- latency
- success rate
- cost

General tiers:
- free/ultra-cheap: public low-risk only
- cheap worker: normal daily work
- reliable/tool-capable: actions
- specialist: vision/coding/research as needed
- premium/reviewer: escalation only

Model identifiers must live in central policy/configuration, not throughout workflows/code.

## 11. Context architecture

Default context assembly is deterministic:
- raw current request
- recent turns
- active state
- structured source-of-truth data
- hybrid retrieved relevant memories/knowledge
- token budget

Context Compiler is optional and conditional only when context size/ambiguity makes it beneficial.

Rules:
- raw user request is always retained
- compiler has no tool authority
- compiler must be benchmarked for fidelity, cost and latency
- never use it merely because it exists

## 12. Retrieval and memory

PostgreSQL is the operational source of truth.
pgvector provides semantic retrieval.

Retrieval is hybrid:
- structured/exact lookup
- keyword/trigram search
- vector similarity
- optional reranking

Memory must record:
- tenant/application/agent/subject scope
- source/provenance
- confidence
- importance
- sensitivity
- verification status
- created/updated/confirmed time
- expiry
- superseded/conflicting relationship
- embedding model/version where applicable

Structured business data always outranks inferred semantic memory.

## 13. Policy and safety

Risk is statically configured per tool/action:
- READ
- WRITE_LOW
- WRITE_IMPORTANT
- DESTRUCTIVE
- FINANCIAL

The model cannot downgrade its own action risk.

Typical flow:
- READ / low-risk: policy may execute directly
- uncertain: optional AI reviewer
- important writes: stricter policy/review
- destructive/financial: human approval where required

Privacy gates are code-enforced before model/provider routing.

## 14. MCP/tool architecture

Nippan MCP is modular, not an all-powerful flat toolbox.

Initial logical domains may include:
- core: memory/tasks/general
- commerce: product/order
- files: R2/Drive
- admin: WordPress/Cloudflare/infrastructure

Bot/Application/Agent profiles receive explicit allowlists and scopes.

Every tool call requires:
- schema validation
- policy check
- risk mapping
- timeout
- idempotency for side effects
- audit record

Domains may later split into separate MCP services without changing the platform contract.

## 15. Data isolation

Every relevant record/request must support appropriate scope keys:
- tenant_id
- application_id
- agent_id
- channel_id
- user_id / subject_id
- conversation_id
- request_id

Use database-level protection such as RLS where appropriate, especially across tenants.

## 16. Reliability

Required foundation capabilities:
- request_id across all hops
- persistent idempotency for side effects
- retry policy with bounded retries/backoff
- dead-letter handling and replay path
- degraded-mode responses
- per-conversation ordering where required
- provider/model fallback
- budgets and kill switches
- backup/restore with tested procedures
- feature flags and rollback

The system must fail visibly rather than silently.

## 17. Observability

Keep v1 simple:
- Cloudflare Worker logs/tracing for edge
- OpenRouter usage/model/provider telemetry
- PostgreSQL ops/audit records for business/system truth
- n8n execution history for background workflows

All layers share request_id/trace correlation.

Do not add another observability platform until current telemetry is insufficient.

## 18. Files and human-facing data

- R2: machine files, images, slips, audio, generated artifacts
- Google Drive: human-facing/shared documents
- Google Sheets: reports/export/manual views only

## 19. SaaS/rental readiness

The platform schema must be able to support future external customers without redesign.

Prepare for:
- tenant isolation
- Agent/Application templates
- entitlements
- quotas/budgets
- usage metering
- per-tenant configuration
- model/tool restrictions
- versioned configuration

Billing itself is not required in v1, but usage attribution must exist from the beginning.

## 20. Existing systems

Existing production Ai-Nippan remains independent until the new core is proven.

Future migration uses adapters and feature flags:
- ModelClient
- ContextProvider
- MemoryStore
- Delivery/Queue
- Telemetry
- Tool/MCP

Use shadow/read-only comparison before traffic cutover and retain rollback.

## 21. Explicitly deferred

Until measurements justify them:
- Cloudflare AI Gateway
- Hyperdrive
- Durable Objects
- Analytics Engine
- D1
- Vectorize
- Cloudflare Workflows
- Redis
- dedicated vector database
- Kubernetes
- unnecessary microservices

## 22. Success criterion

Foundation v1 succeeds when the platform is:
- understandable by one primary operator
- traceable end to end
- cheap at low traffic
- responsive for realtime interaction
- safe across tenants and tools
- easy to add a new Agent/Application without redesigning the Core
- able to adopt newer technology through adapters/policies rather than rewrites
