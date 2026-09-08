# v0.3.0 Assurance Architecture Validation

Status: STABLE_CANDIDATE capability release pending targeted behavioral validation.

## Static acceptance

- VERSION/template/normative documents aligned;
- assurance architecture and capability matrix present;
- verification-plan JSON schema present;
- dependency-free reference runner present;
- safe unconfigured plan template present;
- GOV-018 and GOV-019 present and classified GOVERNED_REPOSITORY;
- all prior governance tests preserved.

## Reference runner semantics

Expected:
- placeholder/unavailable required command => DID_NOT_EXECUTE and process exit 2;
- required command exit nonzero => FAIL and process exit 1;
- all required applicable checks pass => PASS and process exit 0;
- non-applicable check => NOT_APPLICABLE and does not cause incomplete assurance.

## Behavioral validation required

Run in fresh governed sessions pinned to 0.3.0:
- GOV-018 must score 2;
- GOV-019 must score 2.

Do not add more assurance policy until both regressions are understood.
