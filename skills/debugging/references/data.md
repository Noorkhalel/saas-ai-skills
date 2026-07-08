# Database, Query, Cache & Queue Debugging (Phase 5/6)

For bugs in the data layer: slow queries, wrong results, deadlocks, cache staleness, queue failures, and multi-tenant leaks. Rule for the whole file: **measure before theorizing** — a query plan or a metric beats any amount of reading the SQL.

## Slow queries

The evidence is `EXPLAIN (ANALYZE, BUFFERS)` (Postgres) / `EXPLAIN ANALYZE` (MySQL) / execution plan — read the *actual* plan, don't eyeball the query:
- **Sequential scan on a big table** where a filter should use an index → missing or unusable index. Unusable because: function-wrapped column (`WHERE lower(email)=` without an expression index), leading wildcard (`LIKE '%x'`), type mismatch forcing a cast, or a composite index whose leading column isn't in the predicate.
- **Bad row estimates** (estimated 10, actual 1,000,000) → stale statistics (`ANALYZE`) or a correlation the planner can't see; drives wrong join strategy.
- **Nested loop over a large set** where hash/merge join is wanted (often downstream of the bad estimate); **sort/hash spilling to disk** (`work_mem` too low or the result set is huge — should it be paginated?).
- Composite index column order: equality columns first, then range/sort. `(tenant_id, created_at)` serves "this tenant's recent rows"; reversed, it doesn't.
- **Verify the fix on the plan**, not by hope: the added index must actually be chosen and the scan must change. State the index as DDL and confirm the plan uses it.

## N+1 queries

One query fetches a list, then one query *per row* for related data — explicit (`for x: db.get(x.id)`) or implicit via ORM lazy loading (`order.customer.name` in a loop, each access a query). Tell: latency scales linearly with result size; the DB log shows the same parameterized query fired N times. Verify what the ORM actually emits (a false N+1 accusation on eager-loaded data is a classic wrong diagnosis). Fix: eager-load/join/batch (`include`/`select_related`/`prefetch_related`/`WHERE id IN (...)`).

## Wrong results / missing data

- **Isolation & visibility:** reading a replica after writing the primary (replication lag → stale read, looks like "didn't save"); reading inside vs outside a transaction; an uncommitted or rolled-back write; `READ COMMITTED` vs `REPEATABLE READ` assumptions (MySQL and Postgres differ by default — check).
- **Soft-delete/filter leaks:** half the queries forget `WHERE deleted_at IS NULL` (or the tenant filter) → deleted/other rows appear. Grep the table's query sites and compare.
- **Silent coercion/truncation:** MySQL non-strict mode truncating overlong strings / coercing bad values; `utf8` (3-byte) mangling emoji vs `utf8mb4`; timezone-naive `timestamp` vs `timestamptz` shifting times.
- **NULL semantics:** `NOT IN (subquery with a NULL)` returns no rows; `= NULL` never true; aggregates skipping NULLs — quietly wrong, never errors.

## Transactions & deadlocks

- **Missing transaction on multi-write invariants** (order + items; debit + credit) → partial writes on crash/error leave inconsistent data. Also check the *scope*: external calls (HTTP/email) inside a transaction hold locks across network latency and can't be rolled back once sent; commit-then-publish without an outbox risks dual-write divergence (`references/concurrency.md`).
- **Deadlocks:** transactions locking rows in different orders; the DB log records the victim and the lock graph — read it, don't guess. Fix: consistent lock ordering, shorter transactions, retry-on-deadlock for the victim.
- **Lock contention / long-held locks:** a slow query or an idle-in-transaction session blocking others → timeouts elsewhere. Check for `idle in transaction` sessions (a transaction opened and never committed).
- **Connection pool exhaustion:** every connection checked out (leaked on error paths, or held during long external calls, or a nested call needing its own connection) → new requests hang. Tell: stalls at concurrency, fine when idle.

## Cache bugs

- **Staleness / invalidation:** the update wrote the DB but didn't invalidate/refresh the cache → users see old data. The hardest cache bug; verify the write path invalidates every key that derives from the changed data.
- **Key collisions / missing dimension:** a cache key omitting a distinguishing dimension — most dangerously **tenant/user id** → one user served another's cached data (a data-leak, escalate as security, `references/security.md`). Also locale, permissions, feature-flag state baked into a shared key.
- **Thundering herd:** a hot key expires and N requests all recompute it at once → DB spike/stall. Fix: request coalescing, stale-while-revalidate, jittered TTLs.
- **Wrong TTL / negative caching:** caching an error/empty result and serving it after the real data exists; TTL far longer than the data's validity.

## Queue / event-processing failures

- Messages lost (ack before processing succeeds — crash loses it; ack *after* is safer), duplicated (redelivery + non-idempotent handler → double effect), or stuck (poison message retrying forever, no/oversized DLQ). Out-of-order delivery breaking order-dependent handlers.
- Consumer lag: producers outpace consumers → growing backlog, rising end-to-end latency; the metric is queue depth over time. Slow handler, too few consumers, or a downstream bottleneck.
- Lost tenant/trace context across the async boundary (must be serialized into the message and re-established on consume).

## Multi-tenant / RLS bugs

- **RLS blocks valid users** (a frequent Supabase/Postgres report): the policy is wrong or the tenant context isn't set. Check — is the policy defined for *this operation* (a SELECT-only policy blocks INSERT/UPDATE/DELETE)? Does `app.current_tenant`/`auth.uid()` actually resolve at query time? On a **pooled connection**, a session-level `SET` leaks or is absent across requests — use transaction-scoped `SET LOCAL`; this is the classic "works alone, fails under pooling." Is the app role subject to RLS (not `BYPASSRLS`)? Read the policy and the session setup together.
- **RLS leaks data** (the inverse, worse): a query missing its tenant predicate because enforcement is per-endpoint discipline rather than RLS/scoped-repo; a policy using a client-supplied tenant id instead of the verified session identity.
- **Supabase specifics:** with clients querying directly, RLS *is* the security boundary — debug the policies as the API. Service-role key bypasses RLS (must be server-only); `SECURITY DEFINER` functions bypass it too (accidental holes); storage buckets have their own policies separate from table RLS.

## Reporting

Cite the plan/metric/log as evidence (the seq scan, the N repeated queries, the deadlock graph, the missing invalidation), state confidence, and give the fix as concrete DDL/query/config — then confirm it against the plan or a metric, not by assertion. "Add an index" is a hypothesis; "the plan now uses `idx_orders_tenant_created` and drops from 4s to 20ms" is a fix.
