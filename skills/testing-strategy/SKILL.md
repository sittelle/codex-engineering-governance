# Testing Strategy

Derive tests from observable behavior, risk, consequence, architecture, and failure modes.

Use unit/component/integration/contract/E2E/security/performance tests only as appropriate. Test negative/adversarial cases for security boundaries.

Do not optimize for test count or arbitrary coverage percentage. Avoid mocks that erase the behavior actually needing verification.

Deleting, skipping, disabling, or weakening a test is a governance-relevant change, not a routine implementation detail; it must appear in the change summary, and a test that is correctly failing must be fixed at the defect it caught, not silenced.
