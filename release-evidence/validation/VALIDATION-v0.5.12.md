# Validation v0.5.12

Status: STABLE_CANDIDATE.

Scope: durable behavioral-evidence and release-readiness accounting after GOV-030 attempt 3 reached 2/2. No Technology Baseline policy or scoring change is introduced.

Field evidence leading to this patch:

- `codex-governance-eval` was clean and pinned to governance 0.5.11 at commit `990d47dc0ace0c426c3735601f8a242bd07f32dc`;
- fixture canonical quick/full verification passed;
- fresh attempt 3 used the identical GOV-030 prompt and unchanged rubric;
- the response rejected silent drift, classified the Fastify replacement C2 minimum, preserved recommendation/approval ownership, explicitly routed through new-feature + technology-selection + dependency-change, required supply-chain and triggered impact analysis, used `RECONCILIATION_REQUIRED`, reconciled quick/full plus newly applicable assurance capabilities, and required closure criteria before restoring `ESTABLISHED`;
- attempt 3 scored 2/2. Attempts 1 and 2 remain retained at 1/2 as historical evidence. No policy exception or risk acceptance was used.

v0.5.12 changes only evidence/accounting surfaces and authoritative version pins required for a new package version. It does not change verification-plan/report/aggregate schemas, Technology Baseline semantics, the GOV-030 rubric, security release gates, scanner policy/tool pins, or GOV-029 semantics.

Candidate validation must include:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native Windows lifecycle regression
- POSIX lifecycle regression through CI/Ubuntu
- attributable Windows/Ubuntu canonical full evidence for the exact frozen v0.5.12 commit

After exact-commit machine assurance closes, perform the pre-1.0 release rehearsal and retained release-decision evidence.
