# Framework release evidence

For every distributed framework release, retain a release record under `<version>/release-record.md` or an equivalent durable CI/release record.

The record must bind:
- exact clean Git commit;
- distributable filename(s) and SHA-256 digest(s);
- repeatable build/package procedure and relevant runtime/tool version;
- attributable canonical full/aggregate verification evidence;
- capability applicability, findings, missing assurance, approved exceptions, and accepted risks;
- SBOM/signing/provenance references when the approved publication channel makes them applicable;
- final `READY`, `READY WITH ACCEPTED RISKS`, `NOT READY`, or `INCOMPLETE ASSURANCE` decision.

For manual behavioural evidence, retain raw responses and any authenticated
profile outside the repository. A release/validation record may bind a
controlled external archive only by its SHA-256, source identity, score outcome,
and privacy-safe environment categories. Do not commit candidate responses,
local paths, account data, credentials, or chat transcripts.

The release workflow and verification standard remain normative. This directory is only the repository-specific durable evidence convention.

Failed verification evidence remains in the canonical verification/report structure and does not require a parallel record. Explicit approved policy exceptions are governed by `assurance/exception-policy.md`.

Versioned framework validation narratives are retained under `validation/`. These records are historical release evidence; moving or retaining a record does not change its original outcome or make an unfrozen/rejected candidate a release. New `VALIDATION-v*.md` records belong there rather than at repository root.
