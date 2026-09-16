# Validation: v2.0.0-rc.7 Windows metadata-probe preservation

Status: BEHAVIORALLY_ACCEPTED / RELEASE_PENDING.

## Carried evidence

The complete Codex and Claude Code campaigns bound in
`VALIDATION-v2.0.0-rc.5.md`, then carried to rc.6 by
`VALIDATION-v2.0.0-rc.6.md`, carry to this successor. Both campaigns were
clean-environment, protocol-v2 evaluations with 30/30 checksum-verified
responses and scores of 60/60. Their controlled external archive digests and
privacy-safe environment metadata remain unchanged.

## Response-surface preservation

The predecessor candidate is `d7702b5ade07d3af040f0400347675de8ef78dcd`.
This candidate changes only Windows evaluation provenance collection:

- it reads VS Code's installed product metadata instead of launching the VS
  Code Electron CLI for `--version`; and
- it reads extension identity/version from the selected dedicated test
  profile's installed extension manifests instead of asking the Electron CLI
  to list extensions.

The correction prevents an access-denied Crashpad diagnostic when a helper is
itself run inside a Codex sandbox. It does not change scenarios or rubrics,
protocol-v2 prompt rendering, host operating kernel/adapters, managed
instructions, generated global/governed/framework contexts, selected host
integration, or normal host/profile setup behavior. Therefore no fresh manual
campaign is required.

This preservation does not satisfy or replace exact-commit canonical full/CI
evidence, deterministic artifact binding, or an explicit release decision.
