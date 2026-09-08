# Validation v0.5.1

Status: STABLE_CANDIDATE.

Scope: narrow Windows lifecycle-test diagnostic and downloaded-package trust hardening. No target-aware assurance semantics changed.

Required deterministic validation:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native lifecycle mode (`--mode windows` on Windows, `--mode posix` on POSIX)
- `python scripts/verify-framework.py quick --execution-context LOCAL`

Windows field finding:

- PowerShell 7 and Windows PowerShell 5.1 both create the expected empty `docs`, `src`, and `tests` directories in New mode.
- The prior v0.5.0 lifecycle failure was therefore not evidence of a New-project implementation defect.
- The v0.5.0 harness could record a failed prerequisite and then dereference missing outputs, causing a secondary exception that hid the original failure.
- Downloaded unsigned `.ps1` files may also be blocked by Windows trust/execution policy when Mark-of-the-Web is propagated from an archive. v0.5.1 requires bounded diagnostics and documents verify-then-unblock handling rather than execution-policy bypass.

Release remains candidate pending GOV-029 and real Windows/Ubuntu target-aware aggregate field validation.
