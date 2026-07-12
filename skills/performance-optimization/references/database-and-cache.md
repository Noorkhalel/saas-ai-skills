# Database, ORM, and cache playbook

## Database investigation sequence

1. Find the expensive query by total time, p95/p99, calls, rows, and request correlation, not query text alone.
2. Capture actual SQL, representative parameters, schema/indexes, table statistics/cardinality, `EXPLAIN ANALYZE` (buffers where available), and waits/locks.
3. Check query count per request and ORM call sites for N+1, implicit lazy loads, duplicate queries, unbounded relations, per-row writes, and transaction scope.
4. Compare estimated vs actual rows; identify scans, joins, sorts, spills, materialization, lock waits, and connection-pool waits.
5. Test the smallest semantic-preserving fix: shape query/projection, batch/preload, bound pagination, then an evidence-supported index. Re-measure reads and writes.

## Correctness traps

- Offset pagination may become expensive and can duplicate/skip rows under writes; keyset pagination needs a stable, indexed total order and correct cursor semantics.
- Composite-index order follows predicates, equality/range behavior, and sort order; an index that speeds one read can slow writes and consume storage.
- Avoid `SELECT *`; reducing fields must preserve API/client needs and authorization behavior.
- Do not widen transactions, lower isolation, bypass RLS, or hide lock contention merely to lower latency. State the consistency consequence explicitly.
- Pool exhaustion is often a symptom of slow/blocked queries. Bound pool size to database capacity; ensure connections are released and timeout/cancellation paths work.

## Caching design checklist

State the cached value and key dimensions (resource, tenant, user/role, locale, feature version), ownership, TTL/staleness contract, invalidation event, warmup, eviction/capacity, error behavior, instrumentation, and fallback. Prevent stampedes with request coalescing, locks, early refresh, bounded stale-while-revalidate, or TTL jitter. Cache negative results only with a safe short TTL. Do not cache personalized, permission-sensitive, or rapidly changing data without partitioning and invalidation proof.

Metrics: hit/miss/eviction ratios, lookup and origin latency, stale serves, key cardinality/memory, stampede rate, invalidation lag/failure, and origin load before/after.

## PostgreSQL / Supabase specifics

For PostgreSQL, examine `pg_stat_statements`, `pg_stat_activity`, `pg_locks`, autovacuum/bloat, temp-file spills, connection count, and replica lag as relevant. Capture `EXPLAIN (ANALYZE, BUFFERS)` on safe representative queries. In Supabase, treat RLS policy predicates and JWT-derived filters as part of the query: test plans as the calling role, index policy/filter columns where evidence supports it, avoid service-role bypasses, and validate tenant isolation after every query/cache change.
