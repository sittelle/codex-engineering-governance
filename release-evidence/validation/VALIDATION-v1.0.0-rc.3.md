# Validation 1.0.0-rc.3

Status: STABLE_CANDIDATE.

Scope: supersede rejected rc.2 solely to correct the deterministic release-package production defect exposed after the first clean rc.2 commit. No frozen GOV scenario/rubric, governance semantic, assurance semantic, security policy, licensing decision, publication boundary, or behavioral threshold change is authorized.

Rejected predecessor evidence:

- rc.2 private commit: `d949ec714a9e23859c80f638fafabf24613f5de3`;
- prepared rc.2 ZIP SHA-256: `2a9df5d11487a68fe9a57334d2e4d8d4e2eb274e69e5e063c56c50fea4d432a0`;
- clean-HEAD rc.2 ZIP SHA-256: `cf5f756c836749a17d502d3bb364dfdab74d7b5aad3cf34947a7fbd0c4714b77`;
- diagnostic: 299/299 uncompressed member bytes identical, 26 mode differences, no other entry-metadata differences, and 48 compressed-size differences;
- rc.2 was rejected before exact-commit CI/freeze and was never tagged or published.

rc.3 correction:

- canonical release ZIP entries use `ZIP_STORED` rather than DEFLATE, removing zlib-version/host compression variability from byte identity;
- member ordering and timestamp normalization remain deterministic;
- package executable modes remain derived from exact Git HEAD;
- the four POSIX shell entrypoints are intended to be committed executable: `codex-home/install.sh`, `scripts/bootstrap-assurance.sh`, `scripts/manage-governed-project.sh`, and `scripts/update-governed-project.sh`;
- Python tools remain non-executable package files and are invoked through the selected Python interpreter;
- builder regression requires `ZIP_STORED`, Git executable-mode preservation, independent byte-identical rebuilds, SHA-256 sidecar correctness, and dirty-worktree refusal.

Carried 1.0 product decisions remain unchanged:

- MIT, personal prerelease copyright attribution;
- SemVer;
- public artifact: MANIFEST-bounded ZIP + SHA-256 + exact tag/commit;
- repository-owned deterministic package production required;
- SBOM not required under the current no-distributable-third-party-component/dependency-graph facts;
- cryptographic release signing not required for the 1.0 baseline;
- provenance requires exact commit/tag + deterministic artifact digest + attributable verification evidence;
- minimal truthful framework `SECURITY.md`;
- publication remains a separate explicit action.

Behavioral/publication preservation:

- all 86 durable behavioral records remain present and unchanged from rc.2;
- all 30 frozen GOV scenario/rubric files remain byte-identical to v0.5.27;
- the existing approved GOV-029 publication path redaction remains unchanged; its original is retained in the private pre-1.0 archive.

Required gates before final 1.0 acceptance:

1. candidate preflight/application and repository-owned local validation;
2. staged whitespace/path review and clean commit;
3. clean-HEAD rc.3 rebuild must match the prepared rc.3 ZIP byte-for-byte;
4. exact-commit cross-platform CI aggregate: PASS, issues `[]`, 14/14 required checks PASS;
5. fresh 30/30 behavioral campaign against the accepted 1.0 candidate, no critical 0s, GOV-026..GOV-030 all 2/2, total >=58/60 (target 60/60);
6. persist behavioral evidence truthfully and run final exact-commit CI on that evidence-bearing commit;
7. create the clean public 1.0 lineage and final 1.0.0 freeze/tag only after all gates pass;
8. publication remains separately authorized.

No required gate is claimed PASS merely by preparation of rc.3.
