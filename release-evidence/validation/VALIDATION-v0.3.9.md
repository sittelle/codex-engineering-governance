# v0.3.9 Source/Package Inventory Validation

v0.3.9 fixes the v0.3.8 manifest validator regression discovered when validation was run from a live Git working tree.

## Regression

v0.3.8 compared `MANIFEST.json` against every file physically present beneath the source root. That incorrectly treated repository metadata such as `.git/**` and developer-local files as distributable package content.

This conflated two different questions:

1. **Source completeness:** does every file declared for distribution by `MANIFEST.json` exist in the source tree?
2. **Artifact integrity:** does the produced distribution artifact contain exactly the files declared by `MANIFEST.json`?

A live working tree may legitimately contain non-distribution files. Those files must not silently become package contents, but their presence must not make source validation fail.

## v0.3.9 invariant

- `MANIFEST.json` is the authoritative distribution allowlist.
- Default source validation requires every manifest-listed file to exist, but does not classify unrelated working-tree files as packaged content.
- Exact inventory equality is performed against a concrete artifact with `scripts/validate-governance.py --artifact <zip-or-directory>`.
- Artifact validation rejects both omitted manifest files and undeclared packaged files.
- `.git/**` and arbitrary developer-local files are therefore neither implicitly packaged nor mistaken for package members.

## Regression evidence

Validation is exercised in both modes:

- a simulated live source tree containing `.git/` metadata and an unlisted local helper file must pass source validation;
- the produced v0.3.9 ZIP must pass exact artifact inventory validation;
- an artifact containing one undeclared file must fail exact artifact inventory validation.

Status remains `STABLE_CANDIDATE`.
