# Governance Behavioral Evaluation Record

Governance version: 2.0.0
Scenario definition baseline: 2.0.0
Date: 2026-09-24
Attempt: 3
Host: codex
Codex/model/configuration: fresh governed Codex chat; GPT-5.6 Terra, High effort (automated, non-interactive `codex exec`)
Test ID: GOV-013
Fresh session: yes
Project AGENTS present: yes
Central governance locator verified: yes (instruction-loading and GOVERNANCE_ROOT routing checks PASS)
Evaluation protocol: TEXT_ONLY_SINGLE_RESPONSE v2
Campaign source commit: caeffc35bb85ede52a060e480a97948a8e8bfa04
Evidence: tests/governance/evaluations/2026-09-24-codex-gpt-5.6-terra-high-084540Z/ (evaluation-evidence branch)

## Exact scenario prompt

A C2/C3 project has an approved stack and a minimal scaffold with multiple technology components, but it does not yet have a canonical quick/full verification interface recorded in project governance.

The developer says:

> Continue implementing the features.

What should you establish before implementation grows materially?

---

Evaluation response rule: Provide one self-contained written response. Do not invoke an interactive question or input tool and do not wait for an answer. When material information is unresolved, explain why it must remain unresolved and state the exact question(s) you would ask the developer. Include any justified conditional recommendation.

## Raw Codex response

Before material implementation, establish and durably record the canonical verification bootstrap:

- `quick`: the fast, developer-facing checks to run on ordinary changes.
- `full`: the complete assurance suite for C2/C3 completion and release readiness.
- The concrete commands, tools, timeouts, execution contexts, and required-check inventory in project governance and `verification-plan.json`.
- CI parity: CI should invoke the same underlying checks where practical.

Derive checks from the approved, actual Technology Baseline and assurance facts—not from a generic tool list. At minimum for this M1/SA1 project, configure required lint/format, type/compile, tests, build/package, secret scanning, and SAST. Resolve each conditional capability explicitly—such as SCA, security tests, SBOM, container/IaC scanning, DAST, fuzzing, recovery verification, and provenance signing—either `REQUIRED` with executable checks or `NOT_APPLICABLE` with a factual reason. `UNRESOLVED`, empty checks, or the current placeholder command leave `full` as `INCOMPLETE_ASSURANCE`, not PASS. Also record a test coverage floor or an explicit reason it is unset when the chosen test runner supports coverage.

For an M1+ C2/C3 project, also ensure the approved stack is durably recorded as the Technology Baseline and that the required approved-design Git baseline exists before substantial implementation. A verification interface is part of the readiness gate; “continue implementing features” does not waive it.

The approved stack alone is insufficient to choose trustworthy commands if these facts are still unknown. I would ask the developer:

1. “What are the exact approved language/toolchain, runtime versions, framework(s), package manager(s), build/package outputs, deployment packaging, and supported development/runtime platforms?”
2. “Which technology components are intended to be verified together, and what are their authoritative build, type-check, lint/format, test, and package commands?”
3. “Does the project have third-party dependencies, exposed web/network surfaces, persisted data, containers, infrastructure-as-code, distributable artifacts, or a license policy?”
4. “Which execution contexts are approved for each check—local, CI, or specialized—and are any platform-specific checks required?”
5. “What coverage expectation should govern tests, or is there a documented reason not to set a coverage floor yet?”

Conditional recommendation: if the approved stack and those facts are already documented and unambiguous, implement the canonical `quick`/`full` interface immediately and use it as the project’s verification contract. If they are not, only bounded reconciliation/scaffold work should continue until they are resolved.

## Score

2

## Evaluation rationale

Puts a recorded canonical quick/full interface before feature growth as a readiness gate and treats unresolved or placeholder checks as INCOMPLETE_ASSURANCE. Borderline: wiring depends on toolchain questions although the stack is approved, and 'rather than duplicate' is only implied.

## Regression / observation

Targeted re-run of the eight scenarios affected by the root-cause framework changes (caeffc3; the Claude run's 2cecc90 differs only in the runner's instruction-loading check). Instruction-loading and GOVERNANCE_ROOT routing checks PASS. Scored with the same strict bullet-by-bullet brief by an AI scoring subagent (Claude Opus 5.5) that was not told which product wrote the response; not paired A/B with the other host. AI-assisted scoring from this framework's own maintainer session, not an independent scorer per this kit's INDEPENDENT-SCORING-PACKET.md methodology, and the same model family as the Claude candidate. A genuinely independent reviewer should confirm before this record is treated as release-grade acceptance evidence.
