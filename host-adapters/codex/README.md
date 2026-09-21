# Codex managed-configuration templates

`requirements.inform.toml` and `requirements.block.toml` are the Codex
counterpart to `host-adapters/claude/managed-settings.*.json`, from ADR
[0001](../../docs/adr/0001-business-led-mode-architecture.md). IT
deploys exactly one of them, unedited except for `[mcp_servers]` (populate
with the actually-approved servers; an empty table denies all MCP servers by
default), to the path documented in
`docs/business-led/host-policy-surface-verification.md`:

- Unix (Linux/macOS): `/etc/codex/requirements.toml`
- Windows: `%ProgramData%\OpenAI\Codex\requirements.toml`

`requirements.toml` is a hard-constraint file: a conflicting lower-level
value (project or user `config.toml`) is silently replaced with a compliant
one rather than erroring, per Codex's documented managed-configuration
precedence.

## What the two templates do

Both restrict approval policy to `on-request` and sandbox mode to
`read-only`/`workspace-write` (never `danger-full-access`), restrict
permission profiles to `:read-only` and `:workspace`, deny reading common
credential locations (`deny_read`), forbid the same destructive Git history
command prefixes as the Claude Code templates (force-push, hard reset,
filter-branch, update-ref, interactive rebase, reflog expiry/deletion),
allowlist MCP servers, and register `governance.py hook pre-tool` as a
managed `PreToolUse` hook (`allow_managed_hooks_only = true`) for
`apply_patch`/`Bash`.

They differ in exactly one parameter passed to that hook: `--inform` vs
`--enforce`, matching the Claude Code templates.

## What this cannot protect against

Codex's documented managed-configuration surface has no confirmed mechanism
for denying **edits** to specific file paths (only `deny_read`, a read
restriction, is documented). This is a genuine, recorded KNOWN RISK, not an
oversight: `project-governance.yml`, `verification-plan.json`,
`registration.yml`, and similar governance-owned files cannot be
pre-emptively write-protected at this layer the way Claude Code's
`permissions.deny` `Edit(...)`/`Write(...)` rules do it. Codex's sandbox
does independently keep `.git`, `.agents/`, and `.codex/` read-only under
`workspace-write` mode, which is a useful existing floor but does not cover
the governance files above, since those live in the ordinary working
directory. The compensating control is the same one WS1 already built:
`assurance/run-verification.py`'s governance-integrity preflight detects the
edit after the fact in every quick/full report, and the `PreToolUse` hook
above denies (in `--enforce` mode) or warns (in `--inform` mode) based on
that same detection the next time a mutating tool runs. Re-verify this gap
against current Codex documentation before relying on it for a Red-pathway
project; if a file-path deny mechanism is added later, this template should
be extended to use it.
