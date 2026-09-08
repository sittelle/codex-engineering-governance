# Validation v0.5.26

Status: STABLE_CANDIDATE.

Scope: narrow correction of the Windows byte-equivalent `AGENTS.md` activation defect found during v0.5.25 user-host validation. Frozen v0.5.24 remains the reference baseline.

Defect evidence retained from v0.5.25:

- Windows candidate dry-run passed with create 2 / update 16 / unchanged 271 / remove 0;
- candidate apply reached repository-owned lifecycle-common;
- lifecycle-common failed because activation produced a tracked `AGENTS.md` delta despite the managed block already being authoritative;
- candidate application rollback restored the pre-apply MANIFEST-managed bytes and reported PASS;
- v0.5.25 was therefore rejected/superseded before commit/freeze.

v0.5.26 correction:

- when the pre-apply managed `AGENTS.md` block already equals the authoritative template block, `activate-frozen-baseline.py` restores the exact pre-apply `AGENTS.md` bytes after the host-native updater before verification;
- the authoritative managed block is still verified after restoration, so a real governance-block mismatch cannot be hidden;
- lifecycle-common additionally requires exact `AGENTS.md` byte preservation in this already-equivalent case;
- all other v0.5.25 activation behavior and C3 boundaries are unchanged.

Behavioral preservation requirement:

- all 86 durable behavioral evaluation records remain byte-identical to frozen v0.5.24;
- all 30 GOV scenario/rubric files remain byte-identical to frozen v0.5.24;
- no governance instruction, assurance result semantic, exception/risk authority, release threshold, or publication/deployment boundary changes;
- therefore no fresh behavioral campaign is required if preservation checks pass.

Required before freeze:

- package preflight/application/local validation on the Windows user host, including lifecycle-common and lifecycle-windows;
- bounded diff review, commit, and push;
- exact-commit Windows/Ubuntu Framework Verification aggregate PASS;
- tag publication remains a separate explicit action.

Roadmap constraint: after this defect correction, proceed directly to the v1.0 readiness/gap review. Further pre-1.0 convenience tooling is out of scope unless it materially blocks v1.0 acceptance.

Preparation-host results (Linux/x86_64):

- governance validator: PASS (0.5.26), 30 behavioral scenarios, 86 durable records, MANIFEST-complete behavioral evidence;
- candidate validation/application tooling regression: PASS;
- manifest inventory regression: PASS;
- lifecycle POSIX regression: PASS, including frozen-baseline activation dry-run/apply/rollback coverage on the POSIX updater path;
- canonical quick verification in LOCAL/Linux/x86_64: PASS;
- all 86 durable behavioral evaluation records are byte-identical to the v0.5.25 prepared package / frozen v0.5.24 behavioral corpus;
- all 30 GOV scenario/rubric files are byte-identical to the v0.5.25 prepared package / frozen v0.5.24 scenario corpus;
- lifecycle-common and assurance-integration did not complete within the available preparation-host execution window and are not recorded as PASS.

The decisive correction check remains the user-host Windows `apply-candidate-package.py --apply` run, because the rejected v0.5.25 defect was exposed by Windows lifecycle-common. That run must pass repository-owned lifecycle-common, lifecycle-windows, assurance integration, canonical quick/full, and whitespace integrity before any commit.
