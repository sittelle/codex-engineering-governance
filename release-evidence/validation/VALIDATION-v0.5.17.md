# Validation v0.5.17

Status: STABLE_CANDIDATE.

Scope: evidence-preservation correction to the rejected, uncommitted v0.5.16 candidate while retaining its narrow destructive-automation safeguard remediation. No scenario/rubric weakening and no new governance subsystem.

Frozen predecessor evidence:

- v0.5.15 remains the latest frozen cross-platform verified reference at exact commit `c6ab122ab9401a2fa87c77fe504c541a5effe6c7`;
- GitHub Actions Framework Verification run `33510241313` for that exact commit concluded `success`;
- aggregate evidence reports aggregate schema `2`, report schema `5`, `overall: PASS`, `issues: []`, and 14/14 required checks `PASS` across required Windows x86_64 and Linux x86_64 targets.

Candidate-integrity finding that superseded v0.5.16:

- the v0.5.15 campaign was durably preserved on evidence commit `53ce72b`;
- candidate-package comparison found GOV-001 and GOV-002 text semantically unchanged but representation-different, while GOV-003 attempts 1..3 were content-different;
- inspection showed that each changed GOV-003 record had its original `Regression / observation` retry sentence shortened/removed during v0.5.16 preparation;
- v0.5.16 was therefore rejected before commit/freeze rather than normalizing or accepting rewritten historical evidence.

v0.5.17 correction and retained remediation:

- restores all five carried-forward v0.5.15 campaign records to the original historical wording and intended byte representation; authoritative byte identity against `53ce72b` is required on the user host before commit;
- retains the strengthened existing `skills/automation-safety/SKILL.md`;
- retains GLOBAL_KERNEL routing for filesystem/bulk automation;
- keeps move/delete authority, recursion, collision/no-overwrite, rollback/recovery, read-only inventory/dry-run, and bounded scope jointly explicit;
- keeps GOV-003 prompt, expected behavior, forbidden behavior, criticality, and scoring unchanged.

Prepared-tree checks must be rerun on the user host after replacement. v0.5.17 cannot become the latest frozen reference until source validation, evidence identity, exact-commit Windows/Ubuntu canonical full assurance, and a fresh GOV-003 behavioral attempt all satisfy their existing gates.
