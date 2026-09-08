# v0.3.2 Regression / Integration Validation

## Defects addressed

1. Windows direct argv execution could not resolve the Node `npm` command shim even though `shutil.which("npm")` resolved `npm.CMD` successfully in the affected environment.
2. A verification plan could omit a baseline-required capability entirely and still report PASS if all configured checks succeeded.

## Static/integration acceptance

- plan schema v2 and managed capability baseline present;
- required baseline omission => `INCOMPLETE_ASSURANCE`;
- baseline-required downgrade => `INCOMPLETE_ASSURANCE`;
- conditional `UNRESOLVED` => `INCOMPLETE_ASSURANCE`;
- REQUIRED capability without full-stage evidence => `INCOMPLETE_ASSURANCE`;
- required missing executable => `DID_NOT_EXECUTE` / `INCOMPLETE_ASSURANCE`;
- executable is resolved with `shutil.which()` and the resolved path is retained in evidence;
- report contains plan and baseline SHA-256 plus capability preflight;
- bootstrap copies `.governance/assurance-baseline.json`;
- CI invokes the same plan and baseline.

## External Windows evidence

Observed on the affected Windows host before implementation:

```text
resolved: C:\Program Files\nodejs\npm.CMD
version: 11.6.2
exit: 0
```

This establishes the intended portability mechanism for the previously failing `npm` command.

## Behavioral validation required

Run GOV-020 in a fresh governed session pinned to 0.3.2. PASS requires GOV-020 = 2.

Then reconcile one real schema-v1 project to v2 and rerun local quick/full before resuming GitHub field validation.
