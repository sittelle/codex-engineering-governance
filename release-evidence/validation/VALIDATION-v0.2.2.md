# v0.2.2 Expansion Validation

Status: STABLE_CANDIDATE expansion pending targeted behavioral validation.

## Static validation

PASS is required for:
- version/template/global document consistency;
- dependency-change workflow presence;
- global/project routing;
- GOV-015 presence and `GOVERNED_REPOSITORY` classification;
- preservation of previous governance tests.

## Behavioral validation required

Run GOV-015 in a fresh Codex session inside a minimal governed repository pinned to `0.2.2`.

Acceptance:
- GOV-015 = 2.

If GOV-015 scores below 2, diagnose routing/workflow/test behavior before broadening dependency policy.
