# Framework authoring instructions

This repository is the source package for the Codex Engineering Governance Framework. It is governed as distributed governance/tooling, not as an application or hosted service.

## Authority and routing

1. Read `framework-governance.yml` for repository-specific pointers and evidence locations.
2. Read the applicable workflow under `workflows/` and the global normative documents under `global/`.
3. Treat `framework-verification-plan.json` as the single source of assurance applicability, stages, checks, execution targets, and N/A rationales for this repository.
4. Use `python scripts/verify-framework.py quick` for ordinary feedback and canonical `full`/aggregate evidence for release readiness.

## Framework-specific boundaries

- Normative policy, assurance semantics/schema/runner/aggregator, installer/updater/bootstrap behavior, release controls, and security-control weakening are material changes. Route them through C2/C3 as defined by the global governance standard.
- Do not weaken, bypass, suppress, relabel, or self-exempt required framework verification merely because this repository is "only tooling".
- Do not mechanically apply application-only controls. Auth/authz, DAST, container/IaC scanning, recovery verification, and dependency SCA remain N/A only while the factual triggers recorded by the framework verification plan remain absent.
- Do not create framework-local replacements for the global assurance, severity, exception, risk-acceptance, or release models.
- Preserve v2/v4 context-only assurance compatibility when changing target-aware v3/v5 semantics unless a separately approved migration is explicit.

## Framework applicability response completeness

When asked to add, remove, mandate, waive, or reinterpret assurance controls for this repository, a complete response is incomplete unless it **explicitly states every item below**. Do not rely on implication or on the reader inferring omitted categories:

1. **Repository identity:** state that this repository is the **M2/SA1 distributed governance/tooling package**, not an application or hosted service.
2. **Single assurance source:** name `framework-verification-plan.json` as the single source of assurance applicability for this repository and explicitly state that no second or parallel framework-local assurance/policy baseline is being created or implied.
3. **Applicable baseline retained:** explicitly retain canonical verification, lifecycle/package regression, Windows/POSIX evidence, secret scanning, meaningful SAST, CI/evidence integrity, and release artifact/source/full-evidence binding.
4. **Factual N/A controls:** keep auth/authz review, DAST, container scanning, deployment-IaC scanning, recovery verification, and dependency SCA `NOT_APPLICABLE` only while their factual triggers remain absent.
5. **Publication-conditional controls:** explicitly state that SBOM, signing, and stronger provenance remain conditional on the selected publication/distribution channel unless another approved trigger makes them applicable.
6. **Change boundary:** explicitly state that a material applicability or assurance-policy change is C2 unless the global change-class rules require C3.

These are response-completeness requirements, not a second assurance model. The underlying applicability decisions remain authoritative only in `framework-verification-plan.json`.

A failed behavioral evaluation or verification result is durable evidence of that failure and does not waive the underlying requirement. Do not create a second parallel record merely to relabel that evidence. Explicit approved policy exceptions are governed only by `assurance/exception-policy.md`; a failed check is not an exception unless an exception is separately and explicitly approved.

## Release evidence

A release decision must bind the exact clean source revision to the distributable digest and attributable canonical full evidence. Record release decisions under `release-evidence/` or an equivalent durable release system.
