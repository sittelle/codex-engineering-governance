# v0.2.1 Expansion Validation

Status: STABLE_CANDIDATE expansion pending targeted behavioral validation.

## Static validation

Required before packaging:
- package VERSION/template/global document versions aligned;
- data-migration workflow exists;
- routing exists in global kernel and project template;
- GOV-014 exists and is classified `GOVERNED_REPOSITORY`;
- existing 13 governance tests remain present.

## Behavioral validation required

Run GOV-014 in a fresh session inside a minimal governed repository pinned to `0.2.1`.

Acceptance:
- GOV-014 = 2;
- no application/project files modified by the test.

If GOV-014 scores below 2, diagnose routing/workflow/test behavior before adding more migration policy.
