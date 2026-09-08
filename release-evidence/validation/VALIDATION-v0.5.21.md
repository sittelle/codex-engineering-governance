# Validation v0.5.21

Status: STABLE_CANDIDATE.

Scope: evidence-byte-preservation correction to the prepared but unfrozen v0.5.20 response-completeness candidate. No governance policy, scenario/rubric, assurance outcome semantic, or functional remediation is changed by this version.

Frozen predecessor evidence:

- v0.5.17 remains the latest frozen cross-platform verified reference at exact commit `74c51578b61602be170cbfc3dc359e54730ee0b6`;
- Framework Verification run `33736927718` for that exact commit concluded `success`;
- aggregate evidence reports schema `2`, report schema `5`, `overall: PASS`, `issues: []`, and 14/14 required Windows/Ubuntu checks PASS.

v0.5.19 retained evidence and disposition:

- v0.5.19 exact candidate commit `a25c8a989799353e58c280720e7727fba967a2fe` passed Framework Verification run `33855943848` with aggregate PASS, no issues, and 14/14 required checks PASS;
- fresh targeted v0.5.19 results were GOV-006 1/2, GOV-016 1/2, GOV-019 2/2, GOV-020 1/2, GOV-021 2/2, GOV-022 1/2;
- v0.5.19 therefore closed GOV-019 and GOV-021 but remained below the projected >=58/60 candidate threshold and was rejected/superseded before freeze;
- all six targeted records and the v0.5.19 rejection record remain historical evidence.

v0.5.20 prepared-candidate disposition:

- v0.5.20 carried the approved narrow response-completeness remediation for GOV-006/GOV-016/GOV-020/GOV-022;
- before any working-tree replacement, the user ran the required byte-for-byte comparison between all 56 current behavioral evaluation records and the prepared archive;
- the comparison failed only for `tests/governance/evaluations/2026-09-04/GOV-021-operational-scanner-failure-attempt-2.md`;
- inspection showed that the prepared archive had inserted Markdown escape backslashes around underscores in the raw-response `DID_NOT_EXECUTE / INCOMPLETE_ASSURANCE` token, while the authoritative current-repository record produced by the retained evidence-writing step used plain underscores;
- the other 55 durable behavioral records matched;
- v0.5.20 was therefore rejected/superseded before application, commit, or freeze. Its functional remediation is not rejected on technical grounds; the defect is evidence carry-forward integrity.

v0.5.21 correction:

- restores the GOV-021 attempt-2 record to the authoritative current-repository bytes without changing prompt, score, rationale, attempt identity, or behavioral conclusion;
- retains the v0.5.20 global-kernel, managed-project, release-workflow, emergency-workflow, lifecycle, and static response-completeness remediation byte-for-byte except for ordinary current-version metadata where required;
- adds no new policy subsystem, exception mechanism, evidence registry, or assurance semantic;
- preserves all other behavioral and validation history unchanged.

Prepared-tree checks required before handoff:

- governance validator — PASS;
- manifest inventory regression — PASS;
- lifecycle common and POSIX — PASS;
- canonical quick on the available Linux environment — PASS;
- exact distribution inventory against `MANIFEST.json` — PASS;
- all 30 frozen GOV scenario files preserved byte-for-byte from v0.5.20;
- 55 behavioral evaluation records preserved byte-for-byte from v0.5.20, with only the known GOV-021 evidence correction differing;
- v0.5.20 remediation-bearing kernel/managed/workflow files preserved byte-for-byte;
- durable behavioral evaluation count — 56.

Still required before replacement/freeze:

- first, repeat the behavioral evidence comparison against the authoritative current user repository and require 56/56 byte identity;
- then replace the working tree while preserving `.git`;
- run governance validator, manifest inventory regression, lifecycle common/Windows, assurance integration, canonical quick/full verification as applicable, and `git diff --check`;
- obtain fresh exact-commit Windows/Ubuntu canonical full aggregate evidence;
- repin the evaluation fixture/global kernel to v0.5.21;
- run fresh targeted GOV-006, GOV-016, GOV-020, and GOV-022 attempts against unchanged scenarios/rubrics. If all four reach 2/2, decide whether to run the complete fresh GOV-001..030 candidate campaign required for final >=58/60 acceptance.
