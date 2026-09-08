# Local / CI Assurance Architecture

## Purpose

Provide one evidence model for developer verification, Codex verification, CI, and release decisions without forcing every project into the same toolchain.

The architecture is **capability-based**.

Governance may require `SAST`, `SCA`, `SECRETS`, or `TESTS`; it does not require a particular brand when an equivalent control provides suitable evidence.

## Core model

A project defines one canonical verification interface with two stages:

- `quick` — fast feedback for ordinary development;
- `full` — completion/release evidence for the project's current maturity/assurance and change class.

`full` includes all required `quick` checks plus additional assurance capabilities.

CI SHOULD invoke the same underlying plan/check definitions used locally.

Local and CI wrappers may differ only for environment/bootstrap needs, not by silently omitting required checks.

## Evidence states

Each check ends in exactly one machine state:

- `PASS`
- `FAIL`
- `NOT_APPLICABLE`
- `DID_NOT_EXECUTE`

`DID_NOT_EXECUTE` is never PASS.

A tool that is missing, crashes, cannot start, returns malformed evidence, or is prevented from running produces `DID_NOT_EXECUTE` unless a more specific failure result is trustworthy.

Human summaries may additionally classify the overall state as:
- `VERIFIED`
- `UNVERIFIED`
- `KNOWN RISK`
- `ACCEPTED RISK`
- `INCOMPLETE ASSURANCE`
- `REMAINING WORK`

## Applicability

Every configured capability has an applicability decision.

Use `NOT_APPLICABLE` only when the capability truly does not apply to the system/change.

Examples:
- DAST may be `NOT_APPLICABLE` for a local non-networked CLI.
- container scanning may be `NOT_APPLICABLE` when no container artifact exists.
- IaC scanning may be `NOT_APPLICABLE` when the repository has no infrastructure-as-code.

Do not install irrelevant scanners merely to avoid `NOT_APPLICABLE`.

Do not mark a required applicable control `NOT_APPLICABLE` merely because the tool is inconvenient or unavailable.

## Requiredness

Requiredness comes from:
1. maturity/assurance baseline;
2. project profiles and threat model;
3. change class/current workflow;
4. release policy;
5. explicit project policy.

The highest applicable requirement wins.

A project may add stronger checks.

A project must not silently remove a required capability to get green status.

## Quick stage

Quick should normally be fast enough for frequent use.

Typical capabilities:
- format/lint;
- type/compile;
- focused unit tests;
- selected fast integration tests;
- build/import sanity;
- secret scan when fast enough.

Quick is not a substitute for full verification.

## Full stage

Full is the canonical evidence interface for completion/release where required.

Typical capabilities as applicable:
- all quick checks;
- complete tests;
- build/package;
- secret scan;
- SAST;
- SCA/dependency audit;
- security tests;
- SBOM;
- container scan;
- IaC scan;
- DAST;
- fuzz/recovery/performance checks at higher assurance when justified.

## Local / CI parity

The same check IDs and commands SHOULD underlie local and CI execution.

CI MAY add:
- environment setup;
- matrix runtimes/platforms;
- clean checkout;
- artifact upload;
- evidence retention.

CI MUST NOT silently redefine `full` to a weaker set of checks.

If a check can only run in CI or only in a specialized environment, represent that explicitly in the plan/evidence.

## Supported-runtime evidence

Declared support and verified support are distinct.

A package manifest may declare a runtime range. Verification evidence identifies exactly which runtimes/platforms actually executed.

Do not infer compatibility for untested declared versions.

## Canonical plan

The reference plan is `verification-plan.json`.

Each check defines:
- stable `id`;
- `capability`;
- stages (`quick`, `full`);
- argv command;
- applicability;
- requiredness;
- optional timeout;
- optional evidence notes.

Commands are argv arrays, not shell snippets.

This avoids shell-specific chaining and makes execution explicit.

## Reference runner

`assurance/run-verification.py` is a dependency-free reference implementation.

Projects MAY:
- copy/adapt it;
- call it from a project wrapper;
- use an ecosystem-equivalent runner.

Equivalent runners must preserve evidence states and required-control semantics.

## Overall stage result

A stage is:
- `FAIL` if any executed required check fails;
- `INCOMPLETE_ASSURANCE` if a required applicable check is absent or `DID_NOT_EXECUTE`;
- `PASS` only when all required applicable checks pass and no required evidence is missing.

Optional check failures still require reporting and project-specific disposition; they are never hidden.

## Risk acceptance versus missing assurance

Known vulnerability/finding risk acceptance is not the same as a required control failing to execute.

A vulnerability may be accepted under the severity/risk policy where permitted.

A required assurance control that did not execute remains missing evidence. Ordinary vulnerability risk acceptance cannot relabel missing evidence as PASS.

A separate governance/policy exception is required if policy permits proceeding without that required control.

## Release behavior

Critical findings block release.

High findings block release unless exceptional explicit risk acceptance is valid.

Exposed secrets, failed security-critical tests, and required assurance controls that failed to execute block a normal release claim.

Never weaken `full` or edit the verification plan merely to obtain green status.

## Evidence retention

For M1/SA1, console and CI logs may be sufficient when durable and attributable.

For higher assurance or releases, prefer machine-readable verification summaries retained with CI/release evidence.

Evidence should record:
- plan/version or commit;
- stage;
- check IDs/capabilities;
- command executed;
- result;
- exit code;
- duration;
- environment/runtime identifiers where material;
- skipped/not-applicable reason.

## Proportionality

The architecture does not require every project to run every control.

Small M1/SA1 software should have a small, real full path.

Higher assurance should add controls because risk/assurance justifies them, not because more tooling looks professional.
## Project-local and GitHub integration

The reference integration copies the dependency-free runner into `.governance/run-verification.py` so CI does not depend on a developer-machine absolute governance path. The copied runner is managed evidence tooling, not an application runtime dependency.

`verification-plan.json` remains the single underlying check definition. A generated GitHub workflow executes that same plan and uploads the machine-readable report.

A project MAY provide `.governance/ci-bootstrap.py` for CI-only environment/tool installation. Bootstrap may prepare the environment; it MUST NOT remove required checks, alter applicability merely for CI convenience, or redefine `full`.

The bootstrap tooling records hashes for the managed runner and workflow. Existing project-owned runners or unrecognized workflows are preserved/refused rather than overwritten silently.



## Schema v2 capability completeness

Full verification is not permitted to infer completeness from configured checks alone. The project plan contains an explicit capability inventory, and the runner compares that inventory to the managed machine baseline.

A full run is `INCOMPLETE_ASSURANCE` when a baseline capability is omitted, a baseline-required capability is downgraded, a conditional capability remains `UNRESOLVED`, a `NOT_APPLICABLE` decision lacks rationale, or a required capability has no full-stage evidence check.

The project may strengthen conditional capabilities to REQUIRED. The runner cannot prove that a human rationale is substantively correct; governance review remains responsible for truthful applicability decisions.

The reference runner resolves the first argv token with `shutil.which()` using the effective PATH before execution. This preserves one logical command across operating systems where package-manager shims differ (for example `npm` / `npm.cmd`).


## Outcome semantics

A nonzero process exit is not automatically the same kind of evidence. The framework distinguishes:

- `PASS`: the check completed successfully;
- `FAIL`: the check completed and produced a failing test/policy/finding outcome;
- `DID_NOT_EXECUTE`: required evidence was not produced because the tool could not be started or could not complete reliably;
- `NOT_APPLICABLE`: the capability itself does not apply, determined separately from tool availability.

The default result policy is intentionally conservative: exit 0 is PASS; every nonzero exit is FAIL.

A check may use `DOCUMENTED_EXIT_CODES` only to identify tool-documented operational-error exit codes. Requirements:
- exit 0 remains the only PASS;
- an explicit durable contract reference is required;
- mapped operational-error codes become `DID_NOT_EXECUTE`;
- every other nonzero code remains FAIL;
- never map a documented finding/policy-failure code to `DID_NOT_EXECUTE`;
- changing result classification for a required security control is a material C2 assurance-policy change and requires review/approval.

Tool crash, initialization failure, certificate-store failure, timeout, missing executable, unavailable service, or unusable scanner output does not prove a finding and does not prove absence of findings. It is missing assurance evidence.

## Approved execution contexts

Checks may identify `LOCAL`, `CI`, and/or `SPECIALIZED` as allowed execution contexts. A required check also declares whether evidence from any one approved context is sufficient (`ANY`) or whether named contexts must each provide evidence.

Execution context does not change capability applicability. A SAST capability that is required but only supported in approved Ubuntu CI remains REQUIRED; it is not `NOT_APPLICABLE` on Windows.

When a required check is intentionally deferred to another approved context, the current single-run report remains `INCOMPLETE_ASSURANCE` until attributable external evidence is combined.

## Evidence aggregation

Cross-environment evidence may be combined only when it is attributable to the same source state and assurance definition. The reference aggregator requires:
- same project;
- same exact Git commit;
- clean-worktree evidence;
- same verification-plan SHA-256;
- same managed assurance-baseline SHA-256;
- same runner SHA-256;
- full-stage reports;
- consistent required-check inventory.

For a check requiring `ANY`, one PASS in an approved context is sufficient unless another attributable execution produced an actual FAIL. For named required contexts, each named context must provide PASS evidence. `DID_NOT_EXECUTE` in one context may be satisfied by PASS evidence from another context only when the plan permits that context and the execution requirement is otherwise met.

Aggregate evidence MUST make a dominant FAIL observable by naming the failed required check and the context(s) that produced the FAIL. A generic bundle failure or unrelated completeness issue MUST NOT conceal an attributable failing execution.

Do not aggregate evidence from different commits, dirty source trees, materially different plans/baselines, or incompatible runner semantics.


## Commit-bound artifact identity

Cross-environment evidence must not depend on platform-specific checkout transformations such as CRLF/LF conversion.

When the repository worktree is clean and a verification artifact is tracked, the reference runner identifies the verification plan, managed assurance baseline, and managed runner from their committed Git `HEAD` bytes. The report also records the actual working-tree SHA-256 for diagnostics.

Evidence aggregation requires the committed identities to match. For each bound artifact, the authoritative comparison is `source`, `repository_path`, and committed `sha256`; `working_tree_sha256` is diagnostic only and MUST NOT make otherwise identical clean Git-bound evidence incompatible. This means ordinary checkout line-ending conversion does not invalidate otherwise identical evidence for the same commit.

If an artifact is dirty, untracked, outside the governed repository, or cannot be resolved from the checked-out commit, its identity falls back to working-tree bytes for local diagnostic evidence. Such evidence is not eligible for cross-environment completion aggregation.

The actual checked-out `HEAD` is the source commit identity. CI event/environment SHAs are metadata and must not override the commit that was actually verified.


## Assurance environment bootstrap

Project CI bootstrap is part of the assurance evidence chain, not an invisible prerequisite outside it.

If environment/bootstrap fails before required checks can run, the canonical report must still be produced when the managed runner is operational. Required checks are recorded as `DID_NOT_EXECUTE` with a bootstrap/precondition failure disposition, and overall status is `INCOMPLETE_ASSURANCE`.

A red CI job without attributable verification evidence is not the desired steady-state behavior when the framework can safely emit a report.

The managed CI orchestrator runs optional project `.governance/ci-bootstrap.py` and then invokes the canonical full runner. On bootstrap failure it invokes the runner in precondition-failure mode so the same commit/plan/baseline/runner identity is retained in evidence.

## Platform-aware assurance tool locking

Do not assume a dependency lock generated on one operating system is universal. Use `assurance/tool-environment-locks.md`.

A platform-only dependency appearing in a lock for a different execution environment is an assurance-tool environment mismatch. Fix lock resolution/selection; do not disable hashes, use floating versions, drop the required control, or call it `NOT_APPLICABLE`.

## Target-aware verification contracts (v0.5.0)

Verification-plan schema v2 remains the context-only contract used by existing governed projects. It is not retroactively changed by target-aware execution.

Verification-plan schema v3 adds optional `execution.required_targets`. A required target contains a coarse context (`LOCAL`, `CI`, or `SPECIALIZED`), an operating system, and optionally a machine architecture. When target requirements are present:

- `ANY` is invalid in `required_contexts`;
- every target context must be allowed;
- the distinct target contexts must exactly equal `required_contexts`;
- duplicate targets are invalid;
- the trusted runner derives the actual target from the requested coarse execution context plus the actual host OS/machine; callers cannot assert OS/machine identity;
- a nonmatching target is `DID_NOT_EXECUTE` with `ENVIRONMENT_MISMATCH`;
- aggregation requires attributable PASS evidence for every required target;
- an attributable FAIL from a required target remains fail-dominant.

Machine aliases are normalized centrally (`AMD64`/`x64`/`x86_64` -> `x86_64`; `arm64`/`aarch64` -> `arm64`). Human-readable labels such as `CI/Windows/x86_64` are derived; structured target objects are authoritative.

Plan v2 execution continues to emit verification-report schema v4. Plan v3 emits report schema v5 with `execution_target` and target-aware per-result evidence. Historical v4 evidence must never be reinterpreted as proving v3 target guarantees. Context-only aggregation remains bundle schema v1; target-aware v5 aggregation emits bundle schema v2. Mixed v4/v5 evidence is rejected.

### Evidence-producer CI and aggregate gate

When complementary platform targets are required, an individual canonical `full` report may truthfully be `INCOMPLETE_ASSURANCE` because checks assigned to another required target are `DID_NOT_EXECUTE`. CI jobs that produce such reports are evidence producers, not the combined release gate. They may complete operationally when a valid canonical report is retained, without rewriting that report's assurance outcome. The aggregate job consumes all expected attributable reports and is the sole combined assurance gate.

Tool/bootstrap failure must not substitute for canonical evidence. CI captures a bounded bootstrap failure, invokes the same runner with `--precondition-failure`, retains `DID_NOT_EXECUTE / PRECONDITION_FAILURE` evidence and `INCOMPLETE_ASSURANCE`, uploads the report, and lets aggregation make the combined decision. If the canonical runner cannot emit a report, evidence production itself failed and no PASS claim is permitted.
