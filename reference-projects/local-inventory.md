# Reference Project — Local Desktop Inventory

Recommended: M1 / SA1.

Proportionate direction:
- local desktop UI;
- application/domain logic;
- SQLite;
- no web server, Docker runtime, accounts, cloud sync, or microservices without requirement.

Small project may use README + AGENTS + project-governance.yml + combined docs/design.md instead of separate requirements/architecture/security documents.

Quick verify: format/lint/type/unit/selected SQLite integration.
Full: quick + full DB tests + secrets + SAST + SCA + package/build smoke test.
