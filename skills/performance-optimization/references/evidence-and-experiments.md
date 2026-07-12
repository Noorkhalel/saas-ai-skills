# Evidence, experiments, and rollout

## Evidence ladder

**Verified** means directly observed in a trace, profile, plan, metric, reproducible test, or source path. **Likely** is a causal inference consistent with the evidence; include confidence and the missing link. **Hypothesis** is plausible but untested; attach a discriminating test. **Unknown** names an observability gap. Never convert the latter three into facts in the executive summary.

Prefer end-to-end traces with correlated logs/metrics. A profile identifies where CPU or allocations occur, not whether it is the user bottleneck. A database plan predicts cost under a specific parameter/data distribution, not all production queries. Check cardinality estimates against actual rows and inspect representative parameters.

## Baseline and experiment template

Record:

| Item | Required detail |
|---|---|
| Objective | SLO/budget, target percentile, error and correctness constraints |
| Workload | request/job mix, payloads, concurrency/ramp, duration, cache state, data size/skew, tenant mix |
| Environment | version/commit, configuration, region, instance/pod limits, dependency versions |
| Metrics | p50/p95/p99, throughput, error/timeout rate, CPU/memory/GC, DB/cache/queue/dependency signals, cost |
| Comparison | same workload and environment; control/pre-change result; sample count/confidence limitations |

Warm up JITs, pools, and caches intentionally. Run cold-cache separately. Avoid changing load, code, instance class, indexes, and query parameters in one test. Under load, record saturation and queueing: an apparent faster median can coexist with worse p99 or errors.

## Causal test design

Form a testable claim: "At 200 concurrent requests, query Q's sequential scan consumes 55% of trace time; an index on the proven selective predicate should lower DB p95 without degrading writes beyond X." Then define the observation that would refute it. Use feature flags, canaries, A/B or shadow traffic where appropriate; isolate a single material variable.

## Rollout guardrails

Before rollout define success, abort, and rollback: e.g., p99 improves at least 15% with no more than 0.1 percentage-point error increase, no authorization failures, and write p95 within budget. For schema/index changes, choose online/concurrent operations supported by the DB, verify lock behavior, disk/headroom, replica lag, migration order, and a rollback path. Monitor for at least one representative peak or soak period when risk warrants it.

## Useful measurement commands

Use commands appropriate to the deployment and never run production-impacting load tests without authorization.

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT ...;
-- Compare estimated versus actual rows, scan type, loops, sort/hash spill, buffers, and time.
```

```text
Trace: request -> span durations -> downstream calls -> queue/pool waits
Profile: CPU + allocation/heap + GC under representative load
Frontend: Web Vitals + Chrome Performance trace + bundle analyzer
```

## Statistical caution

Tail percentiles require enough samples; report duration and count. Treat small improvements within run-to-run noise as inconclusive. Compare the full distribution and error/saturation/cost. If production traffic is heterogeneous, segment by endpoint, tenant tier, region, payload size, cache state, and status code before drawing conclusions.
