# Nippan AI Platform

ภาษาไทย: อ่าน `README.th.md` (สรุปทั้งโครงการ) และ `FEASIBILITY_REVIEW.th.md` (ประเมินความเป็นไปได้)

Status: **Phase A — market test**

Nippan AI Platform rents AI bots to small Thai businesses: chat, secretary,
and other bot types, all on one platform, priced flat and simple. Phase A
targets up to 30 tenants at 299 THB/month, running on n8n. This is a
deliberately small first version, built to prove the market before
committing to a larger architecture — see `docs/future/README.md` for the
larger version this can grow into.

## Product principles

- Cheap, simple, and easy to understand for a non-technical small-business
  owner
- The underlying AI model/vendor is invisible to customers — never named,
  never selectable; see `docs/product/CUSTOMER_FACING_RULES.md`
- The bot catalog grows by adding small MCP tools, not by rebuilding the
  core — see `docs/product/MCP_TOOLS_V1.md`
- Setup for the business owner (Onboarding) is a conversation, not a form
  — see `docs/product/ONBOARDING_FLOW.md`

## Phase A architecture

```text
End customers  ->  tenant's own LINE OA / web chat
                          |
                          v
                 n8n (self-hosted core)
                /                      \
        MCP tools                   PostgreSQL (lite schema)
  (chat, memory, onboarding,   tenants > bots > channels >
   usage, monitoring, handoff)  end customers > conversations
```

War Room (`docs/warroom/`) sits above this as the operating team — a mix
of the owner acting directly and, as volume justifies it, staffed AI
roles: Project Lead, Development, Audit (incl. Cost Guard), Operations,
Marketing, Model Scout. See `docs/warroom/ROLES.md` for what each does and
the order they come online.

## Key decisions (Phase A)

- Any platform connects through one standard adapter contract; the core
  never knows which platform it's talking to — `docs/product/INTEGRATIONS.md`

- n8n is the runtime core, not a full FastAPI/Cloudflare Worker/
  PostgreSQL+pgvector stack — that stack is preserved in `docs/future/`
  for when scale actually needs it
- OpenRouter is the default model gateway, not the only one — new
  providers can be added; Model Scout watches the market for this
  (`docs/product/MODEL_POLICY.md`)
- Cheap/free models are the default for routine tasks; cost tier follows
  task type, not tenant
- PDPA compliance is built in from Phase A, not deferred —
  `docs/security/PDPA_COMPLIANCE.md`
- Every customer-data table is scoped by tenant and bot, no exceptions —
  `docs/data/LITE_SCHEMA_V1.md`
- Each business uses its own LINE Official Account; chat replies are free
  and unlimited, bot-initiated reminders are capped at 200/month —
  `docs/product/PRICING_V1.md`
- Bots never name their model and never pretend to be human —
  `docs/product/CUSTOMER_FACING_RULES.md`

## Start here

1. `PROJECT_STATE.md` — what's actually built vs. designed
2. `ROADMAP.md` — Phase A/B/C
3. `WORKING_POLICY.md`, `docs/warroom/TASK_CONTROL.md`, `TASKS.md` — how
   anyone (AI or human) operates day to day, and the current task board
4. `AGENTS.md` — behavioral rules for any AI working on this repo
5. `docs/warroom/ROLES.md` — the operating structure
6. `docs/warroom/STARTUP_PLAYBOOK.md` — the concrete step-by-step build
   order from zero
7. `docs/product/` — pricing, segments, onboarding, tools, model policy,
   integrations
8. `docs/security/PDPA_COMPLIANCE.md` — before onboarding any real tenant
9. `docs/future/README.md` — the larger version this can grow into, and
   when to pull each piece back in

## Protected production systems

- `supermansexy-png/Ai-Nippan`
- existing Personal Assistant / n8n production workflows

Do not migrate or rewrite them during the current phase.
