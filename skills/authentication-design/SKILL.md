# Authentication Design

**Version:** 0.1.1  
**Status:** Draft  
**Purpose:** Design authentication, session, credential, enrollment, and recovery lifecycles before implementation.

## Activate When

Use this skill when a project introduces or materially changes local username/password authentication, sessions/cookies, access/refresh tokens, administrator bootstrap, enrollment tokens, certificate-based client/service identity, account recovery/reset, MFA, credential revocation/re-enrollment, or machine/service authentication.

It is REQUIRED before substantial SA-2/SA-3 locally managed authentication implementation.

## Core Principle

Authentication is a lifecycle and trust-boundary design problem, not merely password hashing or token generation. Prefer established platform/framework/library/provider mechanisms over custom authentication protocols.

## Required Inputs

Establish as applicable: actors/identity types, deployment/exposure, assurance level, authoritative identity source, authentication factors, administrative model, recovery expectations, machine/service identities, trust boundaries, and credential-storage environment.

## Identity Lifecycle

Define creation/enrollment, activation, authentication, credential changes, suspension/disablement, revocation, deletion, and recovery/re-enrollment. Do not implement only the happy-path login operation.

## Password Credentials

If passwords are used, use an established password-hashing implementation, define parameter/version migration, never store plaintext/reversible equivalents, define brute-force/rate controls, and define change/reset semantics. Selecting scrypt/Argon2id/bcrypt through a mature implementation is not by itself a complete authentication design.

## Sessions

Define creation, storage, expiration/idle timeout, rotation, revocation, logout, concurrent-session behavior, and browser cookie protections where applicable.

## Bootstrap

Initial administrator/bootstrap flows MUST define where bootstrap may run, how local/operator authority is established, what artifacts it creates, whether it can run more than once, recovery if bootstrap state is lost, and audit evidence. Bootstrap MUST NOT become a hidden permanent backdoor.

## Enrollment Tokens

If one-time enrollment tokens are used, define entropy/source, storage representation, expiry, single-use enforcement, intended identity/device binding where useful, invalidation/revocation, replay behavior, and transport assumptions.

## Certificate / mTLS Identity

If certificate identity is used, define CA ownership, private-key storage, subject/device identity, issuance, validity, renewal, revocation/replacement, CA backup/recovery, CA rotation, and compromise response. Do not generate a local CA without defining its lifecycle.

## Recovery

Recovery flows are authentication flows. Define who may recover, proof required, lost-device/controller behavior, reset/re-enrollment, and emergency administrator recovery. Avoid recovery weaker than the normal authentication model without explicit rationale.

## Authorization Separation

Successful authentication only establishes identity. Invoke `authorization-review` for permission/resource decisions.

## Testing

Test valid/invalid login, brute-force/rate behavior, expired/revoked sessions, logout, password changes/resets, token replay/single-use/expiry, revoked/unknown certificates, recovery, and bootstrap overwrite protection as applicable.

## Output

Produce identity sources/types, authentication mechanism, credential storage, session lifecycle, bootstrap, enrollment, certificate lifecycle, recovery/revocation, rate/abuse controls, security assumptions, negative tests, residual risks, and open questions.

## Stop Conditions

Stop before implementation if recovery semantics, CA/certificate lifecycle, enrollment replay/expiry, bootstrap authority, or safe credential storage are materially unresolved; or if a custom protocol is proposed without compelling justification.

## Forbidden Behaviors

Do not treat password hashing as the entirety of authentication, invent token/session protocols casually, create permanent bootstrap bypasses, issue long-lived enrollment tokens without lifecycle controls, create a CA without recovery/rotation planning, store plaintext credentials, or treat authentication as authorization.
