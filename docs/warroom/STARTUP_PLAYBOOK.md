# Startup playbook — Phase A, step by step

Status: **ACTIVE — this is the execution order for `ROADMAP.md`'s Phase A**

## How to use this file

This is the concrete build order, not the design rationale (that's in
`docs/product/`, `docs/data/`, `docs/security/`). Whoever is doing the
next unit of work finds their current step here, does it, checks it off
by updating `PROJECT_STATE.md`'s "built vs. designed" section, and hands
off per `WORKING_POLICY.md` Rule 5.

Steps are ordered by dependency, not by priority — most steps genuinely
cannot start before the one above it exists.

## Step 0 — Infrastructure exists (not yet done)

- [ ] n8n instance stood up
- [ ] Lite schema (`docs/data/LITE_SCHEMA_V1.md`) implemented as real
      tables
- [ ] `usage-tracker` MCP tool built (Cost Guard depends on this from day
      one — do not defer it past this step)

Exit: an empty but real n8n + database exists. No bot yet.

## Step 1 — One working bot type, end to end

- [ ] `chat-bot-core` MCP tool built
- [ ] `memory-store` MCP tool built (at minimum: layers 1 and 4 — current
      conversation and business info; layers 2-3 can follow once there's
      real conversation volume to summarize)
- [ ] `web-fetch` and `file-reader` MCP tools built
- [ ] Onboarding assistant flow built per `docs/product/
      ONBOARDING_FLOW.md`
- [ ] PDPA consent notice wired into the bot's first message per
      `docs/security/PDPA_COMPLIANCE.md`, Layer 1
- [ ] `CUSTOMER_FACING_RULES.md`'s model-deflection behavior tested — try
      to get the test bot to reveal its model, confirm it deflects

Exit: a single test bot (not a real customer yet) that a business owner
could plausibly use for real, end to end, including Onboarding.

## Step 2 — First real tenant, manually watched

- [ ] Onboard tenant #1 manually, with a human (the owner) watching
      closely — do not automate this step yet, even if Step 1's tooling
      technically allows it
- [ ] Confirm actual per-message cost against the estimate in
      `docs/product/PRICING_V1.md`; update that document with real numbers
      once available
- [ ] Confirm the message quota number in `PRICING_V1.md` (currently a
      placeholder range) against real usage
- [ ] Set up the single monitoring channel per `docs/warroom/
      MONITORING.md`

Exit: one paying tenant, running for at least a few days, with the owner
confident the cost model and quality bar both hold.

## Step 3 — Repeat onboarding, still manual

- [ ] Onboard tenants #2 through roughly #5-10, still manually
- [ ] Start the Decision Log (`docs/warroom/DECISION_LOG_FORMAT.md`) for
      real, if not already running
- [ ] Confirm Audit-role checks (per `docs/warroom/ROLES.md`) are actually
      happening before each new bot type/workflow reaches a real customer
      — this can still be the owner doing the Auditor's job manually

Exit: enough tenants and enough real conversation data that patterns
start showing up — which segments work, where cost estimates were wrong,
what customers ask for that the current tool set can't do.

## Step 4 — Staff the first automated War Room roles

Per `docs/warroom/ROLES.md`'s activation order: Audit roles (Auditor, Cost
Guard) become live AI seats once there's real conversation volume worth
auditing and real usage data worth tracking automatically, rather than the
owner doing it by hand.

- [ ] Auditor staffed
- [ ] Cost Guard staffed, absorbing the manual usage-tracking from Step 2

Exit: the owner is reviewing summaries and red-tier alerts, not doing the
checking personally.

## Step 5 — Expand toward Phase B

Once Phase A's exit condition in `ROADMAP.md` (25-30 tenants, retained,
profitable) is in sight, this playbook hands off to Phase B's looser goal
(add segments/tools) rather than a fixed step list — Phase B work is
demand-driven, tracked via Marketing's signal-gathering per
`docs/warroom/ROLES.md`, not a predetermined sequence.

## What this playbook deliberately skips

Nothing from `docs/future/` appears here. If a step above seems to need
something from that folder (e.g., "we need real RLS" or "we need a proper
dashboard"), that's the signal described in `docs/future/README.md`'s
trigger table — flag it as `NEEDS_DECISION` for Project Lead, don't build
it into this playbook.
