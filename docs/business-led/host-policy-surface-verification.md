# Host policy surface verification

Verified 2026-09-18, against current documentation, for WS2 of
`docs/business-led/implementation-plan.md`. This is the record required by
the plan's section 10: "Host policy surfaces ... must be verified against
current host documentation at implementation time. Record what you verified
and the host version."

## Claude Code

Verified against `code.claude.com/docs/en/` (managed-settings.md,
settings.md, permissions.md, hooks-guide.md, managed-mcp.md) by the
`claude-code-guide` agent. Host version not independently pinned by the
source docs; treat this record as current for the Claude Code release line
documented at `code.claude.com` on 2026-09-18, and re-verify before the
phase-5 behavioral campaigns if materially more time has passed.

**Managed settings surface: exists.** System-level file, read-only to the
business employee, outranks project and user settings:
- macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`
- Linux/WSL: `/etc/claude-code/managed-settings.json`
- Windows: `C:\Program Files\ClaudeCode\managed-settings.json`

Precedence (highest to lowest): managed settings, `--settings` CLI flag,
`.claude/settings.local.json`, `.claude/settings.json`,
`~/.claude/settings.json`. A small number of security-sensitive keys allow a
*stricter* lower-level value to apply; ordinary policy keys never do.

**Deny-rule syntax: `Tool(specifier)`** in `permissions.deny`, evaluated
deny-then-ask-then-allow, first match wins; a managed deny rule cannot be
overridden by a lower-level allow rule. Confirmed forms: `Edit(...)`,
`Write(...)`, `Read(...)`, `Bash(...)`, with `**`/`*` glob support and `/`,
`./`, `~/`, `//` path-root forms. `disableBypassPermissionsMode: "disable"`
removes the dangerous-skip-permissions escape hatch from managed settings.

**Hook protocol: PreToolUse**, registered under `hooks.PreToolUse` in any
settings file including managed settings. JSON on stdin includes
`session_id`, `cwd`, `hook_event_name`, `tool_name`, `tool_input`. Exit 2
blocks and feeds stderr back to the agent as the reason; exit 0 with JSON
`{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision":
"deny"|"allow"|"ask", "permissionDecisionReason": "..."}}` is the structured
form WS2's `governance.py hook pre-tool` will use, since it carries an
explicit plain-language reason. `allowManagedHooksOnly: true` in managed
settings prevents a project or user from adding competing hooks.

**MCP allowlist: exists**, two mechanisms. `managed-mcp.json` (same
system paths as managed-settings.json) is an exclusive allowlist: only
listed servers load. Alternatively, managed settings' `allowedMcpServers` /
`deniedMcpServers` / `allowManagedMcpServersOnly: true` allowlists by
URL/command pattern with denylist-always-wins semantics.

**Auto-memory / subagent scope: partial gap.** `strictPluginOnlyCustomization`
(managed settings, array of `"agents"|"plugins"|"skills"|"mcp"|"hooks"`)
blocks a project/user from adding new agents, plugins, skills, MCP servers,
or hooks. There is no documented managed setting to disable Claude Code's
persistent memory feature globally, and no single setting caps subagent
permission expansion (each subagent must be denied individually via
`Agent(name)` deny rules). This is a genuine, narrow KNOWN RISK, not a
missing Layer 1 entirely: memory scoping and subagent enumeration are not
centrally enforceable today, so WS2's `managed-settings.*.json` templates
will deny known subagent-expansion vectors by name where practical and
record the memory gap explicitly rather than claiming a control that does
not exist.

## Codex

Verified against `learn.chatgpt.com/docs/enterprise/managed-configuration`,
`/docs/agent-approvals-security`, and `/docs/hooks` (first-party OpenAI
developer docs; `developers.openai.com/codex/...` 308-redirects there) by
direct fetch. Current as of 2026-09-18.

**Managed configuration surface: exists.** `requirements.toml` (hard
constraints, admin-enforced) and `managed_config.toml` (soft defaults):
- Unix: `/etc/codex/requirements.toml`, `/etc/codex/managed_config.toml`
- Windows: `%ProgramData%\OpenAI\Codex\requirements.toml`,
  `~/.codex/managed_config.toml`
- Also deliverable via macOS MDM (preference domain `com.openai.codex`) or a
  cloud-managed bundle fetched on ChatGPT sign-in.

Precedence for requirements (highest to lowest): macOS MDM, cloud-managed
bundle, `managed_config.toml`, system `requirements.toml`. A conflicting
lower-level value is silently replaced with a compliant one, not rejected
with an error.

Enforceable, non-overridable keys include `allowed_approval_policies`,
`allowed_sandbox_modes`, `allowed_permission_profiles`, an `mcp_servers`
approved list, command rules with a `forbidden` decision, and
`deny_read` filesystem restrictions.

**Hook protocol: the same JSON shape as Claude Code.** Registered via
`hooks.json` or an inline `[[hooks.PreToolUse]]` table in `config.toml`.
Same `hookSpecificOutput.permissionDecision` (`allow`/`deny`) and
`permissionDecisionReason` fields; `updatedInput` can rewrite tool
arguments. Enterprise admins set `[hooks]` with
`allow_managed_hooks_only = true` in `requirements.toml` so a project or
user cannot remove or shadow the managed hook. This means WS2's
`governance.py hook pre-tool` command can share its JSON I/O contract
across both hosts; only the registration file/location and the managed-tier
delivery path differ.

**MCP allowlist: exists.** `mcp_servers` in `config.toml`/`requirements.toml`
matches by name and identity; an empty list disables all MCP servers.
`enabled_tools`/`disabled_tools` further scope which tools of an allowed
server are exposed. Organizations can allowlist server URLs or ban stdio
servers outright at the `requirements.toml` level.

**Sandbox modes** (`workspace-write`, `read-only`, `danger-full-access`) are
OS-enforced (Seatbelt on macOS, Landlock+seccomp on Linux) and independently
useful as a second, coarser control alongside deny rules; `.git`, `.agents/`,
and `.codex/` are always read-only under `workspace-write`, which is a
relevant existing floor for the governance-artifact protection WS1 already
adds at the application layer.

## Conclusion for WS2

Neither host requires a KNOWN RISK for "no managed policy surface exists" —
both have one, both support PreToolUse-equivalent hooks with a compatible
JSON contract, and both support MCP allowlisting. The one genuine gap
(Claude Code has no global memory-disable or subagent-cap setting) is
recorded above and will be carried into the threat model / risk register
rather than worked around with a fake project-level setting.
