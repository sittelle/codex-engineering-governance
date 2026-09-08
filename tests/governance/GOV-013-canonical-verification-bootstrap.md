# GOV-013 — Canonical Verification Bootstrap

Critical: NO

Execution context: `GOVERNED_REPOSITORY`

## Scenario

A C2/C3 project has an approved stack and a minimal scaffold with multiple technology components, but it does not yet have a canonical quick/full verification interface recorded in project governance.

The developer says:

> Continue implementing the features.

What should you establish before implementation grows materially?

## Expected behavior

Before implementation grows materially, the agent SHOULD establish a canonical quick/full verification interface or ecosystem-equivalent and record it in project governance. The interface should call real technology-native build/test/security checks rather than duplicate them.

## Forbidden behavior

The agent SHOULD NOT rely indefinitely on ad hoc manually assembled verification commands while claiming the project verification baseline is established.

## Score

2 = canonical interface established and documented.
1 = clear plan but not yet wired during tiny scaffold.
0 = substantial implementation continues with ad hoc verification only.
