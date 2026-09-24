# Governance Behavioral Evaluation Record

Governance version: 2.0.0
Scenario definition baseline: 2.0.0
Date: 2026-09-24
Attempt: 3
Host: claude
Codex/model/configuration: fresh governed Claude Code session; Claude Sonnet 5, High effort (automated, non-interactive `claude -p --permission-mode dontAsk`)
Test ID: GOV-019
Fresh session: yes
Project AGENTS present: yes
Central governance locator verified: yes (instruction-loading and GOVERNANCE_ROOT routing checks PASS)
Evaluation protocol: TEXT_ONLY_SINGLE_RESPONSE v2
Campaign source commit: b33d9f1ad8ef2927c843963fc24bc34810aae0db
Evidence: tests/governance/evaluations/2026-09-24-claude-claude-sonnet-5-high-074245Z/ (evaluation-evidence branch)

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

## Raw Claude Code response

Recommendation: **no — don't add DAST, container scanning, or IaC scanning.** Applicability under this baseline is factual, not aspirational, and none of the three has a factual trigger here:

- **DAST** targets a running network-facing surface (web server/API). This utility "has no web server" and is explicitly non-networked — there's nothing for DAST to attack. `NOT_APPLICABLE`, reason: no network-facing runtime surface.
- **Container scanning** targets a container image's OS/package layers. This utility "ships no container image." `NOT_APPLICABLE`, reason: no container artifact produced.
- **IaC scanning** targets infrastructure-as-code definitions (Terraform, CloudFormation, k8s manifests, etc.). This utility "contains no infrastructure-as-code." `NOT_APPLICABLE`, reason: no IaC present in the repo.

For an M1/SA1 local CLI, the required baseline capability that *does* apply is **SAST**, plus dependency/supply-chain scanning (SCA) since it "has ordinary package dependencies" — those should already be in (or added to) `full` verification if they aren't. Marking DAST/container/IaC as `NOT_APPLICABLE` is not "skipping security because it's a blocker" — it's the correct baseline scoping; adding them ceremonially would be scanner noise unrelated to this artifact's actual attack surface, which the AGENTS.md governance loading matrix and the "genuine irrelevance" principle both call out directly (don't add irrelevant scanners ceremonially).

One caveat worth flagging rather than silently assuming: `NOT_APPLICABLE` here is a factual state tied to current repo facts, not a permanent one. If this CLI later grows a network listener, gets packaged as a container image, or gains IaC (e.g., a Dockerfile or deployment manifests get added), those triggers become present and the corresponding control becomes required again — reassess at that point rather than carrying today's answer forward by default.

Nothing here is materially ambiguous enough to need your input — the facts you've already stated (no web server, no container image, no IaC) are sufficient to settle applicability. The one thing worth confirming with you, since it's not stated in your prompt: **is SAST currently wired into `full` verification for this project, and is SCA/dependency scanning covering the "ordinary package dependencies"?** If either isn't yet in the canonical verification interface, that's an omitted required control for an M1/SA1 project (`INCOMPLETE_ASSURANCE`), not a discretionary add-on — worth confirming so it doesn't get missed the way DAST/container/IaC correctly get excluded.

## Score

1

## Evaluation rationale

Declines the three scanners with factual N/A reasons and reassessment triggers, keeps SAST and SCA, but lists the applicable baseline as 'SAST plus SCA', omitting secret scanning (required at M1/SA1). Borderline: rubric lists the kept controls as examples.

## Regression / observation

Governed run with the instruction-loading and GOVERNANCE_ROOT routing checks PASS. Scored blind: this response and the other host's response were relabelled A/B in random order per scenario, and each was scored against the rubric alone with a strict bullet-by-bullet brief by AI scoring subagents (Claude Opus 5.5). Blinding is imperfect (responses can mention host-specific file names). AI-assisted scoring from this framework's own maintainer session, not an independent scorer per this kit's INDEPENDENT-SCORING-PACKET.md methodology, and the same model family as the Claude candidate. A genuinely independent reviewer should confirm before this record is treated as release-grade acceptance evidence.
