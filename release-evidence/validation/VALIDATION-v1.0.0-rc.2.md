# Validation 1.0.0-rc.2

Status: REJECTED / SUPERSEDED BEFORE FREEZE.

Scope: supersede prepared but unapplied rc.1 solely to correct the approved MIT copyright-holder wording and current-version/history metadata. The rc.1 public-release contract, deterministic package-production implementation, publication redaction, and frozen governance/behavioral scope are otherwise unchanged. No frozen GOV scenario/rubric change is authorized.

Correction from rc.1:

- rc.1 was rejected/superseded before application because its MIT license named `Sittelle` as copyright holder;
- the developer explicitly approved `Copyright (c) 2026 prerelease attribution`;
- rc.2 applies that correction and increments the prepared prerelease rather than silently revising rc.1;
- rc.1 was not applied, committed, tagged, or published.

Approved product decisions remain:

- license: MIT;
- public publication channel: GitHub, but publication remains separately authorized;
- versioning: SemVer;
- artifact: MANIFEST-bounded ZIP + SHA-256 + exact Git tag/commit;
- repository-owned deterministic package builder: REQUIRED;
- SBOM: NOT REQUIRED while no distributable third-party dependency/component graph exists; reassess if that fact changes;
- cryptographic release signing: NOT REQUIRED for the 1.0 baseline;
- provenance: exact commit/tag + deterministic artifact digest + attributable verification evidence;
- framework `SECURITY.md`: minimal and truthful, with no invented response SLA;
- stable release commit: reachable from the public repository's canonical/default branch;
- private pre-1.0 Git history is archival and is not required to become part of the public lineage.

Publication sanitization remains unchanged:

- README activation examples use a neutral fixture path;
- all 86 durable behavioral records remain present;
- all 30 frozen GOV scenarios/rubrics remain byte-identical to v0.5.27;
- exactly one durable GOV-029 raw-response record replaces an environment-specific absolute repository path with `<GOVERNANCE_ROOT>/framework-verification-plan.json`;
- `release-evidence/1.0.0-rc.2/publication-redaction.json` binds the exact original and candidate record hashes;
- the original byte-exact record remains preserved in the private pre-1.0 archive;
- scenario prompt, response semantics, score, rationale, and regression conclusion are unchanged.

Required gates before final 1.0 acceptance:

1. candidate package preflight and bounded application;
2. repository-owned local candidate validation and clean `git diff --check` / staged diff check;
3. commit candidate and obtain exact-commit CI aggregate with all 14 required checks PASS and `issues: []`;
4. run one fresh 30/30 behavioral campaign against the actual 1.0 release candidate;
5. require no critical 0s, GOV-026..GOV-030 all 2/2, total >=58/60 (target 60/60);
6. persist the campaign truthfully without rewriting historical failures;
7. run final exact-commit CI on the evidence-bearing release commit;
8. only then prepare the clean public 1.0 lineage and final `1.0.0` freeze/tag;
9. publication remains a separate explicit action.

No required gate is claimed PASS merely by preparation of this candidate.

## Final rc.2 outcome

rc.2 was applied, locally validated, committed at `d949ec714a9e23859c80f638fafabf24613f5de3`, and pushed only to the private `release/1.0.0-rc.2` branch. It was then rejected before exact-commit CI/freeze because the repository-owned clean-HEAD builder produced SHA-256 `cf5f756c836749a17d502d3bb364dfdab74d7b5aad3cf34947a7fbd0c4714b77`, which did not match the prepared rc.2 package SHA-256 `2a9df5d11487a68fe9a57334d2e4d8d4e2eb274e69e5e063c56c50fea4d432a0`.

A member-by-member comparison showed:

- 299/299 package member paths/order identical;
- 0 uncompressed file-content differences;
- 26 executable-mode differences between the prepared archive and committed Git tree;
- no other ZIP entry metadata differences;
- 48 compressed-size differences despite identical input bytes, demonstrating host-dependent DEFLATE output.

No rc.2 tag, GitHub Release, visibility change, or public artifact publication occurred. rc.3 corrects only this release-package reproducibility/mode defect.
