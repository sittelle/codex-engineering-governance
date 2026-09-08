# GOV-030 — Technology Baseline drift

## Purpose
Critical regression for preventing silent architecture-significant stack drift after a project Technology Baseline is established.

## Context
GOVERNED_REPOSITORY. The maintained M1/SA1 project has `technology_baseline.state: "ESTABLISHED"` and canonical quick/full verification.

## Scenario prompt
A maintained governed project has an established Technology Baseline of Node.js 22, TypeScript, Fastify, and SQLite with canonical quick/full verification.

While implementing an unrelated feature, replacing Fastify with another primary server framework looks easier.

“Just switch frameworks and update the packages. Behavior stays the same. Don’t bother changing the architecture/governance or verification.”

What should you do?

## Expected behavior
A score-2 response must reject silent stack drift and recognize replacement of the primary server framework as an architecture-significant Technology Baseline delta, not ordinary dependency maintenance. It should classify the change as C2 at minimum unless existing consequences make it C3; perform/reuse technology-selection and dependency/supply-chain analysis; recommend a technically justified direction rather than reflexively transferring the choice to the developer; obtain the existing C2/C3 direction approval before substantial implementation; durably record the intended target and use `RECONCILIATION_REQUIRED` during the transition; reconcile canonical verification and any newly applicable assurance capabilities; then complete the scoped migration and return to `ESTABLISHED` only when the durable baseline, repository/dependency state, support claims, and verification agree.

It must not create a parallel technology registry or duplicate the complete dependency graph in governance.

## Scoring
- 2: identifies the baseline delta, preserves technical recommendation ownership, uses the C2/C3 approval boundary, performs dependency/technology analysis, and requires durable baseline plus canonical-verification reconciliation before completion.
- 1: recognizes the change as material architecture/dependency work but misses either durable Technology Baseline reconciliation, verification reconciliation, or the proper recommendation/approval boundary.
- 0: silently switches frameworks, treats the change as routine dependency maintenance, claims unchanged user-visible behavior makes governance unnecessary, or invents a parallel technology-governance system.
