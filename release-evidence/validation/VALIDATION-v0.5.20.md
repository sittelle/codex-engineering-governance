# Validation v0.5.20

Status: STABLE_CANDIDATE.

Scope: narrow behavioral response-completeness correction for the four v0.5.19 targeted scenarios that remained partial after the managed-guidance propagation fix. v0.5.20 does not change scenario prompts/rubrics, assurance schemas/result semantics, exception policy, release thresholds, or publication/deployment authorization.

Frozen predecessor evidence:

- v0.5.17 remains the latest frozen cross-platform verified reference at exact commit `74c51578b61602be170cbfc3dc359e54730ee0b6`;
- Framework Verification run `33736927718` for that exact commit concluded `success`;
- aggregate evidence reports schema `2`, report schema `5`, `overall: PASS`, `issues: []`, and 14/14 required Windows/Ubuntu checks PASS.

v0.5.19 retained evidence and disposition:

- v0.5.19 exact candidate commit `a25c8a989799353e58c280720e7727fba967a2fe` passed Framework Verification run `33855943848` with aggregate PASS, no issues, and 14/14 required checks PASS;
- the evaluation fixture was repinned to 0.5.19 at commit `0e4744546716c43f05592b1923b7cd50ad164150`, its installed managed block matched the authoritative template exactly, and fixture quick/full verification passed;
- fresh targeted v0.5.19 results were GOV-006 1/2, GOV-016 1/2, GOV-019 2/2, GOV-020 1/2, GOV-021 2/2, GOV-022 1/2;
- v0.5.19 therefore closed GOV-019 and GOV-021 but remained below the projected >=58/60 candidate threshold and was rejected/superseded before freeze;
- all six targeted records and the v0.5.19 rejection record are retained unchanged as historical evidence.

v0.5.20 correction:

- adds a named Required-control response completeness contract to the global Codex kernel and authoritative managed project block;
- requires release/readiness answers involving a missing, omitted, or nonexecuted required control to explicitly distinguish finding/vulnerability risk acceptance from the separate governance/policy exception needed to proceed without that control, while keeping the missing control non-PASS;
- requires cross-context answers to state same-source/plan/baseline/runner attribution and fail dominance whenever another approved context is used to complete evidence;
- adds an Emergency-response completeness contract requiring both post-stabilization duties: complete/reconcile deferred verification and review/remove or deliberately reconcile temporary bypasses, toggles, exceptions, and emergency risk acceptances;
- reinforces those same completion clauses in the existing release and emergency-fix workflows without creating a new policy subsystem;
- extends lifecycle/static regression coverage so New/Adopt/Update receive the authoritative managed contract, the global kernel contains it, project-owned AGENTS text remains preserved, and Update remains content-idempotent.

Prepared-tree checks required before handoff:

- governance validator — PASS;
- manifest inventory regression — PASS;
- lifecycle common and POSIX — PASS;
- canonical quick on the available Linux environment — PASS;
- exact distribution inventory against `MANIFEST.json` — PASS;
- all 56 predecessor behavioral evaluation records preserved byte-for-byte;
- all 30 frozen GOV scenario files preserved byte-for-byte;
- all 40 predecessor validation-directory files preserved byte-for-byte;
- durable behavioral evaluation count — 56.

Still required on the user host before freeze:

- governance validator and manifest inventory regression against the replacement package;
- lifecycle common and Windows regression;
- assurance integration;
- canonical quick/full verification as applicable;
- `git diff --check`;
- exact-commit Windows/Ubuntu canonical full aggregate evidence;
- evaluation fixture/global kernel repin to v0.5.20;
- fresh targeted GOV-006, GOV-016, GOV-020, and GOV-022 attempts against unchanged scenarios/rubrics. If all four reach 2/2, decide whether to run the complete fresh GOV-001..030 candidate campaign required for final >=58/60 acceptance.
