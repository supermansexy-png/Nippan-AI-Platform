# Dev working guide (build-time)

Status: **ACTIVE — Phase A (dev-time, building the system)**

Purpose: how work is delegated, evidenced and reported while we BUILD the
system on this repo. This is the dev-time counterpart of the runtime
ecosystem in `docs/warroom/ROLES.md`. The owner is Project Lead in Phase A;
Project Lead here is the assistant that prepares work and drafts options.

`AI_OPERATING_PROTOCOL.md` (Intake before work, Delivery with evidence,
verification by a different model) is binding on everything in this
document. `TASK_CONTROL.md` defines the task cards, risk levels, WIP and
budget stop rules. `MODEL_POLICY.md` defines cost/value, Zen, retry and
quality-failure rules. This file only adds the delegation, evidence and
reporting conventions for dev-time work.

## Workflow

Owner → Project Lead → Specialist(s) as required → Reviewer (independent
review when appropriate) → Project Lead → Owner

Do not call every role for every task. Use only the roles actually needed.

Available dev roles, chosen per task:
- **builder** — write/edit code, tests, implementation
- **reviewer** — independent check of L2/L3 work (different model)
- **security** — defensive security review (auth, isolation, secrets)
- **ops** — GitHub, CI, hosting, deployment evidence, operational readiness
- **researcher** — genuine information gap only
- **model-recruiter** — propose/select models and pricing under
  `MODEL_POLICY.md`, propose only; owner approves

Model choice: in dev-time the model name used for a job may be stated
(same-team info, aids review). The "never name your model / never hardcode a
model into a role" rule applies to the runtime layer where real customers
are served — see `MODEL_POLICY.md` and `CUSTOMER_FACING_RULES.md`. The
current roster lives as a data file; model-recruiter proposes, owner
approves. Change a model only when the current one repeatedly fails,
is unavailable, reliability degrades, cost changes materially, a task needs
a capability the current model lacks, or the owner/Project Lead requests
recruitment — never merely because another model scores higher on a
benchmark.

## Delegation policy

Use the smallest appropriate team.

Examples (dev-time):

- Coding task: owner → builder → reviewer → owner
- Schema/tools task: owner → builder → security → reviewer → owner
- Hosting/operational task: owner → ops → reviewer (if needed) → owner
- Security review: owner → security → reviewer (if needed) → owner
- Research: owner → researcher → owner
- Model selection/failure: owner → model-recruiter → owner
- Complex task: Project Lead may call several specialists sequentially,
  then send the combined findings to reviewer

Avoid invoking many specialists simultaneously when sequential work is
sufficient.

Do not call model-recruiter simply because it exists. Do not call builder
for a task that requires no implementation. Do not call researcher when
sufficient evidence already exists. Do not call reviewer repeatedly without
new work or evidence.

## Evidence policy

Never invent: GitHub evidence, commit hashes, CI results, test results,
production state, benchmark results, pricing, uptime, provider status,
audit results, prices, availability.

Clearly distinguish:
- **VERIFIED** — evidence actually provided or retrieved
- **INFERRED** — reasonable conclusion based on available evidence
- **UNKNOWN** — information not currently verified

Never convert intent into proof. "routes are intended to share
authentication" does NOT mean "all routes have been verified to share
authentication".

## Cost and retry

- `MODEL_POLICY.md` section "cost policy — value first": free and cheap
  paid are both allowed; choose the lowest-cost model that reliably
  performs the task. New selections: input ≤ ~$0.25/1M, output ≤ ~$1.00/1M;
  above that, ask the owner. Roster models already approved are not
  re-asked.
- OpenCode Zen = FREE MODELS ONLY (never authorize a paid Zen model).
- Retry/failover: retry Primary at most once → switch to approved Backup →
  both failed: STOP and report. Never create an endless retry loop.
- Quality failure: allow one reasonable correction; if the same model stays
  unsuitable, switch to Backup rather than repeatedly prompting it.

## Security / privacy boundaries

Never request, expose, reproduce, or put into prompts: API keys, access
tokens, passwords, credentials, customer secrets, private production data,
unnecessary personal information. Use synthetic, public or redacted data
whenever possible. Stop and escalate if secrets would be required.

## Production boundaries

PILOT / NON-PRODUCTION by default. Never automatically deploy, merge,
enable production access, alter production routing/config, delete
production data, or promote pilot to production. If a task could affect
production, require explicit owner authorization. Planning, review, code
preparation, tests, documentation and recommendations may proceed within
approved scope.

## Work style

Prefer useful work over ceremony. Do not run unnecessary smoke tests after
a model is already accepted unless a new failure gives a reason. On a real
failure: identify the failing component, fix or route around that specific
problem, continue the real task — avoid restarting the whole validation
process unnecessarily. Do not repeat completed work without a reason. Keep
specialist outputs concise. Project Lead synthesizes rather than
concatenates agent responses.

## War Room (dev-time)

After significant work, Project Lead may convene a War Room. It is a short
synthesis and decision-support summary (not a rerun of completed work). It
should cover, when relevant:

- what was completed
- evidence (models used may be named — dev context)
- important findings and disagreements
- security and operational concerns
- reviewer findings
- unresolved risks
- recommended next action

The owner makes the final decision. Record any decision in
`docs/warroom/decision-log.md` per `DECISION_LOG_FORMAT.md`.

## Final report after a task

Return a concise owner-ready result containing, when relevant:

- Work completed
- Roles/models used
- Verified evidence
- Reviewer verdict (ACCEPTED / RETURNED — see AI_OPERATING_PROTOCOL Gate 4)
- Important findings
- Unresolved risks
- Failures/fallbacks
- Production impact
- Recommended next action

Do not hide failures. Do not exaggerate success. Do not invent evidence.