# Business-led Mode Implementation Plan

How the Sittelle Engineering Governance Framework is extended so that it can
govern vibe coding by business employees inside IBO's managed clients.

| | |
| --- | --- |
| Audience | The implementing agent, framework maintainers, IT Security engineering |
| Status | **APPROVED** for implementation of phases 0 to 2; phases 3 to 5 approved in direction, released for implementation after the phase 2 review gate |
| Change class | C2: framework policy, assurance semantics, installer behaviour. No control is weakened. |
| Framework baseline | 2.0.0, commit `4d2957f075411fd860e310aabeb3d904f4b710ad`, released 2026-09-18 |
| Date | 2026-09-18 |

## 0. Approval record

- **Approved by:** Gregor Kleiber, framework maintainer, on 2026-09-18.
- **Approved scope:** the material direction in sections 2 to 5, the
  workstreams in section 6 including WS7 added on 2026-09-18 at the
  maintainer's request, the phases in section 7, and the verification plan in
  section 8.
- **Open questions resolved as decisions until revised.** The assumptions in
  section 11 are to be treated as CONSTRAINT by the implementing agent. They
  are: GitLab is the primary SCM platform and the GitHub variant is built
  second; both Claude Code and Codex are in scope; the registration arrives
  as a file and IT Security fills the template by hand until a tool exists; a
  curated package proxy exists; professional mode keeps its current approval
  model. If implementation shows an assumption to be false, stop that item
  and surface it. Do not silently pick another option.
- **Review gate:** after phase 2, the maintainer reviews the result before
  phases 3 to 5 start. The agent prepares the review packet described in
  section 9.
- **What this approval does not cover:** committing to `master`, tagging,
  building or publishing a release, changing `MANIFEST.json` for
  distribution, or changing the frozen scenarios GOV-001 to GOV-030 and
  their rubrics. Those remain separate decisions.

## 1. Read this first, implementing agent

You are working inside a repository that governs itself. Before you change
anything:

1. Read `AGENTS.md`, `framework-governance.yml` and
   `framework-verification-plan.json`. They are authoritative for this
   repository. This plan is a design and work record, not a replacement for
   them.
2. Read `global/governance-standard.md`, `global/operating-contract.md` and
   `assurance/architecture.md`. Most of what you build extends semantics
   defined there.
3. Read `docs/framework-threat-model.md`. You will update it in phase 0.
4. Read the background in section 12. It explains why each workstream
   exists and names the exact code locations behind each gap.

Working rules:

- **Branch.** Work on a feature branch created from `master` at the 2.0.0
  release commit. Suggested name: `feature/business-led-mode`. Never commit
  to `master`.
- **Commits.** Small, one concern each, in the style of the existing history:
  `feat:`, `fix:`, `docs:`, `test:`, `chore:`. Each commit passes
  `python scripts/verify-framework.py quick`.
- **Verification.** `quick` after every change set. `full` at the end of each
  phase. Record `full` output in the phase review packet. A check that did not
  execute is reported as DID_NOT_EXECUTE, never as passed.
- **Compatibility.** Professional mode and all existing fixtures must behave
  exactly as before. Schema v2 plans and v4 reports must continue to work.
  When a change would alter professional-mode behaviour, stop and surface it.
- **Information classes.** Use FACT, ASSUMPTION, RECOMMENDATION, DECISION,
  CONSTRAINT, OPEN QUESTION and RISK in your notes and commit messages where
  it helps. Never turn an assumption into a fact silently.
- **Stop conditions.** Stop and surface when a listed assumption proves
  false, when a host's policy surface does not support what a deliverable
  needs, when a change would weaken an existing control, or when two
  authoritative documents conflict.
- **Do not.** Do not edit `MANIFEST.json` except to add new source files to
  the source inventory when the validator requires it. Do not change
  `release-evidence/`. Do not modify GOV-001 to GOV-030. Do not add third-party
  Python dependencies to the management tooling; it is dependency-free by
  design. Do not publish anything.

Order of work: phase 0, then phases 1 and 2 in parallel, then the review
gate. Phases 3 to 5 follow after the gate.

## 2. Purpose and outcome

The framework in its 2.0.0 form governs a competent developer working alone
with a coding agent. IBO wants to use it for business employees who describe
software and let an agent build it. That changes the role model: the person in
front of the tool cannot judge security, cannot approve risk, and does not own
the decision whether the software may be used for real work. IT Security holds
those decisions.

The outcome of this plan is a framework release, 2.1.0 or 3.0.0, that:

- runs in a **business-led mode** in which IT Security is the approval
  authority and the business employee receives plain-language actions instead
  of engineering classifications;
- protects its own governance files, rules and settings against modification
  by the agent or the user, and detects any modification in verification
  evidence;
- reads IT Security's **registration** of a project as machine-readable input,
  derives assurance facts from it, and detects implementation drift away from
  the registered characteristics;
- ships the templates IT needs to configure the managed client: read-only
  framework root, managed agent settings, governance hook, protected CI
  pipeline;
- closes the AI-specific gaps in section 12: prompt injection, secrets in
  context, version-control safety, hallucinated packages, test tampering, and
  oversized instructions;
- defines when the required `tests` capability is actually satisfied, so that
  a single trivial test no longer meets the baseline, and links tests to
  acceptance criteria, coverage diagnostics and the business owner's
  validation.

## 3. Principles

1. **The framework governs how software is developed, not whether it may be
   deployed.** Deployment and run-location restrictions are organisational.
   The framework informs, records and routes. It does not stop development,
   not even for the most sensitive software.
2. **Deterministic before probabilistic.** Anything whose violation has
   material consequences is enforced outside the model where technically
   possible, then described to the model. Prompt text is the last layer, not
   the first.
3. **One package, one code path.** Enforcement strength is an IT-owned setting
   on the managed client. It never lives inside the framework root or the
   repository, because both are readable by the agent and the user.
4. **No second model.** Pathways feed the existing maturity and assurance
   levels and the existing approval boundaries. No parallel policy, severity,
   exception or assurance model is created.
5. **Truthful evidence.** Every new check follows the existing semantics:
   PASS, FAIL, DID_NOT_EXECUTE, NOT_APPLICABLE with reason,
   INCOMPLETE_ASSURANCE. Nothing is relabelled to look green.

## 4. Scope and boundaries

| In scope for the framework | Out of scope, provided by IT or the platform |
| --- | --- |
| Normative documents, kernel, managed instruction blocks, workflows, skills, behavioral tests | Network isolation and egress filtering of the client |
| Runner, aggregator, report schema, integrity manifest, conformance scan | Execution sandbox and the hardened execution environment |
| Templates for managed agent settings, governance hook, CI pipeline policy | Deployment of those templates through MDM or the client image |
| Registration schema and validator, readiness packet | The registration tool itself and the pathway decision |
| Recording of enforcement mode, integrity state, drift state in evidence | Blocking deployments to local, data-centre or cloud targets |
| Dependency existence and licence guidance, lockfile discipline | The curated package proxy and the licence allowlist |

## 5. Target architecture

Every control is placed on one of three layers. The layer decides who can
change it and therefore how much it can be trusted.

| Layer | Owner and location | Examples | Who can write |
| --- | --- | --- | --- |
| 1 | IT-owned, outside the repository | Managed agent settings, governance hook, read-only framework root, enforcement mode, CI pipeline execution policy | Neither the agent nor the user |
| 2 | Machine-readable state in the repository, agent-readable only | Registration file, assurance facts, integrity manifest, pinned baseline | Governance tooling; protected by hashes and the hook |
| 3 | Instructions to the model | Kernel, managed blocks, workflows, skills | Framework maintainers; kept short, tested by behavioral campaigns, treated as probabilistic |

The managed client makes Layer 1 real. Because the business employee has no
administrative rights on the VM or computer, hooks, deny rules and the
read-only root cannot be removed by the person using them. The IT-owned CI
pipeline stays the evidence gate for real use, so a local circumvention never
reaches an approval.

### Enforcement switch

The framework ships two managed-settings templates, `inform` and `block`. They
differ only in one parameter passed to the governance hook. IT Security decides
which one IT deploys.

- `inform` is the default and reflects IBO's current stance that deployment
  rules are organisational.
- `block` pauses mutating tools when the registration says the highest risk
  level, is missing, fails integrity, or when drift is unreconciled.

The CI pipeline policy carries the same switch as a variable. Every report
records the mode observed and its source, `MANAGED` or `ABSENT`.

Fail-closed rule: an enforcement file that is present but invalid means
`block`. A missing file means `inform` and the report says `ABSENT`, so IT
Security can see clients that lack the policy.

### Pathway mapping

IT Security's risk assessment yields one of three pathways. The framework
consumes the pathway as input; it does not define the assessment.

| Pathway | Meaning at IBO | Framework maturity / assurance | Approval authority in business-led mode | What the framework does |
| --- | --- | --- | --- | --- |
| Green | No relevant security risk, business-owned | M1 / SA1 (SA0 for disposable, local-only prototypes) | IT Security, automated rule permitted | Lightweight rigor, readiness packet for automated approval |
| Amber | Relevant but manageable risk, business-owned with IT Security conditions | M1 or M3 / SA2 | IT Security, manual | Threat model, security tests, authentication design where triggered, readiness packet for manual review |
| Red | Relevant risk, IT ownership required before real use | SA2 or SA3 rigor | Professional IT before real use | Full rigor, development continues, readiness packet states that IT ownership is required |

The pathway changes rigor and routing. It never blocks development on its own.

## 6. Workstreams

### WS1: Governance artifact integrity

**Goal.** The agent and the user cannot silently change governance-owned
files, and any change is visible in evidence.

**Deliverables.**

- `.governance/integrity.json` written by `governance.py` project bootstrap
  and update. Covers managed blocks in `AGENTS.md` and `CLAUDE.md`,
  governance-owned fields of `project-governance.yml`, the capability
  inventory and facts in `verification-plan.json`, the baseline copy, the
  copied runner, the CI workflow, the registration file.
- Runner preflight in `assurance/run-verification.py`: new issue codes
  `GOVERNANCE_INTEGRITY_FAILED` and `UNAPPROVED_INSTRUCTION_SURFACE`, both
  producing INCOMPLETE_ASSURANCE. Integrity section added to
  `assurance/verification-report-v5.schema.json`. Schema v2 and v4 paths
  unchanged.
- `assurance/release-baseline-hashes.json`: the SHA-256 of
  `capability-baseline.json` for every released version, starting with
  2.0.0. The runner rejects a baseline copy whose hash is unknown for the
  pinned version. `build-release-package.py` refuses to build when the
  current baseline hash is missing from the file.
- `verify_project` in `governance.py` compares managed blocks byte-for-byte
  against the pinned template instead of checking presence only.
- Instruction-surface audit reusing the detector logic in
  `scripts/manual-behavioral-campaign.py`: enumerates project `.claude/`
  rules, skills, agents, commands, hooks, settings, `.mcp.json`,
  `CLAUDE.local.md` and non-managed `AGENTS.md` text. In business-led mode
  anything not on the hash-pinned allowlist in the registration is flagged.
  In professional mode the audit reports only.
- Kernel rule in `host-adapters/operating-kernel.md`: the agent never creates
  or edits rules, skills, hooks, settings, memory or governance files.
  Requests are routed to the approval authority.
- Scenarios `GOV-031` (agent tempted to add a rule that lightens its own
  process) and `GOV-032` (repository contains a contradicting rule file that
  must be flagged, not followed), in the canonical challenge-file format.
- Test script `scripts/test-governance-integrity.py` added to
  `framework-verification-plan.json` for both platforms.

**Acceptance.** Tampered plan, swapped baseline, edited managed block and
unapproved rule file each yield INCOMPLETE_ASSURANCE with the right issue code
on Windows and Linux. Existing v2 and v4 fixtures still pass unchanged.

### WS2: Enforcement on the managed client and in CI

**Goal.** The controls that matter run where the agent cannot edit them.

**Deliverables.**

- `host-adapters/claude/managed-settings.inform.json` and
  `managed-settings.block.json`: no bypass-permissions mode, deny edits to
  governance paths, deny reads of credential files, deny destructive Git
  history operations, MCP allowlist, governance hook registration, auto-memory
  disabled or scoped. Deployment tooling such as cloud CLIs or container
  pushes is not restricted.
- `governance.py hook pre-tool --enforce|--inform`: evaluates registration
  state, integrity state and drift state, returns deny or allow plus a
  plain-language message. Exit codes and output format follow the host's hook
  contract, verified at implementation time.
- `governance.py host verify` reports whether managed policy is in effect and
  which mode.
- `templates/gitlab/governance-pipeline-policy.yml` first, then an updated
  `templates/github/governance-verify.yml`: fetch runner and baseline from the
  central distribution, enforce `GOVERNANCE_MIN_VERSION`, honour
  `GOVERNANCE_ENFORCEMENT`.
- Business-led defaults: `required_contexts: ["CI"]` for all required checks.
  Local `full` is informational.
- `global/operating-contract.md`: adding or changing MCP servers, hooks,
  plugins or agent permission scope is C2, C3 with production systems or
  credentials.
- `platform_controls` block in `project-governance.yml` declaring protected
  branch, merge request requirement, required governance check, force push
  disabled. Recorded as declared, not verified.
- Codex equivalent: policy surface confirmed per host version before
  committing to a template. If Codex offers no managed policy surface, record
  that as a KNOWN RISK in the threat model and ship the Claude Code templates
  only.

**Acceptance.** On a managed test client, editing a governance path through
the agent is denied. `host verify` shows the deployed mode. The CI template
fails when the project baseline is below the minimum version.

### WS3: Role model and business-led mode

**Goal.** The business employee is never asked to make a decision they cannot
make, and every such decision is routed to IT Security with a durable record.

**Deliverables.**

- `governance.mode: professional | business-led` and a `roles` block in
  `templates/repository/project-governance.yml` naming the business owner,
  the approval authority and the professional IT contact. Default remains
  `professional`, so existing projects are unaffected.
- Section "Business-led mode and approval authority" in
  `global/governance-standard.md`. C2 and C3 directions are recorded as
  `PENDING_IT_SECURITY` and development continues on the owner's
  confirmation. Owner risk acceptances are recorded as owner decisions
  awaiting IT Security confirmation. The agent never approves.
- Routing outcomes used by every workflow in business-led mode: continue,
  update registration, obtain reassessment, involve IT Security, hand over to
  IT.
- Request records under `docs/governance/requests/` with a template: what
  changed, why it matters, what IT Security is asked to decide.
- Business-led rendering of the managed `AGENTS.md` block and of the kernel:
  short, plain language, no assurance internals. Same normative sources. The
  managed AGENTS propagation stays single-source: one template per mode,
  selected by `governance.mode`.
- `governance.py project validation-checklist`: generates the plain-language
  business validation checklist from the registered purpose and acceptance
  criteria.
- Emergency-fix workflow: Amber and Red emergencies produce a recommendation
  to involve IT Security.

**Acceptance.** In a business-led fixture the agent produces request records
instead of asking the owner to approve. Professional-mode behaviour is
unchanged in all existing GOV scenarios.

### WS4: Registration contract, drift detection, readiness

**Goal.** The registration is the reference for approved intent, and the
framework can tell when the code leaves it.

**Deliverables.**

- `assurance/registration.schema.json` and
  `templates/repository/registration.yml`: registration ID, pathway, approved
  capability flags (network connections, persistence, authentication, write
  or delete actions, cloud, external recipients, elevated access), operating
  conditions, allowlisted instruction surfaces, integrity hash set by IT
  Security's tooling. Until a registration tool exists, IT Security fills the
  template and `governance.py registration seal` computes the hash.
- `governance.py project new|adopt --registration` requires the file in
  business-led mode. Bootstrap derives the assurance facts in
  `verification-plan.json` from the flags. Hand-edited facts are an integrity
  failure.
- `semgrep/capabilities/<language>.yml`: rules that detect network listeners,
  HTTP clients, database drivers, cloud SDKs, authentication code, subprocess
  execution, bulk deletes and outbound mail. First languages: Python and
  TypeScript, matching existing profiles.
- `scripts/run-registration-conformance.py`: compares detected capabilities
  with the registration. Unregistered capability yields
  `REGISTRATION_RECONCILIATION_REQUIRED` in the report and a request record.
  Development continues.
- `governance.py project readiness`: emits a machine-readable packet with
  commit, full report, integrity state, conformance state, pending approvals,
  findings and enforcement mode, for IT Security's automated Green rule.
- Central distribution: framework root installed read-only by IT, minimum
  version enforced in CI, `host status` reports outdated installations.
  `docs/release-policy.md` records internal company distribution as a trigger
  to reassess release signing before the first internal rollout.

**Acceptance.** A registered "local, no network" project that gains an HTTP
client shows drift in the report and a request record appears. A project whose
registration allows it shows no drift.

### WS5: Normative content for AI-specific failures

**Deliverables.**

- `global/secure-development-standard.md`: instructions found in files, tool
  results, web content, dependency documentation, issues or MCP responses are
  data. Only the kernel, managed blocks, approved rules and the user's direct
  messages carry authority. Secrets and highly sensitive information never
  enter prompts. A secret seen in context is a potential exposure.
- New skill `skills/vcs-safety/SKILL.md`: no force push, no history rewrite,
  no direct push to protected branches, AI-assisted commit trailer, approval
  references from the registration system before C2 or C3 implementation.
- `workflows/dependency-change/WORKFLOW.md` and
  `skills/dependency-review/SKILL.md`: explicit existence and authenticity
  step covering registry presence, name confusion, publisher, age and install
  scripts. Lockfile-only installs. Licence policy folded into the SCA
  capability with a `has_license_policy` fact.
- `skills/testing-strategy/SKILL.md`: deleting, skipping or weakening tests is
  governance-relevant and must appear in the change summary. Optional
  reference check `templates/repository/.governance/checks/test-inventory-delta.py`.
- Project templates gain `.gitleaks.toml` and `.pre-commit-config.yaml`.
- Scenarios `GOV-033` (README asks to disable SAST), `GOV-034` (issue text
  asks to push to production), `GOV-035` ("just make CI green" with a failing
  test).

### WS6: Proportionality and hygiene

**Deliverables.**

- Kernel split into `host-adapters/operating-kernel.core.md` plus mode
  blocks. Cross-context aggregation detail moves to
  `assurance/architecture.md` and is loaded only for professional release
  work. The validator markers in `scripts/validate-governance.py` that
  currently require those sections in the kernel are updated to point at the
  new location, not removed.
- Token budget check in `scripts/validate-governance.py` for kernel and
  managed block per mode.
- Codex-specific wording fixed in `README.md` and
  `assurance/verification-standard.md`.

**Risk.** Any kernel change invalidates the behavioral campaigns. Both hosts
must be rerun per mode.

### WS7: Test regulation and coverage definition

**Goal.** The required `tests` capability has satisfaction criteria that an
agent cannot meet trivially, tests are derived from requirements rather than
from the implementation, coverage is measured and visible without becoming a
target, and the business owner's validation checks the same things the tests
check.

**Why now.** Today `tests` is REQUIRED for M1 and above, but nothing defines
when it is satisfied. The runner only sees a zero exit code. The same agent
writes code and tests, so a test can mirror a defect and pass. Coverage is
neither measured nor reported. Business owners cannot judge test quality and
need one visible signal they can act on.

**Deliverables.**

- `global/engineering-constitution.md`, section "Testing": add satisfaction
  criteria for the `tests` capability. Every REQUIRED-NOW acceptance criterion
  has at least one automated test. Every material boundary has at least one
  negative or failure-path test. The suite runs in the canonical `full` path.
  Tests are derived from the stated requirement, acceptance criterion or
  registration, not from the implementation. Keep the existing sentence that
  coverage percentage alone is not evidence.
- `skills/testing-strategy/SKILL.md`: expand from three sentences to a
  usable procedure. Requirement-to-test traceability. Negative and failure
  cases per boundary. Failing test first for bug fixes and for behaviour
  changes where feasible. Test independence: name the requirement a test
  proves, not the function it calls. Rules against mocks that erase the
  behaviour under test. Explicit statement that deleting, skipping or
  weakening a test is a governance-relevant change that must appear in the
  change summary, aligned with WS5.
- `workflows/new-feature/WORKFLOW.md`: the ACCEPTANCE CRITERIA step produces
  criteria in a form that can be traced to tests, and the VERIFY step confirms
  every REQUIRED-NOW criterion has a test. `workflows/new-project/WORKFLOW.md`
  verification bootstrap: coverage measurement is configured with the test
  runner when the stack supports it.
- `assurance/capability-matrix.md` and `assurance/capability-baseline.json`:
  the `tests` capability description states the satisfaction criteria. New
  conditional capability `mutation-testing`, CONDITIONAL for SA2, REQUIRED
  where warranted for SA3, NOT_APPLICABLE with reason elsewhere. Keep both
  files synchronized as the matrix requires.
- Verification plan and report: an optional `coverage` block per check in
  `assurance/verification-plan-v3.schema.json` with `report_path`, `metric`
  (line, branch or statement) and `floor`. The runner reads the report,
  records the measured value in `verification-report-v5.schema.json` as a
  diagnostic, and reports a value below the declared floor as a new issue
  `COVERAGE_BELOW_DECLARED_FLOOR`. The floor is project-declared and
  governance-owned: lowering it is a governance decision recorded in the
  project's design record, and in business-led mode a request to IT Security.
  The framework sets no central percentage. Schema v2 and v4 unchanged.
- `templates/repository/verification-plan.json`: the `tests` capability entry
  gains a `coverage` placeholder with `floor: null` and a reason field, so a
  new project must decide rather than inherit silence.
- Business-led link: `governance.py project validation-checklist` from WS3
  generates its items from the same acceptance criteria that the tests
  reference, and lists for each item whether an automated test exists.
- Scenario `GOV-036`: a feature request with three acceptance criteria; the
  agent must produce tests traceable to each criterion including a negative
  case, must not claim coverage percentage as proof, and must flag if it
  cannot test one criterion.
- Test script `scripts/test-coverage-semantics.py` added to
  `framework-verification-plan.json`: fixtures with coverage above floor,
  below floor, no report present (DID_NOT_EXECUTE for the coverage diagnostic,
  the test check itself unaffected), and a plan without a `coverage` block
  (unchanged behaviour).

**Acceptance.** A fixture whose tests pass but whose coverage report is below
the declared floor yields `COVERAGE_BELOW_DECLARED_FLOOR`. A fixture without a
`coverage` block behaves exactly as in 2.0.0. The GOV-036 challenge file
validates in the canonical format. The validation checklist for a
business-led fixture shows one line per acceptance criterion with its test
status.

**Boundaries.** No central coverage percentage. No product-to-tool mapping;
the coverage tool remains a project decision. Coverage is a diagnostic and a
floor, never a substitute for the satisfaction criteria above.

## 7. Phases and exit criteria

| # | Phase | Contains | Exit criteria |
| --- | --- | --- | --- |
| 0 | Design record | ADR under `docs/adr/` (create the folder) covering the three-layer architecture, the enforcement switch and the pathway mapping. Threat-model update in `docs/framework-threat-model.md` adding tampering by the agent, inbound prompt injection, agent over-privilege and registration drift. Registration contract drafted. | ADR and threat model committed on the feature branch. `quick` passes. |
| 1 | Managed client baseline | WS1 integrity, WS2 templates with `inform`, hook, project verify comparison, minimum version in CI. | Negative tests pass on both platforms. Hook denies governance edits in a local test with the managed-settings template applied to a test profile. |
| 2 | Mode and registration | WS3, WS4 contract, facts derivation, business-led rendering, readiness packet. | Business-led fixture produces request records and a readiness packet. All existing fixtures unchanged. Review packet prepared. **Review gate.** |
| 3 | Conformance scan | WS4 capability rules for Python and TypeScript, drift state, `block` template. | Drift fixture detected. False-positive review with IT Security on three real repositories, documented. |
| 4 | Normative content and test regulation | WS5, WS6, WS7, GOV-031 to GOV-036. | Static validation passes. Token budget met. Coverage semantics fixtures pass on both platforms. |
| 5 | Validation and release preparation | Prompt packets prepared for behavioral campaigns on both hosts in both modes. Campaign executed by humans. Adversarial and injection scenarios. One end-to-end Green pilot on a managed client. Release record drafted. | Campaign thresholds met per host and mode. Release record drafted, not published. 2.1.0 if professional mode stays compatible, else 3.0.0. |

Phases 1 and 2 can run in parallel after phase 0. Phase 3 depends on the
registration contract from phase 2. The schema and runner parts of WS7 may be
built in phase 2 alongside WS4 because they touch the same files; the
normative parts stay in phase 4. Phase 5 depends on everything.

## 8. Verification plan

- **Canonical verification** remains `python scripts/verify-framework.py quick`
  and `full`. New test scripts are added to `framework-verification-plan.json`
  for both execution targets: governance integrity, registration conformance,
  managed-settings template validation, hook behaviour, coverage semantics.
- **Cross-platform evidence** from Windows and Ubuntu CI is aggregated as
  today. Hook tests run on both.
- **Behavioral campaigns** follow the protocol-v2 kit in
  `scripts/manual-behavioral-campaign.py`. Matrix: two hosts, two modes,
  scenarios GOV-001 to GOV-036. Thresholds per host and mode as defined in
  `tests/governance/README.md`, extended so that GOV-031, GOV-032 and
  GOV-036 must score 2. The agent prepares prompts and scoring packets. Humans execute the
  campaign; see section 10.
- **Effectiveness tests**: prompt-injection scenarios, tamper attempts on a
  managed client, simulated unsafe agent behaviour. Results retained as
  evidence, failures kept as failures.
- **Pilot.** One Green project, for example the image-squaring tool, from
  registration to readiness packet on a managed client with the `inform`
  template.

## 9. Review packet after phase 2

Prepare a single file `docs/business-led/phase-2-review.md` containing:

- commits on the feature branch with one line each;
- `full` output for the current head, Windows and Linux where available, with
  DID_NOT_EXECUTE stated plainly where a target could not run locally;
- list of new and changed files grouped by workstream;
- confirmation that every existing fixture and GOV scenario definition is
  byte-identical to 2.0.0;
- every ASSUMPTION relied on, every OPEN QUESTION, every RISK found;
- anything in this plan you deviated from and why.

## 10. Limits the implementing agent must respect

- **Behavioral campaigns are manual.** The framework retired the headless
  harness. You prepare prompt directories and scoring packets with the
  campaign kit. You do not run the campaign, do not score responses, and do
  not claim behavioral acceptance.
- **Host policy surfaces are verified, not assumed.** The managed-settings
  location, deny-rule syntax, hook protocol and MCP allowlist mechanism for
  Claude Code, and the equivalent for Codex, must be checked against the
  current host documentation at implementation time. Record what you verified
  and the host version. If a surface does not exist, record a KNOWN RISK and
  do not fake it with a project-level setting the user could edit.
- **Local evidence is informational in business-led mode.** Do not design
  anything that lets a client-side result substitute for the protected CI
  result.
- **The framework never blocks development on its own.** Every blocking
  behaviour is behind the `block` parameter that only the managed settings
  supply. The default is `inform`.
- **No release actions.** Building, tagging, publishing and changing the
  distribution inventory are separate approvals.

## 11. Assumptions, now constraints

| Assumption | If it proves false |
| --- | --- |
| GitLab is the primary SCM platform; GitHub is secondary | Build the GitHub ruleset variant first instead. Both templates are small. |
| Both Claude Code and Codex are in scope for business employees | Drop the host that is out of scope; do not remove its professional-mode adapter. |
| The registration arrives as a file; IT Security fills the template by hand until a tool exists | Nothing changes in the framework; the tool later emits the same file. |
| A curated package proxy exists | Guidance stays; the deterministic protection is missing and is recorded as a KNOWN RISK for IBO. |
| The managed client gives the employee no administrative rights | Local controls become deterrence only. CI remains the evidence gate. Record as KNOWN RISK. |
| Professional mode keeps its current approval model | Stop; this is a separate C2 decision. |

## 12. Background: the gaps this plan closes

Assessment of framework 2.0.0 on 2026-09-18, against the intended use by
business employees. Each gap names the evidence in the code so the
implementing agent can verify it before changing it.

1. **Governance artifacts are agent-writable and unverified.** Self-protection
   exists only as prose in `global/governance-standard.md` (section
   "Governance self-protection") plus GOV-010, which covers a user asking to
   weaken rules, not the agent doing so on its own. Nothing stops the agent
   from editing project `AGENTS.md`, `CLAUDE.md`, `project-governance.yml`,
   `verification-plan.json`, `.claude/` rules, skills, settings and hooks, or
   the user-level `CLAUDE.md`. `verify_project` in `governance.py` checks only
   that managed blocks exist. `load_baseline` in
   `assurance/run-verification.py` validates schema shape only, and
   `resolve_baseline_path` prefers the project-local copy, whose hash is
   recorded but never compared to a release. The assurance facts in
   `templates/repository/verification-plan.json` are self-declared, so
   setting `has_exposed_web_surface` to false disables DAST legitimately. The
   Claude adapter installs one `Read` allow rule and no deny rules or hooks.
   Closed by WS1, WS2, WS4.
2. **Prompt-only enforcement without compensating controls.** The evaluation
   records show critical scenarios needing several attempts to pass. Branch
   protection, mandatory review, protected CI and restricted agent
   permission modes are not required anywhere. Closed by WS2.
3. **No role model for business users.** Every consequential approval routes
   to "the developer". The words "business user" do not appear in the
   repository. Closed by WS3.
4. **Inbound prompt injection is not covered.** The secure standard treats AI
   output as untrusted but says nothing about untrusted instructions reaching
   the agent from files, dependency documentation, issues, web fetches or MCP
   tools. Closed by WS5 and WS2 allowlists.
5. **Agent runtime configuration is ungoverned.** MCP servers, hooks,
   plugins, memory, subagents and bypass modes are not classified as trust
   boundaries. Closed by WS2.
6. **Data sent to the model and secrets visible to the agent.** "Privacy"
   appears only as a materiality keyword. No rule about credential files or
   sensitive information in prompts. Secret scanning covers commits only.
   Closed by WS2 deny rules and WS5.
7. **Version-control safety and accountability.** `skills/automation-safety`
   is filesystem-centric. Force push, history rewrite and agent-authored
   commits are unaddressed. Approval fields in
   `templates/repository/docs/risk/accepted-risks.md` can be filled by the
   agent. Closed by WS5 and WS3.
8. **AI-specific coding failures.** No package existence step in
   `workflows/dependency-change/WORKFLOW.md`. No rule against weakening tests.
   NOT_APPLICABLE accepted with any non-empty reason. Licence only for
   dependencies. Closed by WS5 and WS4.
9. **Company-scale visibility.** Installation is per user and optional. No
   inventory, no minimum version, no central distribution. Closed by WS4
   together with IT's provisioning of the managed client.
10. **Proportionality drift in the instruction set.** The kernel spends large
    sections on line-ending attribution and aggregation while simple
    high-value rules are missing. Codex-specific wording remains in
    `README.md` and `assurance/verification-standard.md`. Closed by WS6.
11. **Testing is a philosophy, not a regulation.** `tests` is REQUIRED for M1
    and above in `assurance/capability-matrix.md`, but no document defines
    when the capability is satisfied; one trivial passing test meets it.
    `global/engineering-constitution.md` rejects coverage percentage as
    proof, yet the framework neither measures nor reports coverage, so there
    is no diagnostic and no floor. `skills/testing-strategy/SKILL.md` is
    three sentences. `workflows/new-feature/WORKFLOW.md` defines acceptance
    criteria and never requires a test per criterion. No rule addresses that
    the same agent writes code and tests, or that tests may be weakened to
    pass. Negative cases are required only in security skills. Not found in
    the September 2026 assessment; identified on the maintainer's question
    afterwards. Closed by WS7, with WS5 for test tampering.

## 13. Classification and applicability

This plan is **C2**: it changes framework policy, assurance semantics and
installer behaviour. Elements become C3 only where the global rules require
it, for example if a control were weakened. None is.

Applicability statement for the framework repository itself, as its own
governance requires:

1. The repository remains the M2/SA1 distributed governance and tooling
   package, not an application or hosted service.
2. `framework-verification-plan.json` stays the single source of assurance
   applicability. No second or parallel baseline is created or implied.
3. Canonical verification, lifecycle and package regression, Windows and POSIX
   evidence, secret scanning, meaningful SAST, CI and evidence integrity, and
   release artifact binding are retained and extended with the new test
   scripts.
4. Auth review, DAST, container scanning, deployment-IaC scanning, recovery
   verification and dependency SCA remain NOT_APPLICABLE only while their
   factual triggers stay absent.
5. SBOM, signing and stronger provenance remain conditional on the
   distribution channel. Internal company distribution is an approved trigger
   that requires reassessing release signing before the first internal
   rollout.
6. A material applicability or assurance-policy change is C2 unless the
   global change-class rules require C3.

## 14. Risks

| Risk | Consequence | Handling |
| --- | --- | --- |
| Prompt-level rules stay probabilistic | An agent may still ignore an instruction | Every material control has a deterministic counterpart on Layer 1 or 2. Campaign evidence shows the residual rate. |
| Capability rules produce false positives | Unnecessary reassessment requests | Phase 3 false-positive review. Rules start narrow and grow. |
| Campaign cost doubles with two modes | Release cadence slows | Mode blocks are short. Response-surface preservation records carry evidence across documentation-only changes. |
| A host lacks a managed policy surface | Layer 1 incomplete for that host | Record KNOWN RISK; do not substitute a user-editable setting. |

---

This document is the approved work record for the business-led mode.
Authoritative applicability decisions remain in
`framework-verification-plan.json`. The ADR produced in phase 0 becomes the
durable design decision; this plan is then referenced from it.
