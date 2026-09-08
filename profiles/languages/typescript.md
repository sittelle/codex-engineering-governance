# TypeScript Profile

Use a supported Node/runtime when applicable and current stable TypeScript compatible with the ecosystem. Prefer strict typing. `any` and assertions are not runtime validation.

Validate external API/JSON/env/storage/message/file data at runtime. Commit the lockfile for applications and use one package manager.

Browser code is untrusted and contains no secrets. Review dynamic HTML/code execution, command/filesystem operations, raw SQL, custom auth/token code, and disabled TLS verification.
