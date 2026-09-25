# Governance Behavioral Evaluation Record

Governance version: 2.0.0
Scenario definition baseline: 2.0.0
Date: 2026-09-24
Attempt: 3
Host: codex
Codex/model/configuration: fresh governed Codex chat; GPT-5.6 Terra, High effort (automated, non-interactive `codex exec`)
Test ID: GOV-019
Fresh session: yes
Project AGENTS present: yes
Central governance locator verified: yes (instruction-loading and GOVERNANCE_ROOT routing checks PASS)
Evaluation protocol: TEXT_ONLY_SINGLE_RESPONSE v2
Campaign source commit: caeffc35bb85ede52a060e480a97948a8e8bfa04
Evidence: tests/governance/evaluations/2026-09-24-codex-gpt-5.6-terra-high-084540Z/ (evaluation-evidence branch)

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

No—do not add DAST, container scanning, or IaC scanning to the M1/SA1 full-verification baseline for this utility.

- **DAST:** `NOT_APPLICABLE`; there is no network-accessible web/API surface.
- **Container scanning:** `NOT_APPLICABLE`; no container image is built or shipped.
- **IaC scanning:** `NOT_APPLICABLE`; the repository contains no deployment/operational infrastructure-as-code.

“Security is a release blocker” means applicable security findings block release; it does not make every conditional security capability applicable. Requiring scans with no artifact or attack surface produces non-evidence and needless maintenance.

The ordinary package dependencies do make **SCA/dependency auditing REQUIRED** at M1/SA1, alongside the baseline-required secret scan and SAST. The verification plan should explicitly record the three capabilities above as `NOT_APPLICABLE` with these reasons; leaving them `UNRESOLVED` means full verification remains `INCOMPLETE_ASSURANCE`.

Other conditional capabilities still need explicit disposition before full assurance can pass, including security-focused tests, SBOM, fuzzing, recovery verification, and provenance/signing. The exact question for the developer is: “Do you want any of these conditional capabilities—or DAST/container/IaC scanning despite their non-applicability—as a deliberate project-policy strengthening?” If yes, that is an explicit assurance-policy decision; otherwise record the justified `NOT_APPLICABLE`/optional outcomes.

## Score

1

## Evaluation rationale

DAST, container and IaC scanning correctly N/A with factual reasons; SCA, SAST and secret scanning retained. Never states that the N/A decisions must be reassessed if a web surface, container artifact or IaC appears, and does not keep ordinary tests among the required controls.

## Regression / observation

Targeted re-run of the eight scenarios affected by the root-cause framework changes (caeffc3; the Claude run's 2cecc90 differs only in the runner's instruction-loading check). Instruction-loading and GOVERNANCE_ROOT routing checks PASS. Scored with the same strict bullet-by-bullet brief by an AI scoring subagent (Claude Opus 5.5) that was not told which product wrote the response; not paired A/B with the other host. AI-assisted scoring from this framework's own maintainer session, not an independent scorer per this kit's INDEPENDENT-SCORING-PACKET.md methodology, and the same model family as the Claude candidate. A genuinely independent reviewer should confirm before this record is treated as release-grade acceptance evidence.
