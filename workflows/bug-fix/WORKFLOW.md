# Bug Fix Workflow

REPRODUCE → ISOLATE → ROOT CAUSE → SECURITY IMPACT → REGRESSION TEST → MINIMAL FIX → ADJACENT CASE REVIEW → VERIFY → DOCUMENT.

Do not patch symptoms while knowingly leaving root cause unresolved. Security-relevant bugs escalate to security review.

## Business-led mode routing

In business-led mode (`governance.mode: business-led`), route this workflow's material decision points through the five outcomes in "Business-led mode routing outcomes" (`global/governance-standard.md`) instead of developer approval: continue, update registration, obtain reassessment, involve IT Security, or hand over to IT. Record a request per "Business-led mode request records" when the outcome is "involve IT Security" or "obtain reassessment".
