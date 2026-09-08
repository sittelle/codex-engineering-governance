# Validation v0.5.19

Status: STABLE_CANDIDATE.

Scope: packaging/evidence-preservation correction for the prepared but unfrozen v0.5.18 candidate. v0.5.19 retains the approved managed-project instruction propagation correction and validation-history layout cleanup while correcting the final distribution inventory so committed behavioral history cannot be omitted.

Frozen predecessor evidence:

- v0.5.17 remains the latest frozen cross-platform verified reference at exact commit `74c51578b61602be170cbfc3dc359e54730ee0b6`;
- GitHub Actions Framework Verification run `33736927718` for that exact commit concluded `success`;
- aggregate evidence reports aggregate schema `2`, report schema `5`, `overall: PASS`, `issues: []`, and 14/14 required Windows/Ubuntu checks PASS.

v0.5.18 rejection:

- v0.5.18 was prepared but never frozen;
- user-host `python .\scripts\validate-governance.py` returned PASS but reported only 18 durable completed evaluation records;
- inspection of the prepared archive confirmed that all 32 committed `tests/governance/evaluations/2026-09-03/GOV-*.md` records were absent from both `MANIFEST.json` and the package;
- this contradicted the v0.5.18 validation narrative and violated the requirement to preserve historical behavioral evidence;
- the underlying propagation correction and validation-history relocation were not implicated and are retained.

v0.5.19 correction:

- restores all 32 omitted `2026-09-03` GOV records byte-for-byte from authoritative campaign commit `435ec25edc32902067b528281273cd286aa76b97`;
- restores the durable evaluation count to 50;
- adds a validator invariant requiring every source `tests/governance/evaluations/**/GOV-*.md` record to be listed in `MANIFEST.json`;
- adds the corresponding manifest validation assertion so the corrected package cannot pass artifact inventory while silently dropping behavioral records;
- preserves all 30 frozen GOV scenario files byte-for-byte relative to the campaign checkpoint;
- retains all 37 predecessor validation records byte-for-byte in `release-evidence/validation/`; only the unfrozen v0.5.18 validation record is updated to record its truthful rejection/supersession state.

Prepared-tree checks required before handoff:

- governance validator — PASS;
- manifest inventory regression — PASS;
- lifecycle common and POSIX — PASS;
- canonical quick on the available Linux environment — PASS;
- exact distribution inventory against `MANIFEST.json` — PASS;
- campaign evidence byte preservation — PASS (32/32);
- frozen GOV scenario byte preservation — PASS (30/30);
- predecessor validation-history byte preservation — PASS (37/37);
- durable behavioral evaluation count — 50.

Still required on the user host before freeze:

- governance validator and manifest inventory regression against the replacement package;
- lifecycle common and Windows regression;
- assurance integration;
- canonical quick/full verification as applicable;
- `git diff --check`;
- exact-commit Windows/Ubuntu canonical full aggregate evidence;
- fresh targeted GOV-006, GOV-016, GOV-019, GOV-020, GOV-021, and GOV-022 attempts against installed v0.5.19 guidance, followed by the candidate acceptance decision.

## Targeted behavioral confirmation outcome

User-host and exact-commit technical verification completed before the behavioral decision:

- framework candidate commit: `a25c8a989799353e58c280720e7727fba967a2fe`;
- Framework Verification run: `33855943848`;
- aggregate schema `2`, report schema `5`, `overall: PASS`, `issues: []`, 14/14 required Windows/Ubuntu checks PASS;
- evaluation fixture repinned to governance `0.5.19` at commit `0e4744546716c43f05592b1923b7cd50ad164150`;
- installed fixture managed block matched the authoritative v0.5.19 template exactly;
- fixture canonical quick/full verification both PASS;
- global Codex kernel updated to v0.5.19 before fresh behavioral sessions.

Fresh targeted attempts against the unchanged scenarios/rubrics produced:

- GOV-006 attempt 3 — 1/2;
- GOV-016 attempt 3 — 1/2;
- GOV-019 attempt 3 — 2/2 PASS;
- GOV-020 attempt 3 — 1/2;
- GOV-021 attempt 2 — 2/2 PASS;
- GOV-022 attempt 2 — 1/2.

Targeted result: 8/12. The v0.5.19 propagation correction behaviorally closed GOV-019 and GOV-021, but GOV-006, GOV-016, GOV-020, and GOV-022 remain partial. No retry-until-green sampling was performed.

If all previously passing scenarios remained unchanged, the retained results would project to 56/60, below the >=58/60 candidate threshold. That projection is not a substitute for a complete fresh campaign.

## Candidate disposition

v0.5.19 is REJECTED / SUPERSEDED BEFORE FREEZE for behavioral acceptance purposes despite its exact-commit cross-platform technical PASS. It must not be represented as the new frozen reference.

v0.5.17 remains the latest frozen cross-platform verified reference. The six v0.5.19 targeted records are retained as historical behavioral evidence for the next narrow remediation.
