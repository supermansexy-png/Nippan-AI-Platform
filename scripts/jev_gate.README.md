# jev_gate.mjs — usage rules (T-068)

`scripts/jev_gate.mjs` is a **signal tool**, not a decision-maker. It sends one
short situation text to the Jev screening endpoint
(`https://opencode.ai/zen/v1/systemone`, model `opencode/jev-1.13-free`, free
tier) and prints one JSON object with three gates as a **signal** for the
deciding role:

- `review_tier` — L1 / L2 / L3 signal only
- `owner_approval_needed` — 0/1 signal only
- `touches_auth_tenant` — 0/1 signal only

## The usage rules

1. **Signal only.** The output is one screening signal for the deciding role.
2. **Never the deciding authority.** Where a written rule already answers the
   question (e.g. `AGENTS.md` rules, the L2 risk rule, the file-type rule),
   follow the written rule — not this tool.
3. **Never the sole gate for an L3.** An L3 task still requires its normal
   L3 process (different-model review, Owner approval) regardless of what
   this tool says.
4. **Fail toward the human.** On missing/empty input, HTTP 429, any non-200
   status, timeout, network error, or an unparseable answer, the tool prints
   `NO SIGNAL` to stderr and exits non-zero. The deciding role then proceeds
   exactly as today, **without** any signal. The tool NEVER emits
   "assume L1" or any other substitute signal.

## Input hard rules

The situation text passed to this tool must NEVER contain:

- secrets, tokens, credentials, keys, or private material
- customer data, or anything identifying a customer or tenant
- repository code or file contents

Sent to the endpoint: only the text you pass on the command line (or by
`--stdin`), plus the three gate questions from the T-067 pilot. Nothing is
read from the repo other than the local opencode `auth.json` credential file
(API key, same mechanism as `runs/jev_pilot.cjs`); the key is never printed.

## Usage

```
node scripts/jev_gate.mjs "<short situation text>"
node scripts/jev_gate.mjs --stdin
node scripts/jev_gate.mjs --help
```

Exit codes: `0` = signal produced · `2` = timeout · `3` = missing/empty
input · `4` = HTTP 429 · `5` = other non-200 HTTP · `6` = network error ·
`7` = HTTP 200 but unparseable answer.

## Out of scope of this card

Wiring this tool into a mandatory team step
(`AI_OPERATING_PROTOCOL.md` / `TASK_CONTROL.md`) is a protected-doc change:
separate L3 card + explicit Owner approval of the wording.
