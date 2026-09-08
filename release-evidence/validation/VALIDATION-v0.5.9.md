# Validation v0.5.9

Status: STABLE_CANDIDATE.

Scope: compatibility hardening for migration of already-governed pre-Technology-Baseline repositories. This version does not alter the approved Technology Baseline policy, assurance schemas, security release gates, scanner policy/pins, or GOV-029/GOV-030 rubrics.

Field defect that triggered the change:

- the `codex-governance-eval` fixture was still pinned to governance 0.4.0 when the first GOV-030 probe was attempted;
- the v0.5.8 governed-project updater preview showed that it would update only governance baseline/source/locator and the AGENTS managed block;
- inspection confirmed the updater preserved an existing `technology_baseline` but did not add one when upgrading a legacy governed manifest that lacked the field;
- therefore a legacy project could claim the v0.5.8+ governance version while lacking the newly required Technology Baseline state.

v0.5.9 correction:

- Windows and POSIX updaters conditionally add a missing top-level `technology_baseline` with `RECONCILIATION_REQUIRED`;
- the standard durable pointer is `docs/design.md#technology-baseline`;
- existing Technology Baselines are preserved rather than overwritten;
- update previews disclose the conditional migration;
- lifecycle tests include legacy-missing-baseline migration plus existing-baseline preservation on Windows and POSIX;
- packaged GOV-029 attempt-3 evidence is restored to the frozen v0.5.7 wording.

Behavioral status:

- GOV-029: PASS at latest completed attempt 3 (2/2).
- GOV-030: no valid completed evaluation record yet. The earlier response from a 0.4.0-pinned evaluation repository is not counted.

Candidate validation must include:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native Windows lifecycle regression
- POSIX lifecycle regression through CI/Ubuntu
- fresh GOV-030 evaluation only after the evaluation fixture is genuinely migrated to the current governance baseline
- attributable Windows/Ubuntu canonical full evidence for the exact frozen v0.5.9 commit

Pre-1.0 release rehearsal remains after GOV-030 and v0.5.9 machine assurance close.
