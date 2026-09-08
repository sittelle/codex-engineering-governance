# v0.3.1 Assurance Integration Validation

Integration only; no new governance policy domain.

Automated validation covers quick/full execution, evidence metadata, NOT_APPLICABLE, required-tool nonexecution, project-local bootstrap, and generated workflow parity.

External field validation still required:
1. run the generated GitHub workflow in a governed project;
2. confirm full passes on the attributable commit and uploads `.governance/evidence/ci-full.json`;
3. deliberately make one required tool unavailable and confirm the job fails with `INCOMPLETE_ASSURANCE`.

Do not weaken the plan to make CI green.

## Local package results

PASS:
- governance static validator;
- Python syntax compilation for assurance scripts;
- POSIX shell syntax checks;
- GitHub workflow YAML parse;
- assurance integration fixture;
- POSIX project lifecycle A-F (dry run, create, refusal, adoption, AGENTS preservation, already-governed refusal).

