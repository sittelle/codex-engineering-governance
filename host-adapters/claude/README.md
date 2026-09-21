# Claude Code managed-settings templates

`managed-settings.inform.json` and `managed-settings.block.json` are Layer 1
templates from ADR [0001](../../docs/adr/0001-business-led-mode-architecture.md).
IT deploys exactly one of them, unedited except for
`allowedMcpServers` (populate with the actually-approved servers for the
deployment; an empty list plus `allowManagedMcpServersOnly: true` denies all
MCP servers by default), to the OS-specific managed-settings path documented
in `docs/business-led/host-policy-surface-verification.md`:

- macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`
- Linux/WSL: `/etc/claude-code/managed-settings.json`
- Windows: `C:\Program Files\ClaudeCode\managed-settings.json`

The business employee and the agent cannot read, edit, or remove this file;
it outranks project and user settings unconditionally.

## What the two templates do

Both deny editing whole-file governance artifacts (`project-governance.yml`,
`verification-plan.json`, `.governance/`, `.claude/`, `.mcp.json`,
`registration.yml`, `CLAUDE.local.md`), reading common credential locations,
destructive Git history operations, and the dangerous-skip-permissions
bypass mode. Both allowlist MCP servers and restrict agents/plugins/skills/
hooks/MCP additions to the managed layer only
(`strictPluginOnlyCustomization`). Both register `governance.py hook pre-tool`
as a `PreToolUse` hook for `Edit`/`Write`/`MultiEdit`/`NotebookEdit`/`Bash`.

They differ in exactly one parameter passed to that hook:
`--inform` (the default) surfaces a governance-integrity or
missing-registration/Red-pathway finding as a visible warning without
blocking; `--block` denies the tool call with the same plain-language
reason. See `governance.py`'s `hook_pre_tool_decision` for the exact
conditions.

## What this cannot protect against

A partial-file edit inside `AGENTS.md`/`CLAUDE.md` (the managed governance
block, alongside legitimate project-specific text in the same file) cannot
be denied at this file-path granularity, since the file also needs to
remain editable for non-managed content. WS1's managed-block byte comparison
and `.governance/integrity.json` are the compensating control: the hook
above surfaces exactly that comparison's result in real time, and
`assurance/run-verification.py`'s preflight surfaces it in every quick/full
report.

Claude Code has no documented managed setting to globally disable the
persistent memory feature or cap subagent permission expansion; see the
"Auto-memory / subagent scope" section of
`docs/business-led/host-policy-surface-verification.md` for the recorded
KNOWN RISK. `strictPluginOnlyCustomization` prevents *adding* new agents,
which narrows but does not eliminate this gap.
