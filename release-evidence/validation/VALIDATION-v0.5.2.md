# Validation v0.5.2

Status: STABLE_CANDIDATE.

Scope: narrow PSScriptAnalyzer signal-calibration patch driven by real Windows framework scanning. No target-aware assurance semantics changed.

Field finding from v0.5.1:

- the locked PSScriptAnalyzer 1.25.0 bootstrap passed on Windows/x86_64;
- positive/negative PSScriptAnalyzer regression fixtures passed;
- scanning the real framework emitted `PSAvoidUsingWriteHost` warnings across intentional CLI status/preview output;
- no other PSScriptAnalyzer rule was present in the captured field output.

v0.5.2 response:

- explicit repository settings exclude only `PSAvoidUsingWriteHost`;
- all other default Warning/Error rules remain active;
- the scanner regression now invokes the production adapter/settings;
- `Invoke-Expression` remains a required positive detection;
- an intentional Write-Host display fixture must pass.

Required deterministic validation:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native lifecycle mode
- `python scripts/test-framework-scanners.py --platform windows` on Windows after locked tool bootstrap
- `python scripts/run-framework-scanner.py psscriptanalyzer` on Windows after locked tool bootstrap
- `python scripts/verify-framework.py quick --execution-context LOCAL`

Release remains candidate pending GOV-029 and real Windows/Ubuntu target-aware aggregate field validation.
