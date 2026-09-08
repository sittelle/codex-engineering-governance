# Verification Standard

Projects define canonical `quick` and `full` verification, recorded durably in project governance/design/build configuration.

The project MAY use the reference `verification-plan.json` contract and runner or an ecosystem-equivalent implementation.

CI SHOULD execute the same underlying checks as local verification where practical.

Required tool startup/crash/service failure/malformed evidence => DID_NOT_EXECUTE.

Required applicable capability missing/nonexecuting => INCOMPLETE_ASSURANCE, not PASS.

Codex uses quick verification during ordinary changes and full verification for release, C2/C3 completion when required, security-sensitive completion, or project policy.

Never modify verification merely to obtain green status without a governance decision.

Declared runtime/platform support is distinct from runtimes/platforms actually verified.

## Technology Baseline reconciliation

Canonical verification is derived from the project's actual Technology Baseline and assurance applicability, not from centrally preferred tools.

When a Technology Baseline is first established or materially changed, reconcile `quick` and `full` verification for the resulting stack. Reassess applicable lint/format, type/compile, tests, build/package, SAST, SCA, platform-specific, and conditional security capabilities as facts require.

Do not implement a central product-to-tool mapping such as “language X always requires tool Y.” The framework governs capability coverage and evidence; concrete tools remain project technical decisions.

A baseline transition remains `RECONCILIATION_REQUIRED` until required verification definitions are current and the repository/baseline state can be truthfully verified. Do not retain stale checks merely to preserve a green result, and do not silently omit newly applicable capabilities.


Required capability omission is missing assurance evidence even if every configured check passes. Schema-v2 full verification MUST compare the project capability inventory with the managed assurance baseline before PASS can be reported. Conditional capabilities must be resolved explicitly; `UNRESOLVED` blocks a full PASS.


## Result and environment semantics

Default check semantics are exit 0 = PASS and nonzero = FAIL. Tool-documented operational-error codes may be classified `DID_NOT_EXECUTE` only through the governed documented-exit-code mechanism; unmapped nonzero codes remain FAIL.

A required capability may execute in an approved CI/specialized environment without being weakened or marked N/A locally. Release/completion evidence spanning environments must be attributable to the same clean commit, plan, baseline, and runner semantics.

## Release artifact and evidence binding

A release decision MUST identify the exact source revision being released and use attributable `full` verification evidence for that same source state. When evidence spans approved execution contexts, aggregation MUST preserve the commit/plan/baseline/runner identity and failure-dominance rules defined by the assurance architecture. Dirty, mismatched, stale, or otherwise non-attributable evidence MUST NOT substantiate release readiness.

For every released package, installer, image, binary, archive, or other distributable artifact, retain an immutable artifact identity appropriate to the medium (normally a cryptographic digest such as SHA-256) and bind that identity to:
- the release/version identifier;
- the exact source revision;
- the build/package procedure or provenance needed to reproduce or explain the artifact;
- the attributable full-verification evidence used for the decision;
- SBOM/provenance/signing evidence when required by project assurance or publication policy.

A package whose source revision or digest cannot be bound to the verified release state is not a verified release artifact. Do not reuse verification from one source state to justify a materially different artifact.

## Retained release decision evidence

Retain a concise release decision record containing at minimum:
- release/version identifier and source revision;
- artifact identities/digests for released distributables;
- applicable maturity/assurance target;
- references to full and aggregated assurance evidence;
- open findings, `DID_NOT_EXECUTE`/`NOT_APPLICABLE` dispositions, accepted risks, and active policy exceptions relevant to release;
- the final READY / READY WITH ACCEPTED RISKS / NOT READY / INCOMPLETE ASSURANCE decision and the developer approval/decision reference when required.

The record may live in an existing release system, repository document, CI/release metadata, or another durable location; a dedicated file is not required.
