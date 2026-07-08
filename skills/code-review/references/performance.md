# Performance Review Checklist (Phase 6)

Performance findings need a **cost model** or they're noise: per what (request? item? render? frame?), on what realistic n, costing what (queries, ms, MB)? "O(n²) over the user's ~20 tags" is not a finding; "O(n²) over order history, unbounded, inside the request path" is. When you can't estimate n, ask — and remember the inverse false positive: flagging readable code as "slow" on paths that run once a day teaches authors to ignore you (and violates the premature-optimization rule you'd apply as an author).

## Algorithmic & computational

- Nested iteration over related collections — especially the disguised forms: `array.includes/indexOf/find` inside a loop (O(n·m) — build a Set/Map first), `filter().map().find()` chains re-scanning per element, sorting inside a loop, `array.shift()`/`unshift` in loops (O(n²) total).
- String concatenation in loops in immutable-string languages (builder/join instead).
- Recomputation of loop-invariant or request-invariant values (compiled regexes, parsed configs, date formatting) — hoist or memoize; conversely, memoization without bounds is a leak (`performance ↔ memory` trade-off — state it).
- Work computed then discarded: fetching/computing everything, then paginating/filtering in memory.

## Memory

- Unbounded caches/maps/arrays that grow with users or time; listeners and timers accumulated without cleanup.
- Whole-file/whole-table loads where streaming or pagination exists — severity scales with user control over the size.
- Large intermediate copies in pipelines (`.map().filter().map()` materializing arrays at each stage on big data — stream/generator/lazy alternatives); closures capturing large scopes in long-lived callbacks.

## I/O and concurrency

- **Sequential awaits on independent operations** — three independent fetches serialized = 3× latency; batch with `Promise.all`/`gather` (but check they're truly independent — see `bugs.md` for the correctness inverse).
- **Blocking calls on concurrency-critical threads:** sync file/DB/network/crypto (`bcrypt.hashSync`, `fs.readFileSync`, `requests` in async Python) on the event loop / async handlers / UI thread. One blocked event loop = the whole process's latency.
- Missing timeouts on outbound calls (a slow dependency becomes *your* outage — worker-pool exhaustion); no connection reuse (new client/connection per request); chatty APIs — response requiring the client to make N follow-up calls, or backend fanning into sequential internal calls.
- DB-specific costs: see `data.md` (N+1, indexes, overfetch dominate real-world backend latency — check them before micro-costs).

## Caching opportunities

Recommend caching only with all three named: **what** (expensive, repeated, tolerably-stale), **where** (in-process, Redis, HTTP/CDN — match scope: per-request memoization vs cross-request cache vs edge), and **invalidation** (TTL? event? never-changes?). A cache recommendation without an invalidation story is a bug recommendation. Quick wins to spot: static/computed responses missing HTTP cache headers or CDN; config/feature-flags re-fetched per request; identical heavy queries within one request (request-scope memo).

## Frontend performance

- **Render waste (React-family — details in `frameworks.md`):** new object/array/closure identities passed as props each render defeating memoization; state in a high-level component re-rendering the world on keystroke; context values recreated per render; missing list virtualization for large lists; layout thrash (interleaved DOM reads/writes).
- **Effects and data fetching:** fetch waterfalls (component mounts → fetch → child mounts → fetch — parallelize or lift); missing debounce on type-ahead requests; polling where the data allows longer intervals or push.
- **Payload:** unbounded API responses rendered wholesale; heavy dependencies bundled for one function; images unoptimized/unsized (layout shift); everything client-rendered when the framework offers static/server rendering for it.

## Reporting

Per finding: location · cost model (per-X, O(what) on realistic n, or measured numbers if tools ran) · severity from *user-felt or bill-felt* impact, not theoretical elegance · fix with its trade-off (memory for speed, staleness for latency, complexity for throughput — name what the fix costs). Separate "will bite at current scale" (findings) from "will bite at 10×" (forward-looking notes) so priorities stay honest.
