# Data Migration Workflow

Use this workflow for changes that move, transform, backfill, reinterpret, delete, repartition, or otherwise materially alter persisted data or schema semantics.

The workflow applies whether the migration is performed by SQL, application code, an ORM migration tool, scripts, import/export jobs, or manual/operator procedures.

## Flow

CLASSIFY → INVENTORY → DEFINE INVARIANTS → DESIGN TRANSITION → PROVE RECOVERY → APPROVE MATERIAL DIRECTION → IMPLEMENT REVERSIBLE STEPS → VERIFY ON REPRESENTATIVE DATA → APPROVE DESTRUCTIVE BOUNDARY → EXECUTE → VALIDATE → DOCUMENT

## 1. Classify

Determine:
- maturity and assurance;
- affected environments and datasets;
- whether the change is C1/C2/C3;
- whether data is sensitive, user-owned, regulated, security-critical, financially material, or operationally consequential.

A schema change is not automatically destructive.

Classify C3 when meaningful existing data may be destroyed, irreversibly transformed, made inaccessible, or when failure could cause high-consequence bulk effects.

## 2. Inventory existing state

Before designing the migration, establish:
- exact tables/collections/files/fields affected;
- approximate volume and cardinality where material;
- nullability/default/uniqueness/reference constraints;
- consumers and producers of the data;
- existing indexes/triggers/views/jobs/caches derived from it;
- deployment/runtime versions that may coexist during rollout;
- known bad/legacy data that could invalidate assumptions.

Do not plan from the target schema alone.

## 3. Define invariants and intended outcome

Record:
- what must remain true before, during, and after migration;
- what information must be preserved;
- any intentional semantic change;
- how old and new representations relate;
- acceptance criteria measurable from data, not only schema shape.

For removal or irreversible transformation, explicitly establish one of:
- the existing data is intentionally obsolete and may be destroyed; or
- an approved preservation/migration destination exists.

Never infer disposability from the requested schema or feature change.

## 4. Design the transition

Prefer reversible, observable transitions.

Where applicable, prefer an expand → migrate/backfill → validate → switch readers/writers → contract sequence rather than combining all changes into one destructive step.

Define:
- migration ordering;
- compatibility between old/new application versions;
- batching, locking, transaction and timeout behavior;
- retry/idempotency semantics;
- interruption/resume behavior;
- handling of invalid or unexpected source rows;
- concurrency/write behavior while migration runs;
- resource/capacity impact;
- whether a maintenance window is required.

Avoid large one-shot transactions when failure/recovery consequences are material unless explicitly justified.

## 5. Prove backup and recovery

For consequential migrations:
- identify the recovery source;
- verify the backup/snapshot/export is current enough for the accepted recovery objective;
- establish that restoration is actually possible;
- define rollback versus restore/recovery accurately.

Do not call a plan “rollback” if the destructive step can only be recovered from backup.

For C3 destructive migrations, unverified recovery is a stop condition unless the developer explicitly accepts the destruction with no recovery path as a distinct material risk.

## 6. Approval before implementation

For C2/C3 migrations, present:
- affected data and environment;
- material invariants;
- transition strategy;
- preservation/obsolescence decision;
- backup/recovery plan;
- rollback/recovery limits;
- validation plan;
- downtime/performance/compatibility impact;
- destructive steps, if any.

Obtain material-direction approval before substantial migration implementation.

## 7. Implement migration mechanics

Implementation should:
- be deterministic and reviewable;
- minimize privileges and affected scope;
- fail clearly rather than silently dropping/reinterpreting data;
- make irreversible steps visibly separate where practical;
- support dry-run/analysis mode when useful;
- emit bounded operational evidence without leaking sensitive data;
- be idempotent or explicitly guarded against accidental rerun where feasible.

Do not hide destructive execution behind startup side effects or ordinary application launch when the action deserves explicit operational control.

## 8. Verify before destructive execution

Before any destructive/irreversible step, verify on representative data:
- transformation correctness;
- constraint/invariant preservation;
- row/object counts or reconciliation metrics where meaningful;
- invalid-data handling;
- interruption/retry behavior where material;
- application compatibility across the planned transition;
- recovery/restore procedure where required.

For production/material datasets, prefer staging/copy/rehearsal evidence when feasible.

## 9. Destructive execution approval

A previous approval of the migration design is not automatically approval to execute a consequential destructive step.

Immediately before the destructive boundary, present:
- what data will become unrecoverable or inaccessible;
- what preservation/backups exist;
- latest preflight/validation evidence;
- rollback/recovery limit;
- exact environment/scope.

Obtain explicit C3 destructive execution approval.

## 10. Execute and validate

After execution:
- run post-migration invariant checks;
- reconcile expected counts/relationships/derived data where material;
- verify the application reads/writes the new representation correctly;
- check error/health/operational signals;
- preserve evidence of migration version/state;
- do not remove backups or compatibility paths until the acceptance window permits it.

If validation fails, stop further contraction/destruction and invoke the planned recovery path.

## 11. Completion evidence

Report:
- migration version/change identifier;
- environments/datasets actually migrated;
- verification performed and actual results;
- backup/recovery evidence;
- destructive approval evidence where applicable;
- known risks, skipped checks, or remaining compatibility cleanup;
- whether old schema/data compatibility code remains.

Use `VERIFIED`, `UNVERIFIED`, `KNOWN RISK`, `ACCEPTED RISK`, `NOT APPLICABLE`, and `REMAINING WORK` accurately.

## Stop conditions

Stop and surface the issue when:
- data purpose/obsolescence is unclear;
- the affected dataset/environment cannot be bounded;
- an invariant cannot be stated or tested where material;
- migration correctness depends on an unverified assumption about existing data;
- destructive recovery is required but unavailable/unverified;
- an unexpected legacy-data case invalidates the migration model;
- the migration requires governance/security weakening;
- destructive execution approval has not been obtained.

## Prohibited behaviors

Do not:
- infer that existing data is disposable because a field/table is being removed;
- silently discard invalid rows to make a migration succeed;
- claim rollback exists when only an untested backup exists;
- combine expansion/backfill/contract steps unnecessarily when compatibility risk is material;
- make destructive migrations auto-run merely because the application starts;
- mark a migration complete based only on successful command exit without data validation.
