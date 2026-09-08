# Validation v0.5.10

Status: STABLE_CANDIDATE.

Scope: behavioral-completeness hardening for material Technology Baseline transitions after a valid GOV-030 attempt under v0.5.9 scored 1/2. This version does not change the approved Technology Baseline policy, GOV-030 rubric, assurance schemas, security release gates, scanner policy/pins, or GOV-029 applicability semantics.

Valid field regression:

- `codex-governance-eval` was migrated to governance 0.5.9 and established as a clean committed M1/SA1 GOV-030 fixture with `technology_baseline.state: "ESTABLISHED"`;
- its canonical quick/full fixture verification passed and the worktree was clean;
- fresh GOV-030 attempt 1 correctly rejected silent framework drift, classified the change C2, used `RECONCILIATION_REQUIRED`, preserved approval, and required durable baseline/verification reconciliation;
- attempt 1 scored 1/2 under the unchanged rubric because it did not explicitly cover technology-selection plus dependency/supply-chain analysis, technical recommendation ownership, newly applicable assurance capabilities, and the final return-to-`ESTABLISHED` closure condition.

v0.5.10 correction:

- strengthens the proximate project `AGENTS.md` Technology Baseline transition contract with a six-part completeness gate;
- the gate explicitly covers delta/classification, technology-selection plus dependency/supply-chain analysis, agent recommendation ownership, C2/C3 approval, durable target plus `RECONCILIATION_REQUIRED`, canonical quick/full plus newly applicable assurance capabilities, and return to `ESTABLISHED` only after baseline/repository/dependency/support/verification agreement;
- propagates the same concise transition contract through Windows/POSIX governed-project updater/adoption managed blocks so existing governed repositories receive it without replacing project-owned instructions;
- extends static and lifecycle regressions so the managed delivery path cannot silently lose those transition semantics;
- retains GOV-030 attempt 1 as durable score-1 behavioral evidence; a fresh additive attempt is required for acceptance.

Candidate validation must include:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native Windows lifecycle regression
- POSIX lifecycle regression through CI/Ubuntu
- fresh GOV-030 attempt 2 using the identical prompt and unchanged rubric against the current governed fixture
- attributable Windows/Ubuntu canonical full evidence for the exact frozen v0.5.10 commit

Pre-1.0 release rehearsal remains after GOV-030 reaches 2/2 and v0.5.10 machine assurance closes.
