# Domain Signatures: Typical Causal Chains by Incident Type

Fast orientation per incident domain: the signature, the usual suspects ranked, and where the Five Whys typically bottoms out. These are *priors to verify against evidence*, never conclusions — the evidence can and does overrule the prior.

## API suddenly returns 500s (esp. after deploy)

Suspects: the deploy (diff the release: new required config/env, changed defaults, migration ordering, dependency bump), then downstream (DB/cache/third-party health at that timestamp), then traffic shape. Evidence: first error's stack + the deploy diff + config diff. Typical roots: config/code shipped through disconnected paths; no startup validation of required config; no canary/smoke gate; error handling that turns a specific failure into a generic 500 (masking). Deep debugging of the fault itself: exit to ordinary debugging once RCA scope is clear.

## Database performance degradation

Suspects by onset: **sudden** → plan flip (stats, threshold crossed, index dropped/bloated), lock contention (long transaction, migration), resource event (failover, noisy neighbor, disk); **gradual** → growth crossing an index/memory boundary, bloat, autovacuum falling behind, connection creep. Evidence: `EXPLAIN ANALYZE` now vs before, `pg_stat_statements` deltas, lock/deadlock logs, table/index sizes, connection counts. Typical roots: queries indexed for last year's data volume; no plan-regression or slow-query alerting; migrations run without lock analysis; no capacity model.

## Intermittent auth failures (JWT/session)

"Random" auth failure is almost always **time- or instance-correlated** — check both before anything else. Suspects: token expiry vs refresh race (fails at exactly N minutes), clock skew between issuers/verifiers, key rotation with instances holding different keys (fails on ~1/N of requests — the load-balancer fingerprint), session-store eviction, cookie attributes dropping on specific flows. Evidence: failure timestamps vs token `iat`/`exp`, failure distribution across pods/hosts, rotation schedule vs onset. Typical roots: rotation designed without an overlap window; no shared/synced key source; refresh race with no single-flight; no auth-failure-rate alert segmented by instance.

## Frontend infinite render loop

Signature: UI freezes/flickers, CPU pegged, "maximum update depth exceeded". Mechanism is circular: render → effect/callback sets state → render. Suspects: effect with an object/array/function dependency recreated every render; setState called during render; parent re-render recreating props feeding a child effect; state update that always produces a new reference even when equal. Evidence: the component named in the error + its effect dependency arrays. Typical roots: unstable identities as dependencies (no memoization discipline); no lint rule (`exhaustive-deps`) enforced; no render-count regression check on hot components.

## Kubernetes CrashLoopBackOff / Docker exits

The exit code + events classify before any theory: `logs --previous` (the crashed instance), `describe` (events, last state). Exit 1 = app startup error (usually config/secret/dependency); 137 = OOMKilled (limit vs footprint); SIGTERM loop = liveness probe killing a slow starter. Typical roots: config/secret renamed with stale references (+ `optional: true` making it silent); probes tuned without measuring real startup; no rollout gate halting a crashing deploy; resource limits set by copy-paste, not measurement.

## Race conditions / duplicate processing

Signature: intermittent, load-correlated, impossible single-user; duplicates or invariant violations (negative stock, double charge). Suspects: check-then-act without atomicity; queue redelivery hitting a non-idempotent consumer (crash between side effect and ack); retry on timeout of a non-idempotent call; concurrent workers sharing state. Evidence: the two interleaved requests'/deliveries' logs (same message id twice = redelivery; different request ids same resource = race), the code's atomicity gap. Typical roots: **idempotency never designed in** (no keys, no dedup, no conditional writes); at-least-once delivery assumed exactly-once; no concurrency tests; invariants enforced in app code instead of constraints.

## Memory leak in long-running services

Signature: gradual climb, restart-resets, restart frequency increasing over days; OOM kills at the end. Suspects: unbounded caches/maps keyed by unbounded values, listeners/timers accumulating, closures pinning large scopes, buffers never flushed. Evidence: memory trend (the shape is the diagnosis), heap snapshot diff naming the growing retainer. Typical roots: cache added without eviction policy (often in a hotfix that skipped review); no memory trend alerting (only OOM crash alerts — detection at 100%); no soak/endurance test in the pipeline.

## CI/CD failure after dependency update

Suspects: the resolved-version diff (lockfile), not the manifest — transitive bumps break with no first-party change; breaking changes in minors (semver is a promise, not a law); peer/ABI/engine mismatches; postinstall scripts; registry/cache flakiness (re-run distinguishes). Evidence: lockfile diff, the failing step's own log (first failure, not the final summary), changelogs of bumped packages. Typical roots: unpinned ranges + no lockfile discipline; dependency updates batched huge instead of small and reviewable; no dependency-diff gate or canary for updates.

## AI agent / MCP workflow failures

The newest domain; treat with the same evidence discipline. Signature classes and suspects:
- **Agent "hallucinates" tool results** → first check whether the tool *actually returned anything*: a wrapper that catches errors and returns empty/default output invites the model to fill the gap; tool timeouts surfaced as empty strings; missing "tool failed" signal in the transcript. The root is usually **silent tool failure + no output validation**, not "the model lied." Evidence: the raw tool-call transcript vs the agent's claims.
- **Wrong/missing context** → context truncation (limits hit silently), stale retrieval, a system prompt overwritten in some path; evidence: the actual assembled prompt/context at failure time (if it isn't logged, that's the observability gap — log it).
- **MCP integration failures** → schema drift between server and client, auth/token expiry mid-session, server process death with client-side generic errors, version skew. Evidence: MCP-layer logs both sides.
Typical roots: no transcript/telemetry for tool calls (can't distinguish model failure from tool failure — the #1 gap); errors coerced to empty results instead of surfaced; no validation of tool outputs against expectations; no eval/regression harness for agent behaviors.

## Security incidents

When the incident *is* or *might be* an exploit: preserve evidence before remediating (logs, access records, artifacts — don't destroy the trail by redeploying); establish the access path and its first use (the timeline extends *backward* — initial access often predates detection by a long time); scope what was reachable (blast radius = data/systems the compromised credential/path could touch, not just what you've confirmed touched). Typical roots: the vulnerability class (see any injection/authz gap) *plus* the detection gap (no alerting on the anomalous access pattern) *plus* excessive standing privilege (blast radius finding). Flag explicitly when incident response (containment, rotation, disclosure) must precede or parallel the RCA — investigation never delays containment.
