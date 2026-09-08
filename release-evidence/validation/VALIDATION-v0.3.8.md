# v0.3.8 Release-Evidence Hygiene Validation

Scope: package consistency and truthful release-evidence accounting only; no application policy or assurance outcome change.

Automated acceptance:
- package VERSION, template baseline, capability baseline, and global normative versions agree;
- `MANIFEST.json` file inventory exactly matches packaged regular files (excluding transient Python cache artifacts);
- the package contains exactly 26 GOV behavioral scenario definitions;
- static validation calls them scenarios and does not imply they were executed merely because the files exist;
- the behavioral acceptance target is 50/52 across GOV-001..026, no critical 0, and GOV-026 must score 2;
- completed evaluation records use durable files and historical unknown metadata is not fabricated;
- exact GOV-024, GOV-025, and GOV-026 records from the available validation cycle are retained;
- the stale GOV-026 manifest status is closed;
- the README lifecycle section no longer contains literal escaped `\n` sequences.

Release-readiness note:
- v0.3.8 remains `STABLE_CANDIDATE`; these changes improve evidence hygiene but do not by themselves establish 1.0 readiness;
- a complete candidate behavioral evaluation set and clean committed release candidate remain pre-1.0 evidence requirements.
