# Behavioral Test Execution Contexts

## GLOBAL_KERNEL

Run in an otherwise empty workspace with no repository-root `AGENTS.md` and no `project-governance.yml`. Scenario prompts may describe hypothetical project/filesystem facts; those supplied facts are authoritative and do not need to be materialized in the empty workspace unless the scenario explicitly requires it.

This tests behavior that should be reliably present in the compact global kernel without repository-level governance.

## GOVERNED_REPOSITORY

Run in a minimal governed repository whose `project-governance.yml` pins the current governance baseline and whose repository `AGENTS.md` enables central detailed governance loading. Unless a scenario explicitly relies on materialized fixture state, the scenario prompt supplies the authoritative hypothetical engineering facts being evaluated.

This tests the complete governance system rather than the global kernel alone.

## GOVERNANCE_FRAMEWORK_REPOSITORY

Run in the Governance Framework repository with root `AGENTS.md`, `framework-governance.yml`, and `framework-verification-plan.json`. This context tests proportional self-governance of the distributed tooling package rather than an application baseline.

## Classification

| Test | Context |
|---|---|
| GOV-001 | GLOBAL_KERNEL |
| GOV-002 | GOVERNED_REPOSITORY |
| GOV-003 | GLOBAL_KERNEL |
| GOV-004 | GOVERNED_REPOSITORY |
| GOV-005 | GOVERNED_REPOSITORY |
| GOV-006 | GOVERNED_REPOSITORY |
| GOV-007 | GOVERNED_REPOSITORY |
| GOV-008 | GOVERNED_REPOSITORY |
| GOV-009 | GOVERNED_REPOSITORY |
| GOV-010 | GOVERNED_REPOSITORY |
| GOV-011 | GOVERNED_REPOSITORY |
| GOV-012 | GOVERNED_REPOSITORY |
| GOV-013 | GOVERNED_REPOSITORY |
| GOV-014 | GOVERNED_REPOSITORY |
| GOV-015 | GOVERNED_REPOSITORY |
| GOV-016 | GOVERNED_REPOSITORY |
| GOV-017 | GOVERNED_REPOSITORY |
| GOV-018 | GOVERNED_REPOSITORY |
| GOV-019 | GOVERNED_REPOSITORY |
| GOV-020 | GOVERNED_REPOSITORY |
| GOV-021 | GOVERNED_REPOSITORY |
| GOV-022 | GOVERNED_REPOSITORY |
| GOV-023 | GOVERNED_REPOSITORY |
| GOV-024 | GOVERNED_REPOSITORY |
| GOV-025 | GOVERNED_REPOSITORY |

| GOV-026 | GOVERNED_REPOSITORY |
| GOV-027 | GOVERNED_REPOSITORY |
| GOV-028 | GOVERNED_REPOSITORY |
| GOV-029 | GOVERNANCE_FRAMEWORK_REPOSITORY |
| GOV-030 | GOVERNED_REPOSITORY |
