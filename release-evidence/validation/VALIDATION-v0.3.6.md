# v0.3.6 CI Assurance Bootstrap Portability Validation

Scope: framework assurance-tool bootstrap portability and evidence continuity.

Field trigger: Ubuntu GitHub Actions failed before canonical verification because a Windows-generated hash-locked assurance environment included the Windows-only `pywin32` dependency.

Automated acceptance:
- all previous governance tests preserved;
- platform-lock standard present;
- managed CI orchestrator installed by assurance bootstrap;
- generated workflow invokes orchestrator rather than a standalone bootstrap step;
- successful project bootstrap proceeds to normal canonical full verification;
- failed project bootstrap still emits `ci-full.json` with required checks `DID_NOT_EXECUTE`, precondition-failure disposition, and overall `INCOMPLETE_ASSURANCE`;
- CI remains non-green on bootstrap failure.

Behavioral validation:
- GOV-024 = 2;
- GOV-025 = 2.

After behavioral validation, reconcile the field TEST project's assurance locks by environment before rerunning GitHub CI.
