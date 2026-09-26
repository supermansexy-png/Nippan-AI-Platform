# Model policy

Status: **ACTIVE — Phase A**

## Gateway

OpenRouter is the default gateway — one integration point for many model
providers. This is not exclusive: any additional provider (Thai-specific
providers, a cheaper specialist API, a free tier from a new entrant) can be
added alongside it. Nothing in this system hardcodes "OpenRouter" as the
only path — see `docs/warroom/ROLES.md`, Model Scout.

## Tier by task, not by tenant

| Task | Model tier |
|---|---|
| Routine end-customer chat (hours, prices, simple Q&A) | Cheapest viable model (free tier or lowest-cost paid, e.g. Gemini Flash-class) |
| Tasks needing accuracy (bookkeeping-style bots, calculations) | Mid-tier model |
| Onboarding (one-time per customer, high-stakes first impression) | Can afford a stronger model — this cost happens once, not every message |

No tenant is on a permanently better or worse model because of who they
are — tier is set by task type, applied uniformly.

## Cost policy — value first

Free and inexpensive paid models are both allowed. Choose the lowest-cost
model that can reliably perform the required task to the required
standard.

A stable inexpensive paid model may be preferred over an unstable free
model when it reduces retries, failures, latency, poor-quality output, or
wasted tokens.

### Self-approval guideline for NEW model selections

- Input: up to approximately **$0.25 per 1M tokens**
- Output: up to approximately **$1.00 per 1M tokens**

If a NEW candidate materially exceeds these limits, ask the Owner before
appointing it.

Models already listed in the current model roster are Owner-approved for
this pilot even if current market pricing temporarily exceeds the general
recruitment threshold. Do not repeatedly ask the Owner to re-approve an
already approved roster model.

## Fallback

Every tier keeps at least one alternative model from a different provider.
See the Retry/Failover policy below for exactly when the Primary is
retried and when the Backup takes over. If Primary and Backup both fail,
the bot sends the outage message in `docs/product/BUSINESS_OPERATIONS.md`
§1 and a red event is logged.

### Retry / failover policy

For transient failures (HTTP 429, HTTP 403 caused by provider
availability, timeout, provider overload, temporary server error,
malformed provider response, truncated response, temporary tool failure):

1. Retry the Primary **at most once** when reasonable.
2. If it fails again, switch to the approved Backup.
3. If the Backup also fails, **STOP and report the failure** to Project
   Lead / Owner.

Never create an endless retry loop.

### Quality failure policy

A technically successful API response may still count as a failure when
the model repeatedly produces incorrect work, hallucinated evidence, poor
instruction-following, missing required output, inappropriate tool use,
broken code, unacceptable review quality, severe formatting failures, or
repeated scope violations.

Allow **one** reasonable correction attempt. If the same model remains
unsuitable, switch to Backup rather than repeatedly prompting it.

### Anti-redundancy (independent review) policy

Review and security work is only meaningful if it can catch the mistakes
of the author that produced the work. Therefore:

- The **reviewer** model must be a **different model** than the current
  **builder** model — and this must hold whether the builder is running
  its Primary or its Backup. Same rule for **security**.
- Concretely: reviewer/security must not share a model with builder's
  Primary **nor** builder's Backup. Checking "different provider" alone is
  not enough — the actual model name must differ (a different provider
  that happens to serve the same model still fails this rule).
- If the Builder's Primary or Backup changes, the Reviewer/Security
  assignments must be re-checked.

Rationale: if Reviewer runs on the same model (even as a different
provider, or only when the builder falls back) as the Builder, a
systematic flaw in that model is invisible to the review. The reviewer
must be a genuinely independent set of eyes, not the same brain.

## OpenCode Zen exception

OpenCode Zen is **FREE MODELS ONLY**. Never apply OpenRouter's paid-model
policy to OpenCode Zen, and never authorize a paid Zen model.

## OpenCode Go — approved provider (Owner decision 2026-09-26)

OpenCode **Go** is a separate provider from Zen (provider id `opencode-go` in
config, model slugs written `opencode-go/<model-id>`). The Project Owner
subscribed to Go at $10/month. Go is an **approved provider** for dev-time
work, and it is NOT covered by the Zen "free models only" rule above.

Go models are already paid for by the subscription, so their per-token list
price is a *usage-meter unit*, not a new cash cost. A Go model may therefore
be used even when its list price would exceed the self-approval guideline —
the cap that applies is the Go per-model usage limit, which the Owner can see
and stop at any time.

- Zen stays free-models-only. Do not mix the two rules.
- Go model ids MUST be written `opencode-go/<model-id>`. A Zen-style
  `opencode/<model-id>` slug for a Go-only model fails with an opaque
  `Unexpected server error` that looks like a permission problem but is a
  naming problem.
- One Go subscription per workspace: the main chat and the headless workers
  share the same 5-hour / weekly / monthly buckets.

### Go usage limits

Limits are denominated in monthly dollar value of usage, in three layers per
model: **5-hour = 20%** of the model monthly limit, **weekly = 50%**,
**monthly = 100%**. When a bucket is empty the request is blocked (free
models still work). Enabling **Use balance** in the console makes Go fall
back to the Zen balance instead of blocking.

A $15 model therefore allows only ~$3 per 5 hours. Queue the strong models
for short high-stakes tasks; do not hold long conversations on them.

### Long-conversation cost rule (Owner-approved 2026-09-26)

A planning conversation re-sends the whole history every turn, so **cached
read** dominates the bill, not output tokens. Measured on a real 202-turn
session (~28M cached-read tokens), against Artificial Analysis indices
verified live on 2026-09-26:

| Go model | intelligence | cached read /1M | That session | Retention |
|---|---:|---:|---:|---|
| `mimo-v2.6-pro` | **46.3** | $0.0036 | **$0.10** | 0 days |
| `grok-4.7` | **46.4** | $0.50 | $14.00 | 30 days |
| `kimi-k3` | 43.6 | $0.30 | $8.40 | 0 days |
| `gpt-6-luna` | 37.3 | $0.01 | $0.28 | 30 days |
| `deepseek-v4.1-flash` | 39.5 | $0.003 | $0.08 | 0 days* |
| `deepseek-v4-pro` | 30.4 | $0.022 | $0.62 | 0 days* |

Rule: **expensive model for a short chat, cheap model for a long chat.**

`grok-4.7` and `mimo-v2.6-pro` have effectively identical intelligence
(46.4 vs 46.3) — Grok costs **138x more** per long thread and retains data
for 30 days. Grok is therefore not used. `kimi-k3` and `qwen3.8-max` are
strong but 25x-175x dearer on a long thread; reserve them for short
high-stakes tasks and final code, where the context is small.

`deepseek-v4-pro` is **rejected** — intelligence 30.4, the lowest of the
set, despite the "Pro" name.

By job:

| Job | Model | Why |
|---|---|---|
| Long planning / strategy conversation | `mimo-v2.6-pro` | best brain per dollar, 0-day retention, 1.05M context |
| Code writing and code review | `kimi-k3` | coding 76.2 / agentic 50.0 — best coder available; but only ~490 requests/month, so use on final code, not every edit |
| Everyday work, high volume | `deepseek-v4.1-flash` | $60 bucket, ~130,000 requests/month |
| Anything sensitive | `mimo-v2.6-pro` or `space-bunny-free` | 0-day retention |


### Go data-handling (privacy) rules

Go publishes retention per model and the project must respect it:

- **0-day retention** — safe for sensitive/redacted input: GLM, Kimi, Qwen,
  MiMo, MiniMax, DeepSeek, LongCat, Hy, `space-bunny-free`.
- **30-day retention — not for secrets**: `grok-4.7`, `grok-4.6`,
  `gpt-6-luna`, `gpt-5.6-luna` (abuse-monitoring logs).
- **Trains on your prompts — never send project or customer data**:
  `muse-spark-1.3-contributor`, `muse-spark-1.2-contributor`.

`opencode-go/space-bunny-free` remains free, unlimited and zero-retention —
keep it as the default whenever retention is unknown or the input is
sensitive.

## Speed matters on LINE

Default models for end-customer replies must answer fast enough for LINE's
reply flow (Auditor measures this in Step 1). A smarter but slow model is
the wrong choice for chat replies.

## Free/cheap models

Explicitly in scope for routine tasks. OpenRouter's free tier and
sub-$0.10/M-token models are the default for anything that doesn't need
high accuracy. This is a cost-control mechanism, not a corner being cut —
see `docs/product/PRICING_V1.md` for why the margin depends on it.

## Work style

Prefer useful work over ceremony.

- Do not run unnecessary smoke tests after a model has already been
  accepted, unless a new failure provides a reason.
- When a real failure occurs: identify the failing component, fix or route
  around that specific problem, then continue the real task. Avoid
  restarting the entire validation process unnecessarily.
- Do not repeat completed work without a reason.

## Model Scout's job

Continuously watches for:
- New models that beat the current pick on price or quality for a given
  tier
- New providers worth adding to the routing options

Proposes swaps to Project Lead. Never swaps automatically — see
`docs/warroom/ROLES.md`.

## Never hardcode a model into a role

Model choice lives in the current model roster, not in role definitions or
agent prompts. A role (see `docs/warroom/ROLES.md`) is filled by whichever
approved model is suitable at the time. Model Scout proposes swaps and
Project Lead approves — no role permanently owns a specific model name.

## Catalogue-wide recruitment (Owner rule)

When recruiting a model for a role (choosing a Primary or Backup), the
Model Scout / recruiter must scan the **whole OpenRouter catalogue**
(500+ models) — not just the already-approved roster or previously known
models. Scan systematically across multiple axes (price, popularity,
recency, benchmarks) using server-side filters so every relevant slice of
the catalogue is covered.

Only after a full-catalogue scan may the recruiter conclude that a
previously approved model is still the best pick — and the breadth of the
scan (queries, rough coverage, date) must be recorded as evidence in the
roster or DELIVERY. Picking from a stale shortlist without scanning is
not allowed.

## What never changes because of this policy

Customer-facing behavior (`CUSTOMER_FACING_RULES.md`) is identical
regardless of which model or provider is actually serving a given message.
Model policy is entirely a backend concern.
