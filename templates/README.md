# Project bootstrap

For a small M1/SA1 project copy:
- `repository/AGENTS.md`
- `repository/project-governance.yml`
- `.editorconfig`
- `.gitignore`
- `docs/design.md`

For M2/M3, SA2/SA3, or more complex systems split design into:
- requirements.md
- architecture.md
- security.md
- ADRs
- risk register
- SECURITY.md when public

Do not fill templates with invented requirements. Discovery comes first.

For M1+ C2/C3 new projects, initialize Git and commit the approved design baseline before substantial implementation.

After stack approval, create the project-native `verify` / `verify-full` interface (or clearly documented equivalent) before implementation expands beyond the initial scaffold.


The repository template expects the central governance repository to be discoverable through `$CODEX_HOME/GOVERNANCE_ROOT`. Run the governance `codex-home/install.ps1` (Windows) or `codex-home/install.sh` (POSIX) before using governed projects.
## Assurance integration

`repository/verification-plan.json` is deliberately unconfigured. It establishes the durable plan location without pretending verification exists before stack selection. After configuring project checks, run `scripts/bootstrap-assurance.*` to install the project-local runner and GitHub Actions baseline.

