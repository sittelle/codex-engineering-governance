# Validation v0.5.5

Status: STABLE_CANDIDATE.

Scope: field-driven cross-platform assurance correction after the first real v0.5.4 Windows/Ubuntu framework verification run. No application-governance expansion.

Evidence from GitHub Actions run `33176254592` at commit `57192c594263411290f192f369c961508b95fea9`:

- Windows and Ubuntu evidence-producer jobs both completed and uploaded canonical report-v5 evidence.
- Aggregate bundle v2 was `FAIL`, proving the combined gate was fail-closed.
- Ubuntu `sast-posix` executed and failed only with ShellCheck `SC1007` on `CDPATH= cd ...` path-resolution idioms.
- Ubuntu `scanner-regressions-linux` returned `DID_NOT_EXECUTE / OPERATIONAL_FAILURE` with exit 125, but v0.5.4 did not retain the scanner-specific operational diagnostic.
- Aggregate reported `ARTIFACT_IDENTITIES_MISMATCH` even though Windows and Ubuntu canonical Git-HEAD plan/baseline/runner SHA-256 values were identical; only Windows `working_tree_sha256` differed from Ubuntu because of checkout-byte normalization.

v0.5.5 response:

- compare cross-report artifact identity using only `source`, `repository_path`, and committed `sha256`; retain `working_tree_sha256` as diagnostic evidence only;
- add integration regression proving diagnostic worktree-hash divergence is accepted and canonical SHA divergence is rejected;
- replace ambiguous POSIX `CDPATH= cd` with explicit `CDPATH='' cd`, with no ShellCheck suppression;
- make temporary scanner fixtures traversable by the pinned non-root Semgrep container;
- retain scanner-specific bounded diagnostics when a regression fixture encounters operational nonexecution.

Required deterministic validation:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native lifecycle mode
- host-native scanner regression where locked tooling is available
- `python scripts/verify-framework.py quick --execution-context LOCAL`
- POSIX shell syntax verification

Release remains candidate pending a clean v0.5.5 Windows/Ubuntu target-aware aggregate field rerun, GOV-029, and pre-1.0 release rehearsal.
