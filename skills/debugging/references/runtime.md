# Backend Runtime, Async, Memory & Exceptions (Phase 5/6)

For bugs in running backend code: crashes, wrong results, hangs, leaks, and the exception-handling that hides all of them. Trace the specific value/flow — these are patterns to *recognize*, then verify against the actual code, not conclusions to assert.

## Null / undefined / absent values

The most common runtime crash. The fix is never a reflexive `?.`/guard — it's finding *why* the value is absent:
- Trace the value backward (`references/workflow.md` data-flow): born where? An unhandled branch (cache miss, DB no-row, failed lookup returning null), an unawaited promise read before it resolves (see async), a destructure of a partial object, an env var/config that's unset, a shape change upstream (API/schema).
- Distinguish "should never be null here" (add an assertion/invariant and fix the source) from "legitimately can be absent" (handle it explicitly — default, early return, error). Silently coalescing absence to a wrong-but-valid value (`?? 0`, `|| {}`) often just moves the crash somewhere harder to find.

## Async / await bugs

- **Missing `await`:** code proceeds before the operation finishes — reads a value not yet set, a promise where a value is expected (`if (isValid(x))` on an async `isValid` is always truthy), or the function returns before the write commits. Symptom: works with a debugger/breakpoint (which adds delay), fails at speed — a timing tell.
- **Fire-and-forget rejections:** an un-awaited async call whose rejection has no handler → unhandled-rejection crash (Node) or silent swallow; the error surfaces detached from its cause. Grep for async calls without `await`/`.catch`.
- **try/catch that can't catch:** wrapping the *call* but not the *await*; throwing inside a callback/`setTimeout`/event handler outside the try; rejections in `.then` with no `.catch`. The catch looks like protection and isn't.
- **`Promise.all` semantics:** one rejection rejects the whole thing and *doesn't* cancel the others (they run on, maybe mutating state) — use `allSettled` when partial success is valid; and `all` over handlers that write shared state is a concurrency bug (`references/concurrency.md`).
- **Sequential vs parallel:** independent awaits run serially = latency bug (perf); dependent operations run in parallel = correctness bug. Match the structure to the real dependency.

## Memory leaks (gradual growth → eventual OOM)

Signature: memory climbs over hours/days and doesn't return after load drops; restart temporarily fixes it. Hunt the roots that never let go:
- **Unbounded caches/maps/collections** keyed by something unbounded (user id, request id) with no eviction/TTL — the #1 server leak. Grep module-level `Map`/`{}`/arrays that only ever grow.
- **Listeners/subscriptions/timers** added per request/mount and never removed (`on(...)`, `addEventListener`, `setInterval`, DB/queue subscriptions) — each accumulates plus its captured scope.
- **Closures capturing large scope** held by long-lived callbacks; **globals** appended to; loggers/buffers retaining request data.
- Method: capture two heap snapshots under steady load, diff for the growing retained set, follow the retainer chain to what holds it. Don't guess the object — let the snapshot name it. (Language specifics: Node `--inspect` heap snapshots; Python `tracemalloc`/`objgraph`; JVM heap dump + MAT; .NET dotnet-gcdump.)
- Not every OOM is a leak: a single huge allocation (loading an unbounded query/file into memory) or load simply exceeding a too-small limit both OOM without leaking — the memory *trend* distinguishes them (`references/evidence.md`).

## CPU spikes / hangs / runaway loops

- 100% CPU with no progress → infinite/near-infinite loop (a termination condition that never trips, a retry with no backoff/cap, a cycle in a graph walk) or catastrophic-backtracking regex on hostile input. Get a CPU profile / thread dump / a few stack samples — they point straight at the hot frame.
- A hung request (not CPU-bound) → blocked on I/O: a lock held too long, a downstream call with no timeout, a connection-pool exhausted (every worker waiting for a connection none will release). Thread/async-task dump shows where they're parked.
- Blocking the event loop / async thread with sync work (sync file/crypto/`JSON.parse` of huge payloads, `hashSync`) stalls *all* concurrency — see `references/frontend.md`/`infra.md` for the framework-specific tells.

## Exception handling & propagation

Bugs *caused by* how errors are handled — often the reason a bug is invisible:
- **Swallowed errors:** empty catch, `catch (e) { log(e) }` then continue on garbage, `.catch(()=>{})`. Ask of every catch: *can the code after this legitimately run if the try failed?* If not, the swallow is hiding the real failure downstream of where it's felt.
- **Over-broad catch** turning a programming bug (null deref, type error) into a generic "something went wrong," erasing the trace. Catch narrowly; let unexpected errors propagate with their stack.
- **Error → wrong signal:** returning null/`-1`/`""` on failure that callers can't distinguish from success; HTTP 200 with an error body; re-throwing a new error that drops the original cause (preserve the chain).
- **Partial failure in loops/batches:** one bad item aborts the batch, or is silently skipped with no record — check the intended contract.
- **Resource leaks on the error path:** connections/files/locks acquired then leaked when an exception skips the release — needs finally/context-manager/using/defer. Recurring "too many connections"/"too many open files" under errors is this.

## Framework tells (backend)

- **Node/Express:** async handler throws don't reach error middleware without a wrapper (Express 4) → unhandled rejection; sync I/O on the event loop stalls everything; module-level mutable state shared across requests leaks between users.
- **FastAPI:** blocking (sync `requests`, sync DB driver) inside `async def` blocks the loop — the #1 FastAPI perf/hang cause; use `async` clients or a sync `def` (thread-pooled).
- **Django:** N+1 via lazy ORM access in loops/templates; `atomic()` scope around multi-write invariants; signals doing critical work with surprising ordering.
- **Spring:** `@Transactional` self-invocation silently non-transactional (proxy bypass); checked exceptions don't roll back by default; lazy-loading exceptions outside the session.
- **.NET:** `async void` swallows exceptions; `.Result`/`.Wait()` deadlocks (sync-over-async); `DbContext` captured across threads.
