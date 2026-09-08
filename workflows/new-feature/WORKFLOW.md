# New Feature Workflow

UNDERSTAND EXISTING CONTEXT → DEFINE BEHAVIOR → IMPACT ANALYSIS → CLASSIFY → ACCEPTANCE CRITERIA → APPROVE C2/C3 → IMPLEMENT SMALLEST COMPLETE CHANGE → VERIFY → DOCUMENT.

Inspect AGENTS, governance manifest, relevant requirements/architecture/security/ADRs/tests first.

Escalate for new persistence, external service, network exposure, auth, sensitive data, privilege, destructive behavior, major dependency, or schema change.

## Technology Baseline escalation

If feature implementation would introduce, remove, or replace architecture-significant language/toolchain, runtime, primary framework/platform, persistence, deployment/packaging, supported target, or another stack-shaping component, do not treat that change as an incidental implementation shortcut.

Pause the ordinary feature path for that delta, route/reuse `technology-selection` and the `dependency-change` workflow (plus data/security/migration workflows when triggered), and produce the required **Technology Baseline Transition Summary** before C2/C3 approval or substantial migration implementation. Continue unrelated feature work on the `ESTABLISHED` baseline when feasible.
