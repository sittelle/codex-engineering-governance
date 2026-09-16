# Behavioral evaluation evidence

## Purpose and boundary

Manual behavioral evaluation measures how a selected Codex or Claude Code
integration responds to the fixed GOV scenarios in a realistic IDE workflow.
It is not a substitute for canonical framework verification, package
production, security scanning, or release approval.

Raw responses, test profiles, authentication state, local paths, account
identities, and chat transcripts remain outside the framework repository.
The repository may retain a privacy-safe acceptance record that binds a
controlled external evidence archive by SHA-256.

## Evidence generations

`METADATA_V1_COMPATIBLE` applies to complete protocol-v2 campaigns collected
before this document. A campaign can be accepted at that level when its source
and responses are bound by Git or an equivalent portable byte comparison, and
the developer has accepted its completed scoring review. It is not rewritten
as Metadata v2 evidence.

`METADATA_V2` applies to future campaigns. It adds a response-influence audit
and a context-content identity while preserving the no-credential/no-path
privacy boundary.

## Metadata v2 contract

The collector records only the following response-relevant facts.

### Source and campaign

- framework version, clean Git commit and tree when Git is available, or a
  portable byte-for-byte source binding when it is not;
- evaluation protocol and rendered-prompt/scenario identities;
- response capture method, campaign timestamp, response checksums, and a
  fresh-chat-per-challenge operator declaration when supplied;
- a pre-capture environment-preflight evidence file, hash-bound from the final
  metadata, with source/context, adapter, editor, integration, profile, and
  influence-audit readiness results;
- one logical context per challenge: `GLOBAL_KERNEL`,
  `GOVERNED_REPOSITORY`, or `GOVERNANCE_FRAMEWORK_REPOSITORY`;
- a deterministic fingerprint of the content supplied by that logical context.

Logical context and fingerprint deliberately replace an absolute project path.
The latter is neither portable nor useful as answer provenance.

### Client and session

- operating-system release and architecture;
- VS Code version, commit, architecture, and extension identifiers/versions;
- selected host/integration identifier and version, plus a native host-runtime
  version only when that runtime is actually part of the tested client;
- requested model, effort, mode, and other declared chat settings.

Model and UI selections are `OPERATOR_DECLARED`: a privacy-preserving helper
cannot truthfully claim to have inspected an IDE chat or its account session.

### Response-influence audit

The audit reports category and state, never instruction text, setting values,
paths, user names, credentials, or chat contents. Its categories are:

- managed, user, project, local, ancestor, and organization instruction files;
- rules, workflows, skills, hooks, commands, and MCP configuration;
- automatic/persistent memory;
- host policy/settings and provider-routing overrides; and
- the framework-managed host adapter and generated challenge contexts.

Each category is `ABSENT`, `EXPECTED_MANAGED`, `DECLARED_INFLUENCE`,
`NOT_APPLICABLE`, or `UNKNOWN`. `NOT_APPLICABLE` includes a durable,
content-free reason: it is used only where the selected host has no local
configuration surface in the evaluation contract. A `VERIFIED_CLEAN` campaign
has only absent, expected-managed, or not-applicable categories in the
applicable detector inventory. A campaign with a declared influence is still
valid evidence for that declared environment; it is simply not evidence of the
clean baseline. An unknown category means the helper could not inspect an
applicable source and must never be reported as clean.

The detector directly examines the managed host adapter, host-home
instruction/rule/skill/plugin/settings locations, the dedicated VS Code
test-profile settings, and the generated global/governed/framework contexts.
For Codex it also traverses the applicable `AGENTS.md` ancestor chain and
checks the documented local project surfaces for configuration, rules, skills,
plugins, MCP, hooks, and commands. Codex categories with no local evaluation
surface are `NOT_APPLICABLE`, not `UNKNOWN`. A filesystem read/parse failure is
`UNKNOWN`. This makes a clean isolated Codex home observable rather than
mistaking missing detector coverage for a host influence.

For example, Claude Code can load user, project, local, ancestor, rules, and
automatic-memory material. The v2 detector therefore audits those categories
without copying their contents. The host-specific detector inventory is
versioned so a new client feature becomes `UNKNOWN` until it is supported.

## Acceptance and release use

Candidate behavioral acceptance requires the scoring threshold defined in
`tests/governance/README.md` for both supported hosts. A score review must be
bound to the frozen packet/archive it assessed. Historical failed campaigns
remain failed evidence; a later passing campaign is additive rather than a
rewrite.

This collector does not yet implement response-surface equivalence as a release
shortcut. A fresh complete campaign is therefore required for each candidate
that seeks behavioural acceptance. Any future equivalence mechanism would need
to bind the canonical GOV scenarios, protocol rendering, host operating kernel,
host adapter, generated governed context, and framework context identity; it
would not weaken the separate exact-source requirement for canonical full
verification and release artifacts.

## Privacy and retention

Keep the raw packet and its archive in controlled external storage. A
repository release record may contain only archive SHA-256 values, source
identity, environment categories, score outcome, and a non-path storage
reference. Never commit raw responses, test profiles, tokens, account details,
or local paths.
