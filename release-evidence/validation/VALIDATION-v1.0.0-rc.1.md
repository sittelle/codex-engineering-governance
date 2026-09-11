# Validation 1.0.0-rc.1

Status: REJECTED / SUPERSEDED BEFORE APPLICATION.

Scope: minimum 1.0 public-release contract and deterministic release-package production on frozen v0.5.27. No frozen GOV scenario/rubric change is authorized.

Rejection / supersession note:

- The prepared rc.1 package used `Copyright (c) 2026 Sittelle` in the MIT license.
- Before candidate application, the developer specified the intended copyright-holder wording as a personal prerelease attribution.
- Per the release rule that a prepared version is never silently revised, rc.1 is retained as a truthful rejected preparation and rc.2 carries the holder correction plus version/history metadata only.
- No rc.1 candidate was applied, committed, tagged, or published.

Approved product decisions:

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

Publication sanitization:

- README activation examples use a neutral fixture path;
- all 86 durable behavioral records remain present;
- all 30 frozen GOV scenarios/rubrics remain byte-identical to v0.5.27;
- exactly one durable GOV-029 raw-response record replaces an environment-specific absolute repository path with `<GOVERNANCE_ROOT>/framework-verification-plan.json`;
- `release-evidence/1.0.0-rc.1/publication-redaction.json` binds the exact original and candidate record hashes;
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
