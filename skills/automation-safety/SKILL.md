# Automation Safety

Establish target scope, including whether nested content may be processed recursively; allowed and forbidden move/delete actions; collision/overwrite semantics; external effects; reversibility/rollback; and privilege.

For filesystem cleanup or organization, do not infer recursive traversal, deletion, or overwrite permission from broad language such as “clean it up.” Treat move authority, delete authority, recursion, collision behavior, and rollback/recovery as distinct semantics that must be resolved before mutation.

Prefer a read-only inventory and dry-run first, no-overwrite by default, bounded scope, operation journals, idempotency, explicit batch limits, quarantine/recovery where consequence warrants, and explicit approval before irreversible action.

Bulk operations may be C3 even if reversible. Explicit approval is required before destructive/high-consequence execution.
