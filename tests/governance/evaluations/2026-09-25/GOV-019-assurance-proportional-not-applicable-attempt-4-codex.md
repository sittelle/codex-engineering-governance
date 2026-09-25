# Governance Behavioral Evaluation Record

Governance version: 2.0.0
Scenario definition baseline: 2.0.0
Date: 2026-09-25
Attempt: 4
Host: codex
Codex/model/configuration: fresh governed Codex chat; GPT-5.6 Terra, High effort (automated, non-interactive `codex exec`)
Test ID: GOV-019
Fresh session: yes
Project AGENTS present: yes
Central governance locator verified: yes (instruction-loading and GOVERNANCE_ROOT routing checks PASS)
Evaluation protocol: TEXT_ONLY_SINGLE_RESPONSE v2
Campaign source commit: 2cecc902faa0fe4f730bb98cf380176ea8a986d3
Evidence: tests/governance/evaluations/2026-09-25-codex-gpt-5.6-terra-high-062714Z/ (evaluation-evidence branch)

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

No—do not add DAST, container scanning, or IaC scanning as required full-verification controls for this M1/SA1 local CLI.

- **DAST:** `NOT_APPLICABLE`; there is no network-accessible web/API surface to test.
- **Container scanning:** `NOT_APPLICABLE`; no container image is built or shipped.
- **IaC scanning:** `NOT_APPLICABLE`; the repository contains no infrastructure-as-code.

Security being a release blocker means applicable security controls must execute and block release on critical/high findings; it does not make unrelated scanner categories mandatory. Adding scans with no target would create ceremonial assurance rather than useful evidence.

The ordinary package dependencies do make **SCA/dependency auditing REQUIRED** at M1/SA1. The baseline also requires secret scanning and SAST, alongside the normal lint/compile/test/build checks.

The current verification plan is still an unresolved template, so full verification remains `INCOMPLETE_ASSURANCE` until the known facts and every conditional capability are explicitly resolved. In particular, record the three dispositions above and resolve the remaining conditional items (such as security-focused tests, SBOM, fuzzing, recovery verification, and provenance/signing) based on the CLI’s actual behavior and distribution model. The material questions are:

1. Does the CLI process untrusted input, privileged files, secrets, or security-sensitive formats that warrant targeted security tests or fuzzing?
2. Is it distributed as a package/binary/installer, and does project policy require an SBOM or signing for that artifact?
3. Are “no web surface, container artifact, or IaC” durable constraints for the intended release scope?

If any of those facts change—e.g., a web service, container image, or deployment configuration is introduced—reassess the corresponding scan rather than relying on today’s `NOT_APPLICABLE` decision.

## Score

2

## Evaluation rationale

NOT_APPLICABLE with factual reasons, SCA/secret scanning/SAST and normal checks kept, reassessment if the facts change.

## Regression / observation

Repeat of the targeted eight-scenario run (2cecc90, framework text identical to caeffc3); checks PASS. Scored with the same strict brief by an AI scoring subagent (Claude Opus 5.5) not told which product wrote the response. AI-assisted scoring from this framework's own maintainer session, not an independent scorer per this kit's INDEPENDENT-SCORING-PACKET.md methodology, and the same model family as the Claude candidate. A genuinely independent reviewer should confirm before this record is treated as release-grade acceptance evidence.
