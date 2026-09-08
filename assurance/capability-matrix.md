# Assurance Capability Matrix

This matrix is a default. Profiles, threat model, workflow, change class, and release policy may strengthen it.

`R` = normally required when applicable.
`C` = conditional/risk-driven.
`N/A` = may legitimately be not applicable.

| Capability | M0/SA0 | M1/SA1 | M2/SA1 | SA2 | SA3 |
|---|---|---|---|---|---|
| lint/format | C | R | R | R | R |
| type/compile | C | R | R | R | R |
| tests | C | R | R | R | R |
| build/package sanity | C | R | R | R | R |
| secret scan | R | R | R | R | R |
| SAST | C | R | R | R | R |
| SCA/dependency audit | C | R when dependencies exist | R | R | R |
| security tests | C | C | C | R | R |
| SBOM | N/A/C | C | R recommended | R | R |
| container scan | N/A/C | N/A/C | N/A/C | R when container artifact exists | R when applicable |
| IaC scan | N/A/C | N/A/C | N/A/C | R when IaC exists | R when applicable |
| DAST | N/A/C | N/A/C | C for exposed web | R for exposed web unless justified | R when applicable |
| fuzzing | N/A/C | N/A/C | C | C | R when warranted |
| recovery verification | N/A/C | C for persisted data | C | R for material operated data | R |
| provenance/signing | N/A/C | C | C/R for distribution | R where ecosystem supports | R |

## Notes

- `when applicable` matters. A local CLI with no web listener does not need DAST.
- SCA requires dependencies to analyze; a standard-library-only program may record the capability as NOT_APPLICABLE with reason.
- A container/IaC capability becomes required because that artifact/boundary exists, not because the project uses GitHub.
- SA2/SA3 required controls that cannot execute produce incomplete assurance, not a lower assurance level.
- The matrix defines assurance capability, not a mandatory vendor/tool.


## Machine-readable companion

`capability-baseline.json` carries the enforceable baseline identifiers. The Markdown matrix remains the human-readable policy source; changes to either must remain synchronized.
