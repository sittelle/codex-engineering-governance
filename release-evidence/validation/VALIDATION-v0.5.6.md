# Validation v0.5.6

Status: STABLE_CANDIDATE.

Scope: Linux scanner-regression fixture calibration after the real v0.5.5 Windows/Ubuntu target-aware aggregate rerun. No production scanner-policy or application-governance expansion.

Evidence from GitHub Actions run `33178142845` at commit `d6e9decd1c3f0d5e5c29ee019e080f1f2c71575d`:

- Windows and Ubuntu evidence producers both completed and uploaded report-v5 evidence.
- Aggregate bundle v2 had no identity issues; the v0.5.5 canonical-vs-working-tree aggregation correction is therefore field-verified.
- Ubuntu `sast-posix` passed; the v0.5.5 `SC1007` production-code correction is therefore field-verified.
- All required checks passed except `scanner-regressions-linux`.
- The retained scanner diagnostics showed exactly two positive-fixture misses: Gitleaks returned 0 for the synthetic PAT fixture and ShellCheck returned 0 for the unquoted-variable fixture.
- Gitleaks 8.30.1's default configuration has the alphabet sequence as a global stopword, explaining the old fixture's intentional filtering.
- ShellCheck production scanning uses `--severity=warning`; the old `SC2086` positive fixture is informational at that threshold, so exit 0 was expected.

v0.5.6 response:

- use a deterministic synthetic GitHub-PAT-shaped value that does not contain the default Gitleaks alphabet stopword;
- explicitly load the repository `.gitleaks.toml` in the Gitleaks directory fixture scan;
- exercise field-observed warning-level ShellCheck `SC1007` as the positive fixture and explicit `CDPATH='' cd` as the clean counterpart;
- preserve production scanner configurations, severity thresholds, result classification, tool pins, target-aware assurance semantics, and application governance unchanged.
- add a repository-owned `.gitattributes` policy with canonical LF text and CRLF only for `.bat`/`.cmd`, and include it in the authoritative distribution MANIFEST.

Required deterministic validation:

- `python scripts/validate-governance.py`
- `git diff --check`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- host-native scanner regression where locked tooling is available
- real host-native production scanner path
- `python scripts/verify-framework.py quick --execution-context LOCAL`

Release remains candidate pending a clean v0.5.6 Windows/Ubuntu target-aware aggregate field rerun, GOV-029, and pre-1.0 release rehearsal.
