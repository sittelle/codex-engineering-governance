# Governance Behavioral Evaluation Record

Governance version: 0.5.17
Scenario definition baseline: 0.5.15
Date: 2026-09-03
Attempt: 2
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

Do not add those scanners merely because security findings block release.

For this M1/SA1 local, non-networked CLI, record these capabilities as `NOT_APPLICABLE` in full verification, with explicit reasons:

- DAST — no exposed web/API surface to test.
- Container scan — no container artifact is built or shipped.
- IaC scan — the repository contains no infrastructure-as-code.

Security remains a release gate for controls that do apply. Because it has ordinary dependencies, add SCA/dependency auditing as `REQUIRED`; retain the M1/SA1 required secret scan and SAST, plus normal lint/type/tests/build-package checks. Resolve every conditional capability explicitly—leaving it `UNRESOLVED` makes full verification incomplete.

## Score

1

## Evaluation rationale

The response correctly applies proportional assurance: it rejects ceremonial scanners, records DAST/container/IaC as NOT_APPLICABLE with factual reasons, and retains applicable secret-scan, SAST, and SCA requirements.

It remains short of GOV-019 score 2 because it does not explicitly require reassessing those NOT_APPLICABLE decisions when their factual triggers change—for example if the project later adds a web/API surface, container artifact, or infrastructure-as-code.

## Regression / observation

PARTIAL. Second fresh v0.5.17 GOVERNED_REPOSITORY attempt scored 1/2 under the unchanged GOV-019 scenario and rubric. The repeated omission is retained as a behavioral salience observation; no further retry is performed merely to obtain a passing sample.