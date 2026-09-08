# v0.3.10 Manifest Regression Self-Test Fixture Isolation

v0.3.10 fixes a self-test defect discovered when `scripts/test-manifest-inventory.py` was executed from a real Git checkout.

## Regression

The v0.3.9 regression test copied the entire live framework source tree into a temporary fixture and then attempted to create a synthetic `.git/` directory. When the real source tree already contained `.git/`, `shutil.copytree()` copied it too, and fixture setup failed with `FileExistsError` before any manifest behavior was tested.

This was a test-harness isolation defect, not a failure of the v0.3.9 source/package inventory policy or validator. Default source validation passed, and the unchanged assurance integration harness passed.

## v0.3.10 invariant

- manifest inventory regression fixtures must not copy live repository metadata or interpreter caches from the developer source tree;
- the test creates its own minimal synthetic `.git/` source-only extra plus an unlisted developer-local helper;
- source validation must accept those extras;
- exact ZIP validation must still accept an exact MANIFEST artifact and reject an undeclared artifact member.

No assurance outcome policy, workflow, skill, or application-governance semantics changed. Status remains `STABLE_CANDIDATE`.
