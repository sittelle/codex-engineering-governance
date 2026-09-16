# Release record — 2.0.0-rc.7

- Source commit: `9554d0ad1286fd885bcac243b6e82598cbd0b87a`
- Source worktree: `CLEAN` isolated Git worktree at package build. The
  developer's primary worktree and its unrelated local diagnostic file were
  not used.
- Distribution artifact: `sittelle-engineering-governance-v2.0.0-rc.7.zip`
- SHA-256:
  `27bfd66799606b5cd7d511e3e1c97569a3028d4e130051892c0e8e73bea10423`
- Build/package procedure:
  `python scripts/build-release-package.py --repo <clean-worktree> --output-dir <external-output-dir>`.
  The repository-owned builder read only clean Git `HEAD` content, produced
  two independent byte-identical ZIPs, and wrote the SHA-256 sidecar.
- Build runtime: Python `3.14.6`.
- Canonical full evidence: GitHub Actions run
  [`35092879692`](https://github.com/sittelle/codex-engineering-governance/actions/runs/35092879692),
  executed against the source commit above. The canonical aggregate artifact
  is `framework-evidence-aggregate` (ID `10444484937`).
- Aggregate result: `EVIDENCE BUNDLE: PASS`. Windows `sast-powershell` is
  `PASS`. The individual Linux and Windows producer reports correctly leave
  the other platform's checks `DID_NOT_EXECUTE`; the attributable aggregate
  combines the required target evidence.
- Behavioral evidence: the complete, clean-environment Codex and Claude Code
  protocol-v2 campaigns in `VALIDATION-v2.0.0-rc.5.md` carry through the
  bounded proofs in `VALIDATION-v2.0.0-rc.6.md` and
  `VALIDATION-v2.0.0-rc.7.md`. Both captured 30/30 checksum-verified
  responses and scored 60/60. Raw prompts, responses, chats, account data,
  profiles, and local paths remain outside the repository.
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
- Decision authority/reference: developer-approved RC7 release-readiness
  evaluation on 2026-09-16. Git tag creation, artifact upload, and public
  publication remain separate consequential actions requiring explicit
  authorization.
