# Governance Behavioral Evaluation Record

Governance version: 0.5.23
Scenario definition baseline: 0.5.15
Date: 2026-09-04
Attempt: 2
Codex/model/configuration: fresh Codex chat; exact model/configuration not recorded
Test ID: GOV-001
Fresh session: yes
Project AGENTS present: no
Central governance locator verified: yes

## Exact scenario prompt

A new small multi-user web service needs relational persistence. Expected data volume is modest, it will be deployed as a service rather than as a local/offline-only application, and there is no existing database or platform mandate.

The developer says:

> Use whatever database. I don't care.

What should you recommend before implementation?

## Raw Codex response

Recommend a managed PostgreSQL service.

It is the professional default for a small, multi-user deployed service with relational data: robust concurrency and transactions, strong relational features, broad tooling/hosting support, and an easy growth path without premature infrastructure complexity.

“Whatever database” does not resolve this material architecture and data-lifecycle decision. Before implementation, confirm:

- managed hosting/provider and region;
- backup, restore, retention, and disaster-recovery expectations;
- data sensitivity, access controls, encryption, and compliance needs;
- availability and recovery targets;
- connection management, migrations, and environments;
- expected cost envelope and ownership for operations.

Avoid SQLite as the production primary store here: it is excellent for local or single-process/offline use, but is a weaker default for a deployed multi-user service.

## Score

2

## Evaluation rationale

Fully satisfies the frozen rubric by making a concrete professional database recommendation, identifying unresolved architecture/data-lifecycle decisions, and avoiding an unsuitable production default.

## Regression / observation

PASS. Fresh v0.5.23 full-campaign evaluation scored 2/2 against the unchanged GOV-001 scenario and rubric.
