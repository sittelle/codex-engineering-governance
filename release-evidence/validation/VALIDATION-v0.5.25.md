# Validation v0.5.25

Status: STABLE_CANDIDATE.

Scope: repository-owned post-freeze activation of the evaluation fixture and global Codex kernel on top of frozen v0.5.24. This is C3 automation because it mutates another Git worktree and user Codex-home state. The user explicitly approved this narrow scope while reaffirming that the main objective is v1.0.

Frozen predecessor evidence:

- v0.5.24 is frozen at exact commit `3640ddf4e725a0ce76df66251587917065c7f0a2`;
- annotated/published tag `v0.5.24` dereferences to that exact commit;
- final Framework Verification run `34092834388` reports aggregate schema `2`, report schema `5`, `overall: PASS`, `issues: []`, and 14/14 required Windows/Ubuntu checks PASS;
- the accepted behavioral contract remains the unchanged v0.5.23 fresh campaign at 60/60, with no critical 0 and GOV-026..GOV-030 all 2/2;
- all 86 durable behavioral evaluation records and all 30 GOV scenario/rubric files remain distribution evidence.

v0.5.25 additions:

- adds `scripts/activate-frozen-baseline.py`;
- defaults to dry-run and requires explicit `--apply`;
- requires a clean evaluation-fixture Git worktree and the expected fixture files before mutation;
- reuses the existing host-native governed-project updater rather than duplicating baseline/managed-block migration policy;
- reconciles exactly one evaluation-fixture `baseline: "<old>"` assertion in `tests/eval-verification.py`;
- verifies target baseline, exact authoritative managed `AGENTS.md` block, fixture quick/full, and `git diff --check`;
- recognizes byte-equivalent managed `AGENTS.md` as a valid no-diff outcome;
- removes only updater-created fixture backup artifacts and permits only `AGENTS.md`, `project-governance.yml`, and `tests/eval-verification.py` in the commit-ready fixture diff;
- reuses the existing host-native Codex-home installer, then verifies global `AGENTS.md` byte identity and `GOVERNANCE_ROOT`;
- snapshots wrapper-owned fixture/global state and reports rollback status if apply/verification fails;
- does not commit/push the fixture and does not publish/tag/release anything.

Regression requirement:

- lifecycle common covers activation dry-run nonmutation;
- successful apply covers baseline/assertion reconciliation, fixture quick/full, exact/global installation, backup cleanup, and the byte-equivalent/no-`AGENTS.md`-diff case;
- dirty fixture state is refused before mutation;
- failed fixture verification restores the original clean fixture bytes and leaves global Codex-home state unchanged.

Behavioral preservation requirement:

- all 86 durable `tests/governance/evaluations/**/GOV-*.md` records remain byte-identical to frozen v0.5.24;
- all 30 `tests/governance/GOV-*.md` scenario/rubric files remain byte-identical to frozen v0.5.24;
- governance/managed behavioral instruction content remains unchanged except ordinary version metadata outside the behavioral contract;
- therefore no fresh behavioral campaign is required unless those assumptions are violated.

Prepared-tree checks required before handoff:

- activation/lifecycle common regression on the available preparation host;
- governance validator and durable-evidence MANIFEST completeness;
- candidate validation/application tooling regression;
- manifest inventory regression;
- lifecycle POSIX regression on the available preparation host;
- assurance integration regression;
- canonical quick verification on the available preparation host;
- exact ZIP distribution inventory against `MANIFEST.json`;
- whitespace integrity equivalent to `git diff --check`;
- byte-preservation comparison of all 86 durable behavioral records and all 30 frozen GOV scenarios against frozen v0.5.24.

Still required before freeze:

- candidate package preflight/application/local validation on the user host;
- bounded candidate diff review, commit, and push;
- fresh exact-commit Windows/Ubuntu Framework Verification aggregate PASS;
- tag publication remains a separate explicit authorization action.

Roadmap constraint: once v0.5.25 is validated/frozen, the next planned activity is a v1.0 readiness/gap review. Additional pre-1.0 convenience tooling is out of scope unless it materially blocks v1.0 acceptance.

Preparation-host results (Linux/x86_64):

- targeted frozen-baseline activation regression: PASS for dry-run nonmutation, bounded apply with byte-equivalent/no-diff managed `AGENTS.md`, fixture quick/full plus global-kernel verification, verification-failure rollback, and dirty-fixture refusal;
- governance validator: PASS (0.5.25), 30 behavioral scenarios, 86 durable behavioral records, MANIFEST-complete behavioral evidence;
- candidate validation/application tooling regression: PASS;
- manifest inventory regression: PASS;
- lifecycle POSIX regression: PASS;
- canonical quick verification in LOCAL/Linux/x86_64: PASS;
- all 86 durable behavioral evaluation records are byte-identical to frozen v0.5.24;
- all 30 GOV scenario/rubric files are byte-identical to frozen v0.5.24;
- preparation-host assurance-integration/full lifecycle-common aggregate did not complete within the available tool execution window and is not recorded as PASS.

The user-host candidate application/local validation remains required and is expected to execute lifecycle-common, the Windows lifecycle slice, assurance integration, canonical quick/full, and whitespace integrity before any candidate commit. Exact-commit cross-platform CI remains required before freeze.

## User-host disposition

Rejected / superseded before freeze. Candidate package dry-run on Windows passed with the expected bounded transition (create 2, update 16, unchanged 271, remove 0). During `--apply`, repository-owned local validation reached lifecycle-common and failed because the activation regression observed `AGENTS.md`, `project-governance.yml`, and `tests/eval-verification.py` as modified; the expected byte-equivalent case permits only the latter two. `apply-candidate-package.py` then restored the pre-apply MANIFEST-managed bytes and reported rollback PASS.

No v0.5.25 commit, exact-commit CI freeze evidence, or tag was created. The failure is retained as a real Windows activation byte-preservation defect and is corrected in v0.5.26 without changing governance/assurance/behavioral semantics.
