# Customer segments

Status: **ACTIVE — Phase A**

## Expected segments

- Online shops (chat + order-taking)
- Appointment-based services (secretary bot: booking, reminders)

## Underserved segments (real market gap — no direct competitor targets these)

These are viable Phase A customers using the same bot infrastructure, just
a different Onboarding conversation and MCP tool mix:

- Solo tradespeople (aircon/plumbing/electrical repair) — answers while
  hands are busy on a job
- Motorcycle taxi / delivery riders — queue and repeat-customer tracking
  while driving
- Small flower shops / grocers, especially with an older, less
  tech-comfortable owner
- Solo massage/beauty clinics — booking while hands are occupied with a
  client
- Pet boarding / grooming — booking, automatic photo updates to owners
- Farmers / wholesale produce sellers — daily price quotes, advance orders
- Secondhand sellers in Facebook groups / flea markets
- Promotion/price-checker bot (reads a store's own listed prices)
- Playlist assistant for DJs/musicians (venue theme -> song suggestions)
- Fortune-telling / lottery-interest bots — entertainment framing only,
  see guardrail note below
- Document/license renewal reminder bot — memory-driven, not just Q&A;
  plays directly to the 4-layer memory system's strength

## Guardrail: fortune-telling / gambling-adjacent bots

Frame strictly as entertainment, not as financial or life advice. Include
a light, natural disclaimer. Watch for signs a user is treating the bot as
a real decision-making tool for gambling — Cost Guard/Support should flag
a pattern of this to Project Lead.

## Deferred segment: elderly companion bots

**Not part of Phase A.** Concept: companionship, medication reminders,
health/diet chat, keeping family informed. Real need, real market size,
genuinely no direct competitor — but this is the highest-risk idea
discussed and needs its own safety framework before any build starts:

- Never let the bot diagnose or give real medical advice — reminders only,
  never adjusting/interpreting medication
- Must have a real emergency-escalation path to family, not just "keep
  chatting"
- Family (not the elderly user) does the initial setup, given the target
  user's likely unfamiliarity with the tech
- Needs input from someone with actual elder-care expertise before writing
  the conversation design — do not let an AI role improvise this alone

Do not build any part of this until Project Lead explicitly moves it into
an active phase with its own safety document.

## Deferred: data purchasing

No dataset marketplace sells what these bots actually need (a specific
customer's prices, hours, tone). That only comes from Onboarding. Buying
external training data becomes relevant only if the specialized/high-value
pivot (`docs/decisions/PIVOT_OPTION.md`) activates and needs deep
domain-specific knowledge no customer's own data provides.
