# ADR-0002 — Control Plane and Multi-Tenant Product Model

Status: Accepted  
Date: 2026-09-22

## Decision
Design the platform around Tenant -> Application -> Agent -> Channel -> Conversation and separate the Control Plane (configuration/dashboard) from the Data Plane (runtime).

## Context
The platform must support Nippan website AI, bots, future apps/programs, internal agents and possible rental/SaaS customers.

## Consequences
- Agent is a role/configuration, not synonymous with bot.
- Dashboard configuration is versioned and publishable/rollbackable.
- Usage attribution, quotas and tenant isolation are first-class.
- Billing can be added later without redesigning identity and usage data.
