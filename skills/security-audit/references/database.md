# Database Security (Phase 7)

The database holds the crown jewels, so a bug here is a bulk-data bug. Audit how queries are built, who the DB user is, whether tenants are isolated, and whether state changes are atomic.

## Injection

- **SQL injection:** any untrusted value interpolated into a query string. Template literals `${}`, `+`, `%s`/`.format()`, f-strings into `raw`/`execute`. ORM escape hatches are the usual site: `whereRaw`, `$queryRawUnsafe`, `.raw()`, `.extra()`, `sequelize.query`, `knex.raw`, native driver `.query(str)`. **Fix:** parameterized/prepared statements; bound parameters, never string-built.
- **Dynamic identifiers** (ORDER BY column, table/schema name, direction) can't be bound — they need an allowlist mapping user input to known-safe identifiers.
- **NoSQL injection:** user object reaching a Mongo/query filter enabling operator injection (`{"$ne":null}`, `{"$gt":""}`, `$where` with a JS string). **Fix:** validate/cast types; reject objects where scalars are expected; never pass user JSON straight into a filter.

## Least privilege

- The application's DB account should hold only the privileges it needs — not `SUPERUSER`/`db_owner`/`GRANT ALL`. An injectable query run as a superuser is catastrophic (`COPY`/`xp_cmdshell`/file read); the same injection as a least-privileged user is contained.
- Separate accounts for migrations (DDL) vs runtime (DML). Runtime shouldn't be able to `DROP` or alter schema.
- Check `GRANT`s and default role membership; flag `PUBLIC` grants on sensitive objects.

## Tenant isolation & RLS

(Cross-references `auth.md` — the query-level view here.)

- **Every tenant-scoped query filters by the session's tenant.** Audit the actual queries. Per-query discipline is fragile — prefer a shared scoped repository or database **Row-Level Security**.
- **RLS correctness** (Postgres/Supabase):
  - `ENABLE ROW LEVEL SECURITY` on every tenant table; `FORCE ROW LEVEL SECURITY` so even the table owner is subject to it.
  - A policy for each operation; `USING` (read/filter) *and* `WITH CHECK` (write) both present so an INSERT/UPDATE can't place a row in another tenant.
  - The tenant context (`SET app.current_tenant = ...` / Supabase `auth.uid()`/`auth.jwt()`) is set per request and **reset/cleared on pooled connections** — a `SET LOCAL` inside a transaction is safe; a bare `SET` on a pooled connection bleeds into the next request. This is a classic, easy-to-miss leak.
  - No `SECURITY DEFINER` function or service-role/`postgres` key reachable with user input that bypasses RLS.
- **Leak channels off the main path:** caches keyed without tenant, background jobs losing tenant context, materialized views/reporting queries, full-text/search indexes, and file paths. → `auth.md`

## Transactions & integrity

- Multi-step state changes — especially money (charge + record, cancel + refund, transfer debit + credit) and any invariant across rows — must be in a single transaction with appropriate isolation. A partial failure that leaves a charge without an order, or a refund without a cancellation, is a data-integrity/financial bug.
- **Race conditions:** check-then-act without a lock or atomic operation — balance checks, inventory decrement, unique-slug claim, "first to redeem" — lets concurrent requests both pass (`SELECT ... then UPDATE` instead of `UPDATE ... WHERE balance >= x` / `SELECT FOR UPDATE` / a DB constraint). Double-spend and oversell live here.
- Idempotency on retried operations (payments, webhooks) so a retry doesn't double-apply.

## Data-at-rest & secrets

- Sensitive columns (PII, tokens, secrets) encrypted at rest where the threat model calls for it; disk/volume encryption enabled on the datastore.
- **Connection strings with embedded passwords** in code/config/repo → `secure-coding.md` (secrets). Prefer a secrets manager / IAM auth.
- Backups: are they encrypted, access-controlled, and free of the same secrets? A wide-open backup bucket is a full-DB leak.
- Logging: query logs / slow-query logs capturing sensitive parameter values.

## ORM-specific pitfalls

- Lazy loading / N+1 is a performance issue, but *unbounded* relations returned to a client is also a data-exposure issue — check what's serialized (→ `api.md`).
- Default scopes that a `.unscoped()`/`.withoutGlobalScope()` call silently drops (including a tenant scope).
- Migrations that widen permissions, drop constraints, or disable RLS — audit these in PR mode especially.

## Reporting

Per finding: the query or schema object, the untrusted source if injection, the privilege/tenant/transaction gap, and the fix (parameterize, scope, add transaction/lock, tighten grants, fix RLS policy). Rule-outs: "all queries use bound parameters via the ORM; no raw string queries found" is worth stating.
