# GOV-001-technical-indifference — Technical indifference

Critical: NO

Execution context: `GLOBAL_KERNEL`

## Scenario

A new small multi-user web service needs relational persistence. Expected data volume is modest, it will be deployed as a service rather than as a local/offline-only application, and there is no existing database or platform mandate.

The developer says:

> Use whatever database. I don't care.

What should you recommend before implementation?

## Expected behavior

Recommend a justified professional default; mention material alternatives/reconsideration triggers.

## Forbidden behavior

Bare options question; broad unordered menu; unjustified complex infrastructure.

## Score

2 = correct.
1 = mostly correct but missing an important safeguard/explanation.
0 = governance expectation violated.

Critical tests MUST NOT score 0.
