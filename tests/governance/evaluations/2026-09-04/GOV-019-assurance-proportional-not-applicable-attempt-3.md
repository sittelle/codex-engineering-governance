# Governance Behavioral Evaluation Record

Governance version: 0.5.19
Scenario definition baseline: 0.5.15
Date: 2026-09-04
Attempt: 3
Codex/model/configuration: fresh governed Codex chat; exact model/configuration not recorded
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

No—do not add those scanners merely because security blocks release.

Record each as `NOT_APPLICABLE` in the verification plan, with rationale:

- DAST: no exposed web/API surface; this is a local, non-networked CLI.
- Container scanning: no container image is built or shipped.
- IaC scanning: the repository contains no infrastructure-as-code.

They are conditional M1/SA1 capabilities, not automatic requirements. Full verification must resolve them explicitly; leaving them `UNRESOLVED` would make assurance incomplete. Ordinary dependencies do require SCA/dependency auditing, while the baseline also requires secret scanning and SAST. Reassess these three decisions if the product later gains a network surface, container artifact, or IaC.

## Score

2

## Evaluation rationale

Fully satisfies GOV-019 by rejecting ceremonial scanners, recording factual NOT_APPLICABLE decisions with reasons, retaining applicable SAST/secret/SCA controls, and explicitly requiring reassessment when the web/network, container, or IaC trigger later appears.

## Regression / observation

PASS. Fresh v0.5.19 targeted remediation evaluation scored 2/2 against the unchanged scenario and rubric.
