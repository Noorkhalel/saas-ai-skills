# Domain selection and AI performance

## Backend stacks

- **Node.js / Express / NestJS:** profile CPU and allocations; check event-loop delay, blocking synchronous work, promise fan-out, libuv thread-pool use, keep-alive, pool waits, and JSON serialization. Clinic.js and flamegraphs are evidence sources, not conclusions.
- **FastAPI / Django:** distinguish async handlers that call blocking libraries from true concurrency; measure worker model, GIL/CPU behavior, ORM query count, connection pool, serializer work, and background-task durability.
- **Spring Boot / ASP.NET:** inspect thread pools, blocking I/O, allocation/GC, connection pools, serialization, ORM/JPA/EF query patterns, and executor saturation before changing pool settings.

## GraphQL

Attribute database calls to resolver paths. Measure query depth/complexity, field cardinality, repeated resolver calls, response size, cache scope, persisted queries, and N+1. Apply DataLoader/batching with request-safe authorization/tenant keys; bound query cost and pagination. Validate caching does not mix users/roles or hide freshness requirements.

## AI/RAG/MCP

Decompose a request into ingestion, embedding, retrieval/filtering/reranking, context construction, model queue/TTFT, generation, tool/MCP calls, parsing/validation, retries, and response streaming. Track per-stage p50/p95, tokens in/out, model/provider, tool count, retrieval corpus/filter cardinality, answer quality/task success, cost, and failure/retry rate.

Optimize in order of proven contribution: eliminate redundant tool calls and duplicate retrieval; narrow retrieval with validated metadata filters; cache versioned safe results/embeddings; parallelize independent bounded calls; stream user-visible generation; use smaller/faster models only with task-quality, safety, and structured-output validation. Preserve citations, tenant filters, permissions, prompt-injection defenses, PII policy, and auditability. Do not assume fewer chunks/tokens improves total experience; measure recall/answer quality and latency together.

## Scenario coverage matrix

| Scenario | First evidence | Common root causes to test | Required guard |
|---|---|---|---|
| Next.js dashboard | CWV + browser/React trace | hydration, rerenders, waterfall, bundle/images | accessibility/visual correctness |
| Node REST API | trace + CPU/profile + DB spans | N+1, event loop, pool/fan-out | API semantics/timeouts |
| FastAPI DB | SQL + plan + pool/worker metrics | blocking calls, ORM, plan/index | transaction behavior |
| Supabase multi-tenant | plan as caller role + RLS tests | policy filters, indexes, N+1 | tenant isolation |
| PostgreSQL | `EXPLAIN ANALYZE` + query stats | missing index, estimates, locks | write/migration safety |
| Docker/Kubernetes | throttling/OOM/HPA/dependency signals | limits, autoscale lag, saturation | availability/cost |
| Redis e-commerce | cache telemetry + origin load | misses/stampede/key design | inventory/price freshness |
| GraphQL | resolver trace + query count | resolver N+1, depth/payload | authorization |
| Millions of jobs | queue age/rates/retries | service-rate deficit, batch/retry | idempotency/order/DLQ |
| RAG/MCP | stage trace + quality metrics | context/tool fan-out, vector/model queue | quality/security/tenant data |
