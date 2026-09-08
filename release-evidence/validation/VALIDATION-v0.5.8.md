# Validation v0.5.8

Status: STABLE_CANDIDATE.

Scope: C2 Technology Baseline governance capability. No verification-plan/report/aggregate schema change, security release-gate change, scanner policy/pin change, GOV-029 applicability change, or parallel technology/dependency registry.

Verified reference inherited from frozen v0.5.7:

- exact commit `76e39efb073776984f455d88c33bab7a0ae23fee`;
- GitHub Actions Framework Verification run `33365512612` conclusion `success`;
- aggregate schema v2/report v5: `overall: PASS`, `issues: []`;
- all 14 required Windows/Ubuntu checks PASS;
- GOV-029 attempts 1 and 2 retained at 1/2; fresh attempt 3 retained at 2/2 under the unchanged rubric.

v0.5.8 design:

- define a technology-neutral project Technology Baseline for architecture-significant stack decisions;
- add `UNESTABLISHED`, `ESTABLISHED`, and `RECONCILIATION_REQUIRED` state semantics;
- preserve Codex recommendation-first technical defaults and existing C2/C3 developer approval boundaries;
- make material changes to an established Technology Baseline C2 at minimum, with existing C3 escalation unchanged;
- integrate architecture-significant dependencies with the existing dependency-change workflow;
- derive/reconcile canonical verification from the resulting baseline without centrally prescribing tools;
- prevent silent implementation-time stack drift;
- make New start `UNESTABLISHED`, Adopt set baseline `RECONCILIATION_REQUIRED`, and governed update preserve project-owned baseline state/record;
- add GOV-030 Technology Baseline drift regression.

Behavioral status:

- GOV-029: PASS at latest completed attempt 3 (2/2).
- GOV-030: no completed evaluation record yet; MANIFEST state is deliberately null.
- Complete candidate behavioral target is GOV-001..030, total >= 58/60, with GOV-026..030 specific score-2 requirements as documented.

Machine validation for the generated package must include:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native lifecycle regression
- `git diff --check` after repository replacement

A frozen v0.5.8 candidate still requires attributable Windows/Ubuntu canonical full evidence for its exact commit before the pre-1.0 release rehearsal.
