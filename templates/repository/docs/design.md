# Project Design

Use this combined document for small M1/SA1 projects. Split into dedicated requirements/architecture/security files when complexity, maturity, or assurance warrants.

## Purpose and actors

## Scope

### Required
- FR-001: ...

### Non-functional
- NFR-001: ...

### Security
- SR-001: ...

### Prohibited behavior
- PROH-001: ...

### Non-goals
- OUT-001: ...

## Data

## Architecture

Describe system boundary, components, persistence, external systems, deployment, and failure behavior.

## Technology Baseline

State is tracked in `project-governance.yml`; this section is the default durable record for architecture-significant technology choices.

| Category | Decision | Scope / role | Material rationale | Constraints / support | Reconsider when |
|---|---|---|---|---|---|
| Language / toolchain | ... | ... | ... | ... | ... |
| Runtime | ... | ... | ... | ... | ... |
| Primary framework | ... | ... | ... | ... | ... |
| Persistence | ... | ... | ... | ... | ... |
| Deployment / packaging | ... | ... | ... | ... | ... |
| Supported targets | ... | ... | ... | ... | ... |

Add or remove rows according to the project. Record stack-shaping decisions, not the complete dependency graph. Exact resolved dependency versions belong in ecosystem manifests/lockfiles unless a version itself is architecture-significant.

## Security assumptions

## Testing and verification

## Open questions
