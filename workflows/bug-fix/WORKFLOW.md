# Bug Fix Workflow

REPRODUCE → ISOLATE → ROOT CAUSE → SECURITY IMPACT → REGRESSION TEST → MINIMAL FIX → ADJACENT CASE REVIEW → VERIFY → DOCUMENT.

Do not patch symptoms while knowingly leaving root cause unresolved. Security-relevant bugs escalate to security review.

## Developer language routing

When `developer_language` is non-professional, route this workflow's material decision points through the five outcomes in "Routing outcomes" (`global/governance-standard.md`) instead of developer approval: continue, update registration, obtain reassessment, involve a Professional, or hand over to a Professional. When it is professional, a decision that would route to "involve a Professional" instead self-certifies with the explicit acknowledgment mechanism in the kernel. Record a request per "Request records" when the outcome is "involve a Professional" (non-professional) or "obtain reassessment".
