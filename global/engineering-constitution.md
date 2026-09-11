# Engineering Constitution

Version 2.0.0-rc.1.

## Objectives

Software MUST be engineered for correctness, security, maintainability, understandability, testability, reproducibility, proportional complexity, and documentation appropriate to its purpose.

## Simplicity

Use the least complex mature architecture that satisfies approved requirements, security, supported platforms, credible scale, and operational needs. Avoid speculative microservices, queues, caches, orchestration, generic extension systems, and abstraction layers.

## Architecture

Architecture follows requirements. Identify system boundary, actors, major components, interfaces, data stores, external systems, trust/privilege boundaries, important data flows, deployment, and failure boundaries as applicable.

Prefer high cohesion, low unnecessary coupling, and explicit ownership.

## Contracts and validation

Important boundaries define input, output, failure, side effects, invariants, and security expectations.

Validate untrusted data structurally and semantically at trust boundaries. Static types are not runtime validation of external input.

## Failure

Security failures fail closed. Invalid critical configuration should fail clearly. Expected operational failures should be handled predictably. Do not expose secrets, stack traces, internal paths, or SQL unnecessarily.

## Data

Collect/store data intentionally. Establish purpose, sensitivity, access, retention, deletion, and recovery where material. Enforce important invariants at the strongest suitable layer.

## Dependencies

Dependencies are security, maintenance, reliability, and supply-chain commitments. Prefer built-in/already-approved capabilities when adequate. Use deterministic resolution where supported.

## Reproducibility

M1+ projects document supported toolchains, dependency resolution, prerequisites, build/test/verification commands.

## Testing

Testing depth follows consequence and risk. Test observable behavior, boundaries, invariants, failures, and negative security cases. Coverage percentage alone is not evidence of correctness.

## Code quality

Prefer idiomatic, explicit, cohesive, boring code over cleverness. Comments explain rationale/invariants, not obvious syntax.

## Documentation proportionality

Governance requires sufficient durable information and evidence, not unnecessary file/document ceremony. Related information MAY be consolidated when authority, clarity, durability, and discoverability remain strong.

## Findings

Meaningful warnings/findings require REMEDIATED, FALSE_POSITIVE, NOT_APPLICABLE, RISK_ACCEPTED, or permitted tracked debt. Never silently ignore or suppress to obtain green status.

## Definition of Done

Applicable requirements satisfied; unintended material scope absent; architecture coherent; tests/checks/security verification passed; dependencies/configuration valid; docs current; blockers resolved; residual limitations/risks disclosed.
