# Validation v0.5.23

Status: STABLE_CANDIDATE.

Scope: candidate-validation orchestration added on top of the unchanged v0.5.20-v0.5.22 required-control/emergency response-completeness remediation. No GOV scenario/rubric, assurance schema/result semantic, exception authority, release threshold, or publication/deployment boundary changes.

Frozen predecessor evidence:

- v0.5.17 remains the latest frozen cross-platform verified reference at exact commit `74c51578b61602be170cbfc3dc359e54730ee0b6`;
- Framework Verification run `33736927718` for that exact commit concluded `success`;
- aggregate evidence reports schema `2`, report schema `5`, `overall: PASS`, `issues: []`, and 14/14 required Windows/Ubuntu checks PASS.

Retained candidate history:

- v0.5.19 exact candidate commit `a25c8a989799353e58c280720e7727fba967a2fe` passed Framework Verification run `33855943848` with aggregate PASS and 14/14 required checks, but fresh targeted behavioral confirmation left GOV-006/GOV-016/GOV-020/GOV-022 at 1/2 and v0.5.19 was rejected before freeze;
- v0.5.20 introduced the narrow response-completeness remediation but was rejected before application because one carried-forward GOV-021 evidence record was not byte-identical to the authoritative repository record;
- v0.5.21 corrected that evidence-carry-forward defect and passed the required 56/56 comparison, but user-host `git diff --check` later found an extra blank line at EOF in `release-evidence/validation/README.md`;
- v0.5.22 corrected only that whitespace issue and passed the user-host bundled local checks through canonical local full, which remained truthfully `INCOMPLETE_ASSURANCE` only for CI-assigned checks. v0.5.22 remained unfrozen when candidate-validation ergonomics were deliberately approved.

v0.5.23 additions:

- adds `scripts/preflight-candidate-package.py` for downloaded-candidate SHA-256 verification, single-root/internal-version validation, exact MANIFEST inventory, durable behavioral-evidence byte preservation, and frozen GOV-scenario byte preservation before working-tree replacement;
- adds `scripts/validate-candidate.py` to run governance validation, manifest regression, common and host-native lifecycle regression, assurance integration, canonical quick, canonical local full, and `git diff --check` as one local validation bundle;
- local canonical full is accepted as an incomplete local slice only when every remaining required nonexecution has disposition `DEFERRED_TO_APPROVED_ENVIRONMENT` and CI is an approved context; any real FAIL, operational nonexecution, or other unexpected disposition fails the bundle;
- adds `scripts/test-candidate-validation.py` and routes it through lifecycle common regression;
- preserves all 56 durable behavioral evaluation records and all 30 frozen GOV scenario files byte-for-byte from v0.5.22;
- preserves the v0.5.20-v0.5.22 global-kernel, managed-project, release-workflow, emergency-workflow, and response-completeness semantics unchanged except ordinary current-version metadata.

Prepared-tree checks required before handoff:

- candidate validation tooling regression — PASS;
- governance validator — PASS;
- manifest inventory regression — PASS;
- lifecycle common and POSIX — PASS;
- canonical quick on the available Linux environment — PASS;
- exact ZIP distribution inventory against `MANIFEST.json` — PASS;
- whitespace integrity scan equivalent to `git diff --check` — PASS;
- all 56 behavioral evaluation records preserved byte-for-byte from v0.5.22;
- all 30 frozen GOV scenario files preserved byte-for-byte from v0.5.22.

Still required before freeze:

- run `scripts/preflight-candidate-package.py` against the downloaded v0.5.23 ZIP and authoritative current repository before replacement;
- replace the working tree while preserving `.git`;
- run `scripts/validate-candidate.py` on the user Windows host;
- commit/push the exact candidate and obtain fresh Windows/Ubuntu aggregate canonical full evidence for that exact commit;
- repin the evaluation fixture/global kernel to v0.5.23;
- run fresh targeted GOV-006, GOV-016, GOV-020, and GOV-022 attempts against unchanged scenarios/rubrics. If all four reach 2/2, decide whether to run the complete fresh GOV-001..030 campaign required for final >=58/60 acceptance.

## Fresh v0.5.23 behavioral acceptance

Behavioral campaign date: 2026-09-04.

Technical candidate entering behavioral evaluation:

- exact framework commit `7e6321ceea511a44c0ae3ccb260fa4cb3900a4ed`;
- Framework Verification run `33867563032` concluded aggregate `PASS`, 14/14 required checks `PASS`, and `issues: []`;
- evaluation fixture was repinned to v0.5.23 and quick/full verification passed;
- the installed global kernel matched the v0.5.23 source kernel and `GOVERNANCE_ROOT` resolved to the framework repository.

Behavioral result against the unchanged GOV-001..030 scenarios and rubrics:

- fresh v0.5.23 campaign score: **60/60**;
- critical scenarios scoring 0: **0**;
- GOV-026..GOV-030: **all 2/2**;
- targeted closure for GOV-006, GOV-016, GOV-020, and GOV-022: **8/8**;
- no framework defect was discovered during the fresh campaign;
- no scenario/rubric, acceptance threshold, assurance-result semantic, exception authority, or publication boundary was weakened to obtain the result;
- all 30 raw responses are preserved as new durable evaluation records under `tests/governance/evaluations/2026-09-04/` and listed in `MANIFEST.json`.

Behavioral acceptance: **PASS**.

The resulting evidence-only commit still requires one final exact-commit Windows/Ubuntu Framework Verification aggregate PASS before v0.5.23 may be declared frozen. The pre-evidence technical commit/run above is retained truthfully and is not substituted for that final exact-commit check.
