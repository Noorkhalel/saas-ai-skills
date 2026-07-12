# Performance, operations, and migrations

## Performance and scalability

Measure with production-like volume, skew, concurrency, cache state, and parameter distributions. Capture query count, p50/p95/p99, rows/buffers, locks/waits, CPU/IO, pool waits, write latency, replication lag, and storage growth. Use `pg_stat_statements` and traces to prioritize total cost and tail latency; use `EXPLAIN (ANALYZE, BUFFERS)` safely for representative queries. A sequential scan can be correct; an index is a hypothesis until a plan/workload proves it.

Use a connection pool matched to database capacity; pool exhaustion often follows slow/blocked transactions. Use read replicas only with explicit read-after-write/staleness behavior. Partition for demonstrated pruning/retention/maintenance or scale need, not as a default. Sharding requires durable routing, balancing/rebalancing, tenant/key locality, global-ID, cross-shard transaction/reporting, backup/restore, and incident plans.

## Zero-downtime change pattern

1. **Assess:** inventory callers, long transactions, table/index size, locks, replication, disk/headroom, version capabilities, and SLO/error budget.
2. **Expand:** add compatible nullable columns/tables/indexes/dual-read-compatible code. Use online/concurrent operations where supported and understand their restrictions.
3. **Backfill:** throttle, batch by stable key, checkpoint/resume idempotently, monitor locks/WAL/replica lag/errors, and avoid one giant transaction.
4. **Verify:** reconcile counts/checksums/invariants, compare old/new reads, and run a canary.
5. **Switch:** deploy readers/writers behind a flag, monitor correctness/latency/errors, and define abort thresholds.
6. **Contract:** only after all old code/backfills/retention windows are gone, remove legacy schema in a separate change.

Rollback may be impossible after destructive or externally consumed writes. Name a forward-repair plan, backups, restore test, and data reconciliation rather than pretending rollback is universal.

## Operational readiness

Define RPO/RTO, tested backups and point-in-time recovery, restore ownership/runbook, replication/failover procedure, capacity/disk growth thresholds, connection and query limits, encryption/TLS/key ownership, least-privilege operational access, schema migration control, audit logging, and maintenance. Monitor availability, latency, error/abort/deadlock rate, connections/pool wait, long transactions, locks, CPU/memory/IO, cache hit, autovacuum/bloat, table/index size, replication lag, backup age/success, and restore drills.

For managed cloud databases, also validate region/residency, private networking, IAM/service identities, maintenance/failover windows, provider quotas, storage autoscaling/cost, replica topology, connection-proxy behavior, encryption-key ownership, audit-log export, and a provider-independent restore exercise. Managed service does not eliminate schema, query, migration, or recovery responsibility.
