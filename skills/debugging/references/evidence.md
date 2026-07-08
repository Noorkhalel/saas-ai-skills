# Reading and Collecting Evidence (Phase 2)

The quality of a diagnosis is capped by the quality of the evidence. This is how to extract the most from each artifact type and what to collect when you can. Read the artifacts *fully* before hypothesizing — the answer is often already in front of you, a few lines above the error.

## Stack traces

- **Read top to bottom and find the first frame in *your* code.** The top frame is often deep in a library (where it threw); the first frame you own is where *you* triggered it — start there, but remember it's where the fault *surfaced*, not necessarily where the bad value was *born*.
- **The exception type classifies the bug:** `NullPointer`/`undefined is not...` → a value wasn't there that code assumed was; `IndexOutOfBounds` → boundary/empty-collection; `ClassCast`/type errors → wrong assumption about shape; timeout → downstream slow/hung; `OOM` → memory (see below); connection/`ECONNREFUSED` → dependency down/misconfigured; permission/`EACCES` → filesystem/user/secret.
- **Read the whole chain.** "Caused by:" / nested/`__cause__` traces point at the *original* failure — the last "Caused by" is usually closest to the root. Async traces may be broken across boundaries; reconstruct the logical flow.
- **Don't fix at the trace line reflexively.** `Cannot read 'id' of undefined` is not fixed by `?.` — it's fixed by finding *why the object is undefined*. The trace tells you *where*; you still owe the *why*.

## Logs and terminal output

- **Read backward from the error, then forward.** The lines *before* the error usually contain the cause (the last successful step, the odd value, the retry, the warning everyone ignored). The error line is the effect.
- **Build a timeline.** Timestamps establish sequence and gaps (a 30s gap before a timeout = something hung). Correlate across services by request/trace id. Note the *first* occurrence — "when did this start?" ties to a deploy/config/traffic change.
- **Distinguish the first error from its cascade.** One root failure often emits dozens of downstream errors; the loudest/most-frequent is rarely the cause. Find the earliest anomalous line.
- **Log levels lie both ways:** real causes hide at WARN/INFO above an ERROR; and a flood of ERRORs may be one cause repeated. Grep for the request that failed, not just the error string.

## Git history and "it worked before"

The single highest-yield lead: **most bugs are regressions.** If it worked and now doesn't, something changed.

- `git log --since` / `--oneline` on the failure window; `git log -p -- <path>` for the fault file; `git blame` on the exact line to see the introducing commit and its intent.
- **`git bisect`** when you can reproduce and know a good commit — binary-searches straight to the culprit commit, the most powerful move you have for a regression.
- For "failed after a merge/deploy": diff the deployed range, and check *non-code* changes too — dependency bumps (lockfile diff), config, env vars, migrations, infra. The bug is often in what changed *around* the code.

## Slow / performance artifacts

- **Measure, never eyeball.** For SQL, `EXPLAIN (ANALYZE, BUFFERS)` — read for seq scans on big tables, bad row estimates, nested loops over large sets, sorts spilling to disk (`references/data.md`). For code, a profiler/flame graph shows where time actually goes — it's routinely somewhere you didn't guess.
- Get the *cost model*: per-request? per-row? O(what) on what n? A "slow" report needs numbers — p50/p95/p99, rows scanned, allocations — before a fix.
- Distinguish *always slow* (algorithm/query/index) from *sometimes slow* (contention, GC pauses, cold cache, N+1 that scales with data, noisy neighbor).

## Crash / OOM / core

- **Exit code + signal classify it:** OOMKilled (137 / SIGKILL by cgroup) ≠ SIGSEGV (native memory) ≠ uncaught exception (nonzero app exit) ≠ SIGTERM (orderly shutdown, e.g. failed liveness probe). Get the exact code before theorizing (`references/infra.md` for container exit codes).
- For OOM: the *trend* matters — gradual climb = leak (`references/runtime.md`); sudden spike = one large allocation/request; sawtooth that outgrows the ceiling = load exceeding capacity. Get the memory graph, not just the crash moment.

## Config, env, and dependencies

- **Config drift** is a top cause of "works on my machine / only in prod": compare env vars, versions, feature flags, resource limits across environments. The bug is frequently *absence* — an unset var falling back to a wrong default.
- Dependency issues: exact resolved versions (lockfile), not the manifest range; a transitive bump can change behavior with no first-party change. Check for version conflicts and native-module/ABI mismatches.

## What to collect, by report

| Report | Pull first |
|--------|-----------|
| "Throws exception X" | Full trace + first-party frame, the code there + callers, inputs at failure, recent changes to that path |
| "500 / server error" | App logs around the request, the trace, the request payload, deploy timeline, downstream health |
| "Slow" | Query plan or profile, the timeline (when/always?), data volume, p95/p99 |
| "Crashes / OOM" | Exit code/signal, memory-CPU trend, logs before crash, restart pattern |
| "Only in prod" | Config/env diff vs working env, data differences, scale/concurrency, resource limits |
| "Intermittent" | Frequency & correlation (time? user? load? host?), concurrency model, external deps (`references/concurrency.md`) |
| "After deploy/merge" | The diff, migrations, dependency/lockfile changes, config changes, `git bisect` |
| "CI/container/pod fails" | Exit codes, events (`describe`/`docker logs`), first failing step, image/resource config (`references/infra.md`) |

When you can't obtain an artifact, name it as a specific request ("share the full stack trace including 'Caused by'", "run `EXPLAIN ANALYZE` on the slow query", "paste `kubectl describe pod`") — a precise ask is a better deliverable than a guess built on the gap.
