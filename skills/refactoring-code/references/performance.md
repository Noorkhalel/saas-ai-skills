# Performance Review During Refactoring

Run this review on every engagement (workflow step 10). Two jobs, in priority order: **don't regress performance with your refactoring**, and **report optimization opportunities you noticed** — as recommendations, because optimizations change code for a different reason than refactoring does and belong in their own step.

## Ground rules

- **Clarity first, then measure, then optimize.** Refactor for structure; profile before optimizing; optimize the measured hot path only. Speculative micro-optimization degrades the structure you just fixed, usually for unmeasurable gains.
- **Optimization is the third hat.** Like behavior changes, performance work is separate from refactoring. Report opportunities; apply them only when asked, and then in their own commits with before/after measurements.
- **The exceptions worth acting on without a profiler** are the algorithmic and I/O-multiplying mistakes below — an N+1 query or an O(n²) loop over unbounded input is a defect class, not a micro-optimization. Still report before fixing (behavior around timing/ordering may be observable).

## Self-check: did the refactoring regress anything?

Structural transformations have known performance failure modes. Check your own diff for:

- **Lost memoization/caching** — Replace Temp with Query re-evaluates per call what was computed once; extracting a cached value into a helper that recomputes. If the query is expensive or called in a loop, memoize or pass the value.
- **New allocations in hot loops** — Introduce Value Object / Replace Primitive with Object inside per-item or per-frame code paths; extracted closures allocated per iteration. Fine almost everywhere; check the hot paths.
- **N+1 introduced by extraction** — a batched query refactored into a clean per-item helper (`getOrderWithDetails(id)` called in a loop) is the classic way refactoring creates N+1. Keep batch boundaries intact when moving data access.
- **Sync/async and laziness changes** — converting eager to lazy (or the reverse), sync to async, changes *when* work happens; that is observable behavior (ordering, error timing) and can also serialize work that was parallel or vice versa.
- **Indirection on extreme hot paths** — virtual dispatch from Replace Conditional with Polymorphism, wrapper layers from Decorator/Facade. Irrelevant in 99% of code; measurable in inner loops of data/graphics/parsing workloads. Know which kind of code you're in.

If the code in scope is known hot-path and the project has benchmarks, run them before and after, and include the numbers in the report.

## Inspection checklist

Report findings in these areas for the code in scope:

**Algorithmic complexity**
- Nested loops over the same or related collections — O(n²) hiding as two innocent loops; `list.contains`/`indexOf`/linear scans inside loops (use a set/map: O(n²)→O(n)); repeated sorting inside loops; string concatenation in loops in languages where strings are immutable (O(n²) total — use a builder/join).
- State the complexity and the realistic n. O(n²) over "user's open tabs" is fine; over "all orders ever" is an incident waiting for growth.

**Database and remote calls**
- **N+1 queries** — a query per item of a fetched list (ORM lazy loading in loops is the classic source). Fix: eager loading/joins/batch endpoints.
- **Repeated identical queries** — same lookup (config, user, feature flags) fetched multiple times per request; queries inside loops that are loop-invariant. Fix: fetch once, pass down (often falls out naturally from Introduce Dependency Injection or parameter passing).
- **Overfetching** — `SELECT *` / whole-entity loads for one field; missing pagination on unbounded result sets.
- Chatty sequential remote calls that could be batched or parallelized.

**Caching opportunities**
- Expensive pure computations with repeating inputs (memoization candidates); stable-per-request data fetched repeatedly (request-scoped cache); rendered fragments/derived data rebuilt identically. Recommend with an invalidation story — a cache without one is a bug factory, and "add a cache" is a behavior-adjacent change (staleness becomes observable).

**Concurrency and I/O**
- **Blocking I/O** on latency-sensitive paths: synchronous file/network/DB calls on UI threads, event loops, or request handlers of async servers; `sleep` in request paths.
- **Missed parallelism** — independent awaits executed sequentially (`await a(); await b();` where `a` and `b` are independent — gather/`Promise.all` them); sequential processing of independent items where the language offers cheap concurrency. (Parallelizing changes ordering/error behavior — recommend, don't silently apply.)

**Memory**
- Unbounded growth: caches without eviction, listeners/subscriptions registered but never removed, collections that only ever grow, closures capturing large contexts in long-lived callbacks.
- Loading entire files/result sets into memory where streaming/iteration exists; retaining large intermediate collections through long pipelines (n copies of the data for an n-stage pipeline — stream or reuse).

**Rendering / recomputation (UI codebases)**
- Work re-done per render/frame that inputs didn't change: derived data recomputed without memoization, new object/closure identities passed to children forcing re-renders, whole-list re-renders on single-item changes (missing keys/virtualization), layout thrash (interleaved reads/writes of layout properties).

## Reporting format

Per finding, in the Performance Review section:

```markdown
- **<category>** — <file:line>
  <what happens and the cost model: per-request? per-item? O(what)?>
  Recommendation: <specific change; note measurement or approval needed if behavior-adjacent>
```

Also state the self-check verdict explicitly: "Refactoring introduces no new allocations, queries, or blocking calls on hot paths" — or what it does introduce and why that's acceptable.
