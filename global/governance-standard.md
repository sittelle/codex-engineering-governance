# Governance Standard

Version 1.0.0.

## Authority

Material conflicts must be surfaced. A lower-level workflow/skill/profile must not silently override approved requirements or higher security/engineering policy.

## Maturity

M0 Exploration — disposable experiment.
M1 Maintained — real software expected to be maintained.
M2 Distributed — intentionally distributed/published/open-sourced.
M3 Operated — actively operated as a service/system for real users or material workloads.

Use the highest applicable level when a single value is required. Reassess when project use changes.

## Versioning

Governance uses MAJOR.MINOR.PATCH. Projects pin a baseline and do not silently migrate. Mandatory security migrations may be designated with rationale, impact, and required verification.

## Exceptions and risks

Risk acceptance and policy exception are distinct. Both are explicit, narrow, traceable, and preferably time/trigger bounded. Neither falsifies evidence.

## Governance self-protection

Routine tasks MUST NOT weaken release blockers, verification, approval boundaries, assurance, or security policy to make a project pass.

## Skills/profiles

Reusable guidance is focused, composable, technology-neutral when possible, and cannot weaken higher layers.


## Technology Baseline

For M1+ projects, architecture-significant technical decisions are governed as the project Technology Baseline and are recorded durably before implementation grows materially once sufficient requirements/architecture constraints exist.

Architecture-significant decisions include, as applicable, primary language/toolchain, runtime family/support range, central application/framework platform, persistence technology/model, deployment/packaging model, supported execution targets, and other stack-shaping components whose replacement materially changes architecture, support, security/trust, operations, supply-chain exposure, or canonical verification.

Governance is technology-neutral: it governs decision quality, materiality, traceability, reconciliation, and evidence. It does not centrally prescribe preferred languages, frameworks, databases, or products. Profiles are reusable guidance selectors, not an allowlist and not the authoritative project stack. Exact dependency graphs and resolved versions remain authoritative in ecosystem manifests/lockfiles unless a specific version is itself architecture-significant.

Project Technology Baseline state uses:
- `UNESTABLISHED` — no durable current baseline has yet been established;
- `ESTABLISHED` — the durable baseline reflects the current intended architecture-significant technology state;
- `RECONCILIATION_REQUIRED` — repository reality, adoption history, or an approved transition is not yet fully reconciled with the durable baseline and verification.

Initial baseline establishment inherits the actual change classification. A material change to an `ESTABLISHED` Technology Baseline is C2 at minimum; C3 applies when existing C3 consequences are present. Routine dependency maintenance that does not materially change the Technology Baseline may remain C1.

The agent recommends technically justified defaults. Explicit developer approval is required through existing C2/C3 or developer-owned product/security/risk boundaries, not merely because a technology name appears in the baseline.

A material baseline transition is complete only when the durable record, implementation/dependency state, supported-platform claims, and canonical verification are reconciled. Silent stack drift is not permitted.

For a C2/C3 Technology Baseline transition, the pre-implementation decision record/response MUST include a structured Technology Baseline Transition Summary covering delta/classification, the agent's technical recommendation, dependency/supply-chain and other triggered impacts, approval state, transition state/durable target, verification/assurance reconciliation, and explicit `ESTABLISHED` closure criteria. This is a required information contract, not a requirement for a separate document.

## Proportionality

Governance governs information/evidence, not document count. Small projects may consolidate documents.

## Behavioral tests

Material governance/prompt changes SHOULD run representative behavioral scenarios. No critical regression test may fail.

## Evidence integrity

Never relabel failed/unexecuted checks as passing, hide accepted risk, or erase evidence to claim compliance.

## New-project evidence boundary

For M1+ C2/C3 projects, the approved design SHOULD be captured in version control before substantial implementation. This establishes traceability, rollback, and a clear design-to-code boundary.

## Verification bootstrap

Once the Technology Baseline is established, canonical quick/full verification SHOULD be established before implementation expands beyond a minimal scaffold. A material Technology Baseline change requires verification reconciliation before the transition is complete.

## Authentication governance

For SA-2/SA-3 locally managed identity, authentication design is a pre-implementation security decision. The agent must not treat password hashing, session cookies, enrollment tokens, or certificate generation as isolated utilities detached from credential lifecycle and recovery.


## Identifier normalization

Machine-readable project configuration uses:
- maturity: `M0`, `M1`, `M2`, `M3`;
- assurance: `SA0`, `SA1`, `SA2`, `SA3`;
- change class: `C0`, `C1`, `C2`, `C3`.

Human-facing prose MAY render assurance as `SA-0` through `SA-3`.

Do not treat formatting differences as distinct assurance levels.

## Governance source resolution

Governed projects SHOULD resolve the central governance repository through the installed Codex-home locator rather than embedding developer-specific absolute paths in each repository.

For C2/C3, security, governance, and release work, unresolved baseline/source mismatch means governance context is incomplete and MUST be surfaced before claiming compliance/readiness.


## Finding acceptance versus assurance-control exception

Risk acceptance for a known security finding and an exception for a required assurance control that did not execute are different governance actions.

A finding acceptance addresses a known, characterized risk.

A required-control exception addresses missing assurance evidence and MUST NOT be used to claim the control passed or found zero issues.

For release-gating purposes, keep these dispositions distinct in durable evidence.


## Adoption of existing repositories

When governance is added to a repository that already contains requirements, design, implementation, dependencies, verification behavior, or risk decisions, the agent MUST NOT represent those pre-existing decisions as historically approved under the newly adopted governance baseline.

Adoption begins in `RECONCILIATION_REQUIRED` state.

Before substantial C2/C3, security-sensitive, or release work, reconcile the existing repository against the current governance baseline and create truthful durable evidence for the post-adoption state.


## Stable-candidate evolution discipline

For a baseline designated `STABLE_CANDIDATE`, global policy changes SHOULD be evidence-driven. A new global rule requires a reproducible governance regression, demonstrated security/safety defect, repeated cross-project proportionality defect, compatibility/integration failure preventing intended policy execution, or intentionally planned new governance capability with corresponding tests. Project-specific preferences or one-off lessons SHOULD remain project-local unless repeated evidence shows a reusable governance need.


## Data migration workflow selection

For material persisted-data or schema transitions, use the dedicated `data-migration` workflow rather than treating migration as an ordinary implementation detail.

The workflow operationalizes existing data-lifecycle, destructive-data, evidence, verification, recovery, and C3 approval requirements. It does not lower those requirements.


## Dependency change workflow selection

For material dependency addition, removal, upgrade, replacement, or lockfile/transitive changes, use the dedicated `dependency-change` workflow.

A dependency change that materially establishes or changes the Technology Baseline is both a dependency/supply-chain change and a governed architecture/technology change; reconcile both dimensions without creating a parallel workflow or dependency registry.

Routine patch maintenance MAY remain lightweight when it does not materially affect security, licensing, runtime/platform support, APIs, architecture, operational behavior, or the Technology Baseline.

The workflow operationalizes existing dependency discipline, security findings, evidence, verification, and approval requirements without making every dependency update ceremonial.


## Emergency fix workflow selection

Use the dedicated `emergency-fix` workflow when incident urgency materially compresses normal delivery sequencing.

The workflow allows proportional compression of discovery/documentation while preserving:
- material approval boundaries;
- security/destructive stop conditions;
- truthful verification status;
- explicit risk/exception handling;
- mandatory post-stabilization reconciliation.

Emergency process MUST NOT become a mechanism for permanently weakening the governance baseline.


### Emergency completion evidence

Emergency stabilization is not equivalent to governance completion.

Any skipped or compressed verification remains `UNVERIFIED` / `INCOMPLETE ASSURANCE` until executed or explicitly dispositioned. Temporary bypasses, toggles, exceptions, and emergency risk acceptances require post-stabilization reconciliation and must not silently persist because service has recovered.


### Emergency service restoration is not completion

Service restoration closes the immediate incident phase, not the governance lifecycle. After stabilization, run deferred verification and reconcile/remove temporary bypasses, toggles, exceptions, and risk acceptances before the emergency work is considered complete.


## Refactor workflow selection

Use the dedicated `refactor` workflow for nontrivial structural changes whose intended outcome is behavior preservation.

A request labeled “refactor” does not override classification. Public contract changes, persisted-data changes, dependency changes, security changes, and product-behavior changes must be separated and governed under their applicable boundaries.


## Canonical assurance architecture

M1+ projects establish a canonical `quick` and `full` verification interface after Technology Baseline establishment and before implementation grows beyond a minimal scaffold.

Assurance is capability-based and tool-independent.

Projects SHOULD keep local and CI verification on the same underlying check definitions. CI bootstrap differences do not authorize silently omitting required controls.

Required applicable checks that fail to execute produce `DID_NOT_EXECUTE` and overall `INCOMPLETE_ASSURANCE`, not PASS.

Capabilities that genuinely do not apply MAY be recorded `NOT_APPLICABLE` with a reason. Do not install irrelevant controls merely for ceremony.

Declared runtime/platform support is not verification evidence; report exactly what environments actually executed.


## Verification capability completeness

Canonical full verification MUST establish both execution success and capability completeness. A required assurance capability omitted from the plan is missing evidence even when every configured command succeeds. Conditional capabilities must be explicitly resolved; absence alone is not `NOT_APPLICABLE`.


## Assurance result-policy and environment boundary

A required assurance tool that cannot complete does not prove a security finding and does not prove safety. Record operational nonexecution separately from completed failing analysis.

The default exit policy remains fail-safe. Tool-specific operational exit-code mappings require a documented contract and are material when they affect a required security control. Do not use custom mappings to convert genuine findings into incomplete/ignored evidence.

Execution location does not determine applicability. Required controls may execute in approved CI/specialized contexts, but completion evidence must be attributable to the same clean source commit, plan, baseline, and runner semantics.
