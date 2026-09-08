# Release Workflow

FIX SOURCE REVISION → LOAD RELEASE ASSURANCE CONTEXT → CHANGE REVIEW → CLEAN BUILD/PACKAGE → FUNCTIONAL/QUALITY CHECKS → SECURITY CHECKS → DEPENDENCY/SBOM/ARTIFACT REVIEW → DOC/RISK REVIEW → FULL/AGGREGATED EVIDENCE → ARTIFACT BINDING → DECISION RECORD → PUBLICATION/DEPLOYMENT.

Use the assurance architecture, verification standard, severity policy, and exception policy. Detailed result, capability-completeness, execution-context, aggregation, and release-blocker semantics remain inherited from those normative sources and MUST NOT be redefined here.

Before READY or READY WITH ACCEPTED RISKS:
- identify the exact clean source revision and applicable maturity/assurance target;
- use attributable canonical `full` verification, aggregating approved contexts when needed;
- reject dirty, mismatched, stale, or otherwise non-attributable evidence;
- confirm required capability completeness and security/dependency release gates;
- bind each released distributable to the source revision and verification evidence with an immutable artifact identity/digest; include SBOM/provenance/signing evidence when applicable;
- retain the minimum release decision record required by the verification standard, including relevant findings, missing assurance, exceptions, and accepted risks.

Decision: READY / READY WITH ACCEPTED RISKS / NOT READY / INCOMPLETE ASSURANCE.

Required scanner/capability `DID_NOT_EXECUTE` means INCOMPLETE ASSURANCE. An attributable required-check `FAIL` remains FAIL even if another approved context passed. Risk acceptance and policy exception do not rewrite underlying evidence. Readiness and consequential publication/deployment are separate approval boundaries.

## Required-control response completeness

When the release/readiness question is caused by a required control that is missing, omitted, or `DID_NOT_EXECUTE`, the response is incomplete unless it explicitly states:
- that the control is required/applicable and the current evidence is non-PASS / `INCOMPLETE_ASSURANCE`;
- that accepting the risk of a known vulnerability/finding is a different decision from granting a governance/policy exception to proceed without the required control, and one cannot substitute for the other;
- that any permitted missing-control exception is separate and does not relabel the missing control as PASS;
- when multiple approved execution contexts are relevant, that evidence must remain attributable to the same clean commit/plan/baseline/runner semantics and an attributable executed `FAIL` remains fail-dominant even if another context passes.

Do not shorten this to “everything else passed” or “CI can run it later”; those phrases omit the decision boundary the release owner must understand.

If a post-release issue is discovered, preserve the affected release/artifact identity and route the work according to impact: plausible security impact → security-review; urgent stabilization → emergency-fix; ordinary product defect → bug-fix. Consequential withdrawal, rollback, replacement, or deployment actions still follow the applicable approval boundary.
