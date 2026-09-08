# Release record — 0.5.13 pre-1.0 rehearsal

- Source commit: `b18d5f11059b3894cd9e215a8d149da3783c114a`
- Source worktree: `CLEAN`
- Distribution artifact(s): `codex-engineering-governance-v0.5.13.zip`
- SHA-256: `FF05CC7F21D97626CA8AA0731BB1844E117814AE790C5098BBDA614F33170326`
- Build/package procedure: Build exclusively from Git `HEAD` bytes using the `MANIFEST.json` distribution allowlist; create a single `codex-engineering-governance-v0.5.13/` ZIP root using Python `zipfile`, DEFLATE level 9, normalized `1980-01-01 00:00:00` member timestamps, and Git-derived executable/non-executable modes. An independent rebuild produced the identical SHA-256.
- Build runtime/tool version: `Python 3.14.6`
- Canonical full evidence: GitHub Actions Framework Verification run `33399810045`, exact source commit `b18d5f11059b3894cd9e215a8d149da3783c114a`; required Windows x86_64 and Linux x86_64 evidence produced successfully.
- Aggregate evidence: `framework-evidence-aggregate/aggregate-full.json` from run `33399810045`; aggregate schema `2`, report schema `5`, `overall: PASS`, `issues: []`, all 14 required checks `PASS`.
- Capability/applicability notes: Framework assurance target `M2/SA1`. Required lint/format, type/compile, tests, build/package, secret scanning, SAST, and security-test capabilities are satisfied. SCA is `NOT_APPLICABLE` because no committed third-party runtime/build/dev dependency graph exists. Container scan, IaC scan, DAST, and recovery verification are `NOT_APPLICABLE` under the recorded framework facts. SBOM, fuzzing, and provenance/signing remain conditional/optional at the current assurance level and must be reassessed if the approved publication channel makes them applicable.
- Findings / missing assurance: `none`; aggregate `issues: []`; no required target or required capability is missing.
- Exceptions / accepted risks: `none`.
- Conditional SBOM/signing/provenance: `NOT APPLICABLE to this rehearsal-only, non-publication decision`. Exact source, artifact digest, repeatable-build, and canonical assurance binding are present. Reassess SBOM/signing/stronger provenance before consequential publication when a publication channel is selected.
- Decision: `READY`
- Decision authority/reference: `Developer explicitly approved the pre-1.0 rehearsal READY decision on 2026-08-31. Publication/deployment is not authorized by this decision.`
