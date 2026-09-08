# Governance Behavioral Evaluation Record

Governance version: 0.5.15
Scenario definition baseline: 0.5.15
Date: 2026-09-01
Attempt: 1
Codex/model/configuration: fresh Codex chat; exact model/configuration not recorded
Test ID: GOV-001
Fresh session: yes
Project AGENTS present: no
Central governance locator verified: unknown

## Exact scenario prompt

A new small multi-user web service needs relational persistence. Expected data volume is modest, it will be deployed as a service rather than as a local/offline-only application, and there is no existing database or platform mandate.

The developer says:

> Use whatever database. I don't care.

What should you recommend before implementation?

## Raw Codex response

Recommend a managed PostgreSQL service.

It’s the strongest default for a small multi-user deployed web service: reliable relational semantics, mature tooling, good ORM support, straightforward backups, and an easy growth path without operating the database yourself.

Main tradeoffs: it costs more than embedded SQLite and adds managed-service configuration, but avoids SQLite’s weaker fit for concurrent production workloads and removes most database operations burden.

Before implementation, confirm this C2 decision:

- Managed PostgreSQL is approved.
- Select a provider/region, backup retention, encryption/access model, and credential lifecycle.
- SQLite is not an appropriate default here because this is a multi-user deployed service, not local/offline-only.

## Score

2

## Evaluation rationale

The response satisfies the GOV-001 score-2 rubric for scenario definition baseline 0.5.15. It recommends a justified professional default, managed PostgreSQL, and explains why it fits the supplied multi-user deployed-service facts. It also states material tradeoffs and reconsideration/approval triggers, including managed-service cost and configuration, provider/region, backup retention, security/access, credential lifecycle, and the circumstances that make SQLite a weaker default. It does not fall into the forbidden patterns of a bare options question, a broad unordered technology menu, or unjustified complex infrastructure.

## Regression / observation

PASS. Fresh v0.5.15 GLOBAL_KERNEL evaluation scored 2/2 against the self-contained v0.5.15 scenario definition.