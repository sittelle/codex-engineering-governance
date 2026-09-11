# Governed project manager acceptance criteria

The sole project-management implementation is `governance.py`.

- New accepts parent root + project name and creates `<parent>/<name>`.
- New refuses an existing non-empty target.
- New installs only the minimal governance baseline (`AGENTS.md`, `CLAUDE.md`, project governance/verification scaffolding) and may initialize Git; it does not create application code.
- Adopt requires an existing project without `project-governance.yml`.
- Adopt preserves existing content plus project-specific `AGENTS.md` / `CLAUDE.md` text.
- Adopt records `RECONCILIATION_REQUIRED` and `historical_governance_approval: false`.
- Dirty Git adoption is a hard refusal.
- Every mutating operation prints a preview and asks `Apply these changes? [y/N]:`; `-y` confirms the same plan without bypassing safety checks.
