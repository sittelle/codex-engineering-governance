# Project updater acceptance criteria

The updater must:
- default to dry-run;
- require AGENTS.md and project-governance.yml;
- refuse dirty Git mutation unless explicitly overridden;
- back up files before writing;
- update only baseline/source/locator metadata in project-governance.yml;
- append/replace only the marked governance-managed block in AGENTS.md;
- preserve maturity, assurance, profiles, verification commands, requirements, architecture, security, risks, and project-specific AGENTS instructions.

Version-specific semantic migrations that require developer decisions MUST NOT be applied automatically by this script.
