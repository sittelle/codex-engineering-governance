# Stable Release and Compatibility Policy

This policy applies to the public stable release line beginning with `1.0.0`.

## Versioning and compatibility

The project uses [Semantic Versioning](https://semver.org/) for public releases.

- **Major** versions may make incompatible changes to stable governance semantics, documented consumer-facing tooling behavior, or documented distribution/file-format contracts.
- **Minor** versions add capabilities in a backward-compatible way.
- **Patch** versions make backward-compatible corrections.
- Pre-release versions such as `1.0.0-rc.3` are evaluation baselines and do not carry the stable compatibility guarantee. A prepared pre-release is never silently revised; a correction receives a new pre-release version.

The compatibility promise covers documented normative governance behavior and interfaces that consumers are told to rely on. Internal implementation details, test/evidence records, and editorial wording are not independently stable APIs unless another document identifies them as normative.

## Release artifact

The public distribution artifact is one MANIFEST-bounded ZIP named `codex-engineering-governance-v<version>.zip`, accompanied by its SHA-256 digest and bound to an exact Git commit and annotated version tag.

The repository-owned `scripts/build-release-package.py` is the canonical package-production path. It:

- refuses a dirty Git worktree;
- reads package bytes from clean Git `HEAD`, not mutable working-tree bytes;
- uses `MANIFEST.json` as the exact distribution allowlist;
- emits one versioned package root;
- uses deterministic member ordering and timestamps, `ZIP_STORED` entries (no host-dependent DEFLATE output), and Git-tree-derived executable modes;
- rebuilds independently and refuses output unless both builds are byte-identical; and
- emits the ZIP SHA-256 sidecar.

Package validation/application remains the responsibility of the existing repository-owned candidate preflight, application, and verification workflows.

## Publication assurance applicability

For the current framework facts and ZIP publication model:

- **SBOM:** not required while the distributed artifact contains no committed third-party runtime/build/development dependency graph or distributable third-party components. Reassess before release if that fact changes.
- **Cryptographic release signing:** not required for the 1.0 baseline.
- **Provenance:** exact Git commit/tag identity, deterministic package production, retained SHA-256, and attributable exact-commit verification evidence are required. Stronger signed provenance must be reassessed if the publication channel or risk profile later requires it.

These are applicability decisions, not permission to mark a required control PASS when it did not execute.

## Release topology and publication authority

Stable release tags must identify an evidence-bearing commit reachable from the repository's canonical/default branch. The public 1.0 lineage may begin from the accepted sanitized 1.0 baseline; the private pre-1.0 development history is not part of the public compatibility contract.

Technical readiness, tagging, and publication are separate decisions. No GitHub Release, visibility change, artifact upload, deployment, or other consequential publication occurs without explicit developer authorization.
