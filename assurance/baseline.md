# Assurance Baseline

## Canonical levels

Every M1+ governed project exposes a canonical `quick` and `full` verification interface once the stack is approved and verification can be bootstrapped.

Capability selection is defined by `capability-matrix.md`, project profiles/threat model, change class, and workflow.

## Evidence states

Machine check states:
- PASS
- FAIL
- NOT_APPLICABLE
- DID_NOT_EXECUTE

`DID_NOT_EXECUTE` is never PASS.

Overall full verification is `INCOMPLETE_ASSURANCE` when any required applicable control did not execute or required evidence is missing.

## Tool independence

Reference candidates include:
- secrets: Gitleaks;
- SAST: Semgrep Community Edition;
- SCA: OSV-Scanner or ecosystem-native audit;
- tests/build/type/lint: technology-native.

Equivalent or stronger tools are acceptable.

Do not substitute a branded-tool checklist for the required assurance capability.


## Machine baseline

`capability-baseline.json` is the executable companion to the human capability matrix. Project-local bootstrap copies it to `.governance/assurance-baseline.json` so local and CI verification can prove which baseline was used.
