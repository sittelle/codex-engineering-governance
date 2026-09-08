# Validation v0.5.27

Status: STABLE_CANDIDATE.

Scope: packaging/whitespace correction only after v0.5.26 passed the decisive Windows candidate application/local-validation path but failed the staged whitespace gate. Frozen v0.5.24 remains the reference baseline.

Defect evidence retained from v0.5.26:

- Windows `apply-candidate-package.py --apply` passed package preflight, bounded MANIFEST transition, installed-byte verification, repository-owned governance/manifest/lifecycle-common/lifecycle-windows/assurance/quick validation, and local-full semantics with only approved CI deferrals;
- the v0.5.25 Windows activation defect was therefore functionally corrected by v0.5.26;
- before commit, `git diff --cached --check` rejected `release-evidence/validation/VALIDATION-v0.5.25.md` because that carried historical validation record ended with an extra blank line;
- v0.5.26 was therefore rejected/superseded before commit/freeze. The staged candidate must not be treated as frozen evidence.

v0.5.27 correction:

- normalizes only the EOF of `release-evidence/validation/VALIDATION-v0.5.25.md` from two trailing LF bytes to one trailing LF byte;
- carries the v0.5.26 activation implementation and regression coverage unchanged;
- adds this v0.5.27 validation/accounting record and ordinary current-version metadata;
- does not rewrite any behavioral evaluation record or scenario/rubric.

Behavioral preservation requirement:

- all 86 durable behavioral evaluation records remain byte-identical to frozen v0.5.24;
- all 30 GOV scenario/rubric files remain byte-identical to frozen v0.5.24;
- no governance instruction, assurance result semantic, exception/risk authority, release threshold, or publication/deployment boundary changes;
- therefore no fresh behavioral campaign is required if preservation checks pass.

Required before freeze:

- package preflight/application/local validation on the Windows user host;
- `git diff --check` and staged `git diff --cached --check` must both be clean;
- bounded diff review, commit, and push;
- exact-commit Windows/Ubuntu Framework Verification aggregate PASS;
- tag publication remains a separate explicit action.

Roadmap constraint: after this packaging defect correction, proceed directly to the v1.0 readiness/gap review. Further pre-1.0 convenience tooling is out of scope unless it materially blocks v1.0 acceptance.
