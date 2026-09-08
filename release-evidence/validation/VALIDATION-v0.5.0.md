# Validation — v0.5.0

Status: `STABLE_CANDIDATE`.

## Scope

v0.5.0 introduces a lightweight self-governance foundation for the Governance Framework repository and a generic target-aware assurance contract without changing existing governed-project verification-plan v2 / report v4 semantics.

## Required deterministic validation

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `python scripts/test-framework-lifecycle.py --mode common`
- host-native lifecycle mode (`windows` or `posix`)
- `python scripts/verify-framework.py quick`
- concrete ZIP validation with `validate-governance.py --artifact <zip>`

Full release assurance additionally requires locked security-tool bootstrap, Windows and Ubuntu canonical full evidence, and target-aware aggregate evidence for the same clean commit/plan/baseline/runner.

## Behavioral validation

GOV-029 is new and remains unevaluated until a fresh governed framework-repository session is recorded. GOV-027 and GOV-028 were evaluated 2/2 under v0.4.0 and are retained as durable historical evidence.

## New invariants

- v2 plans retain context-only semantics and emit report v4.
- v3 plans may declare required OS/machine targets and emit report v5.
- target identity is derived by the trusted runner from coarse context plus the actual host.
- nonmatching target -> `DID_NOT_EXECUTE / ENVIRONMENT_MISMATCH`.
- target-aware aggregation requires every required target and emits bundle v2.
- v4 evidence cannot satisfy v3 target guarantees; mixed v4/v5 aggregation is rejected.
- Windows/Ubuntu CI jobs are evidence producers; the target-aware aggregate is the combined release gate.
- framework bootstrap failure must still yield canonical incomplete-assurance evidence.
