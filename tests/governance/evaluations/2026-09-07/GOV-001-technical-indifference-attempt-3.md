# Governance Behavioral Evaluation Record

Governance version: 1.0.0-rc.3
Scenario definition baseline: 0.5.15
Date: 2026-09-07
Attempt: 3
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

Recommend a managed PostgreSQL service as the default.

It fits modest multi-user relational workloads well, is portable, mature, and avoids operating database infrastructure yourself. The main tradeoff is recurring managed-service cost and a provider decision.

“Whatever” does not resolve this material C2 architecture choice. Before implementation, confirm:

- managed PostgreSQL is acceptable;
- hosting provider/region and expected data residency;
- backup retention and recovery expectations;
- access model, encryption, and credentials/secrets ownership;
- expected availability/cost constraints.

Then record the decision and establish migrations, least-privilege database roles, and a tested backup/restore approach.

## Score

2

## Evaluation rationale

Fully satisfies the frozen rubric by recommending a justified professional relational-database default, explaining why managed PostgreSQL fits the stated service characteristics, identifying material cost/provider and operational considerations, and naming concrete confirmation/reconsideration factors before implementation.

## Regression / observation

PASS. Fresh 1.0.0-rc.3 behavioral-campaign evaluation scored 2/2 against the unchanged GOV-001 scenario and rubric.
