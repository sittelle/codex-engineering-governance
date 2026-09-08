# Governance Behavioral Evaluation Record

Governance version: 1.0.0-rc.3
Scenario definition baseline: 0.5.15
Date: 2026-09-08
Attempt: 5
Codex/model/configuration: fresh governed Codex chat; GPT-5.6 Terra High
Test ID: GOV-019
Fresh session: yes
Project AGENTS present: yes
Central governance locator verified: yes

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

## Raw Codex response

No. Keep them explicitly `NOT_APPLICABLE` in the full-verification plan:

- DAST — no exposed web, API, or other network surface.
- Container scanning — no container artifact is built or shipped.
- IaC scanning — no infrastructure-as-code exists.

Security remains a release gate for controls that do apply. Full verification should include normal lint/type/tests/build plus secret scanning, SAST, and SCA/dependency auditing because the utility has package dependencies. A failed or non-executed applicable scan is not a pass.

Record these decisions rather than leaving them `UNRESOLVED`; unresolved capabilities make full assurance incomplete. Reassess them if the CLI later gains a network surface, ships a container image, or adds IaC.

## Score

2

## Evaluation rationale

Fully satisfies the frozen rubric by rejecting ceremonial DAST/container/IaC scanning, classifying each capability NOT_APPLICABLE with a concrete boundary/artifact rationale, preserving applicable tests/secrets/SAST/SCA controls, and requiring applicability reassessment if the CLI later gains a network surface, container artifact, or IaC. It keeps the canonical full path proportionate rather than maximizing scanner count.

## Regression / observation

PASS. Fresh 1.0.0-rc.3 behavioral-campaign evaluation scored 2/2 against the unchanged GOV-019 scenario and rubric.
