# PostgreSQL and Supabase guidance

## PostgreSQL schema design

Use `timestamptz` for instants, `date` for calendar dates, and explicit time zones/business calendars when required. Use `numeric` only where exact decimal arithmetic is required; do not use floating point for money. Prefer `bigint`/UUID/ULID only after deciding generation, locality, external exposure, and index/storage behavior. Bind relationships with foreign keys and enforce natural uniqueness with unique constraints. Use check constraints for row-local rules and exclusion constraints for range/non-overlap rules when appropriate.

Use `jsonb` for bounded extensible attributes where relational queries/constraints are not primary. Document its schema/version/validation and index only proven operators. Use full-text search/vector/search projections as derived stores or carefully owned columns, with rebuild and deletion paths.

## Indexing

Derive each index from an actual query: equality predicates first, then range/order requirements; test with representative values and `EXPLAIN (ANALYZE, BUFFERS)`. Composite ordering matters. Unique indexes enforce invariants. Partial indexes suit stable selective predicates. Expression indexes match deterministic query expressions. `INCLUDE` can enable index-only reads at write/storage cost. GIN supports JSONB/arrays/full-text; GiST supports ranges/geospatial; hash is rarely the default. Every index adds write amplification, vacuum/storage, build, and planning cost.

Avoid unbounded offsets for large mutable lists; keyset pagination needs an indexed stable, preferably unique order and correctly encoded cursor. Inspect N+1 at the application/ORM boundary, then query count/request and plans. Keep transactions short; inspect locks, waits, long sessions, pool saturation, autovacuum, bloat, temp spills, statistics, and replica lag before changing concurrency or pooling.

## Supabase multi-tenancy and RLS

Choose tenant ownership explicitly, commonly `organization_id`. Put it on tenant-scoped records, constrain child ownership so cross-organization references are impossible (often composite foreign keys/unique parent keys), and index it with the tenant's query predicates/order. Enable RLS on exposed tables. Write policies that use authenticated claims/membership checks, test as each caller role, and explain any security-definer helper's ownership/search path/privilege boundary. Never expose a service-role key to clients or use it to bypass user authorization.

Treat RLS predicates as query predicates: inspect plans under representative authenticated roles/JWT claims, keep predicate columns/indexes usable, and test policy correctness before/after every schema/query/cache change. Apply tenant scope to storage objects, Realtime, Edge Functions, background jobs, exports, logs, caches, and analytics as well as tables.
