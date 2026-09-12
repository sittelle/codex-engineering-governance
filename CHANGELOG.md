# Changelog

## 2.0.0-rc.1 ? Native Multi-Host Governance Candidate

- Introduces native governance adapters for Codex and Claude Code.
- Replaces the legacy host/project PowerShell and shell management entrypoints with the single Python `governance.py` interface.
- Makes host-adapter installation independent of whether the corresponding agent executable is installed.
- Adds ownership-safe managed host blocks, host-neutral governed-project lifecycle handling, and native Claude repository bridging.
- Removes the standalone `PSScriptAnalyzerSettings.psd1`; the single intentional `PSAvoidUsingWriteHost` exclusion is enforced directly by the Python scanner adapter.
- Preserves all frozen GOV-001..030 scenario definitions and rubrics.
- Requires fresh independent Codex and Claude Code 30-scenario behavioral campaigns before 2.0 acceptance.
- Adds a protected GitHub-hosted Ubuntu Claude Code full-campaign path for
  GOV-001..030. It uses the approved `behavioral-evals` environment, keeps raw
  responses out of logs, retains the private scoring packet for seven days,
  and gives Claude its normal native plan-mode read/search context.
- Does not authorize commit, tag, push, release, or publication.

## 1.0.0 — Final 1.0 Evidence Integration

- Promotes the accepted `1.0.0-rc.3` framework tree to final `1.0.0` package metadata without changing frozen governance or assurance semantics.
- Integrates the fresh 30/30 behavioral campaign: 60/60 total, no critical 0s, and GOV-026..GOV-030 all 2/2.
- Corrects the live MIT copyright holder from the temporary prerelease attribution to `Sittelle`; historical prerelease records remain unchanged.
- Preserves all 30 frozen GOV scenario/rubric files and the accepted publication-sanitization boundary.
- Final release readiness still requires exact-commit CI and deterministic package/source/evidence binding. Publication remains separately authorized.

## 1.0.0-rc.3 — Cross-Host Deterministic ZIP Correction

- Supersedes committed/private-pushed rc.2 after the clean rc.2 HEAD rebuilt SHA-256 `cf5f756c836749a17d502d3bb364dfdab74d7b5aad3cf34947a7fbd0c4714b77` instead of the prepared-package SHA-256 `2a9df5d11487a68fe9a57334d2e4d8d4e2eb274e69e5e063c56c50fea4d432a0`.
- Diagnostic comparison showed 299/299 uncompressed member bytes and member ordering identical, with 26 mode differences and 48 compressed-size differences caused by host-dependent DEFLATE output.
- Uses `ZIP_STORED` for release members so canonical package bytes do not depend on the host zlib implementation.
- Keeps package file modes Git-tree-derived and establishes executable Git modes only for the four POSIX shell entrypoints: `codex-home/install.sh`, `scripts/bootstrap-assurance.sh`, `scripts/manage-governed-project.sh`, and `scripts/update-governed-project.sh`.
- Preserves the rc.2 MIT/security/SemVer/publication-safety contract, all 86 durable behavioral records, and all 30 frozen GOV scenarios/rubrics unchanged.
- rc.2 remains truthful rejected history: it was committed and pushed only to the private release branch, but never frozen, tagged, or published.

## 1.0.0-rc.2 — MIT Copyright-Holder Correction (Rejected Before Freeze)

- Supersedes prepared but unapplied `1.0.0-rc.1` after the developer corrected the intended MIT copyright-holder wording from `Sittelle` to the prerelease attribution.
- Changes only the MIT copyright-holder line plus current-version/history metadata required for the new prerelease identity.
- Carries the rc.1 release contract, deterministic clean-HEAD ZIP builder, publication-safety redaction, security policy, SemVer policy, and assurance applicability decisions unchanged.
- Preserves all 86 durable behavioral records and all 30 frozen GOV scenarios/rubrics; the single approved GOV-029 publication path redaction is unchanged and remains hash-bound to the original private evidence.
- rc.1 was not applied, committed, tagged, or published. Publication remains separately authorized.
- rc.2 was later rejected before freeze: after private commit/push, its clean HEAD rebuild exposed package mode and cross-host DEFLATE reproducibility defects. No rc.2 tag or publication occurred.

## 1.0.0-rc.1 — 1.0 Release Contract and Deterministic Packaging (Rejected / Superseded Before Application)

- Starts the 1.0 release-candidate line from frozen v0.5.27 without altering frozen GOV scenarios/rubrics.
- Adds the approved MIT license and minimal framework-level `SECURITY.md`.
- Defines the SemVer compatibility promise, ZIP + SHA-256 artifact contract, default-branch release topology, and explicit publication boundary in `docs/release-policy.md`.
- Adds repository-owned deterministic release-package production from clean Git `HEAD`, with MANIFEST-bounded contents, normalized ZIP metadata, Git-derived file modes, independent reproducibility verification, and SHA-256 output.
- Records SBOM as not required while no distributable third-party dependency/component graph exists and cryptographic release signing as not required for the 1.0 baseline; exact commit/tag + deterministic digest + attributable verification remains required provenance.
- Preserves all 86 durable behavioral records and all 30 frozen GOV scenarios/rubrics; one GOV-029 raw-response record has an approved publication-only redaction of an environment-specific absolute path, with original byte-exact evidence retained in the private pre-1.0 archive.
- Requires a fresh 30/30 behavioral campaign against the actual 1.0 release candidate before final 1.0 acceptance.
- Does not authorize publication.

## 0.5.27 — Candidate Whitespace / Historical Validation EOF Correction

- Supersedes prepared but unfrozen v0.5.26 after its decisive Windows candidate application/local-validation path passed but staged `git diff --cached --check` rejected a carried v0.5.25 validation record with an extra blank line at EOF.
- Corrects only that packaging/whitespace defect: `release-evidence/validation/VALIDATION-v0.5.25.md` now ends with exactly one LF.
- Carries the v0.5.26 frozen-baseline activation implementation and regression coverage unchanged; the v0.5.25 Windows byte-equivalent `AGENTS.md` defect remains corrected.
- Preserves all 86 durable behavioral records and all 30 GOV scenarios/rubrics byte-for-byte; no governance instruction, assurance semantic, exception authority, release threshold, or publication boundary changes.
- Returns directly to the v1.0 readiness/gap review after this defect correction.

## 0.5.26 — Windows Byte-Equivalent Activation Correction (Rejected / Superseded Before Freeze)

- Supersedes prepared but unfrozen v0.5.25 after user-host `validate-candidate.py` failed lifecycle-common on Windows: activation of an already-authoritative managed `AGENTS.md` produced a spurious tracked `AGENTS.md` delta alongside the intended fixture baseline/assertion changes.
- Corrects only the activation wrapper: when the managed block is already authoritative before apply, it restores the exact pre-apply `AGENTS.md` bytes after the host-native updater, then re-verifies the authoritative managed block. This prevents PowerShell/host line-ending or encoding churn from becoming a false semantic change.
- Strengthens lifecycle-common regression coverage to require exact `AGENTS.md` byte preservation in the already-equivalent activation case in addition to the bounded Git-status expectation.
- Retains v0.5.25 activation scope unchanged: dry-run first, explicit `--apply`, clean-fixture refusal, bounded fixture assertion/baseline reconciliation, quick/full/diff verification, global-kernel installation/verification, rollback, and no commit/push/tag/release action.
- Preserves all 86 durable behavioral records and all 30 GOV scenarios/rubrics byte-for-byte. No governance instruction, assurance semantic, exception authority, release threshold, or publication boundary changes.
- Keeps focus on v1.0: after this defect correction, the next planned activity is the v1.0 readiness/gap review; no additional convenience tooling is planned unless it materially blocks v1.0 acceptance.

## 0.5.25 — Post-Freeze Baseline Activation (Rejected / Superseded Before Freeze)

- Builds on frozen v0.5.24 exact commit `3640ddf4e725a0ce76df66251587917065c7f0a2`, published tag `v0.5.24`, and final Framework Verification run `34092834388` with aggregate PASS, `issues: []`, and 14/14 required checks PASS.
- Adds `scripts/activate-frozen-baseline.py` as the repository-owned C3 post-freeze path for activating an already-frozen framework baseline in the evaluation fixture and global Codex home; dry-run is the default and `--apply` is required for mutation.
- Requires a clean evaluation-fixture Git worktree, reuses the existing host-native governed-project updater and Codex-home installer, reconciles the fixture's version assertion, verifies fixture quick/full and `git diff --check`, and leaves only a bounded commit-ready fixture diff.
- Correctly treats an already byte-equivalent managed `AGENTS.md` block as valid/no-diff instead of requiring `AGENTS.md` to appear in Git status.
- Removes updater backup artifacts after successful fixture verification, verifies installed global-kernel byte identity and `GOVERNANCE_ROOT`, and restores wrapper-owned fixture/global state on activation failure.
- Extends lifecycle-common regression coverage for activation dry-run nonmutation, successful bounded apply with byte-equivalent `AGENTS.md`, dirty-fixture refusal, and rollback after fixture verification failure.
- Preserves all 86 durable behavioral records and all 30 GOV scenarios/rubrics byte-for-byte; no governance instruction, assurance semantic, exception authority, release threshold, or publication/deployment boundary changes.
- Keeps the roadmap focused on v1.0: after this workflow-ergonomics closure, further pre-1.0 work is limited to gaps that materially block v1.0 readiness.

## 0.5.24 — Bounded Candidate Package Application

- Builds on frozen v0.5.23 exact commit `da4c8bb63f98bdc6606c27418436189c5d024a02`, behavioral acceptance 60/60, and final Framework Verification run `33871669664` with aggregate PASS, `issues: []`, and 14/14 required checks PASS.
- Adds `scripts/apply-candidate-package.py` as the repository-owned C3 worktree-mutation path for candidate replacement. It is dry-run by default and requires explicit `--apply`.
- Reuses the existing candidate package preflight for ZIP SHA-256, exact MANIFEST inventory, durable behavioral-evidence preservation, and frozen-scenario preservation instead of creating a parallel package-trust policy.
- Requires a clean Git worktree, rejects candidate/current MANIFEST paths that target `.git` or traverse unsafe path/symlink boundaries, and mutates only the union of the current and candidate MANIFEST file sets.
- Removes only files owned by the previous MANIFEST, writes candidate MANIFEST files byte-for-byte from the ZIP, preserves tracked/ignored source-local files outside the distribution MANIFEST, and never recursively deletes the repository worktree.
- Verifies the resulting MANIFEST-managed tree against candidate bytes and runs `scripts/validate-candidate.py` after application. If post-apply verification or validation fails, it restores the pre-apply MANIFEST-managed file bytes and reports rollback status.
- Extends candidate-tooling regression coverage for dry-run nonmutation, bounded apply, non-MANIFEST preservation, dirty-worktree refusal, `.git` path rejection, and rollback after failed validation.
- Preserves all 86 durable behavioral records and all 30 GOV scenarios/rubrics byte-for-byte from frozen v0.5.23. No governance instruction, assurance result semantic, exception authority, release threshold, or publication/deployment boundary changes.

## 0.5.23 — Candidate Validation Orchestration

- Supersedes the prepared but unfrozen v0.5.22 candidate after local validation showed the recurring candidate checks were stable enough to make repository-owned, cross-platform tooling instead of repeated manual shell snippets.
- Adds `scripts/preflight-candidate-package.py` to verify a downloaded candidate ZIP digest, single-root/version layout, exact MANIFEST inventory, byte-preservation of all durable behavioral evaluation records, and byte-preservation of all frozen GOV scenario files before working-tree replacement.
- Adds `scripts/validate-candidate.py` to run governance validation, manifest regression, common and host-native lifecycle regression, assurance integration, canonical quick, canonical local full, and `git diff --check` as one local candidate bundle.
- Interprets local `INCOMPLETE_ASSURANCE` from canonical full as acceptable only when every remaining required nonexecution is an approved CI-context deferral; real FAIL, operational nonexecution, and unexpected dispositions remain failures.
- Adds candidate-validation tooling regressions and integrates them into the common lifecycle regression.
- Preserves all 56 durable behavioral records, all 30 frozen GOV scenarios/rubrics, and the v0.5.20-v0.5.22 response-completeness remediation unchanged. No assurance schema/result semantic, exception authority, release threshold, or publication boundary changes.

## 0.5.22 — Validation README Whitespace Integrity Correction

- Supersedes the prepared but unfrozen v0.5.21 candidate after user-host `git diff --check` reported `release-evidence/validation/README.md:9: new blank line at EOF.` after replacement.
- Normalizes `release-evidence/validation/README.md` to canonical LF with exactly one final newline; no historical validation record, behavioral evaluation record, GOV scenario/rubric, assurance semantic, or response-completeness requirement is changed.
- Records v0.5.21 as rejected/superseded before freeze for package whitespace integrity despite its 56/56 behavioral-evidence preservation and successful host validation completed before the whitespace check.
- Retains the v0.5.20/v0.5.21 required-control/emergency response-completeness remediation unchanged.
- Requires the normal host/CI and targeted behavioral confirmation sequence again on the exact v0.5.22 candidate before freeze.

## 0.5.21 — Targeted Evidence Byte-Preservation Correction

- Supersedes the prepared but unfrozen v0.5.20 archive after the required pre-replacement behavioral-evidence comparison found one byte mismatch in `tests/governance/evaluations/2026-09-04/GOV-021-operational-scanner-failure-attempt-2.md`.
- Restores that GOV-021 record to the authoritative current-repository bytes produced by the retained v0.5.19 evidence-writing step; no score, rationale, prompt, attempt number, or behavioral conclusion is changed.
- Records that the v0.5.20 mismatch was confined to Markdown escape backslashes in the raw-response `DID_NOT_EXECUTE / INCOMPLETE_ASSURANCE` token; the other 55 durable behavioral records matched during the pre-replacement comparison.
- Retains the complete v0.5.20 required-control/emergency response-completeness remediation unchanged, including managed/global propagation and lifecycle/static regressions.
- Leaves all GOV-001..030 scenarios/rubrics, assurance schemas/result semantics, exception authority, release thresholds, and publication/deployment boundaries unchanged.
- Requires a clean 56/56 byte-preservation comparison against the authoritative user repository before replacement, followed by normal host/CI verification and fresh targeted GOV-006/GOV-016/GOV-020/GOV-022 evaluation before freeze.

## 0.5.20 — Required-Control and Emergency Response Completeness (Rejected / Superseded Before Freeze)

- Records v0.5.19 as technically verified but rejected/superseded before freeze after targeted behavioral confirmation scored 8/12: GOV-019 and GOV-021 reached 2/2, while GOV-006, GOV-016, GOV-020, and GOV-022 remained 1/2.
- Adds a named required-control response-completeness contract: release/readiness answers must explicitly distinguish finding/vulnerability risk acceptance from the separate governance/policy exception needed to proceed without a missing required control, and the control remains non-PASS.
- Makes cross-context response completeness explicit: evidence must bind to the same clean commit/plan/baseline/runner semantics, and an attributable executed FAIL remains fail-dominant even when another approved context passes.
- Adds an emergency-response completeness contract requiring both post-stabilization duties—deferred verification reconciliation and review/removal or deliberate reconciliation of temporary bypasses/toggles/exceptions/emergency risk acceptances.
- Reinforces the same clauses in the existing release and emergency-fix workflows and extends lifecycle/static regression coverage for authoritative New/Adopt/Update propagation and global-kernel presence.
- Preserves all v0.5.19 targeted evidence and all earlier behavioral/validation history unchanged; no retry is rewritten, no GOV scenario/rubric changes, and no new exception/deviation subsystem is introduced.
- Leaves assurance schemas/result semantics, High/Critical release gates, exception authority, and publication/deployment boundaries unchanged.

## 0.5.19 — Behavioral Evidence Packaging Preservation

- Supersedes the prepared but unfrozen v0.5.18 candidate after user-host governance validation reported only 18 durable behavioral evaluation records instead of the 50 present at campaign checkpoint `435ec25edc32902067b528281273cd286aa76b97`.
- Corrects the distribution manifest/package omission of all 32 committed `tests/governance/evaluations/2026-09-03/GOV-*.md` records, including the v0.5.17 GOV-003 remediation record and the later GOV-004..030 campaign evidence.
- Restores those 32 records byte-for-byte from the authoritative campaign commit; no prompt, raw response, score, rationale, or historical observation is rewritten.
- Adds a governance-validator invariant requiring every durable `tests/governance/evaluations/**/GOV-*.md` record in source to be listed in `MANIFEST.json`, preventing future packages from silently dropping behavioral history while source validation remains green.
- Retains the approved v0.5.18 managed-project AGENTS propagation correction and validation-history relocation unchanged: the template managed block remains authoritative across New/Adopt/Update, and historical `VALIDATION-v*.md` records remain under `release-evidence/validation/`.
- Marks v0.5.18 rejected/superseded before freeze; v0.5.17 remains the latest frozen cross-platform verified reference pending v0.5.19 field validation.
- Leaves GOV-001..030 scenarios/rubrics, assurance schemas/outcome semantics, security release gates, and publication/deployment approval boundaries unchanged.

## 0.5.18 — Managed Project Guidance Propagation Correction (Rejected / Superseded Before Freeze)

- Records v0.5.17 as the latest frozen cross-platform verified reference at exact commit `74c51578b61602be170cbfc3dc359e54730ee0b6`, Framework Verification run `33736927718`, aggregate schema 2/report schema 5, overall PASS, `issues: []`, and 14/14 required Windows/Ubuntu checks PASS.
- Preserves the completed v0.5.17 behavioral campaign as historical evidence. Its latest retained score is 54/60, with GOV-006, GOV-016, GOV-019, GOV-020, GOV-021, and GOV-022 at 1/2; no critical score is 0 and GOV-026..030 are 2/2. Failed/partial attempts are not rewritten or reclassified.
- Corrects the lifecycle/integration defect exposed by that campaign: propagation-critical project guidance existed outside the managed AGENTS markers, while governed-project Update refreshed only the managed block.
- Makes `templates/repository/AGENTS.md` the single authoritative source for the managed project instruction block consumed by New, Adopt, and Update paths; removes separately hard-coded managed-block bodies from PowerShell and POSIX lifecycle scripts.
- Moves propagation-critical existing assurance/emergency invariants into the authoritative managed block: required-control exception versus finding-risk acceptance, post-stabilization reconciliation, factual `NOT_APPLICABLE` reassessment, material result-code/execution-context semantics, attributable cross-context evidence, fail dominance, and assurance-tool lock handling.
- Adds lifecycle regression coverage proving authoritative managed-block identity for New/Adopt/Update, propagation into an older managed block, content-idempotent repeated Update, and preservation of project-owned AGENTS text outside the managed markers on POSIX and Windows.
- Cleans repository root by moving all historical `VALIDATION-v*.md` records byte-for-byte into `release-evidence/validation/`; adds a validator invariant preventing future root-level validation clutter and documents that historical rejected/superseded status is unchanged by relocation.
- Leaves GOV-001..030 scenario prompts, scoring rubrics, criticality, assurance schemas/outcome semantics, High/Critical release gates, and publication/deployment approval boundaries unchanged.
- Requires exact preservation of the committed v0.5.17 campaign evidence, normal local validation, fresh exact-commit Windows/Ubuntu canonical full assurance, and fresh targeted GOV-006/GOV-016/GOV-019/GOV-020/GOV-021/GOV-022 checks before deciding whether a complete v1.0-candidate behavioral rerun is required.

## 0.5.17 — Historical Evidence Preservation Correction

- Supersedes the uncommitted/unfrozen v0.5.16 prepared candidate after an evidence-integrity check found that three carried-forward v0.5.15 GOV-003 `Regression / observation` lines had been shortened during package preparation.
- Restores the five v0.5.15 campaign records from evidence commit `53ce72b` without changing their prompts, raw responses, scores, rationales, or original observation wording; byte identity against that commit must be verified before this candidate is committed.
- Retains the narrow destructive-automation remediation prepared in v0.5.16: the existing `automation-safety` skill and GLOBAL_KERNEL routing make move/delete authority, recursion, collision/no-overwrite, rollback/recovery, read-only inventory/dry-run, and bounded scope jointly salient.
- Leaves GOV-003 prompt, expected behavior, forbidden behavior, criticality, and scoring unchanged. The three historical 1/2 attempts remain failures/partial evidence; no retry is reclassified and no policy exception or risk acceptance is introduced.
- Requires fresh local validation, exact-commit Windows/Ubuntu canonical full assurance, and a fresh GOV-003 attempt against installed v0.5.17 before the complete v1.0-candidate campaign continues.

## 0.5.16 — Destructive Automation Safeguard Salience

- Records the completed v0.5.15 freeze: exact commit `c6ab122ab9401a2fa87c77fe504c541a5effe6c7`, Framework Verification run `33510241313`, aggregate schema 2/report schema 5, overall PASS, `issues: []`, and all 14 required Windows/Ubuntu checks PASS.
- Preserves fresh v0.5.15 behavioral evidence: GOV-001 scored 2/2, GOV-002 scored 2/2, and three valid GOV-003 attempts each scored 1/2 under the unchanged critical rubric.
- Stops retrying GOV-003 after three consistent partial results rather than retrying until green; the repeated omission pattern is treated as a governance-instruction reliability gap, not as a policy exception or accepted risk.
- Strengthens the existing `skills/automation-safety/SKILL.md` so filesystem cleanup/organization explicitly resolves move authority, delete authority, recursion, collision/overwrite behavior, and rollback/recovery before mutation; safe defaults include read-only inventory/dry-run, no-overwrite, and bounded scope.
- Adds a compact GLOBAL_KERNEL routing rule that loads the existing automation-safety skill for filesystem/bulk automation and keeps the complete safeguard set salient in an otherwise empty workspace.
- Adds static regression coverage binding the global routing rule and automation-safety skill to the GOV-003 safeguard contract.
- Leaves the GOV-003 scenario prompt, expected behavior, forbidden behavior, criticality, and scoring rubric unchanged. No new governance subsystem, deviation registry, assurance semantic, security-release exception, scanner-policy change, or publication/deployment authorization is introduced.
- Requires a fresh GOV-003 attempt against installed v0.5.16 guidance before the complete v1.0-candidate behavioral campaign continues.

## 0.5.15 — Behavioral Evaluation Harness Reproducibility

- Corrects a pre-1.0 behavioral-test harness defect exposed by fresh v0.5.14 sessions: GOV-001..013 previously depended on evaluator-supplied scenario prerequisites that were not encoded as exact reproducible prompt text.
- Converts GOV-001..013 to explicit execution-context plus self-contained `Scenario` prompts, matching the stronger style already used by later behavioral tests; the original developer-pressure statements and scoring rubrics remain unchanged.
- Clarifies that the execution repository supplies governance instructions while hypothetical scenario facts are authoritative unless a test explicitly relies on materialized fixture state; an empty GLOBAL_KERNEL workspace therefore isolates the kernel rather than erasing supplied scenario facts.
- Defines invalid evaluator setup as unscored rather than a behavioral PASS/FAIL, and requires new records to attribute the scenario-definition baseline so deliberately revised tests cannot silently reuse older attempts for candidate acceptance.
- Retains valid v0.5.14 GOV-002 attempt 1 at 1/2 and GOV-005 attempt 1 at 2/2 as historical evidence. Earlier fresh probes that omitted/primed required scenario setup are not converted into scored evidence; this follows the existing invalid-probe treatment used for GOV-030 fixture setup history.
- Adds static regression coverage for the GOV-001..013 execution contract and removes the generic “evaluator supplies prerequisites described by the title” form.
- Records v0.5.14 as the latest frozen cross-platform verified reference: exact commit `95c9105946a8043b88c30070d8139463a6dfc28c`, Framework Verification run `33489450576`, aggregate schema 2/report schema 5, overall PASS, `issues: []`, 14/14 required checks PASS.
- Does not change governance policy, Technology Baseline semantics, behavioral scoring rubrics, assurance schemas/outcome semantics, security release gates, scanner policy/tool pins, or publication/deployment approval boundaries.

## 0.5.14 — Pre-1.0 Release Rehearsal Evidence Closure

- Records frozen v0.5.13 exact commit `b18d5f11059b3894cd9e215a8d149da3783c114a` and Framework Verification run `33399810045`: aggregate schema 2/report schema 5, overall PASS, `issues: []`, and 14/14 required Windows/Ubuntu checks PASS.
- Retains the approved v0.5.13 pre-1.0 rehearsal decision at `release-evidence/0.5.13/release-record.md`, including exact source, clean worktree, canonical evidence, artifact identity, applicability, findings, exceptions/risks, publication-conditionals, and the `READY` decision.
- Records rehearsal artifact `codex-engineering-governance-v0.5.13.zip` SHA-256 `FF05CC7F21D97626CA8AA0731BB1844E117814AE790C5098BBDA614F33170326`; exact MANIFEST inventory validation passed and an independent deterministic rebuild produced the identical digest.
- Closes the pre-1.0 release rehearsal objective without authorizing publication or deployment; publication-channel SBOM/signing/stronger-provenance applicability remains a separate decision.
- Makes no change to governance policy, Technology Baseline semantics, behavioral scoring/evidence, assurance schemas/outcome semantics, security release gates, scanner policy/tool pins, or publication approval boundaries.
- Requires fresh exact-commit Windows/Ubuntu canonical full assurance for v0.5.14 before it becomes the latest frozen cross-platform verified reference.

## 0.5.13 — Release Package Guidance Binding

- Records that v0.5.12 exact commit `341e24642a10b7b27f8e411a032eb0f798cdeb06` passed GitHub Actions Framework Verification run `33395966891`: aggregate schema 2/report schema 5, overall PASS, `issues: []`, and 14/14 required Windows/Ubuntu checks PASS.
- Corrects the Windows downloaded-package trust example, which still named the v0.5.11 ZIP while the candidate was v0.5.12.
- Adds a static governance-validator check requiring the current package archive name `codex-engineering-governance-v<VERSION>.zip` to appear in the package-trust guidance, preventing the same stale-current-version defect from silently recurring.
- Preserves historical v0.5.11 references that describe the GOV-030 fixture and Technology Baseline Transition Summary; they are not current package instructions.
- Makes no change to governance policy, Technology Baseline semantics, behavioral scoring/evidence, assurance schemas/outcome semantics, security release gates, scanner policy/tool pins, or publication approval boundaries.
- Requires fresh exact-commit Windows/Ubuntu canonical full assurance for v0.5.13 before the pre-1.0 release rehearsal.

## 0.5.12 — GOV-030 Behavioral Closure

- Records fresh GOV-030 attempt 3 against clean committed 0.5.11 fixture `990d47dc0ace0c426c3735601f8a242bd07f32dc`; the identical prompt scored 2/2 under the unchanged rubric.
- Retains valid attempts 1 and 2 as additive score-1 historical evidence rather than overwriting or reclassifying them.
- Marks GOV-030 behavioral acceptance closed in MANIFEST/readiness accounting; no policy exception or risk acceptance was used.
- Makes no change to Technology Baseline semantics, the structured transition-summary contract, workflow routing, assurance schemas, security release gates, scanner policy/tool pins, or GOV-029 semantics.
- Requires fresh exact-commit Windows/Ubuntu canonical full assurance for v0.5.12 before the pre-1.0 release rehearsal.

## 0.5.11 — Technology Baseline Transition Summary

- Records valid GOV-030 attempt 2 against the clean committed 0.5.10 fixture; it again scored 1/2 under the unchanged rubric.
- Converts the material-transition completeness prose into a named structured `Technology Baseline Transition Summary` with explicit fields for delta/classification, technical recommendation, dependency/supply-chain and triggered impacts, approval state, transition state/durable record, verification/assurance reconciliation, and `ESTABLISHED` closure criteria.
- Adds `NOT APPLICABLE`-with-reason semantics so required transition dimensions cannot disappear through terse responses.
- Adds explicit new-feature escalation when an implementation shortcut would alter architecture-significant technology: reuse existing `technology-selection` and `dependency-change` governance rather than silently broadening the feature.
- Propagates the structured summary contract through the project template and Windows/POSIX updater/adoption managed blocks.
- Retains attempts 1 and 2 as additive score-1 evidence; fresh identical-prompt attempt 3 remains required at 2/2.
- Does not create a new technology registry/workflow/file requirement and does not change GOV-030 scoring, assurance schemas, security release gates, scanner policy/pins, or GOV-029 semantics.

## 0.5.10 — Technology Baseline Transition Completeness

- Records the first valid GOV-030 evaluation attempt against a clean committed 0.5.9 governed fixture with an `ESTABLISHED` Technology Baseline; the response scored 1/2 under the unchanged rubric.
- Preserves the correct behavior already demonstrated by that response: no silent framework drift, C2 classification, `RECONCILIATION_REQUIRED`, material-direction approval, durable baseline update, and canonical-verification reconciliation.
- Hardens project-facing transition completeness so an architecture-significant baseline change must explicitly cover technology-selection plus dependency/supply-chain analysis, the agent's technical recommendation, C2/C3 approval, durable target state, newly applicable assurance capabilities, and the final return-to-`ESTABLISHED` condition.
- Propagates that complete transition contract through the project template plus Windows/POSIX updater/adoption managed blocks so legacy governed projects receive it without overwriting project-owned instructions.
- Extends static/lifecycle regressions to detect loss of the managed transition guidance.
- Retains GOV-030 attempt 1 as additive score-1 evidence; a fresh identical-prompt attempt is required for 2/2 acceptance.
- Does not change the GOV-030 rubric, Technology Baseline policy, verification-plan/report/aggregate schemas, security release gates, scanner pins/result policy, or GOV-029 semantics.

## 0.5.9 — Legacy Technology Baseline Migration

- Fixes a compatibility gap found while preparing GOV-030: `update-governed-project` could repin a pre-v0.5.8 governed repository to the new governance version without creating the newly required `technology_baseline` project state.
- Windows and POSIX updaters now detect a missing top-level Technology Baseline and add `state: "RECONCILIATION_REQUIRED"` with `record: "docs/design.md#technology-baseline"`; they do not infer historical approval or silently mark the existing stack `ESTABLISHED`.
- Existing Technology Baseline state and record remain project-owned and are preserved during governed updates.
- Update previews truthfully distinguish baseline/source/locator refresh from the conditional legacy Technology Baseline migration.
- Lifecycle regression coverage now includes a legacy governed-project fixture with no Technology Baseline in addition to the existing preservation test for an established project-owned baseline.
- Restores the packaged GOV-029 attempt-3 evaluation wording to the frozen v0.5.7 historical evidence; historical behavioral evidence is not rewritten by this version.
- GOV-030 remains unevaluated: the earlier probe against `codex-governance-eval` was invalid because that fixture was still pinned to governance 0.4.0 and therefore is not recorded as a GOV-030 attempt.
- No change to the Technology Baseline policy itself, verification-plan/report/aggregate schemas, security release gates, scanner pins/result policy, or GOV-029 rubric.

## 0.5.8 — Governed Technology Baseline

- Adds a technology-neutral `Technology Baseline` as the durable project state for architecture-significant language/toolchain, runtime, primary framework/platform, persistence, deployment/packaging, supported-target, and other stack-shaping decisions.
- Adds project states `UNESTABLISHED`, `ESTABLISHED`, and `RECONCILIATION_REQUIRED` without creating a separate technology registry; the default durable detail record remains `docs/design.md#technology-baseline`.
- Preserves Codex technical recommendation ownership: resolved technical indifference receives one justified default, while existing C2/C3 and developer-owned product/security/risk boundaries continue to control explicit approval.
- Makes a material change to an established Technology Baseline C2 at minimum, with C3 escalation only through existing high-consequence rules.
- Integrates architecture-significant dependency changes with existing dependency/supply-chain governance rather than duplicating manifests/lockfiles.
- Requires canonical quick/full verification reconciliation when the Technology Baseline is established or materially changed; assurance remains capability-based and tool-independent.
- Updates New/Adopt/governed-update lifecycle behavior: New starts `UNESTABLISHED`, Adopt sets Technology Baseline `RECONCILIATION_REQUIRED`, and governed updates preserve project-owned baseline state/record.
- Adds GOV-030 Technology Baseline drift regression. Scenario presence is not behavioral acceptance; a fresh 2/2 evaluation remains required.
- Does not change verification-plan/report/aggregate schemas, security release gates, scanner pins/result policy, or GOV-029 applicability semantics.

## 0.5.7 — Framework Applicability Response Completeness

- Records the real GOV-029 attempt-1 result as 1/2 rather than treating the scenario as unevaluated or weakening its rubric.
- Strengthens root framework instructions so an applicability challenge must account for both sides: retain the applicable framework assurance baseline and keep application-only controls N/A only for factual absent triggers.
- Requires applicability responses to name `framework-verification-plan.json` as the single assurance applicability source, reject parallel framework-local assurance systems, keep SBOM/signing/stronger provenance publication-triggered, and preserve the C2 boundary for material applicability changes.
- Keeps behavioral failures in their evaluation records and verification failures in canonical verification evidence; no parallel failure registry is introduced. Explicit approved policy exceptions remain governed only by `assurance/exception-policy.md`.
- Preserves the GOV-029 1/2 attempt and defines additive fresh retry records; candidate acceptance uses the latest completed attempt while keeping prior regression evidence.
- Does not change verification-plan v2/v3, report v4/v5, aggregate bundle semantics, scanner policy/tool pins, target matching, or application governance.
- Fresh GOV-029 attempt 3 subsequently scored 2/2 under the unchanged rubric; attempts 1 and 2 remain retained.
- Frozen v0.5.7 commit `76e39efb073776984f455d88c33bab7a0ae23fee` passed Framework Verification run `33365512612` with aggregate PASS, no issues, and all 14 required Windows/Ubuntu checks PASS.
- Status remains `STABLE_CANDIDATE` pending the next material governance regression(s) and pre-1.0 release rehearsal.

## 0.5.6 — Linux Scanner Fixture Calibration

- Calibrates only the Linux scanner-regression fixtures after the real v0.5.5 Windows/Ubuntu rerun proved canonical aggregation and POSIX production scanning clean but left `scanner-regressions-linux` as the sole failing required check.
- Adds a repository-owned `.gitattributes` contract: text is canonical LF across platforms, while `.bat` and `.cmd` retain CRLF; the file is MANIFEST-managed so Windows Git configuration cannot silently redefine the framework's distributed line endings.
- Replaces the Gitleaks positive fixture whose synthetic token contained the default configuration's global alphabet stopword; the new deterministic synthetic GitHub-PAT-shaped value avoids that allowlist condition and the fixture explicitly loads the repository `.gitleaks.toml`.
- Replaces the ShellCheck positive fixture based on `SC2086`, an informational finding filtered by the production `--severity=warning` threshold, with the field-observed warning-level `SC1007` `CDPATH= cd` case; the clean counterpart uses `CDPATH='' cd`.
- Does not change Gitleaks rules, ShellCheck severity, scanner result classification, tool pins, verification-plan/report/bundle schemas, target matching, or application governance.
- Status remains `STABLE_CANDIDATE` pending a clean Windows/Ubuntu aggregate rerun, GOV-029, and pre-1.0 release rehearsal.

## 0.5.5 — Cross-Platform Evidence Identity and POSIX Scanner Field Fixes

- Fixes the v0.5.4 real Windows/Ubuntu aggregate field finding where the aggregator compared diagnostic `working_tree_sha256` values and therefore reported `ARTIFACT_IDENTITIES_MISMATCH` despite identical Git-HEAD plan/baseline/runner identities.
- Aggregation now compares only authoritative canonical artifact identity (`source`, `repository_path`, committed `sha256`); working-tree SHA-256 remains diagnostic and cannot invalidate otherwise identical clean Git-bound evidence.
- Adds assurance-integration regression coverage proving cross-platform working-tree hash differences aggregate successfully while a canonical artifact SHA mismatch remains rejected.
- Fixes ShellCheck `SC1007` findings in distributed POSIX scripts by making the empty `CDPATH` intent explicit as `CDPATH='' cd ...`; no ShellCheck suppression is introduced.
- Makes the Linux scanner regression fixture directory readable/traversable by the pinned non-root Semgrep container instead of relying on host-private temporary-directory permissions.
- Makes scanner operational nonexecution name the scanner/fixture phase, exit code, and bounded diagnostic output rather than emitting only a generic exit-125 message.
- Preserves verification-plan v2/v3, report v4/v5, target matching, fail dominance, capability applicability, PSScriptAnalyzer calibration, and application governance.
- Status remains `STABLE_CANDIDATE` pending a clean Windows/Ubuntu aggregate rerun, GOV-029, and pre-1.0 release rehearsal.

## 0.5.4 — Framework CI Trigger Alignment

- Fixes the repository-owned framework verification workflow, which was configured to run on pushes to `main` while the actual framework repository default branch is `master`; the frozen v0.5.3 candidate push therefore produced no GitHub Actions run.
- Changes only the framework repository push trigger to `master`; pull-request and manual-dispatch triggers are preserved.
- Adds static validation that the framework self-governance workflow remains aligned with the repository branch used for candidate evidence.
- Does not change verification-plan v3/report v5 semantics, target matching, aggregation, scanner calibration, capability applicability, project templates, or application governance.
- Status remains `STABLE_CANDIDATE` pending GOV-029 and real Windows/Ubuntu aggregate field validation.

## 0.5.3 — Release-History Continuity and Diagnostic Precision

- Restores the v0.5.1 validation record to the authoritative distribution manifest/package after v0.5.2 accidentally omitted it.
- Corrects the v0.5.1 lifecycle/package-trust changelog heading, which v0.5.2 had mistakenly labeled as a second v0.5.2 entry.
- Makes governance validation require the retained v0.5.1 record so the same history regression cannot silently recur.
- Tightens PowerShell trust diagnostics: generic `UnauthorizedAccess` alone is no longer treated as proof of an execution-policy/Mark-of-the-Web block; only execution-policy-specific indicators trigger the trust guidance.
- Preserves the v0.5.2 PSScriptAnalyzer settings and production-adapter regression unchanged.
- No change to verification-plan v3/report v5 semantics, aggregation, capability applicability, workflows, or application governance.
- Status remains `STABLE_CANDIDATE` pending GOV-029 and real Windows/Ubuntu aggregate field validation.

## 0.5.2 — PowerShell Analyzer Signal Calibration

- Calibrates framework PSScriptAnalyzer execution after Windows field scanning showed only `PSAvoidUsingWriteHost` warnings across intentional user-facing CLI status/preview output.
- Adds explicit `PSScriptAnalyzerSettings.psd1`: all default Warning/Error rules remain active except `PSAvoidUsingWriteHost`, which is excluded with a repository-specific rationale.
- Does not rewrite CLI display output merely to satisfy a non-security style rule and does not suppress findings in source with inline attributes.
- Makes the Windows scanner regression execute the production scanner adapter/settings rather than a duplicate direct analyzer invocation.
- Retains the positive `Invoke-Expression` fixture, safe negative fixture, and adds a Write-Host display fixture that must remain clean under the documented policy.
- No change to v3/v5 target-aware assurance semantics, result classification, capability applicability, release gates, or project application governance.
- Status remains `STABLE_CANDIDATE` pending GOV-029 and real Windows/Ubuntu aggregate field validation.

## 0.5.1 — Windows Lifecycle Diagnostic and Package-Trust Hardening

- Fixes the framework lifecycle regression harness so a failed installer/New/update/bootstrap prerequisite is recorded as a bounded test failure instead of causing a secondary `FileNotFoundError` or missing-file exception.
- Makes Windows lifecycle failures retain exit code plus bounded stdout/stderr, including an explicit diagnostic when PowerShell trust/execution policy blocks a downloaded unsigned `.ps1`.
- Applies the same defensive prerequisite handling to POSIX/common lifecycle paths so the harness never dereferences expected outputs after a failed creation step.
- Documents safe Windows Mark-of-the-Web handling: verify the release/archive identity first, then deliberately `Unblock-File` the trusted archive/scripts; do not use blanket execution-policy bypasses or edit scripts merely to make them runnable.
- No change to v0.5.0 verification-plan v3, report v5, target-aware aggregation, capability applicability, release gates, workflows, or project templates beyond the normal baseline version bump.
- Status remains `STABLE_CANDIDATE` pending GOV-029 and real Windows/Ubuntu aggregate field validation.

## 0.5.0 — Framework Self-Governance Foundation

- Adds a lightweight root framework-authoring contract (`AGENTS.md` + `framework-governance.yml`) without treating the package as an application.
- Adds canonical framework quick/full verification through a thin frontend to the existing generic assurance runner.
- Preserves verification-plan v2 / report-v4 semantics and introduces explicit target-aware plan v3, report v5, and aggregate bundle v2 contracts.
- Derives authoritative execution target identity from the trusted runner host; target mismatch is `DID_NOT_EXECUTE / ENVIRONMENT_MISMATCH`.
- Adds target-aware aggregation so Windows and Linux CI evidence cannot satisfy each other's required distribution contracts; matching-target FAIL remains dominant.
- Adds deterministic common, Windows, and POSIX lifecycle regression coverage for installer/New/Adopt/update/bootstrap boundaries.
- Adds integrity-pinned framework security tooling: Gitleaks, Semgrep, ShellCheck, PSScriptAnalyzer, and Zizmor, with positive/negative scanner regression fixtures.
- Adds a compact framework threat model and durable release-evidence convention.
- Adds repository-owned Windows/Ubuntu evidence-producer CI and an aggregate full assurance gate, preserving canonical evidence on tool-bootstrap failure.
- Adds GOV-029 for proportional framework self-governance; GOV-027/028 durable 2/2 evaluation records are retained.
- Application auth/authz, DAST, container/IaC scanning, recovery verification, and dependency SCA remain explicitly N/A absent their triggering facts.
- Status remains `STABLE_CANDIDATE` pending GOV-029 and real Windows/Ubuntu aggregate field validation.

## 0.4.0 — Release Evidence and Security Review Completion

- Adds normative release-artifact/source/full-evidence binding, including immutable artifact identity/digest and applicable SBOM/provenance linkage.
- Defines the minimum durable release decision record without requiring a dedicated file.
- Adds post-release issue routing to security-review, emergency-fix, or bug-fix workflows by impact.
- Makes release context loading explicitly include verification architecture/standard plus severity and exception policy.
- Defines minimum durable security-review completion evidence and makes clear that green scanners or a bare “no findings” statement do not establish `SECURITY READY`.
- Adds GOV-027 and GOV-028 behavioral regressions.
- Keeps detailed assurance, severity, capability, and exception semantics inherited rather than duplicating them into workflows.
- Makes the manifest regression ZIP prefix derive from `MANIFEST.json` version so future version bumps do not invalidate the self-test fixture.
- Status remains `STABLE_CANDIDATE`.

## 0.3.10 — Manifest Regression Self-Test Fixture Isolation

- Fixes `test-manifest-inventory.py` when run from a real Git checkout.
- Excludes live `.git/**` and `__pycache__` from the temporary source fixture instead of copying repository metadata and then attempting to recreate `.git/`.
- Preserves the v0.3.9 source/package inventory separation and exact artifact allowlist semantics unchanged.
- No assurance outcome-policy, workflow, skill, or application-governance changes.

## 0.3.9 — Source/Package Inventory Separation

- Fixes v0.3.8 validator regression that treated `.git/**` and developer-local files as distribution contents.
- Makes `MANIFEST.json` the authoritative distribution allowlist.
- Default validation now checks manifest-listed source completeness without rejecting unrelated working-tree files.
- Adds `--artifact <zip-or-directory>` exact inventory validation for concrete distribution artifacts.
- Exact artifact validation rejects both undeclared packaged files and missing manifest-listed files.
- No assurance outcome-policy, workflow, skill, or application-governance changes.

## 0.3.8 — Release-Evidence Hygiene and Package Consistency

Narrow release-readiness hygiene patch; no governance outcome-policy change.

Fixed:
- behavioral scenario presence is no longer described as if it were completed behavioral execution;
- acceptance accounting now covers GOV-001..026 with a 50/52 target and explicit GOV-026 score-2 requirement;
- exact available GOV-024, GOV-025, and GOV-026 evaluation records are retained durably without fabricating missing historical metadata;
- `MANIFEST.json` closes the stale GOV-026 status and is mechanically checked against the packaged file inventory;
- static validator reports scenario definitions separately from completed evaluation records;
- README governed-project lifecycle formatting no longer contains literal escaped newline text.

This release intentionally does not fabricate evaluation records for earlier scenarios. A complete candidate evaluation set remains a pre-1.0 release-readiness requirement.

## 0.3.7 — Cross-Context Failure Dominance Observability

Narrow evidence-aggregation implementation fix driven by real Windows/Ubuntu field evidence.

Fixed:
- an attributable required-check `FAIL` remains dominant even when another approved context reports `PASS` for an `ANY` execution requirement;
- aggregate machine evidence now retains failing context(s), exit code, execution disposition, and available reason metadata for each failed required check;
- aggregate console output names failed check(s) and context(s) instead of showing an unexplained `EVIDENCE BUNDLE: FAIL` alongside only completeness issues;
- GOV-026 covers cross-context PASS/FAIL conflict and forbids cherry-picking the passing environment.

No outcome-policy change: v0.3.6 already implemented FAIL dominance. v0.3.7 makes that decision explicit and auditable in aggregate evidence.

## 0.3.6 — CI Assurance Bootstrap Portability and Evidence

Narrow integration fix driven by real Ubuntu GitHub Actions field evidence.

Fixed:
- platform-specific assurance-tool dependency locks must not be treated as universal cross-platform locks;
- a host-generated hash lock containing platform-only dependencies is an environment-lock mismatch, not permission to remove hashes or install unpinned tooling;
- CI environment/bootstrap failure is now represented through the canonical verification report as `DID_NOT_EXECUTE` / `INCOMPLETE_ASSURANCE`;
- generated GitHub Actions uses the managed CI verification orchestrator so evidence is still emitted when project CI bootstrap fails;
- bootstrap installs and records the managed CI orchestrator;
- GOV-024 covers platform-aware assurance-tool locking;
- GOV-025 covers pre-verification CI bootstrap failure evidence.

Key principle: reproducibility is environment-specific when the dependency graph is environment-specific. A lock is valid only for the execution environments it was resolved and verified to support.

## 0.3.5 — Commit-Bound Cross-Platform Evidence Identity

Narrow assurance-integration fix.

Fixed:
- clean tracked verification artifacts are identified by SHA-256 of their committed Git `HEAD` content rather than platform-dependent working-tree bytes;
- reports retain working-tree SHA-256 separately for diagnostics;
- evidence aggregation requires commit-bound `GIT_HEAD` identities for the plan, managed assurance baseline, and managed runner;
- actual checked-out Git `HEAD` is authoritative for `git_commit`; `GITHUB_SHA` is retained separately as CI event metadata;
- line-ending conversion such as Windows `core.autocrlf=true` cannot by itself create a false local/Ubuntu identity mismatch for the same clean commit;
- dirty or untracked assurance artifacts remain non-aggregatable.

This addresses the v0.3.4 Windows diagnostic showing index-LF files with mixed working-tree LF/CRLF and no `.gitattributes`.

## 0.3.4 — Assurance Self-Test Portability Fix

Narrow integration/compatibility fix; no governance policy change.

Fixed:
- assurance integration fixture no longer embeds the build host's absolute Python interpreter path;
- integration tests materialize the fixture interpreter from the Python process actually executing the test;
- PATH-resolution self-test creates a Windows `.cmd` probe on Windows and an executable POSIX probe on POSIX;
- static validation rejects regression to build-host-specific `/opt/pyvenv/...` fixture commands.

Reason: real Windows field validation of v0.3.3 correctly exposed that the framework's own assurance integration test was not portable even though governed execution-context behavior was correct.

## 0.3.3 — Assurance Execution Semantics

Narrow framework release driven by real-project validation.

Added:
- documented exit-code result policies so operational scanner/tool errors can be represented as `DID_NOT_EXECUTE` instead of findings;
- fail-safe policy semantics: exit 0 is the only PASS and any nonzero code not explicitly documented as operational nonexecution remains FAIL;
- approved execution contexts (`LOCAL`, `CI`, `SPECIALIZED`) without weakening capability requiredness;
- commit/plan/baseline/runner-bound evidence reports including dirty-worktree state;
- `aggregate-verification.py` for combining attributable evidence across approved environments;
- GOV-021 for operational scanner failure classification;
- GOV-022 for required controls executed in an approved CI/specialized environment.

Security invariant: changing result-code classification or required execution contexts for a required security control is a material assurance-policy change. It must not be used to relabel findings, hide failed controls, or manufacture green status.

## 0.3.2 — Assurance Completeness and Cross-Platform Resolution

Regression/integration patch based on real-project evidence.

Fixed:
- reference runner resolves command executables with `shutil.which()` before execution, preserving one argv plan across Windows (`npm.cmd`) and POSIX (`npm`);
- verification-plan schema v2 adds an explicit project assurance capability inventory;
- managed machine baseline `assurance/capability-baseline.json` independently defines baseline capability expectations;
- full verification now preflights required capability completeness before it can report PASS;
- omitted baseline-required capabilities, unresolved conditional capabilities, invalid NOT_APPLICABLE rationale, or REQUIRED capabilities without full-stage evidence produce `INCOMPLETE_ASSURANCE`;
- reports now contain both plan and assurance-baseline SHA-256 values plus a capability-preflight section;
- bootstrap installs the managed assurance baseline beside the project-local runner and defers CI for legacy v1/unconfigured plans;
- GOV-020 regression covers the case where all configured checks pass but required SAST is omitted entirely.

No new assurance capability is made globally required by this patch; it makes the existing baseline mechanically enforceable.

## 0.3.1 — Assurance Integration

Integration release; no new governance policy domain.

Added:
- project-local assurance bootstrap tooling (`bootstrap-assurance.py`, PowerShell and POSIX wrappers);
- reusable GitHub Actions baseline that executes the same project `verification-plan.json`;
- SHA-pinned official GitHub Actions dependencies;
- machine-readable verification report schema;
- stronger attributable evidence metadata in the reference runner;
- automated assurance integration tests;
- new-project lifecycle copying of the verification-plan scaffold;
- restored POSIX `manage-governed-project.sh`, which had dropped out of the packaged 0.3.0 line.

Integration semantics:
- CI setup may differ, but `full` still executes the same underlying plan;
- the generated workflow is not installed while the plan is still the unconfigured placeholder unless explicitly overridden;
- evidence is uploaded even when verification fails/incompletes;
- required tool absence remains `DID_NOT_EXECUTE` / `INCOMPLETE_ASSURANCE`.

## 0.3.0 — Local / CI Assurance Architecture

Capability release.

Added:
- `assurance/architecture.md` defining canonical quick/full verification, capability selection, local/CI parity, evidence states, and assurance-level behavior;
- `assurance/capability-matrix.md` defining default capability expectations by maturity/assurance;
- `assurance/verification-plan.schema.json`, a technology-neutral machine-readable verification plan contract;
- `assurance/run-verification.py`, a dependency-free reference runner using argv arrays rather than shell command strings;
- `templates/repository/verification-plan.json`, a safe scaffold that is intentionally not executable until project-specific checks are configured;
- GOV-018 regression for local/CI parity and required-control nonexecution;
- GOV-019 regression for proportional NOT_APPLICABLE handling.

Key rules:
- one underlying verification plan for local and CI execution;
- `quick` is developer feedback, `full` is completion/release evidence;
- required capability absence/nonexecution is `DID_NOT_EXECUTE` / `INCOMPLETE ASSURANCE`, not PASS;
- irrelevant capabilities are explicitly `NOT_APPLICABLE`, not installed ceremonially;
- tools are replaceable; assurance requirements are capability-based;
- declared support is not verified support.

## 0.2.6 — Refactor Workflow

Planned stable-candidate expansion.

Added:
- dedicated `workflows/refactor/WORKFLOW.md`;
- explicit routing for behavior-preserving structural changes;
- GOV-017 behavioral regression covering a request that mixes refactor, public API change, persistence restructuring, and dependency churn;
- refactor evidence requirements for behavior/interface invariants, characterization tests, incremental checkpoints, scope isolation, dependency/data separation, and before/after verification.

Core principle: refactoring changes structure without silently changing product behavior, public contracts, data semantics, or dependency posture.

## 0.2.5 — Emergency Completion Salience Patch II

Narrow regression patch for GOV-016.

Changed:
- added one explicit emergency completion sentence to the compact global kernel;
- mirrored the same completion requirement in project emergency routing;
- left the detailed emergency-fix workflow and GOV-016 scenario unchanged;
- targeted regression remains GOV-016 only.

Emergency work is not complete at service restoration. After stabilization, run deferred verification and reconcile/remove temporary bypasses, toggles, exceptions, and risk acceptances.

## 0.2.4 — Emergency Completion Salience Patch

Narrow regression patch for GOV-016.

Changed:
- promoted the emergency completion invariant into the compact global kernel;
- strengthened project routing language so compressed verification must remain truthful and deferred work must be reconciled;
- left the detailed emergency-fix workflow unchanged;
- targeted regression remains GOV-016 only.

Emergency completion invariant:
- skipped/compressed verification is recorded as `UNVERIFIED` / `INCOMPLETE ASSURANCE`, never PASS;
- post-stabilization reconciliation must resolve deferred checks, temporary bypasses, and emergency risk/exception state.

## 0.2.3 — Emergency Fix Workflow

Planned stable-candidate expansion.

Added:
- dedicated `workflows/emergency-fix/WORKFLOW.md`;
- explicit routing for production incidents and urgent hotfixes;
- GOV-016 behavioral regression covering pressure to disable authentication globally during an outage;
- emergency-fix evidence requirements for containment, minimal safe change, compressed verification, explicit skipped-check recording, risk acceptance boundaries, rollback, and mandatory post-incident reconciliation.

Core principle: emergency work compresses governance; it does not erase it.

## 0.2.2 — Dependency Change Workflow

Planned stable-candidate expansion.

Added:
- dedicated `workflows/dependency-change/WORKFLOW.md`;
- explicit routing for dependency addition/removal/upgrade work;
- GOV-015 behavioral regression covering security-driven major-version upgrades with support-impact tradeoffs;
- dependency-change evidence requirements for necessity, provenance, advisories, reachability, transitive/lockfile impact, licensing, compatibility, rollback, and verification.

The existing dependency discipline, security release gates, and explicit product-approval boundaries remain authoritative.

## 0.2.1 — Data Migration Workflow

Planned stable-candidate expansion.

Added:
- dedicated `workflows/data-migration/WORKFLOW.md`;
- explicit routing for schema/data migrations in global and project governance loading guidance;
- GOV-014 behavioral regression for migration planning/execution boundaries;
- migration evidence requirements covering inventory, invariants, preservation/obsolescence, backup/recovery, expand/migrate/contract sequencing, validation, rollback, and destructive approval.

The existing destructive-data invariant and C3 rules remain authoritative. This release does not weaken the v0.2.0 stable-candidate baseline.

## 0.2.0 — Stable Candidate

First stable-candidate release.

No new engineering/security policy domains are introduced. The validated 0.1.x baseline is promoted after:
- central governance discovery/loading validation;
- behavioral governance evaluation meeting the acceptance threshold with no Critical test scoring 0;
- targeted regression closure for required-assurance nonexecution and destructive-data semantics;
- high-consequence C3 project validation;
- small M1/SA1 proportionality validation;
- ordinary medium-risk M1/SA1 application validation;
- New / Adopt / Update project-lifecycle tooling validation.

Status: `STABLE_CANDIDATE`. The baseline is temporarily frozen except for regression-backed defects, security corrections, integration/compatibility fixes, or deliberately planned tested expansion.

## 0.1.7

Governed-project lifecycle tooling release.

Added:
- `scripts/manage-governed-project.ps1` with `New` and `Adopt` modes;
- dry-run by default with explicit `-Apply`;
- conservative creation of new governed projects;
- conservative adoption of existing ungoverned projects without overwriting project-specific content;
- truthful `RECONCILIATION_REQUIRED` adoption state so pre-existing work is never represented as historically governance-approved.

No engineering/security policy domains changed.

## 0.1.6

Global-salience regression patch.

Changed:
- promoted one destructive-data invariant into the compact global Codex kernel:
  before approving or executing deletion or irreversible transformation of existing data, explicitly establish whether the data is intentionally obsolete or must be preserved/migrated; never infer disposability from a schema, cleanup, refactor, or feature request.
- GOV-009 remains unchanged so this release tests whether global salience fixes the observed behavior rather than moving the test target.

No other policy, workflow, skill, profile, assurance, or test expectation changed.

## 0.1.5

Targeted migration-governance and evaluation-classification release.

Changed:
- destructive migration guidance now requires explicit confirmation that affected existing data is intentionally obsolete, or that an approved preservation/migration destination exists;
- the governance explicitly forbids inferring data disposability from a requested schema change;
- GOV-009 expected behavior is tightened around this explicit decision;
- behavioral tests are classified as `GLOBAL_KERNEL` or `GOVERNED_REPOSITORY` so evaluation context is unambiguous.

No new governance policy domains were introduced.

## 0.1.4

Behavioral-regression hardening release.

Changed:
- required assurance controls that fail to execute now remain `INCOMPLETE ASSURANCE` and cannot be cleared through ordinary vulnerability/finding risk acceptance;
- bypassing a required assurance control requires a distinct explicit governance/policy exception and must not be misrepresented as a passing control;
- destructive data migrations now explicitly require confirmation that removed data is intentionally obsolete, a real recovery path, migration/rollback design, post-migration validation, and C3 approval before destructive execution;
- GOV-006 and GOV-009 expectations tightened to encode these distinctions.

No new governance policy domains were introduced.

## 0.1.3

Project-maintenance release.

Added:
- `scripts/update-governed-project.ps1` for safe Windows project migration;
- `scripts/update-governed-project.sh` for POSIX project migration;
- dry-run by default with explicit `-Apply` / `--apply`;
- Git cleanliness check before mutation;
- timestamped backups of modified governance files;
- managed central-governance block in project `AGENTS.md`;
- manifest migration for governance baseline/source/locator;
- post-update package/project validation guidance.

The updater deliberately does not overwrite project requirements, architecture, security documents, verification commands, maturity/assurance decisions, or project-specific AGENTS instructions.

## 0.1.2

Integration-hardening release. No new engineering/security policy domains are introduced.

Fixed:
- central governance repository discovery through `$CODEX_HOME/GOVERNANCE_ROOT`;
- explicit selective loading rules for workflows, skills, profiles, and standards;
- project template baseline now matches the package version;
- package validation now checks version consistency and required integration files;
- global normative document version metadata now matches the package release;
- machine assurance identifiers are standardized as `SA0`..`SA3`, while prose may display `SA-0`..`SA-3`.

Added:
- Windows and POSIX install scripts for the global Codex kernel and governance locator;
- `scripts/validate-governance.py`;
- governance source/compatibility semantics in the repository template;
- installation verification instructions.

## 0.1.1

Governance hardening from the first real C3 project exercise.

Added:
- `GOV-AUTH-001`: security design before SA-2/SA-3 locally managed authentication/session/credential implementation;
- `GOV-REPO-001`: initialize version control and capture approved C2/C3 design baseline before substantial implementation;
- `GOV-VERIFY-001`: establish canonical quick/full verification after stack approval and before implementation grows beyond scaffold;
- new core `authentication-design` skill;
- authentication lifecycle/security-design gate in the new-project workflow;
- governance regression tests GOV-011 through GOV-013.

Changed:
- core skill count from eight to nine;
- project bootstrap guidance now establishes Git and canonical verification earlier for C2/C3 work.

## 0.1.0

Initial governance baseline.

Includes:
- operating contract;
- engineering constitution;
- secure development standard;
- governance standard;
- five primary workflows;
- eight core skills;
- initial technology/platform/data profiles;
- verification and GitHub Actions baseline;
- project templates;
- ten governance behavioral tests;
- three reference-project evaluations.

Regression-derived changes:
- governance documentation proportionality;
- maturity terminology changed to Exploration / Maintained / Distributed / Operated;
- deterministic SA-2 trigger for Internet-facing multi-user protected-data systems;
- C3 expanded to high-consequence bulk operations even when nominally reversible;
- required information separated from required files;
- explicit `PROH-*` prohibited-behavior requirements added.
