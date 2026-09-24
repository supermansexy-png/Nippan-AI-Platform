# Monitoring

Status: **ACTIVE — Phase A**

## Principle

The more autonomy roles get (see the autonomy ladder in `ROLES.md`), the
more monitoring is needed, not less. Monitoring is how the owner keeps
seeing what the system is doing as it grows.

## Who does what

- **Every workflow and every role** writes events to one monitoring log
  (a database table or sheet — one place only).
- **An automated n8n job** assigns each event its level using the rules
  below and sends red events immediately.
- **Auditor** reviews the log (daily in Phase A) and handles escalation.
- **Cost Guard** contributes cost events; it does not own the pipeline.
- **Project Lead (owner)** reads the daily digest and receives red alerts.

Levels are assigned by written rules, not by an AI's judgment of "how
important this feels" — so a new or swapped model cannot quietly change
what gets escalated.

## Levels

**Green — normal.** Logged only. Examples: routine reply, successful
signup, workflow passing audit.

**Yellow — should know.** In the daily digest. Examples: a bot above 80% of
its quota, a repeated question no bot can answer, a model-price change
spotted by Model Scout, error rate above normal but service working.

**Red — must know now.** Sent immediately to the single alert channel.
Examples:
- a bot or tenant projected to cost more than it pays this month
- any sign of cross-tenant data exposure
- a bot revealing its underlying model, or claiming to be human
- a bot giving harmful, false-and-damaging, or off-policy answers
- a data-deletion request that failed
- service down (no replies) for more than 15 minutes
- anything from a segment marked high-risk in `docs/product/CUSTOMER_SEGMENTS.md`

## Keep it simple (Phase A)

- One alert channel (e.g., one LINE chat to the owner).
- No dashboard software: the monitoring table plus a daily digest message.
- Build a real dashboard only when a trigger below is hit.

## Growth triggers

Move to a proper dashboard / multiple channels when: 25+ tenants, the
daily digest takes more than ~15 minutes to read, or a second person helps
monitor.
