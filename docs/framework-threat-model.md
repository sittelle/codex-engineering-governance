# Governance Framework threat model

## Scope and non-goals

Scope: the distributed governance package, its normative content, the single `governance.py` host/project management entry point, assurance bootstrap tooling, verification engine, CI templates, and release artifacts. It is not a hosted application or identity service.

## Assets

- normative governance source and version identity;
- unified host/project management tooling, ownership state, and managed-file/settings boundaries;
- verification plans, runners, aggregation logic, and evidence;
- CI workflow definitions and locked security tooling;
- release packages, digests, and release-decision records.

## Actors and trust boundaries

- maintainer/developer approving material governance decisions;
- local operator running `governance.py` host/project lifecycle commands;
- governed-project filesystem and Git repository;
- GitHub-hosted CI runners and pinned third-party Actions;
- external tool/package registries used only through pinned integrity metadata.

## Entry points and data flows

Package acquisition -> local governance root -> `governance.py` -> Codex/Claude host adapters and governed projects. Host/project arguments, user instruction files, Claude settings, ownership state, and project filesystem content cross the management boundary. Source and verification configuration cross into local/CI runners; multiple attributable reports cross into aggregation. Release source and evidence bind to a distributable digest.

## Threats and required controls

1. **Package or update tampering.** Bind release package digest to exact source and verification evidence; pin external automation/tooling; reject hash mismatches.
2. **Destructive/path-handling mistakes.** Every management mutation previews first and requires `y/N` confirmation (`-y` only supplies that answer); bounded managed-file mutation, target validation, dirty-Git safeguards, backups where project files are replaced, and negative lifecycle tests remain mandatory.
3. **Incorrect update/uninstall or managed-content overwrite.** Update/remove only content identified by managed markers plus recorded version/hash/ownership state; preserve project/user-specific `AGENTS.md`, `CLAUDE.md`, locator/settings content; refuse ambiguous or modified managed content rather than guessing.
4. **CI credential or untrusted-PR exposure.** Least-privilege workflow permissions, no `pull_request_target`, no workflow secrets for verification, `persist-credentials: false`, and workflow static analysis.
5. **Misleading assurance evidence.** Commit/plan/baseline/runner binding; dirty/mismatched evidence rejection; explicit DID_NOT_EXECUTE; target-aware v3/v5 evidence; fail dominance; bootstrap-precondition evidence.
6. **Governance self-weakening.** Material control weakening remains C2/C3 and requires explicit approval; no scanner suppression solely to obtain green status.
7. **Claude adapter over-privilege.** Grant the central governance root through one exact `permissions.allow` `Read(...)` rule. Do not make the central root an additional broadly editable working directory; remove only a rule the framework itself added.

## Residual/conditional risks

The publication channel may later trigger SBOM, signing, or stronger provenance requirements. Those controls are not claimed until the channel and threat model justify them. The framework has no application auth surface, runtime service state, container artifact, or deployment IaC today; those controls remain N/A while those facts remain true.
