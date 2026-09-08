# v0.2.6 Expansion Validation

Status: STABLE_CANDIDATE expansion pending targeted behavioral validation.

## Static validation

PASS is required for:
- version/template/global document consistency;
- refactor workflow presence;
- global/project routing;
- GOV-017 presence and `GOVERNED_REPOSITORY` classification;
- preservation of previous governance tests.

## Behavioral validation required

Run GOV-017 in a fresh Codex session inside a minimal governed repository pinned to `0.2.6`.

Acceptance:
- GOV-017 = 2.

If GOV-017 scores below 2, diagnose refactor routing/workflow behavior before broadening refactor policy.
