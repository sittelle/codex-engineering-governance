# Source Notes

The governance is tool-independent. Volatile implementation/profile guidance should be revalidated periodically.

Current Codex documentation (checked 2026-08-24) confirms:
- global guidance may live in `~/.codex/AGENTS.md`;
- project guidance is discovered from project root down to current working directory;
- closer files override earlier guidance;
- `AGENTS.override.md` takes precedence within a directory;
- the project instruction-chain size defaults to 32 KiB;
- code-review rules can live in the closest applicable `AGENTS.md`.

See:
https://learn.chatgpt.com/docs/agent-configuration/agents-md

OpenAI model guidance also recommends favoring lean prompts and testing prompt changes against representative evaluations:
https://developers.openai.com/api/docs/guides/latest-model

Security/tool implementation candidates in v0.1 are defaults, not policy requirements:
- Gitleaks: secrets
- Semgrep Community Edition: SAST
- OSV-Scanner: dependency vulnerability analysis


## Codex instruction loading note

Current OpenAI material describes user instructions as including `AGENTS.override.md` / `AGENTS.md` from `$CODEX_HOME`, followed by project-root-to-working-directory instruction files subject to the configured size limit. v0.1.2 therefore keeps the global kernel small and uses an explicit locator for detailed governance rather than trying to inject the entire governance repository into AGENTS.md.


## Project updater

The project updater is deliberately a local file migration utility. It does not interpret or approve project security/business decisions; version-specific migrations requiring such decisions remain workflow-driven.
## GitHub Actions baseline references (v0.3.1)

Checked 2026-08-27 against the official GitHub action repositories:

- `actions/checkout` v7.0.1 — `3d3c42e5aac5ba805825da76410c181273ba90b1`
- `actions/setup-python` v7.0.0 — `5fda3b95a4ea91299a34e894583c3862153e4b97`
- `actions/upload-artifact` v7.0.1 — `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`

Official repositories:
- https://github.com/actions/checkout
- https://github.com/actions/setup-python
- https://github.com/actions/upload-artifact



## Framework security-tool pins (v0.5.0)

Checked during v0.5.0 design against official/current project release information where available. The machine-readable authoritative pins are in `tools/framework-tools.lock.json`.

- Gitleaks 8.30.1 — official Linux x64 release archive SHA-256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`.
- ShellCheck 0.11.0 — Linux x86_64 archive SHA-256 `8c3be12b05d5c177a04c29e3c78ce89ac86f1595681cab149b65b97c4e227198`.
- Semgrep CE 1.172.0 — Linux container manifest pinned by immutable OCI digest in the tool lock; local repository rules are version controlled.
- PSScriptAnalyzer 1.25.0 — PowerShell Gallery package SHA-256 `14E634C828EB98EFB9F40B2918BA90F139ED5ECCDF663A2A747736D996995D60`.
- Zizmor 1.28.0 — Linux x86_64 archive SHA-256 `e87b67160194884e375a46a12c57ccc904f762b53845f254fab7f17d98809c09`; 1.28.0 was selected instead of vulnerable 1.27.0.

The framework CI also uses full commit-SHA pins for `actions/checkout`, `actions/setup-python`, `actions/upload-artifact`, and `actions/download-artifact`.

## PSScriptAnalyzer repository settings (v0.5.2)

Windows field validation of v0.5.1 showed that the framework's real PowerShell surface was reported only for `PSAvoidUsingWriteHost`, a Warning-level scripting-style rule. The framework PowerShell scripts intentionally use host-only status/preview output as CLI user interface. v0.5.2 therefore uses an explicit repository settings file that excludes only this rule while retaining all other default Warning/Error rules.

Microsoft documents both explicit settings files (`IncludeRules` / `ExcludeRules`) and `PSAvoidUsingWriteHost` as a Warning-level rule intended to distinguish host-only display from pipeline output. The security-relevant `PSAvoidUsingInvokeExpression` rule remains enabled and is exercised by the framework's production-adapter regression fixture.

References checked 2026-08-28:
- https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/using-scriptanalyzer?view=ps-modules
- https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/rules/avoidusingwritehost?view=ps-modules
- https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/rules/avoidusinginvokeexpression?view=ps-modules


## Release-history continuity (v0.5.3)

v0.5.3 restores `release-evidence/validation/VALIDATION-v0.5.1.md` to the authoritative distribution history after the v0.5.2 package accidentally omitted it. Historical validation records are release evidence and must not disappear from later packages merely because the current patch does not modify their underlying behavior.


## Framework CI branch alignment (v0.5.4)

The framework repository self-verification workflow is repository-specific and is intentionally aligned to the current `master` branch used for candidate evidence. The generic governed-project GitHub Actions template is not changed by this patch; project repositories may have different branch policies.


## v0.5.5 field-evidence note

The first real v0.5.4 Windows/Ubuntu aggregate run proved that the authoritative Git-HEAD SHA-256 identities for `framework-verification-plan.json`, `assurance/capability-baseline.json`, and `assurance/run-verification.py` were identical while Windows working-tree byte hashes differed because of checkout normalization. v0.5.5 therefore enforces the architecture's existing rule that committed identity governs aggregation and working-tree hashes are diagnostic only.

The Ubuntu run also reported only ShellCheck `SC1007` for the `CDPATH= cd ...` idiom. v0.5.5 expresses the intended environment assignment as `CDPATH='' cd ...` rather than suppressing the analyzer. The Linux scanner regression's exit-125 path is made diagnostic and its Semgrep temporary fixture tree is explicitly traversable by the pinned non-root container.

## v0.5.6 Linux scanner-fixture calibration

The real v0.5.5 Ubuntu producer completed all production Linux scanners but showed that two positive regression fixtures were miscalibrated rather than that the scanner policies were weak.

Gitleaks 8.30.1's generated default configuration includes `abcdefghijklmnopqrstuvwxyz` as a global stopword, while its GitHub PAT rule matches `ghp_` followed by 36 alphanumeric characters with entropy >= 3. The prior fixture embedded the alphabet sequence and was therefore intentionally filtered. v0.5.6 uses a deterministic non-stopword synthetic PAT-shaped value and explicitly loads the repository `.gitleaks.toml`.

ShellCheck's `--severity=warning` option considers only error/warning findings; informational/style findings are filtered. The prior positive fixture relied on unquoted-variable `SC2086`, which is informational in ShellCheck 0.11.0. v0.5.6 instead uses the `SC1007` `CDPATH= cd` warning observed by the real v0.5.4 Ubuntu production scan, with `CDPATH='' cd` as the clean counterpart.

References checked 2026-08-28:
- https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/config/gitleaks.toml
- https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/cmd/generate/config/rules/github.go
- https://github.com/koalaman/shellcheck/blob/master/shellcheck.1.md
- https://www.shellcheck.net/wiki/SC1007
- https://www.shellcheck.net/wiki/SC2086

## Validation-package whitespace integrity (v0.5.22)

After the v0.5.21 replacement passed the required 56/56 behavioral-evidence byte comparison and initial host validation, `git diff --check` reported an extra blank line at EOF in `release-evidence/validation/README.md`. The project versioning rule treats a prepared-version correction as a new version rather than a silent revision.

v0.5.22 therefore normalizes only that README to canonical LF with one final newline and updates ordinary current-version/accounting metadata. Historical validation records, all 56 behavioral evaluation records, GOV scenarios/rubrics, assurance semantics, and the v0.5.20/v0.5.21 response-completeness remediation are unchanged.

## Behavioral evidence byte preservation (v0.5.21)

The required pre-replacement comparison of the prepared v0.5.20 archive against the authoritative current repository found exactly one behavioral-record byte mismatch: the packaged v0.5.19 GOV-021 attempt-2 raw response contained Markdown escape backslashes around underscores where the retained repository record did not. The other 55 durable behavioral evaluation records matched.

v0.5.21 corrects only that evidence-carry-forward defect and version/accounting metadata. It deliberately does not reinterpret the response, rescore the attempt, or alter the v0.5.20 response-completeness policy changes. The authoritative repository record remains the source of historical evidence truth.

## Response-completeness salience correction (v0.5.20)

v0.5.20 is grounded in the retained v0.5.19 targeted behavioral evidence rather than a new assurance mechanism. The four remaining partial scenarios all made safe top-level decisions but omitted one already-governed explanatory obligation: GOV-006/GOV-020 omitted the distinction between finding-risk acceptance and a missing-control governance/policy exception; GOV-016 omitted explicit review/removal of temporary emergency measures after stabilization; GOV-022 omitted cross-context fail dominance.

The correction therefore adds compact response-completeness contracts to the global kernel and authoritative managed project block and reinforces the same obligations in the existing release/emergency workflows. Assurance schemas, result semantics, exception authority, scenario prompts/rubrics, and release thresholds remain unchanged.

## Behavioral evidence packaging preservation (v0.5.19)

v0.5.19 makes durable behavioral evaluation records distribution-required evidence: every `tests/governance/evaluations/**/GOV-*.md` source record must be listed in `MANIFEST.json`. This closes the packaging gap that allowed the prepared v0.5.18 archive to pass source validation while omitting the 32 committed 2026-09-03 campaign records.
## Candidate validation orchestration (v0.5.23)

The repeated candidate field-validation sequence is deterministic enough to be repository-owned tooling rather than chat-provided shell snippets. v0.5.23 therefore adds a pre-replacement package/evidence preflight and a post-replacement local validation bundle. The scripts orchestrate existing validators and canonical verification; they do not create a parallel assurance source, redefine PASS/FAIL semantics, or replace exact-commit CI aggregation.

`preflight-candidate-package.py` treats the current repository as the authoritative source for historical behavioral evidence and frozen GOV scenario bytes. `validate-candidate.py` consumes canonical full JSON evidence and accepts local `INCOMPLETE_ASSURANCE` only for approved CI-context deferrals.

## Bounded candidate package application (v0.5.24)

The v0.5.23 field-validation cycle showed that package preflight and post-replacement validation were deterministic, but the actual worktree replacement was still supplied as ad-hoc PowerShell that recursively removed everything except `.git`. That approach also exposed an execution-control weakness in interactive shells: a thrown guard error did not reliably prevent later pasted commands from continuing.

v0.5.24 therefore makes candidate application a repository-owned C3 operation. `apply-candidate-package.py` reuses the existing package preflight, computes the exact transition from the current MANIFEST to the candidate MANIFEST, defaults to dry-run, requires explicit `--apply`, and refuses dirty tracked or non-ignored untracked state. It deletes only files owned by the previous MANIFEST, never recursively deletes the worktree, preserves files outside the distribution MANIFEST, forbids targeting `.git`, verifies candidate bytes after mutation, and runs `validate-candidate.py`. A failed post-apply check triggers restoration of the pre-apply MANIFEST-managed file bytes.

This is workflow safety/ergonomics rather than a new assurance source. The preflight remains authoritative for package/evidence/scenario preservation, `validate-candidate.py` remains authoritative for the local candidate bundle, and exact-commit CI aggregation remains required for freeze.

## 1.0 release-contract baseline (1.0.0-rc.3)

The 1.0 release candidate intentionally stops the 0.5.x feature loop. The remaining changes are release-contract/publication controls: MIT licensing, security reporting expectations, SemVer compatibility, deterministic package production, explicit SBOM/signing/provenance applicability, and publication-safe distribution.

The public lineage is intentionally allowed to begin at the accepted sanitized 1.0 baseline rather than exposing private pre-1.0 Git history. Historical governance/evaluation truth needed for assurance remains in the distribution; the private archive retains the original development provenance.

rc.3 also closes the release-production defect exposed by the clean rc.2 commit: DEFLATE output was not cross-host byte-stable and the prepared archive carried executable modes that were not present in the Git tree. Release ZIP members therefore use `ZIP_STORED`, while executable metadata is derived from committed Git modes.

## Candidate whitespace correction (v0.5.27)

v0.5.27 supersedes prepared but unfrozen v0.5.26 after the latter passed its decisive Windows activation/application validation but failed staged whitespace checking because `VALIDATION-v0.5.25.md` carried an extra blank line at EOF. The correction is limited to normalizing that historical validation-record EOF and current-version accounting; the v0.5.26 activation implementation is unchanged.

This is packaging hygiene, not a new capability. After v0.5.27, work returns directly to the v1.0 readiness/gap review.

## Windows byte-equivalent activation correction (v0.5.26)

User-host v0.5.25 candidate application correctly rolled back after lifecycle-common exposed a Windows-specific false delta: the managed `AGENTS.md` block was already authoritative, but the PowerShell updater rewrote the file with host-native encoding/line-ending behavior and Git reported `AGENTS.md` as modified. The activation semantics were correct; the byte-preservation boundary was incomplete.

v0.5.26 keeps the v0.5.25 activation design and adds one narrow invariant: if the managed block is authoritative before apply, restore the exact original `AGENTS.md` bytes after the updater and verify the authoritative block again. This prevents representation-only churn without masking a real managed-block change. Lifecycle-common now asserts exact byte preservation for that case.

This is a defect correction, not another ergonomics feature. After v0.5.26, work returns directly to the v1.0 readiness/gap review.

## Post-freeze activation orchestration (v0.5.25)

The v0.5.24 freeze/activation sequence showed that candidate preflight/application/local validation were repository-owned, but activating the newly frozen baseline in the evaluation fixture and global Codex home still depended on a long ad-hoc PowerShell wrapper. That wrapper also assumed `AGENTS.md` must appear in the fixture diff, even when the v0.5.24 managed block was intentionally byte-identical to v0.5.23.

v0.5.25 adds `activate-frozen-baseline.py` as a narrow C3 orchestration layer over the existing governed-project updater and Codex-home installer. It does not define new governance or assurance semantics. Dry-run is non-mutating; apply requires a clean fixture, reconciles the evaluation fixture's baseline assertion, validates managed-block equivalence, runs fixture quick/full and whitespace checks, constrains the commit-ready diff, installs/verifies the global kernel, and rolls back wrapper-owned state on failure. Publication/tag/release creation remains outside this tool.

This is intentionally the final ergonomics closure before the v1.0 readiness review. Further pre-1.0 work should address only material readiness defects/gaps.
