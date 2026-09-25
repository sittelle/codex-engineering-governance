# Behavioral Test Execution Contexts

## UNGOVERNED

An otherwise empty directory outside any governed project. No scenario runs here. Since ADR 0005 the governance text loads only from a governed repository's `AGENTS.md`, never from user scope; this context exists to verify that no governance text reaches a session outside a governed project. It replaces the former `GLOBAL_KERNEL` context, whose scenarios (GOV-001, GOV-003) moved to `GOVERNED_REPOSITORY`.

## GOVERNED_REPOSITORY

Run in a minimal governed repository whose `project-governance.yml` pins the current governance baseline and whose repository `AGENTS.md` carries the managed governance block and enables central detailed governance loading. Unless a scenario explicitly relies on materialized fixture state, the scenario prompt supplies the authoritative hypothetical engineering facts being evaluated.

## GOVERNANCE_FRAMEWORK_REPOSITORY

Run in the Governance Framework repository with root `AGENTS.md`, `framework-governance.yml`, and `framework-verification-plan.json`. This context tests proportional self-governance of the distributed tooling package rather than an application baseline.

## Supported agent hosts

For the 2.0 candidate line, behavioral acceptance is host-specific.

The complete GOV-001..036 campaign MUST be executed independently on:

- `codex`;
- `claude`.

A passing campaign on one host does not substitute for the other. Each scenario
still uses the execution context declared below; the host dimension is additional
acceptance evidence and does not modify the canonical scenario goal or rubric.

## Classification

| Test | Context |
|---|---|
| GOV-001 | GOVERNED_REPOSITORY |
| GOV-002 | GOVERNED_REPOSITORY |
| GOV-003 | GOVERNED_REPOSITORY |
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
| GOV-031 | GOVERNED_REPOSITORY |
| GOV-032 | GOVERNED_REPOSITORY |
| GOV-033 | GOVERNED_REPOSITORY |
| GOV-034 | GOVERNED_REPOSITORY |
| GOV-035 | GOVERNED_REPOSITORY |
| GOV-036 | GOVERNED_REPOSITORY |
