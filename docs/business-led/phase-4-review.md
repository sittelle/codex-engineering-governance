# Phase 4 review — business-led mode

Prepared per the same pattern as the phase-2 and phase-3 packets, on
`feature/business-led-mode`. Covers phase 4 as scoped by section 7's phase
table: WS5 (normative content for AI-specific failures), WS6 (proportionality
and hygiene), WS7 (test regulation and coverage definition), and GOV-031 to
GOV-036. GOV-031/032 were actually built in phase 1 (WS1 self-protection);
this phase's scenario work is GOV-033 through GOV-036.

## 1. Commits

10 commits, each verified with `python scripts/verify-framework.py quick`
before the next, oldest first:

1. `a5c815e` test: add GOV-033 to GOV-035 AI-specific untrusted-context scenarios
2. `5061d2c` feat: add untrusted-context principle for embedded/AI-specific instructions
3. `50af320` feat: add vcs-safety skill
4. `c1c39ff` feat: add hallucinated-package defense and has_license_policy fact
5. `8f53813` feat: add project-template .gitleaks.toml and .pre-commit-config.yaml
6. `6000925` feat: add kernel/managed-block token budget check; fix Codex-only wording
7. `1080de1` feat: define tests capability satisfaction criteria and expand testing-strategy
8. `f3be69b` feat: add coverage-floor diagnostics (schema v3/v5 only)
9. `a6b11f3` feat: heuristic automated-test presence in the validation checklist
10. `10c51db` test: add GOV-036 acceptance-criteria-to-test-traceability scenario

## 2. `full` output at current head

Run locally on Windows; no Linux runner is available in this environment.
Identical `DID_NOT_EXECUTE` profile to phases 2 and 3 for every CI-only
check — no new `DID_NOT_EXECUTE` or `FAIL` introduced by this phase.

```
[governance-static]              -> PASS
[python-compile]                 -> PASS
[manual-behavioral-campaign-kit] -> PASS
[assurance-integration]          -> PASS
[governance-integrity]           -> PASS
[registration-conformance]       -> PASS
[coverage-semantics]             -> PASS   (new check, this phase)
[validation-checklist-heuristic] -> PASS   (new check, this phase)
[manifest-package]               -> PASS
[lifecycle-common]                -> PASS
[lifecycle-windows]               -> DID_NOT_EXECUTE (assigned to CI)
[lifecycle-posix]                 -> DID_NOT_EXECUTE (assigned to CI)
[scanner-regressions-linux]       -> DID_NOT_EXECUTE (assigned to CI)
[scanner-regressions-windows]     -> DID_NOT_EXECUTE (assigned to CI)
[secret-scan]                     -> DID_NOT_EXECUTE (assigned to CI)
[sast-python]                     -> DID_NOT_EXECUTE (assigned to CI)
[sast-posix]                      -> DID_NOT_EXECUTE (assigned to CI)
[sast-powershell]                 -> DID_NOT_EXECUTE (assigned to CI)
[workflow-security]               -> DID_NOT_EXECUTE (assigned to CI)

OVERALL: INCOMPLETE_ASSURANCE
```

The phase's exit criterion "coverage semantics fixtures pass on both
platforms" is confirmed on Windows only here; POSIX execution is
`DID_NOT_EXECUTE` locally by design (no Linux runner in this environment)
and remains to be produced by an actual CI run, same as every other
CI-only check throughout this branch.

## 3. New and changed files, by workstream

**WS5 (normative content for AI-specific failures):**
`global/secure-development-standard.md` (new "Untrusted context and
embedded instructions" section), both kernel variants (compact always-loaded
version of the same principle), `skills/vcs-safety/SKILL.md` (new),
`workflows/dependency-change/WORKFLOW.md` and `skills/dependency-review/SKILL.md`
(hallucinated-/typosquatted-package existence-and-authenticity step,
lockfile-only installs), `has_license_policy` fact (template/framework
plans, `capability-matrix.md`; `capability-baseline.json` itself
deliberately not touched, see section 5), `skills/testing-strategy/SKILL.md`
(one-sentence WS5 addition; WS7 expands it fully), `templates/repository/.gitleaks.toml`
and `.pre-commit-config.yaml` (new, wired into `governance.py`'s
`template_paths()`/`apply_project_new()`), `tests/governance/GOV-033*`
through `GOV-035*` (new) and their wiring.

**WS6 (proportionality and hygiene):** token-budget check in
`scripts/validate-governance.py` for both kernels and both managed AGENTS.md
blocks (character-count proxy, generous headroom, confirmed to actually
fire); a single pointer from the kernel's cross-context assurance sections to
`assurance/architecture.md`; two leftover single-host ("Codex") sentences in
`README.md` and `assurance/verification-standard.md` fixed to read
host-neutrally. The plan's literal wording ("moves to architecture.md and
is loaded only for professional release work") was **not** followed as
written — see section 5.

**WS7 (test regulation and coverage definition):**
`global/engineering-constitution.md` (tests-capability satisfaction
criteria), `skills/testing-strategy/SKILL.md` (full rewrite),
`workflows/new-feature/WORKFLOW.md` and `workflows/new-project/WORKFLOW.md`
(acceptance-criteria-to-test traceability, coverage-floor bootstrap),
`mutation-testing` capability documented in `capability-matrix.md`
(`capability-baseline.json` itself deferred, same as `has_license_policy`),
`assurance/verification-plan-v3.schema.json` and
`assurance/verification-report-v5.schema.json` (optional `coverage` block:
`report_path`/`metric`/`floor`/`reason`, a tool-agnostic JSON summary the
project's own check produces), `assurance/run-verification.py`
(`coverage_diagnostic`/`coverage_summary`, wired into `summarize()` and
`main()`), `scripts/test-coverage-semantics.py` (new), `governance.py`
(`project validation-checklist`'s `automated_test` heuristic),
`scripts/test-validation-checklist.py` (new), `tests/governance/GOV-036*`
(new) and its wiring.

## 4. Existing fixtures and GOV scenarios: confirmed byte-identical

```
git diff --quiet master..HEAD -- 'tests/governance/GOV-0[0-2][0-9]*.md' 'tests/governance/GOV-030*.md'
# exit 0 — no difference
```

GOV-001 through GOV-030 remain byte-identical to the 2.0.0 baseline, as in
every previous phase's packet. Professional-mode behavior: every commit that
touched shared code (`governance.py`, `assurance/run-verification.py`) was
followed by `scripts/test-management.py --mode common` and
`scripts/test-assurance-integration.py`, both of which exercise the
professional-mode-only path; neither required a modification to pass.
`scripts/test-governance-integrity.py`'s `test_v2_plan_unaffected_by_tampering`
and `scripts/test-coverage-semantics.py`'s `test_v2_plan_has_no_coverage_field`
both explicitly confirm schema v2 plans / v4 reports carry none of this
phase's new fields.

## 5. Deviations from the plan, and why

- **WS6's kernel restructuring was not implemented as literally written,
  by explicit maintainer direction.** The plan says cross-context
  aggregation detail (`Assurance-answer precision`, the local/CI split
  response checklist, the outcome/environment and tool-bootstrap
  invariants) "moves to `assurance/architecture.md` and is loaded only for
  professional release work." Several frozen scenarios (GOV-018, GOV-022,
  GOV-024–026) test this exact content in ordinary, non-release-framed
  conversations. Gating the obligation text itself behind a release-work
  trigger risked a real behavioral regression against them, not just a
  wording change — flagged to the maintainer before implementation (see
  the conversation record), who chose "keep the rule statements, move
  only elaboration." What was actually built: the existing marker-checked
  sections stay word-for-word in the kernel; one new pointer sentence
  references `assurance/architecture.md` as the mechanics/reference detail
  behind them. The token-budget check WS6 also asks for was still built
  and confirmed to actually fire; all four budgets (both kernels, both
  managed blocks) are comfortably within budget today without any wording
  change being required to pass it.

- **WS7's coverage feature is v3/v5-only, not extended to v2/v4, after an
  initial attempt to extend it was reverted.** Reasoning during
  implementation: coverage floors aren't inherently "target-aware" the way
  v3's `execution.required_targets` is, and the default project template
  (`templates/repository/verification-plan.json`) stays on schema v2 for
  every new project including business-led ones — so restricting coverage
  to v3 would make the template's own coverage placeholder meaningless for
  most real projects. That reasoning is plausible but was weighed against
  an explicit, specific instruction in the plan's own text, in the same
  sentence describing the feature: "...records the measured value in
  `verification-report-v5.schema.json` as a diagnostic... Schema v2 and v4
  unchanged." Deferring to the explicit instruction over the secondary
  architectural inference, the v2/v4 schema additions were reverted before
  committing. Net effect: `templates/repository/verification-plan.json`'s
  `tests` capability does **not** get the coverage placeholder the plan
  also literally asks for, since the schema legitimately doesn't support
  it on v2. See section 6 for why this is a symptom of a larger,
  pre-existing gap rather than a new one.

- **`capability-baseline.json` was not touched for either `has_license_policy`
  (WS5) or `mutation-testing` (WS7).** This file's content is release-hash-pinned
  in `assurance/release-baseline-hashes.json` against the actual published
  2.0.0 commit (`4d2957f`) — verified early in WS5 that the recorded hash
  matches that commit's content exactly, byte for byte. `VERSION` is still
  `2.0.0` on this branch. Editing the file now would trip — correctly —
  the release-baseline integrity check WS1 built earlier in this same
  effort, which would mean weakening the very control this branch exists
  to strengthen, to make a documentation-consistency point pass. Both
  facts are documented in `capability-matrix.md` with an explicit note
  that the machine-readable baseline picks them up at the next version
  cut; confirmed harmless in the meantime, since `required_if` enforcement
  reads a project's own plan facts, never `capability-baseline.json`'s
  descriptive top-level facts list.

- **The validation-checklist's `automated_test` field is a keyword-based
  presence heuristic, not the "same acceptance criteria that tests
  reference" the plan describes.** No acceptance-criteria file format
  exists anywhere in the framework for such a link to bind to — the
  registration schema has no acceptance-criteria field, and
  `workflows/new-feature/WORKFLOW.md`'s ACCEPTANCE CRITERIA step records
  criteria in the change record/conversation, not a structured file
  `governance.py` can parse. Designing that format would be materially
  larger scope than this phase's remaining budget. What was built instead:
  a genuine (not fake) heuristic that searches the project's `tests/` tree
  by file name and content for capability-related keywords, explicitly
  documented in the tool's own `note` field and the function's docstring
  as a presence indicator, not a verified link. This is a real,
  independently useful signal, not a placeholder, but it is not what the
  plan's sentence literally promises.

## 6. Open questions and known risks

**KNOWN RISK, discovered while implementing WS7's coverage feature —
new projects, including business-led ones, default to schema v2 and stay
there indefinitely unless someone hand-edits `schema_version`.** WS1's
`governance_integrity_preflight` and `instruction_surface_audit`
(business-led governance-artifact tamper detection) and WS7's coverage
floors are all schema v3/v5-only. `governance.py project new`/`adopt` never
sets `schema_version`; it is whatever `templates/repository/verification-plan.json`
declares, which is `"2"`, regardless of `--mode`. Concretely: a fresh
business-led project today has **none** of WS1's governance-artifact
integrity protection active until someone manually changes
`verification-plan.json`'s `schema_version` from `"2"` to `"3"` — a step
with no CLI flag, no documented procedure, and no prompt anywhere in the
framework telling a business owner or IT Security this is necessary. This
predates phase 4 (WS1 was built in phase 1) and is not something this
phase's work introduced, but phase 4's coverage work is the second
capability to run into the same wall, which is what surfaced it clearly
enough to write down. Worth a deliberate decision before this framework is
relied on for real business-led deployments: should business-led projects
(or all M1+ projects) start on schema v3 by default, and if so, is that a
template change, a `governance.py project new` behavior change, or both.

**OPEN QUESTION, same root cause — the coverage placeholder the plan asks
for in `templates/repository/verification-plan.json` was not added,**
since the template is schema v2 and coverage is v3-only. Once the
schema-v2-default question above is resolved, revisit whether the template
should gain the placeholder then.

**RESOLVED — WS6's kernel-restructuring compatibility risk**, per section 5:
maintainer chose "keep the rule statements, move only elaboration" over the
plan's literal "gate behind release-work framing" wording.

**KNOWN LIMITATION — GOV-033 through GOV-036 are not yet behaviorally
validated.** Same status as GOV-031/032 from phase 2: written, wired,
statically validated, format-checked by
`scripts/manual-behavioral-campaign.py self-test`, but not yet run against
a live Codex or Claude Code session. Phase 5 is where behavioral campaigns
happen.

## 7. What phase 5 inherits

Every workstream (WS1 through WS7) named in the plan's section 6 is now
built. Phase 5 (validation and release preparation) is prompt packets for
behavioral campaigns on both hosts in both modes, human-executed campaigns
covering adversarial/injection scenarios, one end-to-end Green pilot on a
managed client, and a drafted (not published) release record. The
schema-v2-default gap in section 6 is worth resolving before or during
phase 5's campaign planning, since it directly affects what a business-led
GOV-031–036 campaign would actually be testing against (a v3-upgraded
fixture, matching how `scripts/test-governance-integrity.py` and
`scripts/test-coverage-semantics.py` already upgrade their own fixtures, or
the as-shipped v2 default, which exercises none of WS1/WS7's protections).
