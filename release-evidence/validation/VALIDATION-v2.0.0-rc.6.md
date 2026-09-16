# Validation: v2.0.0-rc.6 response-surface preservation

Status: BEHAVIORALLY_ACCEPTED / RELEASE_PENDING.

## Carried evidence

The Codex and Claude Code campaigns bound in
`VALIDATION-v2.0.0-rc.5.md` carry to this successor candidate. Both were
complete, clean-environment, 30/30 hash-verified protocol-v2 campaigns scored
60/60. Their external archive digests and privacy-safe environment metadata
remain unchanged and are not copied here.

## Response-surface preservation

The predecessor evidence-bearing commit is
`becb3ef09cd25d8b8a1b7592320fbec5f211ee3d`. This candidate changes only:

- the Windows bootstrap helper's `Set-TestProfileTheme` function, adding a
  `ShouldProcess` gate around its existing write; normal `-Apply` execution
  performs the same directory creation and settings write as before; and
- the durable policy/documentation needed to recognize this bounded class of
  non-response-affecting successor.

The following remain unchanged: GOV scenarios and rubrics, protocol-v2 prompt
rendering, host operating kernel and adapters, managed instructions, generated
global/governed/framework contexts, selected host integration, and normal test
profile setup behavior. Therefore no fresh manual campaign is required.

This preservation does not satisfy or replace exact-commit canonical full/CI
evidence, deterministic artifact binding, or an explicit release decision.
