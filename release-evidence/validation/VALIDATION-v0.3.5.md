# v0.3.5 Commit-Bound Evidence Identity Validation

Scope: cross-platform evidence identity only.

Field evidence from Windows v0.3.4 showed `core.autocrlf=true`, index LF, mixed working-tree LF/CRLF, and no `.gitattributes`. Raw working-tree SHA-256 is therefore not a stable cross-platform identity mechanism.

v0.3.5 acceptance:
- clean tracked plan/baseline/runner identities use committed Git `HEAD` bytes;
- reports separately retain working-tree SHA-256 diagnostics;
- aggregation requires `GIT_HEAD` source identities and a clean worktree;
- dirty/untracked artifacts remain non-aggregatable;
- checked-out `HEAD` is authoritative over CI event metadata;
- prior outcome, execution-context, and completeness semantics remain unchanged;
- Windows integration test passes.

Behavioral regression: GOV-023.
