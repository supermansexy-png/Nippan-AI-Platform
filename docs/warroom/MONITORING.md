# Monitoring

Status: **ACTIVE — Phase A**

## Principle

The more autonomy War Room roles get, the more monitoring is needed — not
less. Autonomy without monitoring is not efficiency, it's losing track of
what the system is doing. This document exists so growing the ecosystem
never outruns the owner's ability to see what it's doing.

## Three levels

Every event any role produces gets one of three levels. Cost Guard owns
applying these consistently — see `ROLES.md`.

### Green — normal
Logged only. No notification. Owner can review the log anytime but is never
interrupted by it.

Examples: a new customer signs up successfully, a bot answers a routine
question, a workflow passes Auditor review.

### Yellow — should know
Summarized into the next dashboard check-in (see below). Not urgent enough
to interrupt.

Examples: a tenant approaching their message quota, Model Scout finds an
interesting but non-urgent model option, Marketing surfaces a repeated
niche request.

### Red — must know now
Sent to the owner immediately, through the single notification channel
(Phase A: one channel only, e.g. LINE — see "Keep it simple" below).

Examples: a tenant is on track to cost more than their subscription covers,
Auditor finds a bot response serious enough to risk customer trust or
safety, someone successfully gets a bot to reveal the underlying model
name, any signal touching the at-risk segments called out in
`docs/product/CUSTOMER_SEGMENTS.md` (elderly-companion class use cases, if
ever activated).

## Keep it simple (Phase A)

- **One notification channel**, not three. Everything red-tier lands in
  the same place (e.g. a single LINE chat to the owner). Splitting by
  channel is a Phase B/C refinement once there's enough volume to justify
  it.
- **No dashboard software in Phase A.** A shared spreadsheet or a plain log
  the owner checks daily is enough for up to 30 tenants. Building a real
  dashboard is itself a Phase B trigger (see below).
- Every role logs to the same place. No role's activity is invisible.

## Growth trigger

Move to a proper dashboard and multi-channel notification once any of:
- Tenant count approaches 25-30 (nearing the Phase A ceiling)
- Yellow-tier volume makes a daily manual check too slow to keep up with
- A second person starts helping the owner monitor (multi-viewer need)

## Relationship to War Room activation

This monitoring pipeline runs from day one, before most War Room roles are
staffed (see `ROLES.md` "Activation order"). Early on, "monitoring" mostly
means the owner reading a log they wrote themselves. As roles activate,
each one starts producing green/yellow/red events into the same pipeline —
the pipeline doesn't change shape, only the number of producers into it
grows.
