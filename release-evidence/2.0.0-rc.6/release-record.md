# Release record — 2.0.0-rc.6

- Source commit: `d7702b5ade07d3af040f0400347675de8ef78dcd`
- Source worktree: `CLEAN` at package build. An unrelated local diagnostic
  file is not part of the source revision or artifact.
- Distribution artifact: `sittelle-engineering-governance-v2.0.0-rc.6.zip`
- SHA-256:
  `b6d1f0fe12d9f5de9d91242a0ea76cae5391e5ba3381baaa2d797481e5a956e8`
- Build/package procedure:
  `python scripts/build-release-package.py --repo . --output-dir <external-output-dir>`.
  The repository-owned builder read only clean Git `HEAD` content, produced
  two independent byte-identical ZIPs, and wrote the SHA-256 sidecar.
- Build runtime: Python `3.14.6`.
- Canonical full evidence: GitHub Actions run
  [`35090502462`](https://github.com/sittelle/codex-engineering-governance/actions/runs/35090502462),
  executed against the source commit above. The canonical aggregate artifact
  is `framework-evidence-aggregate` (ID `10444351116`).
- Aggregate result: `EVIDENCE BUNDLE: PASS`. The Windows PowerShell SAST
  check, which had failed on the predecessor source revision, is `PASS` for
  this exact source revision. The individual Linux and Windows producer
  reports correctly leave the other platform's checks `DID_NOT_EXECUTE`; the
  attributable aggregate combines the required target evidence.
- Behavioral evidence: the complete, clean-environment Codex and Claude Code
  protocol-v2 campaigns recorded in
  `release-evidence/validation/VALIDATION-v2.0.0-rc.5.md` carry to this
  source under the bounded response-surface-preservation proof in
  `release-evidence/validation/VALIDATION-v2.0.0-rc.6.md`. Both campaigns
  captured 30/30 checksum-verified responses and scored 60/60. Raw prompts,
  responses, chats, account data, profiles, and local paths remain outside
  the repository.
- Capability/applicability: this is the M2/SA1 distributed governance/tooling
  package. `framework-verification-plan.json` remains its single source of
  assurance applicability. The required canonical verification, lifecycle and
  package regression, Windows/POSIX evidence, secret scanning, meaningful
  SAST, CI/evidence integrity, and release artifact/source/full-evidence
  binding are retained. Auth/authz review, DAST, container and deployment-IaC
  scanning, recovery verification, and dependency SCA remain
  `NOT_APPLICABLE` only under their recorded factual triggers.
- Findings / missing assurance: none attributable to this source revision.
- Exceptions / accepted risks: none.
- Conditional SBOM/signing/provenance: SBOM and cryptographic signing are not
  required for the present ZIP publication model and recorded framework facts;
  they must be reassessed if the distribution channel or factual triggers
  change. Provenance is supplied by the exact commit, deterministic artifact
  digest, and attributable cross-platform canonical evidence above.
- Decision: `READY` for release preparation.
- Decision authority/reference: developer-approved RC6 release-readiness
  evaluation on 2026-09-16. Git tag creation, artifact upload, and public
  publication remain separate consequential actions requiring explicit
  authorization.
