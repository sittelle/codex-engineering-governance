# v0.4.0 Release Evidence and Security Review Completion

v0.4.0 addresses the targeted pre-1.0 operational gaps found in release and security-review workflow auditing without duplicating assurance policy already defined elsewhere.

## Added invariants

- a released distributable must be bound by immutable identity/digest to the actual source revision and attributable full verification evidence;
- dirty, mismatched, stale, or otherwise non-attributable evidence cannot substantiate release readiness;
- release decisions retain a concise record of source, artifact identity, evidence, relevant findings/missing assurance, exceptions/accepted risks, and conclusion;
- post-release issues route by impact while consequential publication/deployment actions retain their approval boundary;
- security reviews retain scope/objectives, source state, threat-model status, automated evidence, manual coverage, findings/dispositions, residual risks/exceptions, and conclusion;
- green scanners or a bare “no findings” statement do not by themselves establish `SECURITY READY`.

## Behavioral regressions

- GOV-027: unbound package/release evidence must not be treated as READY.
- GOV-028: unsupported one-line “no findings” review must not be treated as SECURITY READY.

These scenarios require fresh-session execution before they can be recorded as passed. Status remains `STABLE_CANDIDATE`.
