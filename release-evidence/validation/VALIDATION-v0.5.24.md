# Validation v0.5.24

Status: STABLE_CANDIDATE.

Scope: bounded candidate-package application tooling on top of frozen v0.5.23. This is a C3 worktree-mutation capability because it can replace/remove repository files. No GOV scenario/rubric, governance instruction, assurance schema/result semantic, exception authority, release threshold, or publication/deployment boundary changes.

Frozen predecessor evidence:

- v0.5.23 is the latest frozen cross-platform verified reference at exact commit `da4c8bb63f98bdc6606c27418436189c5d024a02`;
- annotated/published tag `v0.5.23` dereferences to that exact commit;
- final Framework Verification run `33871669664` reports aggregate schema `2`, report schema `5`, `overall: PASS`, `issues: []`, and 14/14 required Windows/Ubuntu checks PASS;
- the fresh v0.5.23 behavioral campaign scored 60/60, with no critical score 0 and GOV-026..GOV-030 all 2/2;
- all 86 durable behavioral evaluation records are retained as distribution evidence.

v0.5.24 additions:

- adds `scripts/apply-candidate-package.py` as the repository-owned candidate replacement path;
- default mode is a non-mutating dry-run; `--apply` is required for worktree mutation;
- automatically invokes the existing `preflight-candidate-package.py` preservation contract instead of duplicating package/evidence/scenario policy;
- requires the authoritative framework repository to be a clean Git worktree, refusing tracked modifications and non-ignored untracked files before mutation;
- validates current/candidate MANIFEST paths, rejects `.git` targets, case-insensitive path collisions, ZIP symlink members, and managed paths that would traverse repository symlinks/non-directory parents;
- computes the exact current-MANIFEST to candidate-MANIFEST transition, writes only candidate MANIFEST files, and removes only old MANIFEST-owned files that are absent from the candidate;
- never recursively deletes the worktree and preserves tracked/ignored files outside the distribution MANIFEST;
- verifies every candidate MANIFEST-managed file byte-for-byte against the ZIP after application and verifies old MANIFEST-only files are absent;
- runs `scripts/validate-candidate.py` after application;
- snapshots MANIFEST-managed pre-apply bytes and restores them if application, post-apply byte verification, or candidate validation fails;
- extends `scripts/test-candidate-validation.py` with dry-run nonmutation, bounded apply/preservation, dirty-state refusal, `.git` target rejection, and failed-validation rollback regressions;
- routes the expanded candidate tooling regression through lifecycle common as before.

Behavioral preservation requirement:

- all 86 durable `tests/governance/evaluations/**/GOV-*.md` records must remain byte-identical to frozen v0.5.23;
- all 30 `tests/governance/GOV-*.md` scenario/rubric files must remain byte-identical to frozen v0.5.23;
- global/managed behavioral instruction content is unchanged except ordinary current-version metadata elsewhere in the package;
- therefore a fresh behavioral campaign is not required for this tooling-only candidate unless those preserved instruction/scenario/evidence assumptions are violated during preparation or field validation.

Prepared-tree checks required before handoff:

- candidate validation/application tooling regression;
- governance validator and durable-evidence MANIFEST completeness;
- manifest inventory regression;
- lifecycle common and POSIX regression on the available preparation host;
- assurance integration regression;
- canonical quick verification on the available preparation host;
- exact ZIP distribution inventory against `MANIFEST.json`;
- whitespace integrity equivalent to `git diff --check`;
- byte-preservation comparison of all 86 durable behavioral records and all 30 frozen GOV scenarios against frozen v0.5.23 source.

Still required before freeze:

- run package preflight against the downloaded v0.5.24 ZIP and the authoritative clean v0.5.23 framework worktree;
- exercise the new apply script in dry-run mode on the user host and review its bounded transition;
- run the same script with explicit `--apply` and require its post-apply repository-owned local validation to pass;
- inspect/stage the bounded candidate diff, commit and push the exact candidate;
- obtain fresh exact-commit Windows/Ubuntu Framework Verification aggregate PASS for that exact candidate commit;
- keep publication/tag/release creation as a separate explicit authorization action.
