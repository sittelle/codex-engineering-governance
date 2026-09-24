# New Feature Workflow

UNDERSTAND EXISTING CONTEXT → DEFINE BEHAVIOR → IMPACT ANALYSIS → CLASSIFY → ACCEPTANCE CRITERIA → APPROVE C2/C3 → IMPLEMENT SMALLEST COMPLETE CHANGE → VERIFY → DOCUMENT.

Inspect AGENTS, governance manifest, relevant requirements/architecture/security/ADRs/tests first.

Escalate for new persistence, external service, network exposure, auth, sensitive data, privilege, destructive behavior, major dependency, or schema change.

## Technology Baseline escalation

If feature implementation would introduce, remove, or replace architecture-significant language/toolchain, runtime, primary framework/platform, persistence, deployment/packaging, supported target, or another stack-shaping component, do not treat that change as an incidental implementation shortcut.

Pause the ordinary feature path for that delta, route/reuse `technology-selection` and the `dependency-change` workflow (plus data/security/migration workflows when triggered), and produce the required **Technology Baseline Transition Summary** before C2/C3 approval or substantial migration implementation. Continue unrelated feature work on the `ESTABLISHED` baseline when feasible.

## Acceptance criteria and test traceability

The ACCEPTANCE CRITERIA step produces criteria in a form that can be traced to tests: each REQUIRED-NOW criterion stated concretely enough that a specific automated test (or tests) can be named against it, including the negative/failure case where the criterion has a material boundary. Do not leave criteria as vague intent that only the implementation itself could be checked against.

The VERIFY step confirms every REQUIRED-NOW acceptance criterion actually has a corresponding automated test in the canonical `full` path before the feature is reported complete. A criterion with no test is reported as such, not silently dropped or assumed covered. See `skills/testing-strategy/SKILL.md` for how to derive and write those tests.

## Documentation

The DOCUMENT step is part of the change, not a follow-up: update the user, API, or operator documentation the feature affects, and name which documents in the plan. If no documentation is affected, record `NOT APPLICABLE` with a reason.

## Developer language routing

When `developer_language` is non-professional, route this workflow's material decision points through the five outcomes in "Routing outcomes" (`global/governance-standard.md`) instead of developer approval: continue, update registration, obtain reassessment, involve a Professional, or hand over to a Professional. When it is professional, a decision that would route to "involve a Professional" instead self-certifies with the explicit acknowledgment mechanism in the kernel. Record a request per "Request records" when the outcome is "involve a Professional" (non-professional) or "obtain reassessment".
