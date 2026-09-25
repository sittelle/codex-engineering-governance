# ADR 0005: Load governance only in governed projects

## Status

Proposed, 2026-09-25. Requested by Gregor Kleiber, framework maintainer: the
framework should be present only in governed projects, not in every Claude
Code or Codex session on the machine, and should impose the lowest token cost
that still achieves its goals. To be implemented after the current regression
campaign. This is a C2 change (installer behavior, templates, normative text
layout, evaluation contexts) and needs maintainer approval of the detailed
design below before implementation.

## Context

### Current layout

- `governance.py host install` writes the operating kernel (source
  `host-adapters/operating-kernel.md`, 19,992 of its 20,000-character budget)
  into user scope: a managed block in `~/.claude/CLAUDE.md` and in
  `~/.codex/AGENTS.md`, plus the `GOVERNANCE_ROOT` locator and, for Claude, two
  read-permission rules.
- Each governed project carries `AGENTS.md` (17,508 characters: a 9,103-character
  managed block plus 8,405 characters of loading matrix and project sections),
  and `CLAUDE.md`, which imports it with `@AGENTS.md`.

So the kernel loads into every session on the machine, governed or not
(~20,000 characters with no use outside governed work), and a governed
session loads kernel plus project file (~37,500 characters), much of it
duplicated: the managed block restates kernel invariants in condensed form.
The same rules are maintained in four places (kernel, the regenerated
`codex-home/AGENTS.md`, the template's managed block, and marker lists in
`scripts/validate-governance.py` and `scripts/test-framework-lifecycle.py`),
which already caused sync defects during the 2026-09 campaigns.

### Vendor guidance

- Anthropic ([memory docs](https://code.claude.com/docs/en/memory)): user
  `~/.claude/CLAUDE.md` is for "personal preferences for all projects" and
  applies to "every Claude Code session on the machine, in every repository.
  For repository-specific guidance, commit a project CLAUDE.md instead."
  Organization-wide mandatory rules belong in the managed-policy `CLAUDE.md`.
  Keep each file under about 200 lines; move multi-step procedures to skills
  or path-scoped rules. Imports load at launch and do not reduce context.
- OpenAI ([AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md)):
  a global `~/.codex/AGENTS.md` for guidance across repositories, project
  `AGENTS.md` files from the Git root down to the working directory,
  concatenated. `CODEX_HOME` selects "a different profile".

Both vendors place repository-specific guidance in the repository.

### Constraints found

- **Claude external imports:** an import in a project `CLAUDE.md` that
  resolves outside the project (for example `@~/.claude/...`) needs a one-time
  approval dialog per project; declining disables it permanently, and the
  dialog cannot appear in non-interactive runs.
- **Codex has no import mechanism** in `AGENTS.md`.
- **Codex project-doc budget:** `project_doc_max_bytes`, 32 KiB by default.
  Verified in `codex-rs/core/src/agents_md.rs`: the budget covers project
  files only (the global file is not counted), and a file exceeding the
  remaining budget is truncated, not skipped. Content past the limit is
  silently lost.
- **Codex untrusted projects:** project `AGENTS.md` files are not loaded at
  all for an untrusted project (same source file).

## Options considered

| Option | Summary | Verdict |
|---|---|---|
| A. Separate config homes | Install into `~/.claude-governed` / `~/.codex-governed`; a shell wrapper selects them when the working directory contains `project-governance.yml`. | Works without framework changes, but depends on per-user shell setup, needs a separate sign-in per home, and the VS Code extension does not follow the wrapper. `CODEX_HOME` profiles are documented by OpenAI; `CLAUDE_CONFIG_DIR` is not presented by Anthropic as a profile mechanism. |
| B. Home-directory import | Project `CLAUDE.md` imports `@~/.claude/sittelle/kernel.md`; Codex uses a `CODEX_HOME` profile. | Two mechanisms; the Claude import needs a per-project approval that non-interactive runs cannot give. |
| C. Kernel in the project | The project's `AGENTS.md` managed block carries the whole host-neutral kernel, merged and deduplicated with today's managed content. Codex reads it natively, Claude through the existing `@AGENTS.md` import. | One mechanism for both hosts, vendor-aligned, no external imports, no per-user setup, works in the VS Code extension. **Proposed.** |
| D. Status quo | Global kernel. | Contradicts the requirement. |

## Decision (proposed)

Adopt option C.

1. **Governance text lives only in the governed project.** The managed block
   of `templates/repository/AGENTS.md` (and `AGENTS.non-professional.md`)
   becomes the single normative always-loaded text: today's kernel content
   plus today's managed-block content, deduplicated, written host-neutrally
   (both hosts' locator paths in one sentence; no host-specific "Active host"
   line).
2. **One canonical source.** A single source file (for example
   `host-adapters/governance-block.md`) replaces `host-adapters/operating-kernel.md`,
   the generated `codex-home/AGENTS.md`, and the separately edited template
   block; `governance.py project new/update` renders it into projects. The
   validator and lifecycle tests check markers against that one source.
3. **Host level keeps only machine-specific state.** `host install` writes the
   `GOVERNANCE_ROOT` locator and, for Claude, the two exact read rules (root
   and locator), and no instruction text. `host update` removes the
   framework-owned block from existing `~/.claude/CLAUDE.md` / `~/.codex/AGENTS.md`
   installations under the existing ownership rules (only the recorded
   block, refuse if modified).
4. **Budgets sized to the hosts.** The whole project `AGENTS.md` stays at or
   below 28 KiB (bytes, UTF-8), leaving headroom under Codex's 32 KiB
   truncation limit for project-owned sections; the validator measures bytes
   of the rendered file, not characters of the source. Target for the merged
   managed block: at most 24,000 characters.
5. **No governance outside governed projects.** Nothing is written to user
   scope that loads into ungoverned sessions. A new governed project is
   started with `governance.py project new`, after which the new-project
   workflow applies inside it.
6. **Company deployment unchanged in principle.** Organization-mandatory
   rules remain the managed-policy layer (existing managed-settings hooks,
   optionally a managed `CLAUDE.md` / Codex `requirements.toml`), which users
   cannot exclude.

## Runtime token impact (estimate, to be measured during implementation)

| Session | Today | Proposed |
|---|---|---|
| Outside a governed project | ~20,000 characters (kernel) | 0 |
| Inside a governed project | ~37,500 characters (kernel + project file, with overlap) | at most 28 KiB, target lower after deduplication |

Moving situational checklists to on-demand native skills (a separate
proposal, not part of this ADR) could reduce the governed figure further.

## Consequences

Positive:

- Ungoverned sessions carry no framework text and no token cost.
- Governed sessions load one deduplicated document instead of two overlapping
  ones.
- One source of normative text removes the four-copy sync problem.
- The governance text in a project matches the baseline the project pins;
  instruction/version drift between a central install and a project
  disappears.
- Works identically in the CLI and the VS Code extension, with no shell setup.

Negative and risks:

- Kernel updates reach a project only through `governance.py project update`
  (consistent with baseline pinning, but a behavior change for users used to
  a single host-level update).
- The phase before a project exists is no longer governed by default.
- Codex does not load project `AGENTS.md` in an untrusted project; the
  project must be trusted for governance to apply.
- A project `AGENTS.md` over 32 KiB is silently truncated by Codex; the byte
  budget and the instruction-loading check must guard this.
- GOV-001 and GOV-003 run in the `GLOBAL_KERNEL` context (kernel without a
  project), which ceases to exist.

## Implementation plan

1. Write the merged, host-neutral block source; measure deduplication against
   the budgets.
2. `governance.py`: render the new block in `project new/update`; reduce
   `host install` to locator and read rules; migrate existing host installs by
   removing the recorded instruction block. Update `scripts/test-management.py`
   and the lifecycle tests.
3. Validator: one marker source, byte budget of the rendered project file.
4. Evaluation harness: replace the "installed kernel" probe with a
   project-block probe; add a negative probe that an ungoverned directory has
   no governance text in context; add a probe line near the end of the
   project file so Codex truncation is detected.
5. Scenario contexts: move GOV-001 and GOV-003 to the governed-project context
   (scenario definition revision, recorded here once approved).
6. Docs: README host-adapter section, framework threat model (smaller
   user-scope footprint), evaluation VM docs.
7. Full campaign on both hosts.

## Open questions for approval

1. GOV-001/GOV-003: move to the governed-project context (recommended), or
   keep a separate "fresh governed project" context.
2. User scope: write nothing at all (recommended, per the requirement), or a
   one-line pointer to `governance.py project new` at a cost of about 100
   characters per session.
3. Byte budget: 28 KiB for the whole project file (recommended), or document
   raising `project_doc_max_bytes` in Codex configuration instead.
