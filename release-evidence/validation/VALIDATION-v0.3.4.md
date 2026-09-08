# v0.3.4 Assurance Self-Test Portability Validation

Scope: integration-test portability only. No governance policy semantics changed.

The v0.3.3 Windows field test established that governed execution-context reconciliation behaved correctly, while the central framework integration suite itself was not portable because it embedded a build-host Python path and used a POSIX-only PATH probe.

v0.3.4 acceptance:
- no `/opt/pyvenv` reference remains in assurance fixtures;
- fixture commands are materialized with the interpreter executing the integration harness;
- PATH-resolution probe is `.cmd` on Windows and executable script on POSIX;
- complete integration suite passes on the packaging host;
- Windows execution of `python scripts/test-assurance-integration.py` is the field regression check.

No TEST-project application feature work is required.
