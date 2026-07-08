# Database Review Checklist (Phase 5)

Review the code's *conversation with the database* — queries, transactions, schema, migrations — plus the multi-tenant section for any SaaS code. Verify query-shape claims against the actual ORM semantics (lazy vs eager) before reporting; N+1 accusations that turn out to be eager-loaded are classic false positives.

## Query efficiency

- **N+1 queries:** a query inside a loop over a previous query's results — explicit (`for order: db.query(...)`) or implicit via ORM lazy loading (`order.customer.name` inside the loop; each access = a query). Verify: what does the ORM actually emit here? Fix: eager load (`include`/`select_related`/`prefetch_related`/JOIN) or batch (`WHERE id IN (...)`). Severity scales with the loop's n and the endpoint's traffic — a hot list endpoint = HIGH.
- **Missing indexes** for the query shapes in this code: filters/sorts/joins on unindexed columns; composite order wrong (range column before equality); `LIKE '%x'` and function-wrapped columns (`lower(email)` without expression index) that can't use indexes. You usually can't see the schema — say what index the query *needs* and ask, rather than asserting it's missing.
- **Overfetching:** `SELECT *` / whole entities for one field; missing pagination on unbounded lists (`findAll()` on a user-growable table is a latent outage); loading rows to count them (`len(query.all())` vs `COUNT`); N sequential queries mergeable into one.
- **Chatty patterns:** query-per-item writes where bulk insert/update exists; per-request reconnection instead of pooling; transactions held across external calls (also a correctness finding — `bugs.md`).

## Transactions & consistency

- Multi-write invariants without a transaction (order + items; balance + ledger) — if the process dies between writes, is the data valid?
- Isolation assumptions: check-then-act on the DB (unique-check then insert; stock-check then decrement) still races *inside* default isolation levels — the fix is constraints + conflict handling or atomic conditional writes, not "wrap it in a transaction" alone.
- Application-enforced integrity that the schema should own: uniqueness by pre-query, FKs "handled by the app", required fields nullable in the schema. The second writer (job, script, support tool) won't run the app checks.
- Soft-delete leaks: `deleted_at` model where half the queries forget the filter — grep for the tables and compare.

## Schema red flags (when schema/models are in scope)

- Missing FK constraints/NOT NULLs where the model implies them; floats for money; strings for structured data the code then parses everywhere; EAV-style "flexible" tables; JSON columns queried by inner fields constantly (should be columns); no `created_at`/`updated_at` on business tables; enum-by-convention with no constraint.

## Migration risks (when migrations are in the diff)

- **Locking:** adding NOT NULL with default / index without `CONCURRENTLY` / type changes = table rewrite or long lock on busy tables.
- **Deploy-order hazards:** code reading a column the migration adds (or dropping one old code still reads) — is the migration backward-compatible one release in each direction? Renames must be expand→migrate→contract, never in-place.
- **Data migrations inside schema migrations** on large tables (timeout, lock); irreversible destructive changes without an explicit call-out.

## Multi-tenant / SaaS review

For any code where rows belong to tenants/organizations — this section outranks everything else in the file, because the failure is a data breach:

- **Every tenant-owned query filters by tenant.** Read each query in the diff/file: is there a tenant/org predicate? A single missing filter on a list/get/update/delete = CRITICAL. Grep the model/table names across the codebase for unscoped access if you have repo access.
- **Tenant id comes from the session/token, never the request.** `where org_id = req.body.orgId` is cross-tenant access by construction — the classic. Also verify membership: user's token must be validated as belonging to that org (not just "a valid user").
- **Enforcement mechanism over discipline:** RLS policies (check them: is the policy on *all* operations — SELECT/INSERT/UPDATE/DELETE? does the app role bypass RLS? is `app.tenant_id` set per request/connection — pooling can leak session state!), or a scoped-repository chokepoint. Flag per-endpoint hand-filtering as an architecture finding even when each instance is currently correct.
- **Leak surfaces beyond queries:** cache keys without tenant id; search indexes queried without tenant filter; object-storage paths/signed URLs not tenant-scoped; background jobs that lose tenant context (or run one query for *all* tenants and fan out — check the fan-out respects boundaries); aggregate/analytics endpoints crossing tenants; unique constraints that are global when they should be per-tenant (email unique per org?) — and per-tenant when the collision leaks existence.
- **Supabase-specific:** client-side queries live under RLS as the *only* wall — review the policies, not the client code; service-role keys must never reach the client; storage buckets need their own policies (a public bucket next to careful RLS is a common hole).

## Reporting

Per finding: the query (file:line), what the DB actually does (queries emitted, locks taken, rows scanned), the realistic cost or breach scenario, and the fix (specific: the eager-load call, the index columns, the constraint DDL, the RLS policy shape). If you can't see schema/indexes/policies, list them under questions — "show me the RLS policy on `documents`" is a better review artifact than a guessed finding.
