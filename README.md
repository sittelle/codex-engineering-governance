# Codex Engineering Governance

> **Release status: STABLE CANDIDATE** — approved for regular supervised use after validation. This is not formal compliance certification and does not authorize unattended high-consequence autonomy.

Version **1.0.0**.


`1.0.0` is the final 1.0 release tree promoted from the accepted rc.3 baseline. rc.3 closed the release-package reproducibility defect by using `ZIP_STORED` and Git-tree-derived executable modes. The required fresh behavioral campaign completed 30/30 scenarios with 60/60 points, no critical 0s, and GOV-026..GOV-030 all 2/2; all 116 durable behavioral evaluation records are included. All 30 frozen GOV scenario/rubric files remain unchanged, and no governance or assurance semantic is changed by the final evidence/version integration. Technical readiness does not authorize publication.

A technology-neutral governance baseline for using Codex as a professional software-engineering agent while preserving developer control over product intent, material tradeoffs, security risk, and consequential actions.

## Design goals

- specification before implementation;
- recommendation-first technical guidance;
- material ambiguity remains unresolved;
- no unexpected material behavior;
- proportional engineering rigor;
- secure-by-design/default;
- evidence-based completion;
- release-blocking security policy;
- durable repository context rather than chat-only memory.

## Codex instruction architecture

Install `codex-home/AGENTS.md` as the global `~/.codex/AGENTS.md`.

Each governed project then receives its own repository-root `AGENTS.md` from `templates/repository/AGENTS.md`.

Keep `AGENTS.md` concise. Detailed requirements, architecture, security context, ADRs, and risks belong in project documents and are read when the active workflow requires them.


## Windows downloaded-package trust

Windows may attach Internet-zone metadata (Mark-of-the-Web) to a downloaded ZIP and propagate it to extracted `.ps1` files. Under common `RemoteSigned` execution-policy configurations, PowerShell can then refuse to run the unsigned framework scripts even though their contents are unchanged.

Treat this as a package-trust decision, not permission to bypass PowerShell policy. Prefer this sequence for a package obtained from a trusted release channel:

1. verify the downloaded archive's published SHA-256/release identity;
2. unblock the **verified archive before extraction**;
3. extract it normally;
4. run the scripts without `-ExecutionPolicy Bypass`.

Example after comparing the archive hash with the published release record:

```powershell
Get-FileHash .\codex-engineering-governance-v1.0.0.zip -Algorithm SHA256
Unblock-File .\codex-engineering-governance-v1.0.0.zip
```

If the archive was already extracted and the verified extracted `.ps1` files still carry zone metadata, unblock only those trusted scripts deliberately:

```powershell
Get-ChildItem . -Recurse -File -Filter *.ps1 | Unblock-File
```

Do not edit/resave scripts merely to make them executable: doing so changes distributed artifact bytes and obscures package/evidence identity. Do not weaken machine-wide execution policy or use a blanket execution-policy bypass just to make governance tooling run.

## Main areas

- `global/` — normative engineering/security/governance standards.
- `workflows/` — task-specific execution procedures.
- `skills/` — reusable specialist reasoning procedures.
- `profiles/` — technology/platform specialization.
- `templates/` — project bootstrap material.
- `assurance/` — verification and release-gate policy.
- `release-evidence/` — durable release records and versioned validation history (`release-evidence/validation/`).
- `tests/governance/` — behavioral regression scenarios.
- `reference-projects/` — governance validation scenarios.


## Framework repository self-governance

The governance source repository dogfoods only the controls that materially apply to distributed governance/tooling. `framework-governance.yml` contains repository-specific pointers; `framework-verification-plan.json` is the single assurance applicability source. Application auth/authz, DAST, container/IaC scanning, operational recovery verification, and dependency SCA remain N/A while their factual triggers are absent.

Canonical repository verification:

```text
python scripts/verify-framework.py quick
python scripts/verify-framework.py full
```

Verification-plan schema v3 adds target-aware evidence for required OS/machine contracts. Existing project plan schema v2 remains supported unchanged. Windows and Ubuntu CI produce canonical full reports; `aggregate-full` is the combined assurance/release gate.
For this framework repository, push-triggered self-verification is bound to the repository `master` branch; pull requests and manual dispatch remain available.

## Default classification

Maturity:
- M0 Exploration
- M1 Maintained
- M2 Distributed
- M3 Operated

Security assurance:
- SA-0 Experimental
- SA-1 Standard
- SA-2 Elevated
- SA-3 High Assurance

Change consequence:
- C0 Trivial
- C1 Normal
- C2 Material
- C3 Critical/high consequence

## Important principle

Governance requires sufficient durable information and evidence, **not unnecessary document ceremony**. Small projects may consolidate requirements, architecture, security assumptions, and test notes when clarity and discoverability remain strong.

## Technology Baseline

For M1+ governed projects, architecture-significant choices are recorded as a project-owned Technology Baseline rather than being left as chat-only stack decisions.

The default project manifest contains:

```yaml
technology_baseline:
  state: "UNESTABLISHED"
  record: "docs/design.md#technology-baseline"
```

States are `UNESTABLISHED`, `ESTABLISHED`, and `RECONCILIATION_REQUIRED`.

The baseline records stack-shaping decisions such as primary language/toolchain, runtime, central framework/platform, persistence, deployment/packaging, supported targets, and other components whose replacement materially changes architecture, support, security/trust, operations, supply-chain exposure, or canonical verification. It does **not** duplicate the complete dependency graph; exact resolved versions remain in ecosystem manifests/lockfiles.

The governed path is:

`Requirements / Constraints → Architecture → Technology Selection → Technology Baseline → C2/C3 approval where required → durable project record → canonical verification → implementation`

A material later baseline change is C2 at minimum, uses normal dependency/security/data workflows as applicable, remains `RECONCILIATION_REQUIRED` during transition, and is complete only after the durable record, repository/dependency state, support claims, and canonical verification agree.

Technology neutrality is preserved: governance controls the decision process and evidence, not which language/framework/database must be chosen.

## Core skills

The v0.1.1 core includes `authentication-design` in addition to technology-selection, architecture-design, threat-modeling, authorization-review, dependency-review, testing-strategy, automation-safety, and security-review.


## Central governance discovery

The installed global kernel is intentionally compact. Detailed governance is located through:

```text
$CODEX_HOME/GOVERNANCE_ROOT
```

If `CODEX_HOME` is unset, the installer uses:

```text
~/.codex
```

`GOVERNANCE_ROOT` contains one absolute filesystem path: the root of this governance repository.

For a governed project, Codex should:
1. read project `AGENTS.md` and `project-governance.yml`;
2. resolve `GOVERNANCE_ROOT`;
3. verify the central repository `VERSION` against the project's pinned baseline when the task is C2/C3, security-sensitive, or release-related;
4. load only the applicable workflow, skills, profiles, and detailed standards.

The locator prevents hard-coding a developer-specific governance path into every project.

## Version semantics

The package `VERSION` is the governance distribution version. Public stable releases use SemVer; compatibility, package-production, provenance, and publication rules are defined in `docs/release-policy.md`.

The four files under `global/` are normative package documents and follow the package version.

Machine-readable assurance identifiers use:

```text
SA0
SA1
SA2
SA3
```

Human prose may render them as `SA-0` through `SA-3`.


## Updating an existing governed project

Use the project updater instead of manually changing the pinned baseline.

Windows preview:

```powershell
.\scripts\update-governed-project.ps1 -ProjectRoot "D:\development\example"
```

Apply after reviewing the preview:

```powershell
.\scripts\update-governed-project.ps1 -ProjectRoot "D:\development\example" -Apply
```

If `-ProjectRoot` is omitted, the script prompts for it.

POSIX preview:

```bash
./scripts/update-governed-project.sh /path/to/project
```

Apply:

```bash
./scripts/update-governed-project.sh /path/to/project --apply
```

The updater:
- verifies the target looks like a governed project;
- compares the project pin with this governance repository `VERSION`;
- refuses mutation on a dirty Git worktree unless explicitly overridden;
- creates timestamped backups;
- updates only governance baseline/source/locator metadata;
- installs/refreshes a marked central-governance loading block in project `AGENTS.md`;
- preserves project-specific instructions and design/security content.

It does **not** automatically accept new risks, change maturity/assurance, rewrite project requirements, or modify project verification commands.


## Behavioral-test execution contexts

Behavioral tests declare one of two execution contexts:

- `GLOBAL_KERNEL` — run in an empty workspace with no project `AGENTS.md` or `project-governance.yml`;
- `GOVERNED_REPOSITORY` — run in a minimal governed repository with a current project baseline so detailed central workflows/skills/standards are part of the intended evaluation path.

Do not score a `GOVERNED_REPOSITORY` test as if the compact global kernel alone were expected to reproduce every detailed invariant.


## Governed project lifecycle

Use `scripts/manage-governed-project.ps1` on Windows.

New governed project, preview then apply:

```powershell
.\scripts\manage-governed-project.ps1 -Mode New -ParentRoot "D:\development" -ProjectName "my-project"
.\scripts\manage-governed-project.ps1 -Mode New -ParentRoot "D:\development" -ProjectName "my-project" -Apply
```

Adopt an existing ungoverned project, preview then apply:

```powershell
.\scripts\manage-governed-project.ps1 -Mode Adopt -ProjectRoot "D:\development\existing-project"
.\scripts\manage-governed-project.ps1 -Mode Adopt -ProjectRoot "D:\development\existing-project" -Apply
```

If parameters are omitted, the script prompts interactively. New mode refuses an existing non-empty target. Adopt mode preserves existing project content and records `RECONCILIATION_REQUIRED`; it never retroactively claims that pre-existing work was governance-approved.


## Deterministic release package production

Build a candidate/release artifact only from a clean committed repository state:

```powershell
python .\scripts\build-release-package.py
```

The builder reads MANIFEST-managed bytes from exact Git `HEAD`, uses deterministic `ZIP_STORED` members plus Git-tree executable modes, independently rebuilds the archive to prove byte reproducibility, writes `codex-engineering-governance-v1.0.0.zip`, and writes its `.sha256` sidecar. It does not commit, tag, push, create a GitHub Release, or change repository visibility.

## Candidate validation and application workflow

Use the repository-owned candidate tooling instead of manually repeating validation commands or recursively replacing the worktree.

Preflight a downloaded candidate first:

```powershell
python .\scripts\preflight-candidate-package.py `
  --zip "$HOME\Downloads\codex-engineering-governance-v1.0.0.zip" `
  --sha256 <expected-sha256>
```

The preflight verifies the ZIP digest and exact MANIFEST inventory and requires all current durable behavioral evaluation records plus all frozen GOV scenario files to be byte-identical in the candidate package. It fails before replacement if historical evidence or scenario definitions drift.

Plan the bounded worktree transition (dry-run is the default):

```powershell
python .\scripts\apply-candidate-package.py `
  --zip "$HOME\Downloads\codex-engineering-governance-v1.0.0.zip" `
  --sha256 <expected-sha256>
```

After reviewing the plan, apply it explicitly:

```powershell
python .\scripts\apply-candidate-package.py `
  --zip "$HOME\Downloads\codex-engineering-governance-v1.0.0.zip" `
  --sha256 <expected-sha256> `
  --apply
```

The application tool automatically reruns package preflight, requires a clean Git worktree, preserves `.git` and non-MANIFEST source/local files, writes only candidate-MANIFEST files, removes only files owned by the previous MANIFEST, verifies the resulting MANIFEST-managed bytes, and then runs `scripts/validate-candidate.py`. It never recursively deletes the worktree. If application or post-apply validation fails, it restores the pre-apply MANIFEST-managed file bytes and reports rollback status.

If the currently installed baseline predates `apply-candidate-package.py`, extract the trusted candidate archive to a temporary directory and run the candidate copy of the script with `--repo` pointing at the authoritative framework worktree; after v0.5.24 is installed, future candidates can invoke the repository copy directly.

The local validation bundle runs governance validation, manifest regression, lifecycle common plus the host-native lifecycle path, assurance integration, canonical quick verification, canonical local full verification, and `git diff --check`. A local full result may remain `INCOMPLETE_ASSURANCE` only when every remaining required nonexecution is an approved CI-context deferral; real FAIL, operational nonexecution, or another unexpected disposition fails the bundle. Exact-commit cross-platform CI evidence is still required before freeze.

## Post-freeze baseline activation

After a framework version is already frozen/tagged, use the repository-owned activation tool to repin the evaluation fixture and install/verify the global Codex kernel instead of pasting a multi-step shell sequence. This tool is specific to the framework evaluation fixture plus Codex home; it does not publish tags/releases or alter the frozen framework tree.

Preview only (default):

```powershell
python .\scripts\activate-frozen-baseline.py `
  --fixture "D:\development\codex-governance-eval"
```

Apply explicitly after reviewing the plan:

```powershell
python .\scripts\activate-frozen-baseline.py `
  --fixture "D:\development\codex-governance-eval" `
  --apply
```

The activation tool requires a clean fixture Git worktree, invokes the existing governed-project updater, reconciles the evaluation fixture's baseline assertion, verifies the authoritative managed `AGENTS.md` block (including the valid no-diff case when it is already byte-equivalent), runs fixture quick/full verification plus `git diff --check`, removes updater backup artifacts, and requires the remaining fixture diff to be commit-ready and bounded to `AGENTS.md`, `project-governance.yml`, and `tests/eval-verification.py`. It then installs the global kernel with the existing host-native installer and verifies byte identity plus `GOVERNANCE_ROOT`. Dry-run is non-mutating; apply failures restore the wrapper-owned fixture/global state.

The activation path remains available for already-frozen baselines. Release-candidate evaluation and final public-lineage preparation remain separate from activation.

## Stable-candidate change discipline

The v0.2.x line is intentionally conservative. Global policy should change only for a reproducible governance regression, security defect, integration/compatibility defect, repeated cross-project proportionality failure, or deliberately planned new capability with tests. Project-specific lessons remain project-local unless repeated evidence shows a reusable governance need.


## Data migration workflow

Use `workflows/data-migration/WORKFLOW.md` for schema/data changes that move, transform, delete, reinterpret, backfill, repartition, or otherwise materially alter persisted data.

The workflow is intentionally broader than destructive deletion. It applies to migrations where correctness depends on:
- old/new data invariants;
- compatibility during rollout;
- backfill/transformation semantics;
- preservation/recovery;
- post-migration validation.

Destructive steps remain subject to the global destructive-data invariant and explicit C3 approval boundary.


## Dependency change workflow

Use `workflows/dependency-change/WORKFLOW.md` when adding, removing, upgrading, replacing, pinning, or materially reconfiguring a dependency.

The workflow distinguishes:
- low-risk patch/minor maintenance;
- security-driven dependency changes;
- major-version/API/runtime-support changes;
- dependency replacement/removal;
- direct versus transitive effects.

It requires technical due diligence without turning every routine patch update into an architecture exercise.


## Emergency fix workflow

Use `workflows/emergency-fix/WORKFLOW.md` for production incidents, active outages, severe regressions, urgent security containment, and other situations where normal delivery time is materially compressed.

The workflow keeps only the minimum safe governance needed to act quickly:
- confirm the incident and affected scope;
- prefer containment/rollback over broad weakening;
- make the smallest viable change;
- preserve security/destructive stop conditions;
- run the minimum meaningful verification;
- record anything skipped;
- require explicit risk acceptance where residual risk is knowingly introduced;
- reconcile and complete deferred evidence after stabilization.

Emergency does not mean governance-free.


## Refactor workflow

Use `workflows/refactor/WORKFLOW.md` for structural/code-quality changes whose intended outcome is behavior preservation.

The workflow distinguishes:
- pure/internal refactoring;
- public API/contract changes;
- persistence/data-model changes;
- dependency/toolchain changes;
- performance/security behavior changes.

Material non-refactor changes are split into their appropriate workflow/approval boundary rather than being hidden inside “cleanup.”


## Local / CI assurance architecture

v0.3.0 introduces a technology-neutral verification contract.

A governed project may use the reference JSON plan/runner or an ecosystem-equivalent interface, but it must preserve the same semantics:
- canonical `quick` and `full`;
- named assurance capabilities;
- explicit applicability;
- truthful PASS / FAIL / NOT_APPLICABLE / DID_NOT_EXECUTE evidence;
- local and CI execution of the same underlying checks;
- no silent downgrade when a required control cannot run.

See:
- `assurance/architecture.md`
- `assurance/capability-matrix.md`
- `assurance/verification-plan.schema.json`
- `assurance/run-verification.py`

The reference runner is dependency-free Python and uses argv arrays, so checks do not depend on shell-specific `&&` syntax. It is a reference implementation, not a mandatory application runtime dependency.


## Bootstrap project-local assurance

After the project stack and canonical checks are defined, install the project-local assurance runner and GitHub baseline.

Windows preview/apply:

```powershell
.\scripts\bootstrap-assurance.ps1 -ProjectRoot "D:\development\my-project"
.\scripts\bootstrap-assurance.ps1 -ProjectRoot "D:\development\my-project" -Apply
```

POSIX preview/apply:

```sh
./scripts/bootstrap-assurance.sh --project-root /path/to/project
./scripts/bootstrap-assurance.sh --project-root /path/to/project --apply
```

The bootstrap preserves an existing verification plan, installs the reference runner under `.governance/`, records hashes, ignores local evidence, and installs `.github/workflows/governance-verify.yml` only after the plan is configured. A project may add `.governance/ci-bootstrap.py` for CI-only environment/tool setup; that hook must not redefine or weaken the plan.

The generated workflow uses SHA-pinned official GitHub Actions dependencies. Future action updates are dependency changes and should be reviewed accordingly.


## Verification plan schema v2

`verification-plan.json` now carries an explicit capability inventory, while `.governance/assurance-baseline.json` is managed from the governance package. Full verification compares the two before executing checks.

This prevents a false-green plan that simply omits a required capability.

The reference runner also resolves the first argv element with `shutil.which()` using the check environment PATH. A logical command such as `["npm", "test"]` therefore remains one cross-platform plan: Windows may resolve it to `npm.cmd`, while POSIX resolves `npm`.

Existing schema-v1 plans are not silently treated as assurance-complete. They may still be inspected/migrated, but canonical full verification remains `INCOMPLETE_ASSURANCE` until reconciled to v2.


## Assurance execution semantics

v0.3.3 distinguishes three materially different outcomes:

- the assurance tool completed and passed;
- the assurance tool completed and reported a policy/test finding (`FAIL`);
- the assurance tool did not successfully complete (`DID_NOT_EXECUTE` → `INCOMPLETE_ASSURANCE`).

The default remains fail-safe: exit `0` is PASS and every other exit code is FAIL. A project may classify explicitly documented nonzero tool-error exit codes as `DID_NOT_EXECUTE` only with a `DOCUMENTED_EXIT_CODES` policy and a durable contract reference. Unknown/unmapped nonzero codes remain FAIL.

Checks may also declare approved execution contexts. A required capability may be evidenced in CI or another approved specialized environment without being made `NOT_APPLICABLE` on a developer workstation. Single-environment `full` remains incomplete until all required execution-context evidence exists.

Use `assurance/aggregate-verification.py` (or the project-managed copy) to combine full reports. Aggregation requires the same project, exact Git commit, clean worktree evidence, verification-plan hash, assurance-baseline hash, and runner hash.


## v0.3.4 portability note

The assurance integration fixture is host-neutral. Its static plan uses the test-only `__TEST_PYTHON__` placeholder, materialized by the integration harness with the interpreter actually running the test. The PATH-resolution probe is `.cmd` on Windows and an executable script on POSIX. This affects only framework self-testing.

## v0.5.11 Technology Baseline Transition Summary

v0.5.11 retains the existing Technology Baseline policy and unchanged GOV-030 rubric, but makes the pre-implementation output contract explicit. For a C2/C3 architecture-significant transition, the response/readiness/design record emits a `Technology Baseline Transition Summary` with labeled fields for delta/classification, technical recommendation, dependency/supply-chain and triggered impacts, approval state, transition state/durable record, verification/assurance reconciliation, and `ESTABLISHED` closure criteria. A genuinely irrelevant field is stated `NOT APPLICABLE` with reason rather than silently omitted. New-feature work that discovers/proposes such a stack delta routes into the existing technology-selection and dependency-change mechanisms.

## v0.5.10 Technology Baseline transition completeness

v0.5.10 records the first valid GOV-030 attempt as 1/2 and strengthens only the proximate project instruction path needed for consistent transition behavior. A material change to an established Technology Baseline must explicitly cover technology-selection plus dependency/supply-chain analysis, the agent's recommendation, C2/C3 approval, durable target state with `RECONCILIATION_REQUIRED`, canonical quick/full plus newly applicable assurance capabilities, and return to `ESTABLISHED` only when the durable baseline, repository/dependency state, support claims, and verification agree. The GOV-030 rubric and underlying policy are unchanged.

## v0.5.9 Legacy governed-project Technology Baseline migration

v0.5.9 closes the compatibility gap found while preparing GOV-030: a repository already governed under a pre-Technology-Baseline version could previously be repinned to the new framework while still lacking the new baseline state. The Windows and POSIX governed-project updaters now detect a missing `technology_baseline` section and add `RECONCILIATION_REQUIRED` with the standard durable record pointer. Existing Technology Baselines are preserved byte-for-byte in substance; the updater does not infer historical approval or silently mark an older stack `ESTABLISHED`. Lifecycle regressions cover both legacy migration and preservation of an existing project-owned baseline.

## v0.5.8 Technology Baseline governance

v0.5.8 makes architecture-significant technology decisions a first-class governed project state without prescribing technologies. New M1+ projects begin `UNESTABLISHED`; adopted repositories begin `RECONCILIATION_REQUIRED`; an established baseline cannot silently drift through implementation or dependency maintenance. Material baseline changes are C2 at minimum, reuse existing technology/dependency/data/security analysis, and require canonical-verification reconciliation. GOV-030 covers the drift-prevention path.

## v0.5.7 framework applicability response completeness

GOV-029 attempts 1 and 2 each scored 1/2 and remain retained. The six-part response-completeness contract then produced fresh attempt 3 at 2/2 under the unchanged wording/rubric. The frozen v0.5.7 commit `76e39efb073776984f455d88c33bab7a0ae23fee` also passed GitHub Actions run `33365512612` with aggregate schema v2/report v5, `overall: PASS`, `issues: []`, and all 14 required Windows/Ubuntu checks PASS.

## v0.5.6 Linux scanner fixture calibration

The real v0.5.5 Windows/Ubuntu rerun reduced the aggregate failure to the Linux positive-fixture regression only: production Gitleaks, Semgrep, ShellCheck, Zizmor, and the Windows PSScriptAnalyzer path otherwise passed. The Gitleaks fixture had used an alphabet-sequence token that the pinned default configuration intentionally treats as a stopword, while the ShellCheck fixture exercised informational `SC2086` under a production threshold that admits only warning/error findings. v0.5.6 corrects those fixtures without weakening scanner policy: it uses a non-stopword deterministic synthetic PAT-shaped value with the repository Gitleaks configuration, and it uses the field-observed warning-level `SC1007` case for ShellCheck.

## v0.5.5 cross-platform field fixes

The first real Windows/Ubuntu framework aggregate run confirmed that Git-canonical plan/baseline/runner hashes match across platforms while checkout-byte hashes may differ because of line-ending normalization. Aggregation therefore compares only the canonical Git-bound identity (`source`, `repository_path`, committed `sha256`); `working_tree_sha256` remains diagnostic.

The same field run found ShellCheck `SC1007` in POSIX `CDPATH` path-resolution idioms and an opaque Linux scanner-regression operational failure. v0.5.5 fixes the shell syntax without suppressing ShellCheck, makes the non-root Semgrep fixture mount readable, and retains bounded scanner-specific diagnostics for any future operational nonexecution.

## Cross-platform evidence identity

For clean tracked project assurance artifacts, verification evidence binds to committed Git `HEAD` content, not the platform-specific bytes produced by checkout. This keeps local Windows and Ubuntu CI evidence comparable when Git performs ordinary line-ending conversion.

Reports also record working-tree hashes for diagnostics. Dirty/untracked artifacts are not eligible for cross-environment aggregation.


## v0.3.9 source/package inventory validation

Source-tree validation no longer mistakes Git metadata or developer-local files for distributable package content. `MANIFEST.json` is the distribution allowlist; exact package inventory is checked against a concrete ZIP or extracted package with `python scripts/validate-governance.py --artifact <path>`.

## v0.3.8 release-evidence hygiene

The static validator distinguishes **behavioral scenarios** from completed behavioral evaluations. Scenario files are not counted as if they had been executed. Completed evaluations use durable records under `tests/governance/evaluations/`. The package manifest is also checked against the actual packaged file inventory so missing or unlisted files cannot silently pass static validation.

The current behavioral acceptance rule is documented in `tests/governance/README.md`; a 1.0 candidate requires a complete candidate evaluation set rather than relying on historical scenario-file counts.

## v0.3.7 aggregate failure observability

Cross-environment aggregation is fail-dominant: if an attributable execution of a required check reports `FAIL`, a `PASS` from another approved context cannot mask it, including for `required_contexts: ["ANY"]`. The aggregate report and console output identify the failed check and failing execution context(s). `DID_NOT_EXECUTE` deferral remains distinct and may be satisfied by valid PASS evidence in another permitted context when the plan allows it.

## v0.3.6 CI bootstrap evidence and tool locks

The generated GitHub workflow invokes `.governance/run-ci-verification.py`. The orchestrator runs optional project CI bootstrap and always routes into canonical full verification when the managed runner remains operational. Bootstrap failure therefore produces `DID_NOT_EXECUTE` / `INCOMPLETE_ASSURANCE` evidence instead of merely ending the job before `ci-full.json` exists.

Assurance-tool dependency locks are environment-bound unless proven universal. Prefer explicit per-environment locks for platform-sensitive Python/binary tooling; never drop hashes or pinning merely because a lock generated on one OS fails on another.

### Failure evidence versus policy exceptions

Behavioral failures/regressions are retained in their evaluation records, and verification failures remain in canonical verification evidence/reports. Neither requires a second parallel record. Explicit approved policy exceptions remain governed only by `assurance/exception-policy.md`; a failure is not an exception or waiver by itself.
