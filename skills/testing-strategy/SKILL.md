# Testing Strategy

Derive tests from observable behavior, risk, consequence, architecture, and failure modes. Testing depth follows consequence and risk, not a fixed template.

Use unit/component/integration/contract/E2E/security/performance tests only as appropriate. Do not optimize for test count or arbitrary coverage percentage; coverage percentage alone is not evidence of correctness.

## Requirement-to-test traceability

Derive tests from the stated requirement, acceptance criterion, or registration -- not from reading the implementation and writing a test that confirms it does what it does. Every REQUIRED-NOW acceptance criterion needs at least one automated test that traces back to it. When you cannot test a criterion (no feasible harness, environment, or observable signal), say so explicitly rather than silently omitting it or claiming coverage you do not have.

Name a test for the requirement or behavior it proves, not the function or method it calls. A reader should understand what would be broken if the test failed without opening the implementation.

## Negative and failure cases

Every material boundary -- a security boundary, an authorization edge, a data-integrity constraint, an external-integration failure mode, an input-validation limit, or a similar consequential edge -- needs at least one negative or failure-path test, not only a happy-path test that exercises the boundary being respected correctly.

## Failing test first

For bug fixes, write a test that reproduces the defect and fails before the fix, then passes after it. For behavior changes where feasible, write the test for the new behavior before implementing it. This is not required when genuinely infeasible (for example, a pure refactor with no behavior change), but skipping it should be a deliberate call, not a default.

## Test independence and mocks

A test should be able to fail for the reason it claims to test, independent of implementation details that could change without changing the behavior under test. Avoid mocks, stubs, or fakes that erase the actual behavior needing verification -- mocking the exact component whose logic is under test defeats the test's purpose, even if it passes.

## Test tampering is governance-relevant

Deleting, skipping, disabling, or weakening a test is a governance-relevant change, not a routine implementation detail; it must appear in the change summary. A test that is correctly failing must be fixed at the defect it caught, not silenced, reduced in scope, or marked `xfail`/`skip` to obtain a green run. "Just make CI green" is satisfied by fixing the underlying defect, never by removing the coverage that found it.
