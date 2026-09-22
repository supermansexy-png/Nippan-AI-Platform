# Nippan AI Platform — Proposed Roadmap

This roadmap is intentionally phased. Each phase should produce testable artifacts before the next begins.

## Phase 0 — Architecture review and benchmark design

Deliverables:
- Foundation architecture
- Data ownership map
- Security/privacy classification
- Model policy design
- Cloudflare responsibility map
- Benchmark suite specification
- Migration contract for existing bots

Exit criteria:
- Major architecture decisions recorded
- No unresolved source-of-truth ambiguity
- Two independent AI reviews reconciled

## Phase 1 — Model Gateway Foundation

Build:
- OpenRouter credentials by project/bot
- Central model policy/presets
- Free -> cheap -> reliable -> premium fallback
- Provider/privacy constraints
- Structured output contracts
- Cost/latency/error telemetry

Do not migrate production bots yet.

## Phase 2 — Data Foundation

Build:
- PostgreSQL
- pgvector
- schema namespaces for core/chat/memory/ops/files
- backup/restore plan
- retention rules
- tenant/bot/user/channel scoping
- audit identifiers and idempotency keys

Google Sheets remains reporting/export only.

## Phase 3 — Memory v2 + Context Engine

Build:
- recent conversation store
- rolling summaries
- active state
- semantic long-term memory
- retrieval/reranking
- Context Compiler
- memory writer/reviewer policy
- token budgets

Benchmark continuity, Thai reference resolution and token savings.

## Phase 4 — Cloudflare Edge Foundation

Build only components proven useful:
- Worker gateway
- webhook verification/normalization/rate control
- Queues for durable background workloads
- R2 for machine files
- Analytics Engine where it adds operational value

Evaluate, do not automatically adopt:
- AI Gateway in front of OpenRouter
- Hyperdrive
- Durable Objects

Avoid initially unless requirements change:
- D1 (duplicates PostgreSQL)
- Vectorize (duplicates pgvector)
- Workflows (duplicates n8n)

## Phase 5 — Personal Assistant v2

Use the personal assistant as the first full conversational migration:
- natural-language router
- memory v2
- OpenRouter policy
- MCP/tools
- reviewer gates
- cost telemetry

Keep rollback to current workflow.

## Phase 6 — Slip Bot

Second Bot Profile; intentionally minimal conversation:
- LINE group event intake
- slip-image validation/extraction
- duplicate detection
- R2 object storage
- PostgreSQL transaction record
- optional Sheets report sync
- monthly summaries

## Phase 7 — Existing Nippan Customer Bot Adapter

Only after the core is stable:
- keep existing commerce/order business rules
- add model adapter to shared model gateway
- add shared telemetry
- map memory via adapter instead of destructive rewrite
- durable queue migration if justified
- progressively migrate retrieval/memory

No big-bang rewrite.

## Future bot enablement

The platform should allow a new bot to be created primarily from:
- Bot Profile
- Model Policy
- Memory Policy
- Tool Policy
- Data Policy
- Risk Policy
- Channel Adapter

Future business bots are requirements placeholders only; they are not part of current implementation scope.
