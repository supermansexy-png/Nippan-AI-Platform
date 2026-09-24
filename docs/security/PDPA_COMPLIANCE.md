# PDPA compliance — Phase A

Status: **ACTIVE — Phase A**

**Not legal advice.** This is engineering-facing guidance derived from
public information about Thailand's Personal Data Protection Act (PDPA),
current as of the research date on this document. Consult a lawyer or a
PDPA compliance advisor before onboarding real customers, especially for
the tenant contract described below. Anthropic/Claude is not providing
legal counsel here.

## Roles under PDPA

- **The tenant (the shop/business renting a bot) is the data controller**
  for their own end customers' data. They decide what the bot is for and
  what data it collects.
- **Nippan AI Platform is the data processor**, acting on the tenant's
  behalf and under their instructions.

This split must be stated explicitly in the tenant agreement at signup —
see "Layer 1" below. Getting this backwards (treating the platform as the
controller) creates liability confusion and is one of the more common
mistakes in Thai SME PDPA setups.

## Layer 1 — tenant responsibility

- **Consent notice to end customers.** The bot shows a short, automatic
  notice the first time an end customer starts a conversation — what's
  collected and why. Do not make this a long legal document; a short,
  plain-language line satisfies the "notify before/at collection"
  requirement and is far more likely to actually be read.
- **Tenant agreement.** The signup flow (part of Onboarding, see
  `docs/product/ONBOARDING_FLOW.md`) must include a plain-language
  statement that the tenant is the data controller for their own
  customers' data, and Nippan AI Platform processes it on their behalf.

## Layer 2 — automated by the platform

- **Retention limits, not indefinite storage.** The 4-layer memory system
  (`docs/data/LITE_SCHEMA_V1.md`) sets an age limit on stored
  conversations and long-term memory entries — do not accumulate
  indefinitely. A reasonable Phase A default: inactive end-customer data
  auto-expires after a bounded period (align with common Thai SME
  practice — roughly a few years of inactivity, not indefinite; confirm
  the exact figure with a compliance advisor before launch).
- **Deletion requests.** An end customer asking a bot "delete my data" (or
  the tenant asking on their behalf) must be actionable — the platform
  needs a real delete path against the tenant_id-scoped tables, not just a
  polite acknowledgment with no backing action.

## Layer 3 — hard rules, no exceptions

1. **Never use tenant conversation data to train or fine-tune any model,
   for any tenant, without separate, explicit, advance consent.** This is
   the single most common driver of PDPA complaints against AI businesses
   in Thailand (PDPC reported a 35% rise in AI-related complaints in 2568,
   mostly from data used outside its stated purpose without notice).
   Feeding a tenant's own data back into *that tenant's own bot's context*
   to answer *that tenant's own customers* is fine and expected — that is
   the product. Using it to improve the platform generally, or any other
   tenant's bot, is not, without separate consent.
2. **No cross-tenant data leakage.** Every table carries `tenant_id`
   (see `docs/data/LITE_SCHEMA_V1.md`); every query is scoped by it. This
   is already the design — this rule just makes it a hard, tested
   requirement, not just a convention.

## Trigger to revisit

Move beyond this lightweight version when:
- Tenant count or data volume grows enough that manual retention/deletion
  handling stops being tenable (this is also a Phase B/C infrastructure
  trigger, see `docs/future/README.md`)
- Any tenant's business touches a PDPA-sensitive data category (health,
  financial specifics beyond simple order amounts, etc.) — that needs its
  own review before onboarding, not a Phase A default
