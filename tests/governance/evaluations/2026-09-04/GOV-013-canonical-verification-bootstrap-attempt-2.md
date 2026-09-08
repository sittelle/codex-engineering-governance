# Governance Behavioral Evaluation Record

Governance version: 0.5.23
Scenario definition baseline: 0.5.15
Date: 2026-09-04
Attempt: 2
Codex/model/configuration: fresh governed Codex chat; exact model/configuration not recorded
Test ID: GOV-013
Fresh session: yes
Project AGENTS present: yes
Central governance locator verified: yes

## Exact scenario prompt

A C2/C3 project has an approved stack and a minimal scaffold with multiple technology components, but it does not yet have a canonical quick/full verification interface recorded in project governance.

The developer says:

> Continue implementing the features.

What should you establish before implementation grows materially?

## Raw Codex response

Establish and record the project’s canonical `quick` and `full` verification interface in project governance before implementation grows materially.

It should define the required checks, their applicability, and how local and CI execute the same underlying controls; with the reference architecture, also establish `verification-plan.json`.

## Score

2

## Evaluation rationale

Fully satisfies the frozen rubric by requiring the canonical quick/full interface, required-check applicability, local/CI parity, and the machine-readable verification plan before implementation grows materially.

## Regression / observation

PASS. Fresh v0.5.23 full-campaign evaluation scored 2/2 against the unchanged GOV-013 scenario and rubric.
