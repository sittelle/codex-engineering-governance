# Technology Selection

Activate for consequential language/framework/database/runtime/infrastructure choices and for proposed changes to an established Technology Baseline.

Establish requirements, platforms, deployment, trust/data, scale, maturity/assurance, distribution, licensing, and support constraints first.

Compare at most a few serious candidates on fit, security maturity, ecosystem/support, maintenance, dependency burden, testing, deployment, portability, performance, and license. Recommend ONE default and explain reconsideration triggers.

When product/security constraints are resolved and the developer is technically indifferent, make the technically justified recommendation/default rather than asking the developer to choose among equivalent technologies.

For architecture-significant choices, identify the Technology Baseline impact and produce enough durable decision content to record:
- category and selected technology/approach;
- scope/role;
- material rationale and meaningful alternatives/tradeoffs;
- supported runtime/platform or deployment constraints;
- supply-chain/dependency implications where relevant;
- canonical-verification implications;
- reconsideration triggers.

Do not duplicate the complete dependency graph in the Technology Baseline. Exact resolved dependency versions remain in ecosystem manifests/lockfiles unless a version is itself architecture-significant.

A material change to an `ESTABLISHED` Technology Baseline is C2 at minimum and requires the existing C2/C3 readiness/approval boundary before substantial implementation. Keep the baseline `RECONCILIATION_REQUIRED` during an approved transition until durable record, repository state, and canonical verification agree.

For a material baseline transition, return a **Technology Baseline Transition Summary** before substantial implementation. Explicitly label: `Delta / classification`, `Technical recommendation`, `Dependency / supply-chain and triggered impacts`, `Approval state`, `Transition state / durable record`, `Verification / assurance reconciliation`, and `ESTABLISHED closure criteria`. Do not collapse these into “update as needed”; state `NOT APPLICABLE` with reason where a dimension is genuinely irrelevant.

Do not choose based on hype, agent familiarity, or speculative future scale. Do not create a central preferred-technology allowlist.
