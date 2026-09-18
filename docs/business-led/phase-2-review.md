# Phase 2 review packet — business-led mode

Prepared per section 9 of `docs/business-led/implementation-plan.md`. Covers
phases 0 through 2 (WS1, WS2, WS3, WS4) on `feature/business-led-mode`,
branched from `master` at `4d2957f075411fd860e310aabeb3d904f4b710ad`
(release 2.0.0). This is the review gate: phases 3–5 do not start until the
maintainer has reviewed this packet.

## 1. Commits

32 commits, each verified with `python scripts/verify-framework.py quick`
before the next, oldest first:

1. `d0d375f` docs: add business-led mode implementation plan and management description
2. `32f1db6` docs: add ADR for business-led mode three-layer architecture
3. `3c4f930` docs: extend framework threat model for business-led mode
4. `d30636d` docs: draft business-led mode registration contract
5. `c0aa44f` fix: verify_project compares managed blocks byte-for-byte
6. `023a5c1` feat: write governance-artifact integrity manifest per project
7. `181f049` feat: runner preflight for governance-artifact integrity and instruction surfaces
8. `e04335f` feat: pin released assurance-baseline hashes and verify them at three points
9. `3e10586` feat: add governance self-protection rule to the operating kernel
10. `3deb0d6` test: add GOV-031 and GOV-032 governance self-protection scenarios
11. `0aec4c0` test: add governance-integrity regression to canonical full verification
12. `dff88d9` feat: classify agent runtime configuration changes as C2/C3
13. `c910fb5` feat: add declared platform_controls block to the project template
14. `ca41953` docs: record host policy surface verification for WS2
15. `8573c1c` feat: add governance.py hook pre-tool for PreToolUse enforcement
16. `ca9053b` feat: add Claude Code managed-settings templates (inform/block)
17. `30579ff` feat: report managed policy presence and mode in host status/verify
18. `5df0ec8` feat: enforce GOVERNANCE_MIN_VERSION and record CI enforcement mode
19. `892969a` feat: add GitLab pipeline policy template, update GitHub template
20. `1a0d7ca` feat: add Codex managed-configuration templates (inform/block)
21. `328d89a` fix: correct governance_owned_yaml_block over-matching bug
22. `b6e0d1f` feat: add governance.mode and roles to the project template
23. `65ca281` docs: define business-led mode approval authority and routing outcomes
24. `c44d702` feat: route Amber/Red business-led emergencies to IT Security
25. `68d1d62` feat: route business-led mode decisions in every remaining workflow
26. `1a43c43` docs: incorporate maintainer's business/IT-security risk split into the plan
27. `130e3b6` feat: reconcile business-led risk routing with the BUSINESS/IT_SECURITY split
28. `b9b799f` feat: business-led plain-language kernel and project AGENTS.md, mode-aware rendering
29. `b60e1c6` feat: registration contract, sealing, and assurance-fact derivation
30. `221f077` feat: add governance.py project readiness packet
31. `d3c13f1` docs: record internal distribution as a release-signing reassessment trigger
32. `c3d05cc` feat: add governance.py project validation-checklist

## 2. `full` output at current head

Run locally on Windows (this development machine); no Linux runner is
available in this environment, so the Linux-required checks are recorded as
they were reported: `DID_NOT_EXECUTE`, never as passed.

```
[governance-static]        -> PASS
[python-compile]           -> PASS
[manual-behavioral-campaign-kit] -> PASS
[assurance-integration]    -> PASS
[governance-integrity]     -> PASS   (new check, WS1)
[manifest-package]         -> PASS
[lifecycle-common]         -> PASS
[lifecycle-windows]        -> DID_NOT_EXECUTE (assigned to CI)
[lifecycle-posix]          -> DID_NOT_EXECUTE (assigned to CI)
[scanner-regressions-linux]   -> DID_NOT_EXECUTE (assigned to CI)
[scanner-regressions-windows] -> DID_NOT_EXECUTE (assigned to CI)
[secret-scan]               -> DID_NOT_EXECUTE (assigned to CI)
[sast-python]                -> DID_NOT_EXECUTE (assigned to CI)
[sast-posix]                 -> DID_NOT_EXECUTE (assigned to CI)
[sast-powershell]            -> DID_NOT_EXECUTE (assigned to CI)
[workflow-security]          -> DID_NOT_EXECUTE (assigned to CI)

OVERALL: INCOMPLETE_ASSURANCE
```

This is the identical set of `DID_NOT_EXECUTE` results present before any
business-led-mode work started (confirmed at the end of phase 0 and
re-confirmed here): every CI-only check was already CI-only in 2.0.0's
`framework-verification-plan.json`, unchanged by this work. The two new
local-executable checks this work added — `governance-integrity`
(commit 11) and the `governance-integrity`-adjacent assertions inside
`assurance-integration` — both PASS. No new `DID_NOT_EXECUTE` or `FAIL` was
introduced. CI (Linux + Windows) evidence for the CI-only checks is
`DID_NOT_EXECUTE` locally by design and remains to be produced by an actual
CI run on this branch, which the implementing agent did not trigger (no
push/PR was made; see section 6).

## 3. New and changed files, by workstream

**Phase 0 (ADR, threat model, registration draft):**
`docs/adr/0001-business-led-mode-architecture.md` (new),
`docs/framework-threat-model.md` (modified: threats 9–12, new assets/actors),
`docs/business-led/registration-contract-draft.md` (new, superseded in
content by WS4's `assurance/registration.schema.json`, kept as the
design-history record).

**WS1 (governance artifact integrity):**
`governance.py` (`verify_project` byte comparison,
`write_integrity_manifest`, `governance_owned_yaml_block` + fix),
`assurance/run-verification.py` (`governance_integrity_preflight`,
`instruction_surface_audit`, `release_baseline_preflight`),
`assurance/release-baseline-hashes.json` (new),
`assurance/verification-report-v5.schema.json` (new optional fields),
`host-adapters/operating-kernel.md` (self-protection section),
`codex-home/AGENTS.md` (regenerated rendering),
`scripts/bootstrap-assurance.py` / `scripts/build-release-package.py`
(release-hash enforcement), `scripts/test-governance-integrity.py` (new),
`framework-verification-plan.json` (new check), `tests/governance/GOV-031*`
and `GOV-032*` (new) plus their wiring in `scripts/validate-governance.py`,
`scripts/manual-behavioral-campaign.py`, `tests/governance/README.md`,
`TEST-CONTEXTS.json`, `TEST-CONTEXTS.md`.

**WS2 (enforcement on the managed client and in CI):**
`docs/business-led/host-policy-surface-verification.md` (new),
`host-adapters/claude/` (new: `README.md`, `managed-settings.inform.json`,
`managed-settings.block.json`), `host-adapters/codex/` (new: `README.md`,
`requirements.inform.toml`, `requirements.block.toml`), `governance.py`
(`hook pre-tool`, `managed_policy_status`, `host status`/`verify` output),
`templates/gitlab/governance-pipeline-policy.yml` (new),
`templates/github/governance-verify.yml` (modified: min-version/enforcement
variables), `assurance/run-ci-verification.py` (min-version check,
`ci_enforcement` annotation), `global/operating-contract.md` (agent runtime
configuration boundary), `templates/repository/project-governance.yml`
(`platform_controls` block).

**WS3 (role model and business-led mode):**
`templates/repository/project-governance.yml` (`governance.mode`, `roles`),
`global/governance-standard.md` (business-led approval-authority section,
routing outcomes, request records), `templates/repository/docs/governance/requests/REQUEST-template.md`
(new), all nine `workflows/*/WORKFLOW.md` (business-led routing notes),
`templates/repository/docs/risk/accepted-risks.md` (risk classification
field), `host-adapters/operating-kernel.business-led.md` (new),
`templates/repository/AGENTS.business-led.md` (new), `governance.py`
(mode-aware rendering throughout, `project validation-checklist`).

**WS4 (registration contract, drift detection, readiness):**
`assurance/registration.schema.json` (new),
`templates/repository/registration.yml` (new), `governance.py`
(`registration seal`, registration parsing/validation/fact-derivation,
`project new|adopt --registration`, `project readiness`),
`docs/release-policy.md` (internal-distribution trigger note).

**Not built (phase 3+, out of scope for this packet):**
`semgrep/capabilities/<language>.yml`, `scripts/run-registration-conformance.py`,
acceptance-criteria-to-test traceability for `validation-checklist` (WS7).

## 4. Existing fixtures and GOV scenarios: confirmed byte-identical

```
git diff --quiet master..HEAD -- 'tests/governance/GOV-0[0-2][0-9]*.md' 'tests/governance/GOV-030*.md'
# exit 0 — no difference

git diff --quiet master..HEAD -- tests/assurance/ tests/governance/evaluations/ \
  tests/governance/REGRESSION-v0.1.4.md tests/governance/REGRESSION-v0.1.5.md tests/governance/REGRESSION-v0.1.6.md
# exit 0 — no difference
```

GOV-001 through GOV-030 and every existing evaluation record, regression
fixture, and assurance test fixture are byte-identical to the 2.0.0
baseline. The only files touched under `tests/` are the two new scenarios
(GOV-031, GOV-032) and their wiring (`README.md`, `TEST-CONTEXTS.json`,
`TEST-CONTEXTS.md`).

Professional-mode behavior: verified continuously, not just at the end.
Every commit that touched shared code (`governance.py`,
`assurance/run-verification.py`, `assurance/run-ci-verification.py`) was
followed by `scripts/test-management.py --mode common`,
`scripts/test-framework-lifecycle.py --mode common`, and
`scripts/test-assurance-integration.py`, all of which exercise the
professional-mode-only path and none of which required a single
modification to pass. Schema v2 plans / report schema v4 are explicitly
covered by `scripts/test-governance-integrity.py`'s
`test_v2_plan_unaffected_by_tampering`, which applies every tamper case used
against schema v3 and confirms the v2/v4 report carries neither new field.

## 5. Assumptions (plan section 11)

All six treated as CONSTRAINT throughout; none proved false during
implementation:

- **GitLab primary, GitHub secondary** — held. `templates/gitlab/governance-pipeline-policy.yml`
  was built before updating `templates/github/governance-verify.yml`, per
  the stated fallback order.
- **Both Claude Code and Codex in scope** — held. Both hosts have managed
  policy surfaces, both got full templates (managed-settings.json /
  requirements.toml), and `governance.py hook pre-tool` is shared between
  them since both hosts confirmed the same `hookSpecificOutput` JSON
  contract.
- **Registration arrives as a file; IT Security fills it by hand** — held.
  `governance.py registration seal` exists exactly because no registration
  tool exists yet, matching the stated fallback.
- **A curated package proxy exists** — not exercised. Nothing in phases 0–2
  depended on it; WS5 (phase 4) is where dependency-existence guidance would
  actually use it.
- **The managed client gives the employee no administrative rights** — held
  as a design assumption throughout (it is why Layer 1 controls are trusted
  at all), not independently verified since no actual managed client exists
  to test against in this environment.
- **Professional mode keeps its current approval model** — held. See
  section 4's continuous-regression evidence.

## 6. Open questions and known risks

**OPEN QUESTION — host-client end-to-end behavior not verified.** Every
piece of hook logic and every managed-settings/requirements template was
verified by direct invocation (`governance.py hook pre-tool` fed real JSON
on stdin, including through an actual shell invocation of the exact command
string the templates register) and by static validation (JSON/TOML parsing,
required markers, cross-template diffing). What was **not** verified: an
actual Claude Code or Codex client, with the managed-settings/requirements
template applied, actually invoking the hook and actually denying a tool
call. This environment has no live host client to test against. This is the
same limitation the plan already anticipates for behavioral campaigns
(section 10: manual, not run by the implementing agent) and should be
treated the same way — a managed test-client verification step for phase 5,
not something claimed as done here.

**OPEN QUESTION — interactive `governance.py` menu not extended.** The
parameterized CLI (`governance.py project new --mode ... --registration
...`, `governance.py host install --kernel-mode ...`) is fully wired. The
interactive menu (`governance.py` with no arguments) still creates
professional-mode projects and installs the professional kernel only; it
was not extended to prompt for mode/registration/kernel-mode. Anyone using
business-led mode must use the parameterized CLI. Flagging this rather than
silently leaving a gap; low risk since IT Security's own tooling would
invoke the parameterized form, but worth a deliberate decision rather than
an oversight.

**KNOWN RISK — Claude Code has no documented global memory/subagent-cap
setting.** Recorded in `docs/business-led/host-policy-surface-verification.md`
and `host-adapters/claude/README.md`. `strictPluginOnlyCustomization`
narrows but does not eliminate this gap.

**KNOWN RISK — Codex has no documented file-path write-deny mechanism.**
Only `deny_read` is documented; there is no confirmed equivalent of Claude
Code's `permissions.deny` `Edit()`/`Write()` rules. Recorded in
`host-adapters/codex/README.md`. The compensating control (WS1's
governance-integrity preflight, surfaced through the same hook) is real but
detects after the fact rather than preventing the edit.

**KNOWN LIMITATION — `validation-checklist` has no acceptance-criteria
traceability.** Stated in the command's own output (`note` field), not just
here: WS7 (phase 4) is what would link checklist items to the same
acceptance criteria the automated tests trace to. Today's checklist is
generated from the registration's `purpose` and capability flags only.

## 7. Deviations from the plan, and why

- **Registration schema gained a `purpose` field not in the phase-0
  draft.** Discovered while building `validation-checklist`
  (commit 32, `c3d05cc`): the plan's WS3 text requires generating the
  checklist "from the registered purpose," but neither the phase-0 draft
  nor the WS4 schema (built earlier, commit 29) had a `purpose` field. Added
  it to the schema, template, and `parse_registration`/`validate_registration`
  rather than leaving `validation-checklist` unable to do what its own
  deliverable text requires.
- **The maintainer revised the plan mid-implementation** (commit 26,
  `1a43c43`): risk acceptance changed from a single "everything awaits IT
  Security" model to a two-tier BUSINESS/IT_SECURITY classification, and the
  registration was reframed as a living document the agent proactively
  updates rather than a one-time form. This was found as an on-disk change
  to `docs/business-led/implementation-plan.md` and
  `management-description.md` not made by the implementing agent, mid-session, without a git commit already covering
  it. Read in full, accepted as the current direction (the "note above the
  frame" guidance: a changed-on-disk file is usually deliberate), and the
  already-built WS3 work reconciled with it in the following commit
  (`130e3b6`). Flagging clearly here in case this understanding of the
  revision's authorship is wrong.
- **WS7's schema/runner parts were not built**, despite the plan's
  permissive "may be built here because they touch the same files as WS4"
  (section 7's phase table). Read as optional, not required; given the
  volume of phase-0–2 work, deferred entirely to phase 4 where WS7 already
  belongs, rather than partially building a workstream that is not yet
  approved for implementation as a whole.
- **A real bug was found and fixed mid-session, not just avoided**
  (commit 21, `328d89a`): `governance_owned_yaml_block`'s regex used
  DOTALL, so it matched from `governance:` to the end of the file instead of
  just the block. This was caught because adding the `mode` field (commit
  22) made the over-match visible (the extracted "block" printed the whole
  rest of the file). Before the fix, WS1's own integrity check would have
  flagged *any* edit to `project-governance.yml` — including ordinary
  project-owned fields — as tampering. Fixed in both copies of the function
  (`governance.py` and `assurance/run-verification.py`, which must stay
  byte-identical since one hashes what the other re-verifies), with a
  dedicated regression test (`test_project_owned_field_edit_is_not_flagged`)
  added the same commit.

## 8. What phase 3 inherits

The registration contract, drift-detection hook points
(`governance_integrity_preflight`, `instruction_surface_audit`), and the
`block` enforcement mode are all real and working; phase 3's job is to make
`instruction_surface_audit`'s business-led comparison exact (today it only
checks "does a registration exist," per the documented placeholder in
`assurance/run-verification.py`) by building the actual capability-detection
rules (`semgrep/capabilities/<language>.yml`) and
`scripts/run-registration-conformance.py`, and to run the false-positive
review against three real repositories the plan calls for.
