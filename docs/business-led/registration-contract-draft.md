# Registration contract — design draft

Phase 0 design draft for the registration contract named in
`docs/business-led/implementation-plan.md` WS4 and referenced by ADR
[0001](../adr/0001-business-led-mode-architecture.md). This is not the
schema. It fixes the shape and semantics so that phase 2 can formalize it as
`assurance/registration.schema.json` and
`templates/repository/registration.yml` without a mid-phase redesign. If
implementation in phase 2 finds a field here unworkable, that is an OPEN
QUESTION to surface, not a license to silently redesign this contract.

## Purpose

The registration is IT Security's record of what a business-led project is
approved to be and do. It is Layer 2 (agent-readable, governance-tooling
writable; see the ADR). The framework derives assurance facts from it and
later detects when implementation drifts away from it. It is not a project
plan, not a requirements document, and not something the agent or the
business employee fills in on their own.

## Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `registration_id` | string | Stable identifier IT Security assigns to this registration, independent of the project name. |
| `pathway` | enum: `green`, `amber`, `red` | The risk-assessment outcome from `docs/business-led/implementation-plan.md` section 5. Drives maturity/assurance and approval routing; does not itself gate development. |
| `business_owner` | string | Who owns the outcome and validates acceptance criteria. Maps to `roles.business_owner` in `project-governance.yml` (WS3). |
| `approval_authority` | string | The IT Security contact or team who approved this registration and who receives routed decisions. Maps to `roles.approval_authority`. |
| `capabilities` | object of booleans | Approved capability flags: `network_connections`, `persistence`, `authentication`, `write_or_delete_actions`, `cloud`, `external_recipients`, `elevated_access`. Each is IT Security's explicit approval that the project may exhibit that capability, not a detection result. |
| `operating_conditions` | free-text/structured, IT Security's choice | Conditions attached to the pathway (for example, Amber conditions under which the business owner may proceed). Recorded, not interpreted by the framework beyond display. |
| `allowlisted_instruction_surfaces` | list of `{path, sha256}` | The exact project `.claude/` rules, skills, agents, commands, hooks, settings, `.mcp.json`, and non-managed `AGENTS.md`/`CLAUDE.md` text IT Security has reviewed and approved. Anything present but not on this list is flagged by the instruction-surface audit (WS1). |
| `integrity` | `{sha256, sealed_by, sealed_at}` | The hash IT Security's tooling (or, until a tool exists, `governance.py registration seal`) computes over the registration content, so a later hand-edit is detectable. |

## Derivation into existing assurance facts

The registration does not introduce a parallel fact model. Its capability
flags are the source the framework reads to set the existing
`verification-plan.json` `assurance.facts` block and the existing
`project-governance.yml` `project.maturity` / `project.assurance` fields:

- `capabilities.network_connections` or `capabilities.cloud` -> informs
  `has_exposed_web_surface`;
- `capabilities.persistence` -> informs `has_persisted_data`;
- `capabilities.authentication` or `capabilities.elevated_access` ->
  triggers the authentication-design boundary in
  `global/operating-contract.md` when locally managed identity is present;
- `pathway` -> informs `project.maturity` / `project.assurance` per the
  pathway-mapping table in the ADR (Green: M1/SA1, or SA0 for disposable
  local-only prototypes; Amber: M1 or M3/SA2; Red: SA2 or SA3).

Facts derived this way are governance-owned. A hand-edited fact that
contradicts its registered derivation is an integrity failure (WS1), not a
project-local decision.

## Lifecycle

1. IT Security fills the registration template by hand (assumption in plan
   section 11: no registration tool exists yet). If this assumption proves
   false before phase 2 implementation, the tool's output must still conform
   to this contract; nothing else changes.
2. `governance.py registration seal` computes `integrity.sha256` over the
   content IT Security approved.
3. `governance.py project new|adopt --registration <file>` requires the file
   in business-led mode, derives the assurance facts above, and refuses to
   proceed if the registration fails to parse or its seal does not verify.
4. `scripts/run-registration-conformance.py` (WS4, phase 3) later compares
   detected capabilities against `capabilities` and reports
   `REGISTRATION_RECONCILIATION_REQUIRED` on drift, per threat 12 in
   `docs/framework-threat-model.md`.

## Deferred to phase 2 implementation

- The exact JSON Schema (`assurance/registration.schema.json`) and template
  (`templates/repository/registration.yml`), including validation error
  messages.
- Whether `operating_conditions` needs internal structure or remains free
  text for phase 2's scope (structure can be added later without breaking
  this contract, since it is display-only today).
- The exact seal algorithm's canonicalization of the registration content
  (for example, key ordering) before hashing, needed so
  `governance.py registration seal` is reproducible.
