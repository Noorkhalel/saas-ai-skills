# Cloud, containers, Kubernetes, queues, and APIs

## Containers and Kubernetes

Compare requested/limited CPU and memory with observed usage, throttling, OOM/restarts, GC, startup/readiness, pod scheduling, HPA decisions/lag, node pressure, and load-balancer distribution. More replicas help only if work is stateless or safely partitioned and a shared dependency has capacity. Check noisy neighbors, image/startup cost, connection reuse, log volume, and cross-zone/region traffic. Avoid raising limits or HPA maxima without cost and downstream-capacity analysis.

## Queues and background work

Measure arrival rate, completion rate, queue depth/oldest age, active workers, retry rate, failure/poison rate, payload size, and downstream saturation. If arrival rate exceeds sustained service rate, tuning concurrency is not a solution; add capacity, reduce work, shed/load-shape traffic, or change the architecture. Use bounded queues, backpressure, deadlines, idempotency keys, retry budgets with jitter, dead-letter handling, and ordering/partition semantics where required. Batch only when it improves per-item cost within latency/fairness and memory limits.

## APIs and dependencies

Trace endpoint time into serialization, application, pool/queue wait, database, and each dependency. Bound inputs, pagination, filters, sort fields, result size, fan-out, and GraphQL depth/complexity. Use compression only when transfer savings exceed CPU/latency cost; validate client support and streaming behavior. Use deadlines propagated across calls, sensible per-attempt timeouts, capped retries with jitter, circuit breaking/load shedding, and idempotency for retried writes. Batching can remove round trips but can worsen tail latency or authorization complexity.

Use CDN/HTTP/browser caching only with explicit `Cache-Control`, validators, vary dimensions, invalidation/versioning, and personalized-content protection. Monitor origin offload, hit ratio, stale responses, and invalidation health.
