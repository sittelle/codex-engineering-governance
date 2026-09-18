# Phase 3 review — business-led mode

Prepared per the same pattern as `docs/business-led/phase-2-review.md`, on
`feature/business-led-mode`. Covers phase 3 (conformance scan) as scoped by
section 7's phase table: capability rules for Python and TypeScript, drift
state, and the `block` template. The `block` template itself was already
built and live-tested in phase 1 (see phase-2 packet section 6); this phase's
work is the capability-detection rules, the conformance scanner, drift-state
evidence in the readiness packet, and closing the instruction-surface-audit
placeholder phase 2's packet flagged as inherited work (section 8 there).

## 1. Commits

6 commits, each verified with `python scripts/verify-framework.py quick`
before the next, oldest first, starting from the phase-2 packet's final
head (`4a0728f`):

1. `bd4787d` feat: add semgrep capability-detection rules and synthetic fixtures
2. `6367189` feat: add registration conformance scanning script
3. `8065725` test: add heuristic registration-conformance regression suite
4. `821f866` chore: wire registration-conformance into manifest and verification plan
5. `b5be1e9` feat: surface conformance/drift state in the readiness packet
6. `7e441ad` feat: exact hash-pinned instruction-surface allowlist comparison

## 2. `full` output at current head

Run locally on Windows; no Linux runner is available in this environment,
so the Linux/CI-required checks are recorded as `DID_NOT_EXECUTE`, matching
the identical profile recorded in the phase-2 packet — no new
`DID_NOT_EXECUTE` or `FAIL` was introduced by this phase's work.

```
[governance-static]        -> PASS
[python-compile]           -> PASS
[manual-behavioral-campaign-kit] -> PASS
[assurance-integration]    -> PASS
[governance-integrity]     -> PASS
[registration-conformance] -> PASS   (new check, this phase)
[manifest-package]         -> PASS
[lifecycle-common]         -> PASS
[lifecycle-windows]        -> DID_NOT_EXECUTE (assigned to CI)
[lifecycle-posix]          -> DID_NOT_EXECUTE (assigned to CI)
[scanner-regressions-linux]   -> DID_NOT_EXECUTE (assigned to CI)
[scanner-regressions-windows] -> DID_NOT_EXECUTE (assigned to CI)
[secret-scan]               -> DID_NOT_EXECUTE (assigned to CI)
[sast-python]                -> DID_NOT_EXECUTE (assigned to CI)
[sast-posix]                 -> DID_NOT_EXECUTE (assigned to CI)
[sast-powershell]            -> DID_NOT_EXECUTE (assigned to CI)
[workflow-security]          -> DID_NOT_EXECUTE (assigned to CI)

OVERALL: INCOMPLETE_ASSURANCE
```

## 3. Substitution for the plan's IT Security review requirement

The plan's phase-3 exit criteria call for "false-positive review with IT
Security on three real repositories, documented." No IT Security function
or real target repositories exist in this environment. The maintainer's
explicit direction (2026-09-18): *"Yes, these 'IT Security involvement'
tests will not be part of our real testing. Maybe we can find some
behavioural tests that is a heuristic to a real scenario. Go."*

The substitute built is `scripts/test-registration-conformance.py`, wired
into `framework-verification-plan.json` as a permanent `full`-stage check
(`registration-conformance`), not a one-off validation. It exercises:

- **Recall**: every one of the 7 capability rules (network_connections,
  persistence, authentication, elevated_access, write_or_delete_actions,
  cloud, external_recipients) fires on a synthetic positive trigger, for
  both Python (`semgrep/capabilities/python.yml`) and TypeScript/JavaScript
  (`semgrep/capabilities/typescript.yml`).
- **Precision**: a capability-free negative fixture (`tests/capabilities/*/negative.*`)
  produces zero findings for both languages.
- **End-to-end conformance behavior**: an unregistered capability produces
  `REGISTRATION_RECONCILIATION_REQUIRED` and a `REQUEST-*-capability-drift.md`
  record (never a blocking exit code); a fully registered/clean project
  produces `PASS` with no record; a missing or seal-tampered
  `registration.yml` produces `DID_NOT_EXECUTE`.
- **Readiness-packet integration**: `governance.py project readiness
  --conformance-report` surfaces the conformance result as a
  non-blocking, informational field.

This is explicitly a heuristic stand-in, not equivalent evidence to a
domain expert reviewing real, messy, first-party code for false positives
the synthetic fixtures cannot anticipate (dynamic imports, reflection,
wrapped/aliased calls, framework-specific idioms). Recorded as an open
risk in section 5.

## 4. New and changed files

`semgrep/capabilities/python.yml`, `semgrep/capabilities/typescript.yml`
(new): 8 rules each, one or more per capability, `metadata.capability`
mapping to the registration schema's 7 flags.
`tests/capabilities/python/{positive,negative}.py`,
`tests/capabilities/typescript/{positive,negative}.ts` (new): synthetic
recall/precision fixtures.
`scripts/run-registration-conformance.py` (new): compares detected
capabilities against a sealed `registration.yml`; writes a request record
on drift; `DID_NOT_EXECUTE` (exit 3) on missing/invalid registration or
unavailable `semgrep`, exit 0 otherwise (conformance scanning never blocks
development, matching the framework's standing invariant).
`scripts/test-registration-conformance.py` (new): the heuristic regression
suite described in section 3.
`governance.py` (`build_readiness_packet` gains an optional
`--conformance-report`-derived `conformance` field, informational only —
it does not participate in the readiness `blocking`/`disposition`
calculation).
`assurance/run-verification.py` (`instruction_surface_audit` rewritten
from its documented placeholder — "presence of registration.yml is
sufficient" — to an exact comparison against
`registration.yml`'s `allowlisted_instruction_surfaces`; new local helpers
`registration_seal_valid`, `registration_sealed_content`,
`parse_allowlisted_instruction_surfaces`, self-contained since this file
is copied standalone into every governed project and must not import
`governance.py`).
`scripts/test-governance-integrity.py` (corrected the now-invalid
assumption in `test_unapproved_instruction_surface` that a mere
`registration.yml`'s presence suppresses the flag; two new tests for
exact-match/hash-drift and tampered-seal-untrusts-allowlist).
`framework-verification-plan.json`, `MANIFEST.json`,
`scripts/validate-governance.py` (wiring for all of the above).

## 5. Open questions and known risks

**KNOWN RISK — heuristic tests are not a substitute for real-repository
false-positive review.** Per section 3, explicitly accepted by the
maintainer as this environment's ceiling, not treated as equivalent
evidence. If this framework is deployed against real first-party
repositories, running an actual false-positive pass against a handful of
them before relying on `REGISTRATION_RECONCILIATION_REQUIRED` as an
automated Green-rule input remains genuinely valuable and is not made
redundant by this suite.

**KNOWN LIMITATION — capability detection covers only Python and
TypeScript/JavaScript.** Per the plan's explicit phase-3 scope ("matching
existing profiles"). A project in any other language gets
`detected_languages()` returning nothing for that source, so
`run-registration-conformance.py` reports `PASS` with zero detected
capabilities rather than flagging the language as unscanned — this is
silent, not `DID_NOT_EXECUTE`, and is worth a deliberate decision before
this scanner is treated as authoritative evidence for a non-Python/TS
project.

**KNOWN LIMITATION — `run-registration-conformance.py` depends on
`semgrep` being present on the project's own PATH**, not the framework's
own Docker-pinned invocation used for `scripts/run-framework-scanner.py`.
This was an established design choice (project-level template tooling vs.
the framework's own CI scanning), not new to this phase, but it means a
project without `semgrep` installed gets `DID_NOT_EXECUTE`, not a
blocking failure — consistent with the "never blocks development"
invariant, but something IT Security's automated Green rule needs to
treat as "no evidence" rather than "clean."

**RESOLVED, inherited from the phase-2 packet's section 8 — the
`instruction_surface_audit` placeholder.** Closed by commit `7e441ad`
(section 4). Not re-tested against a live Codex/Claude Code session (no
VM round-trip this phase) — the unit-level fix is verified; live
host-client confirmation of this specific change is not, matching the
same caveat already recorded for the earlier hook-coverage fix.

**OPERATIONAL NOTE — `pip install semgrep` in this development
environment modified global site-packages** and reported dependency
conflicts with unrelated tools already installed on this machine
(`fastapi`, `platformio`, `spotdl`). It did not affect this repository's
own tooling (semgrep is invoked via `shutil.which`, not imported), but is
worth the maintainer's awareness for this machine's Python environment
hygiene; a virtualenv-scoped install would avoid it in the future.

## 6. What phase 4 inherits

The capability-detection rules, conformance scanner, and exact
instruction-surface allowlist comparison are real and working. Phase 4
(WS5, WS6, WS7, GOV-031 to GOV-036 per the plan's phase table) is
unaffected by anything in this phase's scope — no normative content,
kernel, or test-regulation work was touched here.
