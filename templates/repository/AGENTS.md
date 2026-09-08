# Repository Engineering Instructions

Governance baseline: see `project-governance.yml`.

Before substantial work:
1. read this file and `project-governance.yml`;
2. resolve the central governance root using the manifest locator (`$CODEX_HOME/GOVERNANCE_ROOT` by default);
3. select and read the applicable central workflow;
4. load relevant central skills/profiles and only the detailed standards needed by the task;
5. read relevant project requirements/design/security/ADR/risk material;
6. inspect affected implementation/tests;
7. resolve material ambiguity before C2/C3 implementation.

For C2/C3, security-sensitive, governance, or release work, compare the central governance repository `VERSION` with the project-pinned baseline. Surface unresolved mismatch; do not silently claim baseline compliance.

## Scope and ambiguity

Vague/indifferent answers are unresolved when they materially affect behavior, security, privacy, data, architecture, interfaces, dependencies, privileges, cost, destructive actions, publication, or deployment.

For technical choices, recommend a default. For unresolved product/security intent, ask focused questions.

Do not add material behavior, external communication, persistence, telemetry, dependencies, privileges, trust boundaries, or speculative scope without requirement/accepted recommendation.

## Change classification

C0 trivial; C1 normal; C2 material; C3 critical/high consequence.

C2/C3 requires a readiness summary and approval of material direction. C3 includes consequential destructive/bulk actions even if nominally reversible.

## Security

Critical and High findings block release under the default baseline, except exceptional explicit High risk acceptance. Never weaken/suppress controls just to pass.

## Verification

Quick: `<set in project-governance.yml>`
Full: `<set in project-governance.yml>`

Required unexecuted checks are not passes.

## Code Review Rules

Flag:
- unintended scope;
- new dependencies/data/network/permissions/trust boundaries;
- authn/authz weaknesses;
- security-control weakening;
- destructive behavior;
- missing tests/docs;
- broad scanner suppressions.

Prefer concise, behavior-oriented review rules; formatting belongs in CI.

## New-project implementation boundary

For M1+ C2/C3 new projects, capture the approved design in Git before substantial implementation.

For SA-2/SA-3 locally managed authentication, invoke `authentication-design` before implementing password/session/enrollment/certificate-trust mechanisms.

After Technology Baseline establishment, establish canonical quick/full verification before implementation grows beyond the initial scaffold.

## Technology Baseline

For M1+ projects, treat architecture-significant language/toolchain, runtime, primary framework/platform, persistence, deployment/packaging, supported-target, and similar stack-shaping decisions as the governed Technology Baseline referenced by `project-governance.yml`.

Do not silently introduce, remove, or replace architecture-significant technology during implementation. Routine dependency maintenance remains lightweight when it does not materially change the baseline.

If repository reality and the durable Technology Baseline materially diverge, surface it and use `RECONCILIATION_REQUIRED` until the intentional target, durable record, implementation/dependency state, support claims, and canonical verification are reconciled. Approved migration/reconciliation work may proceed; unrelated substantial implementation should not.

Material changes to an `ESTABLISHED` Technology Baseline are C2 at minimum and use the normal C2/C3 recommendation and approval boundary. Reconcile canonical quick/full verification for the resulting stack before the transition is complete.

### Material Technology Baseline transition completeness

For an architecture-significant transition from an `ESTABLISHED` Technology Baseline, produce a **Technology Baseline Transition Summary** before C2/C3 direction approval or substantial migration implementation. The response/record is incomplete unless it explicitly labels and resolves every applicable field:

- `Delta / classification` — identify the baseline delta and C2/C3 classification.
- `Technical recommendation` — invoke/reuse `technology-selection`, state the agent's technically justified direction and rationale, and do not reflexively transfer the choice.
- `Dependency / supply-chain and triggered impacts` — perform dependency/supply-chain analysis and route data/security/migration analysis when triggered.
- `Approval state` — identify whether existing C2/C3 direction approval is required/obtained before substantial migration implementation.
- `Transition state / durable record` — record the intended target and use `RECONCILIATION_REQUIRED` during the approved transition.
- `Verification / assurance reconciliation` — reconcile canonical quick/full verification and newly applicable assurance capabilities for the resulting stack.
- `ESTABLISHED closure criteria` — return to `ESTABLISHED` only when the durable baseline, repository/dependency state, support claims, and verification agree.

Use `NOT APPLICABLE` with a reason instead of silently omitting a genuinely irrelevant field. The summary may be in the response/readiness/design record; it does not require a separate file.

Do not create a parallel technology registry or duplicate the complete dependency graph in governance.


## Central governance loading matrix

Use the minimum relevant detailed context.

- New project: `workflows/new-project/WORKFLOW.md`; technology-selection and architecture-design; threat/authentication/security skills when triggered.
- New feature: `workflows/new-feature/WORKFLOW.md`; if implementation proposes an architecture-significant Technology Baseline delta, also route `technology-selection` plus `workflows/dependency-change/WORKFLOW.md` and any triggered migration/security workflow.
- Bug fix: `workflows/bug-fix/WORKFLOW.md`; security-review when vulnerability impact is plausible.
- Security review: `workflows/security-review/WORKFLOW.md`, `global/secure-development-standard.md`, applicable security skills, assurance policy.
- Release: `workflows/release/WORKFLOW.md`, `assurance/verification-standard.md`, `assurance/architecture.md`, `assurance/severity-policy.md`, `assurance/exception-policy.md`, and applicable profiles/skills.
- Data/schema migration: `workflows/data-migration/WORKFLOW.md`; testing strategy and applicable data/profile guidance; destructive-data/C3 rules when triggered.
- Dependency change: `workflows/dependency-change/WORKFLOW.md`; dependency-review, testing strategy, security-review, and relevant profiles when triggered.
- Emergency fix: `workflows/emergency-fix/WORKFLOW.md`; load only the detailed security/verification context required by the incident, keep the patch bounded, record skipped checks as `UNVERIFIED` / `INCOMPLETE ASSURANCE` rather than PASS. Emergency work is not complete at service restoration: after stabilization, run deferred verification and reconcile/remove temporary bypasses, toggles, exceptions, and risk acceptances.
- Refactor: `workflows/refactor/WORKFLOW.md`; preserve approved behavior/contracts, characterize underspecified behavior, and split public API/data/dependency/security deltas into their proper workflow.
- C2/C3 architecture/security decisions: also read `global/operating-contract.md`, `global/engineering-constitution.md`, and relevant secure/governance standard sections.

Do not bulk-load every profile/skill into context.


<!-- BEGIN CODEX-GOVERNANCE-MANAGED -->
## Central governance integration

This project is governed by the baseline recorded in `project-governance.yml`.

Before substantial work:
1. read this repository `AGENTS.md` and `project-governance.yml`;
2. resolve the central governance repository using the manifest locator (`$CODEX_HOME/GOVERNANCE_ROOT` by default);
3. select and read the applicable central workflow;
4. load only relevant central skills/profiles and detailed standards;
5. read relevant project design/security/ADR/risk material;
6. inspect affected implementation/tests.

For C2/C3, security-sensitive, governance, or release work, compare the central governance `VERSION` with the project-pinned baseline. Surface unresolved mismatch before claiming governance compliance or readiness.

If feature implementation proposes an architecture-significant Technology Baseline delta, do not bury the delta inside ordinary feature work; keep unrelated work on the established baseline when feasible and route the delta through `workflows/new-feature/WORKFLOW.md`, `technology-selection`, and `workflows/dependency-change/WORKFLOW.md` plus any triggered migration/security workflow.

Do not silently drift from an `ESTABLISHED` Technology Baseline. Before C2/C3 approval or substantial architecture-significant stack migration, emit a `Technology Baseline Transition Summary` with explicit fields for Delta/classification, Technical recommendation, Dependency/supply-chain and triggered impacts, Approval state, Transition state/durable record (`RECONCILIATION_REQUIRED`), Verification/assurance reconciliation (including newly applicable capabilities), and `ESTABLISHED` closure criteria. Do not omit a field; use NOT APPLICABLE with reason when genuinely irrelevant.

### Propagated assurance and emergency invariants

- Canonical assurance: after Technology Baseline establishment, establish project `quick`/`full` verification and, when using the reference architecture, `verification-plan.json`. Local and CI use the same underlying required checks. Required nonexecution is `INCOMPLETE_ASSURANCE`; genuine irrelevance is `NOT_APPLICABLE` with reason.
- Assurance completeness and exceptions: full verification accounts for every managed baseline capability. Omitted required capabilities, unresolved conditional capabilities, and required capabilities with no full-stage evidence are `INCOMPLETE_ASSURANCE`. Known vulnerability/finding risk acceptance is distinct from missing required-control evidence and cannot substitute for it. Proceeding without a required control requires a separate explicit governance/policy exception where policy permits; the missing control itself remains non-PASS.
- Required-control response completeness: when release/readiness depends on a missing, omitted, or nonexecuted required control, a complete answer explicitly states the control is required, the `INCOMPLETE_ASSURANCE` consequence, that vulnerability/finding risk acceptance is not the governance/policy exception required to proceed without the control, and that the missing control remains non-PASS even if such an exception exists. If cross-context evidence is involved, the answer also states same-source/plan/baseline/runner attribution and that any attributable executed `FAIL` remains fail-dominant even when another approved context passes.
- Applicability is factual: tool inconvenience or unavailability does not make an applicable control `NOT_APPLICABLE`. Reassess a `NOT_APPLICABLE` decision when its factual trigger changes, including introduction of the corresponding web/network surface, container artifact, infrastructure-as-code, dependency graph, persisted operational data, or other governed capability trigger.
- Assurance outcome semantics: operational tool failure is `DID_NOT_EXECUTE`, not a finding or PASS. Documented result-code classification and required execution-context semantics are assurance policy; do not change them merely to obtain green status. Changing result classification for a required security control is a material C2 assurance-policy change requiring review/approval.
- Cross-context evidence: CI/specialized evidence counts only when attributable to the same clean commit, verification plan, managed assurance baseline, runner semantics, and required-check inventory. An attributable executed `FAIL` remains fail-dominant even if another approved context reports PASS; `ANY` never authorizes masking a real failure.
- Assurance tool locks: select a reproducible lock matching each approved execution environment; incompatible/missing locks or CI bootstrap failure remain `DID_NOT_EXECUTE` / `INCOMPLETE ASSURANCE`, never a reason to weaken pinning or applicability.
- Emergency completion: urgency may compress process but does not erase material approval/security boundaries. Service restoration is not governance completion; after stabilization, run deferred verification and review/remove or deliberately reconcile temporary bypasses, toggles, exceptions, and emergency risk acceptances. A complete emergency answer explicitly states both post-stabilization duties: complete/reconcile deferred verification, and review/remove or deliberately reconcile those temporary measures. Mentioning only deferred verification is incomplete.

Do not bulk-load every skill/profile. Project-specific instructions outside this managed block remain authoritative subject to the normal governance hierarchy.
<!-- END CODEX-GOVERNANCE-MANAGED -->
