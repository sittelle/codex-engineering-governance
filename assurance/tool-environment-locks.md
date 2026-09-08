# Assurance Tool Environment Locks

## Purpose

Assurance tools are part of the verification environment. Their installation must be reproducible without pretending one operating-system-specific dependency resolution is universal.

## Core rule

**A dependency lock is valid only for the execution environments it was intentionally resolved and verified to support.**

A lock generated on Windows that contains a Windows-only dependency such as `pywin32` must not be reused unmodified as an Ubuntu lock. Likewise, a Linux-only wheel/binary set is not evidence for Windows support.

## Acceptable strategies

Use one of these approaches:

1. **Environment-specific lock sets** — preferred when tool dependency graphs differ by OS, architecture, or interpreter version. Example naming may include `windows-amd64-py3.14`, `linux-amd64-py3.13`, etc.
2. **A demonstrably universal lock** — acceptable only when the resolver records correct environment markers and artifact hashes for every approved target and the lock is tested on those targets.
3. **Tool-native multi-platform lock metadata** — acceptable when the package manager can reproducibly select the exact target graph without weakening pinning or integrity verification.

## Required properties

For each approved assurance execution environment, record or derive:
- operating system;
- architecture when relevant;
- interpreter/runtime version when dependency resolution depends on it;
- exact direct/transitive tool versions;
- integrity hashes or equivalent immutable artifact identity where supported;
- the lock/manifest selected for that environment.

CI/bootstrap logic must select a matching lock deliberately. It must not silently fall back to another platform's lock.

## Failure semantics

If no compatible assurance-tool lock exists, or installation fails because the selected lock cannot resolve for the current environment:
- do not remove hashes;
- do not switch to floating/unpinned versions merely to make CI green;
- do not mark the assurance capability `NOT_APPLICABLE`;
- record the verification environment/bootstrap as `DID_NOT_EXECUTE`;
- overall assurance remains `INCOMPLETE_ASSURANCE`.

Fix the lock generation/selection and rerun on the same attributable source state.

## Scope changes

Adding a new supported verification environment (for example Linux CI in addition to Windows local) can require a new lock set. This is assurance-tooling integration, not product behavior.

Changing tool versions, integrity sources, or dependency graphs remains a dependency/assurance-tooling change and must be reviewed proportionately.

## Examples

Bad:

```text
requirements-assurance.txt generated on Windows
contains pywin32==...
Ubuntu install fails
→ remove --require-hashes and pip install semgrep
```

Good:

```text
Windows assurance lock  → resolved/tested for Windows
Ubuntu assurance lock   → resolved/tested for Ubuntu CI
bootstrap selects exact matching lock
missing matching lock   → DID_NOT_EXECUTE / INCOMPLETE_ASSURANCE
```
