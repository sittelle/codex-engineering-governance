# Validation v0.5.4

Status: STABLE_CANDIDATE.

Scope: narrow framework-repository CI trigger alignment patch. No assurance outcome, target, scanner, capability, or application-governance semantics changed.

Finding from the first frozen v0.5.3 field attempt:

- commit `3dc3215290bdddc9316d076b7758c510d9e7b8b6` was pushed to `master`;
- `gh run list --limit 5` returned `no runs found`;
- the repository-owned `.github/workflows/framework-verify.yml` push trigger was limited to `branches: [main]`;
- therefore no canonical Windows/Ubuntu field evidence was produced.

v0.5.4 response:

- aligns the repository-owned framework verification push trigger to `master`;
- preserves pull-request and `workflow_dispatch` triggers;
- validates the framework workflow branch marker so the same mismatch is not silently reintroduced;
- deliberately leaves the generic governed-project workflow template unchanged because this defect is specific to the framework repository's branch identity.

Required deterministic validation:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native lifecycle mode
- host-native scanner regression where locked tooling is available
- `python scripts/verify-framework.py quick --execution-context LOCAL`

Release remains candidate pending a clean v0.5.4 commit, real Windows/Ubuntu target-aware aggregate field validation, and GOV-029.
