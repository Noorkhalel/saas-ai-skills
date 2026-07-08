# Bug report: orders list endpoint is extremely slow

**Symptom:** `GET /api/orders?since=…` (the "recent orders for my organization" screen) takes 3–6 seconds
and has gotten worse as the `orders` table grew. It's now ~48 million rows across all organizations.
Each organization has at most a few thousand orders. The endpoint was fast a year ago.

**The query the ORM emits:**

```sql
SELECT *
FROM orders
WHERE org_id = $1
  AND created_at > $2
ORDER BY created_at DESC
LIMIT 50;
```

**`EXPLAIN (ANALYZE, BUFFERS)` output:**

```
Limit  (cost=0.00..1893452.10 rows=50 width=412) (actual time=4211.882..4211.901 rows=50 loops=1)
  ->  Sort  (cost=1893452.10..1894920.55 rows=587380 width=412) (actual time=4211.880..4211.888 rows=50 loops=1)
        Sort Key: created_at DESC
        Sort Method: top-N heapsort  Memory: 71kB
        ->  Seq Scan on orders  (cost=0.00..1873874.00 rows=587380 width=412)
              (actual time=0.020..4102.551 rows=612394 loops=1)
              Filter: ((org_id = '8a3f…'::uuid) AND (created_at > '2025-06-01'::timestamptz))
              Rows Removed by Filter: 47987606
        Buffers: shared hit=1204 read=1387219
Planning Time: 0.211 ms
Execution Time: 4212.004 ms
```

**Existing indexes on `orders`** (from `\d orders`):

```
Indexes:
    "orders_pkey" PRIMARY KEY, btree (id)
    "orders_created_at_idx" btree (created_at)
    "orders_status_idx" btree (status)
```

**Note:** `org_id uuid NOT NULL`, `created_at timestamptz NOT NULL`. The app is multi-tenant;
every orders query is scoped by `org_id`.
