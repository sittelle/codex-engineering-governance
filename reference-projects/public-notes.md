# Reference Project — Public Multi-user Notes

Recommended: at least M2 and likely M3 when operated; SA2 minimum due Internet-facing multi-user protected data.

Simple architecture:
Browser -> web/API application -> PostgreSQL.
React/TypeScript + FastAPI/Python is one credible default, not a global mandate.

Do not silently invent authentication product semantics. Resource-level authorization is mandatory.

Release evidence: tests, negative authz tests, secrets, SAST, SCA, threat model, manual security review, SBOM, and DAST where practical.
