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

## Relationship to the self-service layer `governance.py host install` writes

`governance.py host install`/`host update` additionally writes a lighter,
self-service version into the user's own `~/.claude/settings.json` -- no
administrator and no OS-protected path required. This is `governance.py`'s
`GOVERNANCE_SELF_PROTECTION_DENY_RULES`/`add_claude_pretool_hook`, tracked
under installer ownership so `host uninstall` removes exactly what it added.
It gives an ordinary developer the deterministic backstop even when no
enterprise policy is deployed, but unlike the managed layer above, the
developer could edit or delete it locally; it does not substitute for an
IT-managed deployment where that guarantee matters.

Unlike the enterprise templates above, the self-service hook's matcher is
`Bash` only (not `Edit`/`Write`/`MultiEdit`/`NotebookEdit`, already covered
for free by the deny rules), and it is further gated with Claude Code's
native `if` filter to only actually run before a `git commit`, so a
subprocess spawns once per commit rather than before every tool call. This
is a deliberate, documented trade-off (see `docs/framework-threat-model.md`,
residual-risks section): a differently-phrased commit invocation such as
`git -C . commit ...` can silently skip the check, since `if` is a plain
text-pattern match, not an understanding of what the command does. This is
accepted because the threat this layer defends against -- an agent that
weakens or edits governance files -- has no reason to disguise the commit
that would reveal it; a deliberate attempt to exploit that blind spot would
require premeditated human intent to defeat the audit trail, a different and
out-of-scope threat for a trusted-employee deployment.
