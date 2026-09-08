# v0.3.3 Assurance Execution Semantics Validation

Status: STABLE_CANDIDATE expansion pending targeted behavioral validation.

## Automated acceptance

- package/version/template/global consistency;
- schema-v2 plan remains compatible with safe defaults;
- STANDARD result policy: nonzero => FAIL;
- documented operational exit code => DID_NOT_EXECUTE / INCOMPLETE_ASSURANCE;
- result policy rejects zero or undocumented custom operational mappings;
- approved execution-context deferral remains incomplete in a single report;
- CI/specialized PASS evidence can satisfy the same required check only through commit/plan/baseline/runner-bound aggregation;
- aggregation rejects mismatched commits and dirty/unknown worktree evidence;
- prior capability-completeness and executable-resolution tests remain passing.

## Behavioral validation

Run GOV-021 and GOV-022 in fresh governed sessions pinned to 0.3.3.

Do not expand policy further until both are understood.
