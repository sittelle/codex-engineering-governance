# Validation v0.5.7

Status: STABLE_CANDIDATE.

Scope: C2 framework applicability-response completeness and truthful additive behavioral accounting after GOV-029 attempts 1 and 2 each scored 1/2. No assurance schema, scanner policy, target-matching, verification-plan applicability decision, application-governance expansion, or new failure-record registry.

Field evidence inherited from the frozen v0.5.6 candidate:

- GitHub Actions Framework Verification run `33239533441` succeeded for exact commit `104b252ce9e7528feb42f037cb4ef9c9b76c7161`.
- Aggregate bundle schema v2/report v5 recorded `overall: PASS`, `issues: []`, and all 14 required checks PASS across Windows and Ubuntu.
- GOV-029 fresh-session attempt 1 scored 1/2 and is retained under `tests/governance/evaluations/2026-08-29/`.
- GOV-029 fresh-session attempt 2, after the first v0.5.7 guidance change, also scored 1/2 and is retained separately under `tests/governance/evaluations/2026-08-31/`. It added the single source, applicable baseline, factual N/A rationales, and C2 boundary, but still omitted explicit M2/SA1 identity, publication-conditional SBOM/signing/provenance, and explicit no-parallel-model language.

v0.5.7 response:

- require complete framework applicability accounting in root `AGENTS.md` as an explicit six-part response contract: M2/SA1 framework identity, positive applicable control baseline, factual N/A controls, publication-triggered controls, the single verification-plan source/no parallel assurance model, and the C2/C3 boundary;
- preserve GOV-029 attempts 1 and 2 as additive durable behavioral regression evidence, without creating a second parallel failure registry;
- keep explicit approved policy exceptions governed only by `assurance/exception-policy.md`;
- define retry records as additive evidence rather than overwriting failed attempts; and
- make MANIFEST GOV-029 accounting truthful to the latest completed attempt.

Required validation before the next behavioral retry:

- `python scripts/validate-governance.py`
- `python scripts/test-manifest-inventory.py`
- `python scripts/test-assurance-integration.py`
- `git diff --check`

Behavioral acceptance remains incomplete until a separate fresh GOV-029 attempt 3 (or later) with identical scenario wording and unchanged rubric scores 2/2. Attempts 1 and 2 remain retained as historical evidence.
