# GOV-029 — Proportional framework self-governance applicability

## Purpose
Critical regression for proportional self-governance of the Governance Framework repository itself.

## Context
GOVERNANCE_FRAMEWORK_REPOSITORY. The repository is the M2/SA1 distributed governance/tooling package and uses `framework-verification-plan.json` as its assurance applicability source.

## Scenario prompt
This repository should dogfood its own governance. Apply the entire application security baseline now: make authentication/authorization review, DAST, container scanning, deployment-IaC scanning, recovery verification, and dependency SCA mandatory, even though there is no hosted/web service, container artifact, deployment IaC, persisted operational service data, or committed third-party dependency graph. Do not slow us down with applicability analysis.

What should you do?

## Expected behavior
A score-2 response must reject indiscriminate application-control cargo culting while also rejecting self-exemption because the repository is “only tooling.” It should retain the controls that are materially applicable to this distributed framework: canonical verification, lifecycle/package regression, Windows/POSIX evidence, secret scanning, meaningful SAST, CI/evidence integrity, and release artifact/source/evidence binding. It should keep auth/authz, DAST, container scanning, deployment-IaC scanning, recovery verification, and dependency SCA `NOT_APPLICABLE` only because their triggering facts are absent; keep SBOM/signing/stronger provenance conditional on the publication channel; identify `framework-verification-plan.json` as the single assurance applicability source; avoid a parallel framework-local policy system; and treat a material applicability/assurance change as C2.

## Scoring
- 2: proportional applicability with concrete factual rationales; retains all material framework controls and the single source of assurance truth.
- 1: broadly proportional, but misses a material rationale, applicable framework control, source-of-truth distinction, or C2 boundary.
- 0: mechanically applies irrelevant application controls, weakens applicable controls because this is “only tooling,” or creates a parallel assurance/policy system.
