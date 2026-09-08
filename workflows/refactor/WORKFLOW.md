# Refactor Workflow

Use this workflow for structural changes intended to preserve externally observable behavior and approved product semantics.

Examples:
- extract/merge modules or classes;
- move code across layers;
- simplify control flow;
- introduce interfaces/adapters/repositories;
- rename internal symbols;
- reduce duplication;
- reorganize packages;
- improve testability without changing product behavior.

Core principle:

**Refactoring changes structure. It does not silently change product behavior, public contracts, data semantics, support promises, dependency posture, security boundaries, or operational effects.**

## Flow

CLASSIFY → DEFINE INVARIANTS → CHARACTERIZE CURRENT BEHAVIOR → BOUND SCOPE → PLAN INCREMENTS → APPROVE MATERIAL NON-REFACTOR DELTAS → REFACTOR → VERIFY EQUIVALENCE → CLEANUP → DOCUMENT

## 1. Classify the request

Separate the requested work into:
- pure/internal refactor;
- bug fix;
- feature/behavior change;
- public API/contract change;
- persistence/schema/data migration;
- dependency/toolchain change;
- security/authorization/authentication change;
- performance/operational behavior change.

Do not call all requested cleanup a refactor merely because the developer used that word.

Route material non-refactor parts through the applicable workflow and approval boundary.

## 2. Define behavior and contract invariants

Before substantial refactoring, establish what must remain unchanged.

As applicable:
- public API signatures and semantics;
- CLI/UI behavior;
- persistence/data semantics;
- error behavior;
- authorization/security outcomes;
- external side effects;
- network/file/process behavior;
- supported runtimes/platforms;
- ordering/idempotency/concurrency semantics;
- performance/resource constraints when they are contractual or operationally material.

If the developer intends one of these to change, classify that delta separately.

## 3. Characterize current behavior

Where existing behavior is insufficiently specified:
- inspect current tests and callers;
- add focused characterization/regression tests before restructuring;
- capture important edge/error cases;
- distinguish observed existing behavior from desired behavior.

Do not encode clearly accidental/unsafe behavior as a permanent invariant without surfacing it.

When observed behavior conflicts with approved requirements/security rules, stop and resolve the conflict rather than preserving it blindly.

## 4. Bound the scope

Identify:
- modules/components to change;
- callers/consumers;
- interfaces/contracts that must stay stable;
- files/config/dependencies explicitly out of scope.

Avoid bundling:
- unrelated dependency upgrades;
- formatting churn across unaffected files;
- feature additions;
- schema migrations;
- broad renames of public APIs;
- speculative architectural rewrites.

A refactor should reduce or preserve complexity, not create a larger unapproved architecture.

## 5. Choose the smallest useful design

Recommend the simplest structural improvement that addresses the actual maintainability/testability problem.

Prefer:
- explicit boundaries over unnecessary abstractions;
- incremental extraction over big-bang rewrite;
- existing language/framework mechanisms over new libraries;
- composition/interfaces only where they improve a real boundary.

Do not introduce repositories, factories, dependency injection frameworks, event buses, plugin systems, or other patterns merely because they are considered “clean architecture.”

Architecture follows demonstrated requirements.

## 6. Separate public API changes

Renaming/removing/changing a public method, endpoint, CLI option, serialized field, event, protocol, or documented integration point is not pure refactoring.

Before such a change:
- identify consumers;
- state compatibility impact;
- recommend migration/deprecation strategy where applicable;
- obtain approval for the contract change.

Internal symbol renames that do not alter supported interfaces may remain part of the refactor.

## 7. Separate persistence/data changes

Moving persistence code into another layer can be a refactor.

Changing:
- schema;
- stored representation;
- data retention;
- migration semantics;
- transaction/isolation behavior;
- destructive behavior

is a data/persistence behavior change and must be analyzed separately. Use the data-migration workflow when persisted data is materially transformed/moved/removed.

Do not hide schema/data changes behind repository-layer extraction.

## 8. Separate dependency changes

Do not opportunistically update or add unrelated dependencies during a refactor.

If a new dependency is genuinely required by the structural design:
- justify necessity;
- use the dependency-change workflow when material;
- inspect lockfile/transitive impact;
- obtain approval where the dependency introduces a material tradeoff.

Keep dependency churn in a separate commit/change where practical.

## 9. Plan incremental checkpoints

For nontrivial refactors, prefer a sequence where each checkpoint:
- compiles/builds;
- passes relevant tests;
- preserves behavior;
- is small enough to review/revert.

Examples:
1. add characterization tests;
2. introduce internal seam/interface without changing behavior;
3. move one responsibility;
4. redirect callers;
5. remove dead path;
6. cleanup naming/structure.

Avoid a rewrite that leaves the repository unverifiable until the final step.

## 10. Implement

During implementation:
- keep changes scoped;
- preserve behavior/invariants;
- avoid unrelated cleanup;
- retain compatibility adapters temporarily when safer;
- remove dead code only after callers/tests prove it is unused;
- keep commits/review units understandable where practical.

If implementation reveals a required behavior change, stop and surface it rather than silently absorbing it.

## 11. Verify equivalence

Run canonical verification plus targeted before/after evidence.

As applicable:
- unit/regression/characterization tests;
- API/contract tests;
- integration tests;
- data/persistence tests;
- auth/security tests;
- CLI/UI snapshots or functional checks;
- supported runtime/platform verification;
- performance checks when material.

A successful build alone does not prove behavior preservation.

Do not claim equivalence for untested material behavior.

## 12. Remove transitional structure carefully

After callers have moved and verification passes:
- remove dead adapters/legacy paths;
- simplify temporary seams;
- update docs/comments that describe old structure;
- verify no hidden consumer still depends on the removed path.

Public compatibility layers follow approved deprecation policy, not refactor convenience.

## 13. Completion evidence

Report:
- structural changes made;
- explicit non-goals;
- invariants preserved;
- characterization/regression evidence;
- any public/data/dependency/security changes that were separated out;
- verification actually executed and results;
- unverified areas;
- remaining transitional/deprecation work.

Use `VERIFIED`, `UNVERIFIED`, `KNOWN RISK`, `ACCEPTED RISK`, `NOT APPLICABLE`, and `REMAINING WORK` accurately.

## Stop conditions

Stop and surface the issue when:
- required behavior/invariants cannot be established;
- the refactor would silently change a public contract;
- persisted-data semantics would change without migration analysis;
- a dependency change is being smuggled into cleanup without review;
- characterization reveals behavior that conflicts with approved requirements/security;
- the rewrite cannot be kept in verifiable increments without a justified reason;
- verification needed to establish equivalence cannot execute.

## Prohibited behaviors

Do not:
- use “refactor” as permission for product behavior changes;
- rename/remove public APIs without treating that as a contract change;
- change schema/data semantics under a repository-layer extraction;
- perform unrelated dependency upgrades;
- add architectural patterns without a demonstrated need;
- rewrite large areas in one unverifiable jump when incremental migration is practical;
- claim behavior preservation from successful compilation alone;
- preserve known insecure behavior solely because existing tests encode it.
