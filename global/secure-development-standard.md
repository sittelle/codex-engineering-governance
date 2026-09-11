# Secure Development Standard

Version 2.0.0-rc.1.

## Assurance

SA-0 Experimental — disposable/local, no meaningful sensitive data/exposure/privilege.
SA-1 Standard — default maintained personal/internal software.
SA-2 Elevated — meaningful network exposure, multi-user identity, protected/sensitive data, material integrations/privilege/automation.
SA-3 High Assurance — security-critical/high-value secrets/privileged/dangerous/high-consequence systems.

An Internet-reachable application that authenticates multiple users or protects user-specific data MUST default to at least SA-2 unless documented analysis demonstrates the risk driver does not apply.

## Requirements and threats

Security requirements are first-class. SA-2/SA-3 require proportionate threat modeling covering assets, actors, entry points, trust/privilege boundaries, data flows, abuse cases, controls, assumptions, and residual risk.

## Defaults and privilege

Secure by default. Deny by default. Fail closed. Least privilege for users, processes, containers, DB accounts, service identities, CI tokens, and integrations.

## Authentication

Use mature platform/library/provider mechanisms. Do not invent password hashing, session, token, MFA, reset, or authentication protocols when established mechanisms exist.

For SA-2/SA-3 systems with locally managed authentication or enrollment, a security design MUST precede substantial implementation and cover as applicable:
- identity source and account lifecycle;
- password/credential storage;
- session creation, storage, expiry, rotation, revocation, and logout;
- recovery/reset;
- brute-force/rate controls;
- enrollment-token lifetime, single-use semantics, and revocation;
- certificate identity, issuance, storage, renewal, revocation, and CA recovery/rotation;
- compromise and re-enrollment behavior;
- administrator bootstrap and recovery.

Security primitives MAY be used through established libraries, but primitive selection alone does not constitute an authentication design.

## Authorization

Authentication is not authorization. Authorize actor/action/resource/condition at the authoritative boundary. Client UI and identifier obscurity are not security controls. Test negative access cases.

## Untrusted input

Treat HTTP, headers/cookies, files, JSON/XML/YAML, CLI/env, archives, URLs, external APIs, DB imports, IPC, Git input, and AI output as untrusted where applicable. Validate and bound resource consumption.

## Injection and output

Use structured/parameterized APIs for SQL, shell/PowerShell, templates, LDAP/XPath/NoSQL, HTML, and similar executable contexts. Apply context-aware output encoding/sanitization.

## Secrets

Never intentionally store real secrets in source, Git history, logs, fixtures, images, docs, or built artifacts. A committed real credential is potential compromise; analyze exposure and rotate/revoke as appropriate.

## Cryptography

No custom primitives/protocols. Use maintained established libraries and CSPRNGs.

## Logging

Log security-relevant events without passwords, tokens, keys, authorization headers, or unnecessary sensitive content.

## Supply chain and CI

Inventory material dependencies, use deterministic resolution, scan vulnerabilities, review security-sensitive dependencies, constrain CI privileges, protect secrets, and maintain artifact traceability.

## Verification

Combine threat/design review, tests, SAST, SCA, secret scanning, build/config review, and DAST/fuzz/container/IaC controls where risk warrants. A scanner is evidence, not proof.

## Findings and release

Finding statuses: OPEN, REMEDIATING, MITIGATED, FALSE_POSITIVE, NOT_APPLICABLE, RISK_ACCEPTED, CLOSED.

Critical: release blocker.
High: release blocker absent exceptional explicit developer risk acceptance.
Required security tool DID_NOT_EXECUTE: release assurance incomplete and release not ready.

The agent may analyze and recommend risk acceptance but MUST NOT approve it.


## Required-control execution semantics

A required assurance control that did not execute successfully is not equivalent to a security finding and MUST NOT be represented as `PASS`, "zero findings", or successful assurance.

If a required SAST, secret scan, SCA, DAST, container, IaC, or other mandated assurance control is unavailable, fails to run, is misconfigured, or otherwise produces no valid result:

- status is `INCOMPLETE ASSURANCE`;
- release readiness remains blocked where that control is required;
- ordinary vulnerability/finding risk acceptance does not convert the missing evidence into a pass.

Proceeding without a required assurance control requires a distinct, explicit governance/policy exception that:
- identifies the missing control and affected release/scope;
- explains why execution is impossible or disproportionate;
- records compensating evidence/controls;
- names the approving developer/owner;
- is time-bounded or release-bounded;
- preserves the truthful status that the required control itself did not pass.

The agent MUST NOT approve such an exception on its own and MUST NOT silently make the control optional.
