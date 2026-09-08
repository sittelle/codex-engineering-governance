# Validation v0.5.14

Status: STABLE_CANDIDATE.

Scope: durable evidence/readiness accounting after successful completion of the pre-1.0 release rehearsal against frozen v0.5.13. No governance or assurance outcome-policy change.

Field evidence closed by this version:

- v0.5.13 was frozen at commit `b18d5f11059b3894cd9e215a8d149da3783c114a`;
- GitHub Actions Framework Verification run `33399810045` for that exact commit concluded `success`;
- retained `aggregate-full.json` reports aggregate schema `2`, report schema `5`, `overall: PASS`, `issues: []`, and all 14 required checks `PASS` across the required Windows x86_64 and Linux x86_64 targets;
- the rehearsal distributable `codex-engineering-governance-v0.5.13.zip` was built exclusively from exact Git `HEAD` bytes using the `MANIFEST.json` allowlist, Python 3.14.6 `zipfile`, DEFLATE level 9, normalized ZIP timestamps, and Git-derived file modes;
- exact artifact inventory validation passed; artifact size was 273,282 bytes and SHA-256 was `FF05CC7F21D97626CA8AA0731BB1844E117814AE790C5098BBDA614F33170326`;
- an independent rebuild using the same procedure produced the identical SHA-256;
- the proposed `READY` rehearsal decision was explicitly approved by the developer; no exception or accepted risk was used;
- the durable decision record is retained at `release-evidence/0.5.13/release-record.md`; publication/deployment remains a separate approval boundary.

v0.5.14 records that closure and updates package-version metadata/current package guidance. It does not change Technology Baseline semantics, behavioral rubrics or durable evaluations, verification-plan/report/aggregate schemas, assurance result policy, security release gates, scanner policy/tool pins, or publication/deployment approval boundaries.

Candidate validation for v0.5.14 must include:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native Windows lifecycle regression
- POSIX lifecycle regression through CI/Ubuntu
- canonical quick verification
- attributable Windows/Ubuntu canonical full evidence for the exact frozen v0.5.14 commit

The pre-1.0 release rehearsal objective itself is closed by the retained v0.5.13 READY record; v0.5.14 still requires its normal exact-commit assurance before becoming the latest frozen cross-platform verified reference.
