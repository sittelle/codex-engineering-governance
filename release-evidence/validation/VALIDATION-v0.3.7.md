# v0.3.7 Cross-Context Failure Dominance and Aggregate Observability Validation

Scope: evidence aggregation only; no new assurance capability or application policy domain.

Field trigger: real Windows LOCAL + Ubuntu CI evidence for the same governed TEST commit produced a correct `EVIDENCE BUNDLE: FAIL`, but console output listed only missing required evidence and did not identify the attributable CI check failure. The aggregate implementation already gave any attributable required-check FAIL precedence over PASS evidence from another context; the failure cause was insufficiently observable in the aggregate output.

Automated acceptance:
- all previous governance tests preserved;
- any required-check FAIL in any attributable report dominates PASS evidence from another approved context for the same commit/plan/baseline/runner state;
- aggregate machine evidence records failing context(s), exit code, disposition, and reason reference available from the input report;
- aggregate console output names the failing check and failing context(s);
- `DID_NOT_EXECUTE` cross-context completion semantics remain unchanged;
- commit/plan/baseline/runner identity and clean-worktree aggregation gates remain unchanged.

Behavioral validation:
- GOV-026 must score 2.

Field follow-up: rerun aggregation for the same TEST evidence after updating only managed governance artifacts; do not modify application behavior merely to make the project green.
