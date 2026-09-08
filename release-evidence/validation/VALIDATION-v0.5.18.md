# Validation v0.5.18

Status: REJECTED / SUPERSEDED BEFORE FREEZE.

Scope: managed-project instruction propagation correction discovered by the completed v0.5.17 behavioral campaign, plus the approved release-evidence layout cleanup. This uses the existing managed AGENTS and release-evidence mechanisms; it does not add a parallel governance subsystem or change behavioral scenarios/rubrics.

Frozen predecessor evidence:

- v0.5.17 is the latest frozen cross-platform verified reference at exact commit `74c51578b61602be170cbfc3dc359e54730ee0b6`;
- GitHub Actions Framework Verification run `33736927718` for that exact commit concluded `success`;
- aggregate evidence reports aggregate schema `2`, report schema `5`, `overall: PASS`, `issues: []`, and 14/14 required Windows/Ubuntu checks PASS.

Behavioral evidence driving this correction:

- the v0.5.17 campaign checkpoint is preserved on `eval/1.0-candidate-v0.5.17` at commit `435ec25edc32902067b528281273cd286aa76b97`;
- latest retained campaign score: 54/60;
- GOV-006, GOV-016, GOV-019, GOV-020, GOV-021, and GOV-022 each ended at 1/2; no critical scenario scored 0; GOV-026..030 scored 2/2;
- retries were stopped after repeated partials rather than repeated until green;
- the 32 evaluation records already present under `tests/governance/evaluations/2026-09-03/` in the campaign checkpoint, including the earlier GOV-003 remediation record, were imported into this candidate byte-for-byte.

Confirmed propagation defect and correction:

- v0.5.17 `templates/repository/AGENTS.md` placed several project assurance invariants after `<!-- END CODEX-GOVERNANCE-MANAGED -->`;
- governed-project Update refreshed only the managed block, so existing repositories could be repinned without those newer instructions;
- New, Adopt, and Update also carried multiple separately hard-coded managed-block representations;
- v0.5.18 makes the template managed block authoritative and has lifecycle scripts extract/copy that block rather than duplicating its body;
- the authoritative block now contains the existing propagation-critical assurance/emergency invariants relevant to the observed misses;
- project-owned AGENTS text outside the managed markers remains preserved.

Approved release-evidence layout cleanup:

- all 37 predecessor `VALIDATION-v*.md` files were moved byte-for-byte from repository root into `release-evidence/validation/`;
- the v0.5.18 validation record is created in that directory from the outset;
- historical outcomes are unchanged by relocation, including the rejected/superseded status represented by `VALIDATION-v0.5.16.md`;
- `MANIFEST.json`, `SOURCES.md`, release-evidence guidance, and validator paths now use the new location;
- the governance validator rejects future root-level `VALIDATION-v*.md` files.

Prepared-tree checks completed in this build environment:

- committed v0.5.17 campaign evidence byte-preservation comparison — PASS (32/32 records);
- predecessor validation-history byte-preservation comparison — PASS (37/37 records);
- `python scripts/validate-governance.py` — PASS;
- `python scripts/test-manifest-inventory.py` — PASS;
- `python scripts/test-framework-lifecycle.py --mode common` — PASS;
- `python scripts/test-framework-lifecycle.py --mode posix` — PASS;
- POSIX shell syntax checks for both lifecycle scripts — PASS;
- Python syntax compilation for modified lifecycle/validator/bootstrap code — PASS;
- `python scripts/verify-framework.py quick --execution-context LOCAL` — PASS on Linux/x86_64;
- framework scanner regression could not execute in this build environment because the locked Linux scanner tooling is unavailable;
- assurance integration was attempted in this constrained build environment but did not complete within the available execution window; it is not recorded as PASS.

## Rejection / supersession

User-host validation of the prepared v0.5.18 replacement package reported only 18 durable behavioral evaluation records. Inspection showed that the distribution manifest/package omitted all 32 committed `tests/governance/evaluations/2026-09-03/GOV-*.md` records, despite this record's prepared-tree statement that those records had been imported. The prepared-tree comparison was therefore not sufficient evidence of final package inclusion.

v0.5.18 was never frozen. It is superseded by v0.5.19, which restores the omitted records byte-for-byte and adds a validator invariant binding all durable behavioral evaluation records to the distribution manifest. The propagation correction and validation-history relocation themselves are retained.

Still required on the user host before freeze:

- governance validator and manifest inventory regression against the replacement package;
- lifecycle common and Windows regression;
- assurance integration;
- canonical quick and full verification as applicable;
- `git diff --check`;
- exact-commit Windows/Ubuntu canonical full aggregate evidence;
- fresh targeted GOV-006, GOV-016, GOV-019, GOV-020, GOV-021, and GOV-022 behavioral attempts against installed v0.5.18 guidance; then decide whether a complete GOV-001..030 candidate rerun is warranted.
