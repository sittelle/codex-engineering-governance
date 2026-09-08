# Governed project manager acceptance criteria

- New mode accepts parent root + project name and creates `<parent>/<name>`.
- New mode refuses an existing non-empty target.
- New mode installs only the minimal governance baseline and may initialize Git; it does not create an approved-design commit or application code.
- Adopt mode requires an existing project without `project-governance.yml`.
- Adopt mode preserves existing content and existing design.
- Adopt mode records `RECONCILIATION_REQUIRED` and `historical_governance_approval: false`.
- Both modes are dry-run by default.
