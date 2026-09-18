# Release record — 2.0.0

- Source commit: `4d2957f075411fd860e310aabeb3d904f4b710ad`.
- Source worktree: `CLEAN` at package build.
- Distribution artifact: `sittelle-engineering-governance-v2.0.0.zip`.
- SHA-256:
  `a63fea125ab810ce23977469efad5ce068e96fbdbdd80caf5a9bf791e5965985`.
- Build/package procedure:
  `python scripts/build-release-package.py --repo <clean-worktree> --output-dir <external-output-dir>`.
  The repository-owned builder read clean Git `HEAD`, produced two independent
  byte-identical ZIPs, and emitted the SHA-256 sidecar.
- Build runtime: Python `3.14.6`.
- Canonical full evidence: GitHub Actions
  [run 35313950525](https://github.com/sittelle/codex-engineering-governance/actions/runs/35313950525),
  executed against the exact source commit above. Its aggregate artifact is
  `framework-evidence-aggregate` (ID `10534153429`).
- Aggregate result: `EVIDENCE BUNDLE: PASS`; all 14 required checks are
  `PASS`, with zero aggregate issues. The individual Windows and Linux
  producers correctly leave checks for the other platform as
  `DID_NOT_EXECUTE`; the attributable aggregate supplies the required target
  combination.
- Behavioral evidence: the clean-environment protocol-v2 Codex and Claude
  Code campaigns in `VALIDATION-v2.0.0-rc.5.md` carry through the bounded
  response-surface preservation records for rc.6, rc.7, and v2.0.0. Both
  campaigns captured 30/30 checksum-verified responses and scored 60/60.
  The final documentation-only corrections do not alter prompts, rubrics,
  generated contexts, host adapters, host integrations, profile setup, model,
  effort, or any other response-affecting surface. Raw responses, chats,
  profiles, account state, and local paths remain controlled external
  evidence.
- Repository identity and assurance source: this is the M2/SA1 distributed
  governance/tooling package, not an application or hosted service.
  `framework-verification-plan.json` is the single source of assurance
  applicability; this record creates no parallel policy or assurance baseline.
- Applicable baseline retained: canonical verification, lifecycle/package
  regression, Windows/POSIX evidence, secret scanning, meaningful SAST,
  CI/evidence integrity, and release artifact/source/full-evidence binding all
  executed as above.
- Factual `NOT_APPLICABLE` controls: auth/authz review, DAST, container
  scanning, deployment-IaC scanning, recovery verification, and dependency
  SCA remain `NOT_APPLICABLE` only while their recorded factual triggers are
  absent.
- Conditional publication controls: SBOM, signing, and stronger provenance
  remain conditional on the publication/distribution channel or another
  approved factual trigger. For this ZIP release, provenance is the exact
  source commit, annotated tag, deterministic digest, and attributable
  cross-platform evidence.
- Change boundary: a material assurance-applicability or policy change would
  be C2 unless the global change-class rules require C3. No such policy change
  is made by this release; the public tag and release publication were the
  separately authorized C3 actions.
- Findings / missing assurance: none attributable to the released source.
- Exceptions / accepted risks: none.
- Decision: `READY`.
- Decision authority/reference: explicit developer authorization on
  2026-09-18 to fast-forward `master`, create/push annotated tag `v2.0.0`,
  and publish the stable release with the ZIP and SHA-256 sidecar.
- Publication: [GitHub stable release v2.0.0](https://github.com/sittelle/codex-engineering-governance/releases/tag/v2.0.0).
  Post-publication verification downloaded both assets, matched the ZIP and
  sidecar SHA-256 values above, confirmed `master` points to the source
  commit, and confirmed that the annotated tag dereferences to that same
  commit.
