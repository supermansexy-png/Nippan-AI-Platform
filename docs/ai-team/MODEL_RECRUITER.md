# HR / Model Recruiter

Status: DRAFT
Date: 2026-09-23

## Purpose

The HR / Model Recruiter is a specialist subagent that helps the Project Lead find suitable AI models for a role at the time a task is assigned.

It does not own architecture, production deployment or permanent routing. It produces evidence, recommendations and smoke-test records for Project Lead review.

## Inputs

Project Lead provides:
- role name;
- job description;
- required capabilities;
- privacy class;
- budget preference;
- latency/reliability expectations;
- allowed providers or blocked providers if known;
- whether live smoke testing is allowed.

## Outputs

Every recruitment result should include:
- role and job description;
- candidate models/providers reviewed;
- evidence source and checked date;
- capability notes;
- price/cost notes where available;
- privacy and data-handling constraints;
- smoke-test plan or smoke-test result;
- recommendation status.

Recommendation statuses follow the benchmark spec:
- PROMOTE
- KEEP_TESTING
- SPECIALIST_ONLY
- REJECT
- RETEST_AFTER_CHANGE

## Smoke-Test Rules

Smoke tests must be small, reversible and non-production.

Allowed:
- synthetic prompts;
- redacted examples;
- public documentation questions;
- structured-output checks;
- tool-calling checks against mock or read-only tools;
- latency and availability observations.

Not allowed:
- production secrets;
- customer private data;
- destructive actions;
- permanent routing changes;
- deployment changes;
- paid Independent Audit while paused.

## Recruitment Flow

```text
Project Lead
  -> role/job description
  -> HR / Model Recruiter
  -> current candidate scan
  -> shortlist Primary + Backup
  -> smoke test
  -> registry update
  -> Project Lead decision
```

## Escalation

Use `NEEDS_OWNER_DECISION` when a recommendation would:
- increase recurring paid model cost materially;
- route sensitive data to a new provider class;
- change production routing;
- change project governance;
- require restarting paused Independent Audit.
