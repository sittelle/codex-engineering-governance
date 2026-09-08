# Validation v0.5.11

Status: STABLE_CANDIDATE.

Scope: behavioral-delivery hardening after valid GOV-030 attempt 2 under v0.5.10 again scored 1/2. The Technology Baseline policy and unchanged GOV-030 rubric remain authoritative.

Field evidence leading to this patch:

- `codex-governance-eval` was clean and pinned to governance 0.5.10 at commit `188bf17569766dbc90c9fc2b72f5813e51645189`;
- fixture canonical quick/full verification passed;
- fresh attempt 2 rejected silent/incidental framework drift, classified the delta C2 at minimum, preserved approval, required dependency/framework analysis, used `RECONCILIATION_REQUIRED`, and required durable baseline plus canonical quick/full reconciliation;
- attempt 2 scored 1/2 because it still omitted explicit recommendation ownership, explicit technology-selection plus dependency/supply-chain routing, newly applicable assurance-capability reconciliation, and the final `ESTABLISHED` closure condition.

v0.5.11 correction:

- introduces a named **Technology Baseline Transition Summary** as a structured information/output contract, not a new file or parallel governance system;
- the summary explicitly labels delta/classification, technical recommendation, dependency/supply-chain and other triggered impacts, approval state, transition state/durable record, verification/assurance reconciliation, and `ESTABLISHED` closure criteria;
- requires `NOT APPLICABLE` with reason rather than silent omission of a genuinely irrelevant transition dimension;
- adds explicit new-feature escalation when implementation discovers/proposes an architecture-significant Technology Baseline delta, routing to existing `technology-selection` and `dependency-change` mechanisms instead of treating it as an implementation shortcut;
- propagates the structured summary contract through the project template and Windows/POSIX updater/adoption managed blocks;
- extends static/lifecycle regression markers for the structured summary and new-feature routing;
- retains GOV-030 attempts 1 and 2 as additive score-1 evidence. A fresh identical-prompt attempt 3 is required for acceptance.

No change to verification-plan/report/aggregate schemas, security release gates, scanner policy/tool pins, GOV-029 semantics, or the GOV-030 rubric.

Candidate validation must include:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native Windows lifecycle regression
- POSIX lifecycle regression through CI/Ubuntu
- fresh GOV-030 attempt 3 using the identical prompt and unchanged rubric against a clean current governed fixture
- attributable Windows/Ubuntu canonical full evidence for the exact frozen v0.5.11 commit

Pre-1.0 release rehearsal remains after GOV-030 reaches 2/2 and v0.5.11 machine assurance closes.
