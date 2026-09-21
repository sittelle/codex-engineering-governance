# Security Review Workflow

SCOPE/OBJECTIVES → CONTEXT/SOURCE STATE → ATTACK SURFACE → THREAT MODEL → CONTROL REVIEW → AUTOMATED EVIDENCE → MANUAL REASONING → FINDINGS → REMEDIATION/RISK → RETEST → CONCLUSION → RETAIN REVIEW EVIDENCE.

Reuse and revalidate an existing threat model when it remains applicable; create or update one when assurance level, architecture, trust boundaries, or material change requires it. Detailed authentication, authorization, input, secrets, cryptography, logging, data, supply-chain, severity, exception, and assurance semantics remain inherited from the secure-development and assurance standards plus applicable specialist skills.

Manual review covers authorization, business logic, trust assumptions, privilege, failure behavior, data exposure, insecure defaults, and other risks scanners cannot establish. A vulnerability finding and missing assurance evidence are distinct states.

A security-review completion record MUST durably identify at minimum:
- review scope, security objectives, and exact source/revision reviewed;
- applicable architecture/trust boundaries and threat-model status;
- automated evidence consulted and required controls that did not execute;
- material manual-review coverage;
- findings and their severity/status/disposition;
- residual risks, explicit risk acceptances, and policy exceptions relevant to the conclusion;
- final SECURITY READY / SECURITY READY WITH ACCEPTED RISKS / NOT SECURITY READY / INCOMPLETE ASSURANCE conclusion.

The record may be represented in an existing issue/review/release system or repository evidence; a dedicated document is not required. `No findings` by itself is not sufficient evidence for SECURITY READY.

Conclusion: SECURITY READY / SECURITY READY WITH ACCEPTED RISKS / NOT SECURITY READY / INCOMPLETE ASSURANCE.

## Developer language routing

Classify a finding requiring risk acceptance as `BUSINESS` or `PROFESSIONAL` per "Developer language and professional decisions" (`global/governance-standard.md`). A `BUSINESS` risk (within the owner's own responsibility) may be accepted by the owner directly and recorded as final. A `PROFESSIONAL` risk (information exposure, unsafe components, access, or effects on other systems) routes to "involve a Professional" and is recorded `PENDING_PROFESSIONAL_REVIEW` until confirmed when `developer_language` is non-professional, or self-certified with explicit acknowledgment and documented as a professional decision when it is professional. When the classification is unclear, classify as `PROFESSIONAL`. `SECURITY READY WITH ACCEPTED RISKS` means every `PROFESSIONAL` risk in it was confirmed by a Professional (or self-certified as such), not that the business owner alone accepted it; a `BUSINESS`-only acceptance does not require that confirmation.
