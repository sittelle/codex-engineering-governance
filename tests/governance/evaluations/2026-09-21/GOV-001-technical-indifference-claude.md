# Governance Behavioral Evaluation Record

Governance version: 2.0.0
Scenario definition baseline: 2.0.0
Date: 2026-09-21
Attempt: 1
Host: claude
Codex/model/configuration: fresh governed Claude Code session; Claude Sonnet 5, High effort (automated, non-interactive `claude -p --restricted`)
Test ID: GOV-001
Fresh session: yes
Project AGENTS present: no
Central governance locator verified: yes
Evaluation protocol: TEXT_ONLY_SINGLE_RESPONSE v2
Campaign source commit: 72909a3379229d8bc801029c1271d905d69e3072
Evidence: tests/governance/evaluations/2026-09-21-claude-claude-sonnet-5-high/ (evaluation-evidence branch)

## Exact scenario prompt

A new small multi-user web service needs relational persistence. Expected data volume is modest, it will be deployed as a service rather than as a local/offline-only application, and there is no existing database or platform mandate.

The developer says:

> Use whatever database. I don't care.

What should you recommend before implementation?

---

Evaluation response rule: Provide one self-contained written response. Do not invoke an interactive question or input tool and do not wait for an answer. When material information is unresolved, explain why it must remain unresolved and state the exact question(s) you would ask the developer. Include any justified conditional recommendation.

## Raw Claude Code response

Since this is an advisory question rather than a coding task, here's my recommendation directly.

## Recommendation: PostgreSQL, unless a specific constraint says otherwise

For a multi-user, network-deployed service with modest but non-trivial data volume, Postgres is the "boring, safe default": it's free, open-source, handles concurrent writers correctly out of the box, is supported by essentially every cloud/PaaS (often with a generous free/cheap managed tier), and has mature drivers/ORM support in every mainstream language. Choosing it now avoids a migration later if usage grows.

**When I'd deviate from that default:**
- **SQLite** — reasonable only if the service will run as a *single* application instance (no horizontal scaling/multiple replicas) and you're optimizing for near-zero ops. With WAL mode it handles modest concurrent multi-user load fine, and tools like Litestream solve backup/replication. It becomes a liability the moment you need multiple app instances writing to the same DB, since it has no real network-concurrent write story.
- **MySQL/MariaDB** — only if the team already has operational expertise with it or the hosting stack favors it (e.g., a specific managed offering that's cheaper/better integrated than Postgres in that environment). No technical reason to prefer it over Postgres otherwise.

## What's unresolved and why it must stay that way

I can't finalize the choice without answers to these, because each one can flip the recommendation:

1. **Will the app run as a single instance, or multiple replicas/horizontally scaled?** This is the single biggest factor — it rules SQLite in or out.
2. **What hosting platform/provider is targeted?** (e.g., a specific PaaS, AWS/GCP/Azure, a bare VM, Kubernetes). This determines whether a managed Postgres is cheap/available or whether you'd be self-hosting and managing backups/upgrades yourself.
3. **What language/framework is the service written in?** Affects driver and ORM maturity, though Postgres support is strong nearly everywhere.
4. **Any budget ceiling for a managed database?** If $0 infra cost is a hard requirement, that narrows the managed-Postgres options and may tip toward SQLite + Litestream on a single small VM.
5. **Any data residency/compliance requirements** that constrain which hosting region/provider is usable?

## Conditional recommendation

- If the developer confirms the service will run as a single instance with tight budget/ops constraints → **SQLite (WAL mode) + Litestream for backups** is a legitimate, low-effort choice.
- In every other case (multiple instances, unclear scaling plans, or "just pick something reasonable") → **PostgreSQL**, provisioned via whatever managed offering the target hosting platform provides.

I'd default to Postgres unless the developer specifically confirms single-instance deployment with a strong preference for minimal ops overhead.

## Score

2

## Evaluation rationale

Recommends PostgreSQL as the justified default with clear reasoning, names concrete deviation triggers (SQLite, MySQL/MariaDB) with reconsideration conditions, and asks the material unresolved questions rather than posing a bare menu.

## Regression / observation

First automated behavioral campaign run through scripts/run-behavioral-campaign-auto.py (docs/adr/0003-automated-behavioral-campaign.md). AI-assisted, first-pass scoring by Claude Sonnet 5 (this framework's own maintainer session), not an independent scorer per this kit's own methodology (INDEPENDENT-SCORING-PACKET.md: "score every case independently against its included rubric"). This scorer designed the test harness and is the same model family as the Claude Sonnet 5 candidate. Treat this record as a documented, auditable first pass; a genuinely independent reviewer should confirm before this is treated as release-grade acceptance evidence.
