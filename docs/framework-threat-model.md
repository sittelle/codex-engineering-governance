# Governance Framework threat model

## Scope and non-goals

Scope: the distributed governance package, its normative content, the single `governance.py` host/project management entry point, assurance bootstrap tooling, verification engine, CI templates, and release artifacts. It is not a hosted application or identity service.

## Assets

- normative governance source and version identity;
- unified host/project management tooling, ownership state, and managed-file/settings boundaries;
- verification plans, runners, aggregation logic, and evidence;
- CI workflow definitions and locked security tooling;
- locally retained manual behavioral-evaluation response packets;
- dedicated local VS Code test profiles, which can contain agent authentication
  state but are never campaign/package artifacts;
- local checksum-locked VM bootstrap artifacts and their installer cache;
- release packages, digests, and release-decision records;
- when developer_language is non-professional: the project registration file and the assurance facts
  derived from it, the governance-artifact integrity baseline, and the
  Professional's approval-authority state.

## Actors and trust boundaries

- maintainer/developer approving material governance decisions;
- local operator running `governance.py` host/project lifecycle commands;
- governed-project filesystem and Git repository;
- GitHub-hosted CI runners and pinned third-party Actions;
- external tool/package registries used only through pinned integrity metadata;
- when developer_language is non-professional: the business employee operating a managed client
  without administrative rights, who directs the agent but cannot judge
  security or approve risk, and a Professional, who holds approval authority and
  configures the Layer 1 managed policy the employee cannot alter (see
  `docs/adr/0001-business-led-mode-architecture.md` and
  `docs/adr/0002-developer-language-and-professional-terminology.md`);
- untrusted inbound content reaching the agent during normal work: file
  contents, tool/command output, web-fetched pages, dependency documentation,
  issue/PR text, and MCP tool responses. This content can attempt to redirect
  the agent's behavior and is a trust boundary regardless of mode.

## Entry points and data flows

Package acquisition -> local governance root -> `governance.py` -> Codex/Claude host adapters and governed projects. Host/project arguments, user instruction files, Claude settings, ownership state, and project filesystem content cross the management boundary. Source and verification configuration cross into local/CI runners; multiple attributable reports cross into aggregation. Release source and evidence bind to a distributable digest.

When developer_language is non-professional, the Professional's registration crosses into the project as
machine-readable input at bootstrap; derived assurance facts and the
integrity baseline cross into the runner and the governance hook. The managed
client's Layer 1 settings (deny rules, hook, read-only framework root) and the
CI pipeline's enforcement variable cross into every agent session and every
protected pipeline run.

## Threats and required controls

1. **Package or update tampering.** Bind release package digest to exact source and verification evidence; pin external automation/tooling; reject hash mismatches.
2. **Destructive/path-handling mistakes.** Every management mutation previews first and requires `y/N` confirmation (`-y` only supplies that answer); bounded managed-file mutation, target validation, dirty-Git safeguards, backups where project files are replaced, and negative lifecycle tests remain mandatory.
3. **Incorrect update/uninstall or managed-content overwrite.** Update/remove only content identified by managed markers plus recorded version/hash/ownership state; preserve project/user-specific `AGENTS.md`, `CLAUDE.md`, locator/settings content; refuse ambiguous or modified managed content rather than guessing.
4. **CI credential, manual-response, or untrusted-PR exposure.** Routine
   verification workflows receive no secrets. The manual behavioral kit does
   not invoke an AI, accept an API key, initialize Git, upload responses, or
   overwrite an existing campaign directory. Its optional Windows/Ubuntu
   conductor only copies a rubric-free prompt to the local clipboard, opens the
   declared local context, and records an operator-pasted response. Force-close
   is unavailable without a separately marked VS Code test profile outside both
   the framework source and campaign; it never targets the normal profile.
   Test profiles and raw responses remain under the tester's local control and
   are excluded from campaign/scoring/package content. Workflow static analysis
   remains required.
5. **Unreviewed VM bootstrap or installer substitution.** The optional exact
   route accepts only a reviewed lock with HTTPS source URLs and SHA-256 pins,
   re-verifies cached/downloaded artifacts before install, refuses mismatches
   and existing partial artifacts, and requires a separate explicit install
   confirmation. The current-release route deliberately obtains vendor
   `latest` packages only for disposable VMs; its results are never claimed
   bit-for-bit reproducible, and the response-relevant installed environment
   is captured with the campaign. Neither route accepts licence terms or signs
   in on behalf of an operator.
6. **Misleading assurance evidence.** Commit/plan/baseline/runner binding; dirty/mismatched evidence rejection; explicit DID_NOT_EXECUTE; target-aware v3/v5 evidence; fail dominance; bootstrap-precondition evidence.
7. **Governance self-weakening.** Material control weakening remains C2/C3 and requires explicit approval; no scanner suppression solely to obtain green status.
8. **Claude adapter over-privilege.** Grant the central governance root through one exact `permissions.allow` `Read(...)` rule. Do not make the central root an additional broadly editable working directory; remove only a rule the framework itself added.
9. **Governance-artifact tampering by the agent (non-professional developer_language).** An agent
   directed by a business employee who cannot judge security may edit or
   remove governance-owned files -- managed blocks in `AGENTS.md`/`CLAUDE.md`,
   `project-governance.yml` governance-owned fields, the capability/facts
   inventory in `verification-plan.json`, the baseline copy, the copied
   runner, the CI workflow, or the registration file -- to make a project pass
   or to widen its own operating room. Byte-for-byte managed-block comparison,
   a release-pinned baseline-hash allowlist, and an instruction-surface audit
   against a hash-pinned registration allowlist detect this and produce
   `INCOMPLETE_ASSURANCE` with a specific issue code rather than a silent
   pass. Deterministic Layer 1 controls (deny rules, hook, read-only framework
   root) prevent the edit outright where the managed client is trustworthy;
   the detection above remains the backstop where it is not.
10. **Inbound prompt injection.** Instructions embedded in files, tool
    results, web content, dependency documentation, issues, or MCP responses
    can attempt to redirect agent behavior, including toward weakening its
    own governance. Only the kernel, managed blocks, approved rules, and the
    user's direct messages carry authority; content from every other source
    is data, never instruction. This is a Layer 3 (prompt) control and is
    treated as probabilistic; material consequences are additionally covered
    by a Layer 1/2 control from this list where one exists (for example,
    threat 9 for a request to edit governance files, or threat 7's
    `vcs-safety` control for a request to force-push).
11. **Agent over-privilege via runtime configuration.** MCP servers, hooks,
    plugins, subagents, memory, and permission/bypass modes are configuration
    surfaces that change what the agent can do, not ordinary project content.
    An unreviewed addition or change to any of them is a trust-boundary
    change. When developer_language is non-professional these surfaces are enumerated by the
    instruction-surface audit (threat 9) and, where materiality is not
    self-evident from the audit alone, governed as a C2 (C3 with production
    systems or credentials) decision under `global/operating-contract.md`,
    never silently self-approved by the agent.
12. **Registration drift.** A project's registered capability flags (network
    connections, persistence, authentication, write/delete actions, cloud,
    external recipients, elevated access) can fall out of sync with what the
    code actually does, whether by omission, later feature growth, or
    deliberate evasion. Capability-detection rules compare implementation
    against the registration; an unregistered capability produces
    `REGISTRATION_RECONCILIATION_REQUIRED` and a durable request record
    routed to a Professional. Development continues; the drift is surfaced, not
    blocked, consistent with the framework never blocking development on its
    own.

## Residual/conditional risks

The publication channel may later trigger SBOM, signing, or stronger provenance requirements. Those controls are not claimed until the channel and threat model justify them. The framework has no application auth surface, runtime service state, container artifact, or deployment IaC today; those controls remain N/A while those facts remain true.

The non-professional developer_language model carries additional residual risk while its constraining
assumptions hold (`docs/business-led/implementation-plan.md` section 11): if
a managed client turns out to grant the business employee administrative
rights, Layer 1 controls become deterrence only and the CI pipeline remains
the sole trustworthy evidence gate. If a curated package proxy does not
exist, dependency-existence and authenticity guidance remains in force but
its deterministic backstop is absent. If Codex offers no managed policy
surface equivalent to Claude Code's managed settings, Codex's Layer 1 is
incomplete and this is recorded as a known risk rather than papered over with
a project-level, user-editable setting.
