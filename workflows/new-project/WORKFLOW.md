# New Project Workflow

DISCOVER → REQUIREMENTS → MATURITY/ASSURANCE → THREAT/RISK → ARCHITECTURE OPTIONS → TECHNOLOGY SELECTION → TECHNOLOGY BASELINE → IMPLEMENTATION PLAN → READINESS GATE → INITIALIZE → VERIFICATION BOOTSTRAP → IMPLEMENT → VERIFY.

Material vague answers remain unresolved. Technical choices receive a recommendation. Product/security intent is asked.

Before READY FOR IMPLEMENTATION for C2/C3 summarize purpose, FR/NFR/SR/PROH/OUT, architecture, Technology Baseline, data/security implications, assumptions, open questions, plan, and verification.

Initialize only after material direction approval. Empty repository is not permission to choose a stack or architecture silently.

## Technology Baseline

For M1+ projects:
- begin from `technology_baseline.state: "UNESTABLISHED"`;
- after requirements/architecture constraints are sufficient, invoke `technology-selection` for consequential choices;
- record architecture-significant technology decisions in the durable record referenced by `project-governance.yml`;
- include primary language/toolchain, runtime, central framework/platform, persistence, deployment/packaging, supported targets, and other stack-shaping components only as applicable;
- keep exact dependency graphs in ecosystem manifests/lockfiles rather than duplicating them in governance;
- set the state to `ESTABLISHED` only when the durable record reflects the intended direction and any required C2/C3 approval has occurred.

A technically justified C1 default does not require ceremonial approval merely because it becomes part of the baseline. C2/C3 Technology Baseline direction does.

Do not begin substantial implementation while an M1+ Technology Baseline is `UNESTABLISHED` or unresolved, except bounded scaffold/reconciliation work needed to establish it.

## Authentication-design gate

If the project is SA-2/SA-3 and will locally manage authentication, sessions, enrollment, credentials, or certificate trust:
- invoke `authentication-design`;
- document the credential/session/trust lifecycle;
- resolve material recovery/revocation/bootstrap questions;
- approve the security direction before implementing auth plumbing.

## Version-control baseline

For M1+ C2/C3:
- initialize Git after the approved design and Technology Baseline direction are recorded;
- capture an approved-design baseline commit before substantial implementation.

## Verification bootstrap

After Technology Baseline establishment and initial repository scaffold:
- define canonical quick verification;
- define canonical full verification;
- derive applicable lint/type/test/build/SAST/SCA/platform and other assurance checks from the actual stack and project assurance facts;
- ensure CI can later call the same underlying logic where practical.

Do this before implementation grows beyond the initial scaffold.

If the Technology Baseline later changes materially, reconcile canonical verification before the transition is considered complete.
