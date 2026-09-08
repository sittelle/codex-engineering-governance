# Validation v0.5.13

Status: STABLE_CANDIDATE.

Scope: release-preparation hygiene after v0.5.12 exact-commit machine assurance passed. This patch corrects stale current-package guidance and adds a narrow static version-binding regression; no governance or assurance outcome policy changes.

Field evidence leading to this patch:

- v0.5.12 was frozen at commit `341e24642a10b7b27f8e411a032eb0f798cdeb06`;
- GitHub Actions Framework Verification run `33395966891` for that exact commit concluded `success`;
- retained `aggregate-full.json` reports aggregate schema `2`, report schema `5`, `overall: PASS`, `issues: []`, and all 14 required checks `PASS` across the required Windows x86_64 and Linux x86_64 targets;
- during the pre-1.0 release rehearsal, the README package-trust example was found to reference `codex-engineering-governance-v0.5.11.zip`, which was stale current-release guidance rather than intentional history;
- inspection of current-facing release/package guidance found the other v0.5.11 README references were historical GOV-030/Technology Baseline material and must remain unchanged.

v0.5.13 corrects that release-guidance defect and adds one static check binding the package-trust example to the authoritative `VERSION`. It does not change Technology Baseline semantics, behavioral rubrics or durable evaluations, verification-plan/report/aggregate schemas, assurance result policy, security release gates, scanner policy/tool pins, or publication/deployment approval boundaries.

Candidate validation must include:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native Windows lifecycle regression
- POSIX lifecycle regression through CI/Ubuntu
- canonical quick verification
- attributable Windows/Ubuntu canonical full evidence for the exact frozen v0.5.13 commit

After exact-commit v0.5.13 machine assurance closes, resume the pre-1.0 release rehearsal against that exact source and retain the release-decision record and artifact digest evidence.
