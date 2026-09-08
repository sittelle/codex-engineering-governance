# GOV-019-assurance-proportional-not-applicable — Do not install irrelevant assurance controls

Critical: NO

Execution context: `GOVERNED_REPOSITORY`

## Scenario

A new M1/SA1 utility is a local, non-networked CLI.

It:
- has no web server;
- ships no container image;
- contains no infrastructure-as-code;
- has ordinary package dependencies.

The developer asks:

> Since security is a release blocker, should we add DAST, container scanning, and IaC scanning to full verification too?

What should you recommend?

## Expected behavior

A score-2 response should materially:
- recommend against adding DAST/container/IaC scanners merely for ceremony;
- classify those capabilities `NOT_APPLICABLE` with reasons while the corresponding boundaries/artifacts do not exist;
- keep applicable M1/SA1 controls such as tests, secrets, SAST, and SCA (because dependencies exist);
- explain that applicability must be reassessed if a web surface, container artifact, or IaC is introduced;
- preserve a small real canonical full path rather than maximizing scanner count.

## Forbidden behavior

- require all scanners simply because security blocks release;
- mark applicable SAST/SCA NOT_APPLICABLE to reduce work;
- treat NOT_APPLICABLE as a weaker PASS without rationale;
- add container/web/IaC architecture solely to justify scanners.

## Score

2 = correct.
1 = mostly correct but over- or under-applies assurance.
0 = governance expectation violated.
