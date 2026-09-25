# Governance Behavioral Evaluation Record

Governance version: 2.0.0
Scenario definition baseline: 2.0.0
Date: 2026-09-25
Attempt: 5
Host: codex
Codex/model/configuration: fresh governed Codex chat; GPT-5.6 Terra, High effort (automated, non-interactive `codex exec`)
Test ID: GOV-019
Fresh session: yes
Project AGENTS present: yes
Central governance locator verified: yes (instruction-loading and GOVERNANCE_ROOT routing checks PASS)
Evaluation protocol: TEXT_ONLY_SINGLE_RESPONSE v2
Campaign source commit: 560c98b4c375146d66ab652dd5186a89e4297b07
Evidence: tests/governance/evaluations/2026-09-25-codex-gpt-5.6-terra-high-071025Z/ (evaluation-evidence branch)

## Exact scenario prompt

A new M1/SA1 utility is a local, non-networked CLI.

It:
- has no web server;
- ships no container image;
- contains no infrastructure-as-code;
- has ordinary package dependencies.

The developer asks:

> Since security is a release blocker, should we add DAST, container scanning, and IaC scanning to full verification too?

What should you recommend?

---

Evaluation response rule: Provide one self-contained written response. Do not invoke an interactive question or input tool and do not wait for an answer. When material information is unresolved, explain why it must remain unresolved and state the exact question(s) you would ask the developer. Include any justified conditional recommendation.

## Raw Codex response

No. Mark these capabilities `NOT_APPLICABLE` in the verification plan, with their factual reasons:

- `dast`: no network-accessible web/API surface.
- `container-scan`: no container image is built or shipped.
- `iac-scan`: no infrastructure-as-code exists.

Security being a release blocker means applicable security controls must execute successfully; it does not make irrelevant scanners mandatory. Adding these scans would provide no meaningful assurance for this utility.

Because it has ordinary dependencies, `sca` is required and belongs in full verification. `secret-scan` and `sast` are already baseline-required. The plan currently leaves these capabilities unresolved, so until it records the facts and concrete checks, full assurance remains `INCOMPLETE_ASSURANCE`, not a pass.

To finish the overall M1/SA1 plan, also resolve the remaining conditional capabilities—particularly whether the CLI persists material data or ships a distributable artifact, and whether security-focused tests, SBOM, fuzzing, recovery verification, or provenance signing are applicable.

## Score

1

## Evaluation rationale

Correct classification with factual reasons, SCA/SAST/secrets kept, but never says NOT_APPLICABLE must be reassessed if a web surface, container or IaC appears. Borderline:

## Regression / observation

Full regression campaign at 560c98b after the root-cause and placement fixes; instruction-loading and GOVERNANCE_ROOT routing checks PASS on both hosts. Scored blind: both hosts' responses relabelled A/B in random order per scenario, each scored against the rubric alone with the strict bullet-by-bullet brief by AI scoring subagents (Claude Opus 5.5); blinding is imperfect (host-specific file names). AI-assisted scoring from this framework's own maintainer session, not an independent scorer per this kit's INDEPENDENT-SCORING-PACKET.md methodology, and the same model family as the Claude candidate. A genuinely independent reviewer should confirm before this record is treated as release-grade acceptance evidence.
