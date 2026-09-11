# Project updater acceptance criteria

The updater is the `project update` operation in the sole management entry point, `governance.py`. It must:

- print a preview before mutation and require `y/N` confirmation (`-y` supplies only that confirmation);
- require `AGENTS.md` and `project-governance.yml`;
- refuse dirty Git mutation with no force override;
- back up existing governed files before writing them;
- update only governance baseline/source/locator metadata in `project-governance.yml`;
- append/replace only the marked governance-managed block in `AGENTS.md`;
- create or update only the marked Claude adapter block in `CLAUDE.md`;
- preserve maturity, assurance, profiles, verification commands, requirements, architecture, security, risks, established Technology Baseline state, and project-specific host instructions;
- migrate a legacy project with no Technology Baseline to `RECONCILIATION_REQUIRED` rather than inventing an established state.

Version-specific semantic migrations that require developer decisions MUST NOT be applied automatically.
