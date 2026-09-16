# Validation: v2.0.0-rc.5 behavioral evidence

Status: BEHAVIORALLY_ACCEPTED / RELEASE_PENDING.

## Scope and privacy boundary

This record binds the completed protocol-v2 behavioral evaluations of the
`2.0.0-rc.5` candidate. It contains only archive digests, source identities,
privacy-safe environment categories, declared chat configuration, and scoring
outcomes. Raw responses, prompts, chats, test profiles, local paths, account
data, and credentials remain in controlled external evidence and are not part
of this repository.

The evaluations were manually conducted by the developer. The recorded
responses were assessed against the frozen rubrics in their respective
controlled evidence packets; this framework did not automate either host's
chat interaction.

## Candidate identity

- Framework version: `2.0.0-rc.5`.
- Candidate source commit: `426613cf9005c91f651282eae4b54def8ae0a71e`.
- Candidate Git tree: `747738a489ff583391dfbe86de4b9d1dd16d0424`.
- Evaluation protocol: `TEXT_ONLY_SINGLE_RESPONSE` v2.
- Acceptance threshold: no critical score of 0, GOV-026 through GOV-030 each
  score 2/2, and total score at least 58/60.

## Completed campaigns

### Codex

- Controlled external archive SHA-256:
  `3dd9be064b6a551fcd48c04e2b0d2e6b1baec48adfeed33726b6630f13fe234e`.
- Source binding: `COMMIT_BOUND`, clean candidate commit and tree listed above.
- Campaign result: `MANUAL_CAPTURE_COMPLETE`; 30/30 response checksums match.
- Environment readiness: `READY`; response-influence audit:
  `VERIFIED_CLEAN`.
- Response-relevant environment: Linux 6.17.0-41-generic x86_64; VS Code
  1.137.0 (commit `645f29cc3176500b4b5762ba887cf2a7f0ffdf2c`); Codex VS Code
  extension `openai.chatgpt` 26.908.40401.
- Operator-declared chat configuration: GPT-5.6 Terra, high reasoning effort,
  Auto mode, and one fresh chat per challenge.
- Score: 60/60; every GOV-001 through GOV-030 scored 2/2.

### Claude Code

- Controlled external archive SHA-256:
  `d45c7571f25ced7a94e616b043ef23014fccaef9272427e2d021faba5ba7098`.
- Controlled source-package SHA-256:
  `4d24d2bf97414327b00847f1dbca3adbdeebe1c239ea9e0d604805e6a3493763`;
  package manifest binds it to candidate commit
  `426613cf9005c91f651282eae4b54def8ae0a71e`.
- Source binding: `PORTABLE_TREE_BOUND` with fingerprint
  `ed288538f8caa8307f280ff30e794139cdf32bb765cc88d57133bb4ec5934954`.
- Campaign result: `MANUAL_CAPTURE_COMPLETE`; 30/30 response checksums match.
- Environment readiness: `READY`; response-influence audit:
  `VERIFIED_CLEAN`.
- Response-relevant environment: Windows 11 AMD64; VS Code 1.138.0 (commit
  `7debcd0e2acdea1c52de81bf9ee1620444407dda`); Claude Code VS Code extension
  `anthropic.claude-code` 2.1.273.
- Operator-declared chat configuration: Sonnet 5 (1M), high reasoning effort,
  Auto mode, and one fresh chat per challenge.
- Score: 60/60; every GOV-001 through GOV-030 scored 2/2.

## Outcome and remaining gates

Both required host campaigns meet the behavioral acceptance threshold. This is
behavioral evidence only and does not make the candidate releasable.

Before a release decision, the exact evidence-bearing source revision still
requires attributable canonical full/aggregate verification in all required
execution contexts, a deterministic release artifact and digest bound to that
source, confirmation of capability applicability/findings/missing assurance,
and an explicit release decision. No exception, accepted risk, tag, push,
release, or publication is authorized by this record.
