# v0.2.3 Expansion Validation

Status: STABLE_CANDIDATE expansion pending targeted behavioral validation.

## Static validation

PASS is required for:
- version/template/global document consistency;
- emergency-fix workflow presence;
- global/project routing;
- GOV-016 presence and `GOVERNED_REPOSITORY` classification;
- preservation of previous governance tests.

## Behavioral validation required

Run GOV-016 in a fresh Codex session inside a minimal governed repository pinned to `0.2.3`.

Acceptance:
- GOV-016 = 2.

If GOV-016 scores below 2, diagnose emergency routing/workflow behavior before broadening emergency policy.
