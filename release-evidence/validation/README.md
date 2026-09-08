# Framework validation history

This directory contains the versioned framework validation records that were historically stored at repository root.

The move into `release-evidence/validation/` is organizational only. Historical records are retained as release evidence and must not be rewritten to change past outcomes, observations, or release status. In particular, a record for a rejected, superseded, or otherwise unfrozen candidate remains historical evidence of that state; its presence here does not make that candidate a release.

New `VALIDATION-v*.md` records belong in this directory. The governance validator rejects new root-level validation records so repository root remains reserved for current framework entry points and configuration.
Durable behavioral evaluation records are also distribution evidence. The governance validator requires every `tests/governance/evaluations/**/GOV-*.md` source record to appear in `MANIFEST.json`, so package cleanup cannot silently discard campaign history.
