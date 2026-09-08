# PostgreSQL Profile

Choose because client/server concurrency/centralization/operational requirements justify it.

Use least-privilege runtime accounts, parameterized queries, deliberate transactions/isolation, constraints, versioned migrations, bounded pooling/timeouts, secure transport when warranted, controlled schema ownership/search path, and tested backup/recovery for important systems.

Do not run application traffic as superuser or add HA/replication speculatively.
