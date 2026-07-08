# Timeline Reconstruction and Failure Propagation (Phase 3)

The timeline is the skeleton every other finding hangs on. Build it before arguing causes: causality must respect chronology, and half the time the ordered timeline *hands you* the trigger.

## Building the timeline

Assemble every timestamped event from the evidence into one ordered sequence, tagged with its source:

```
NORMAL STATE      14:00-  baseline: error rate 0.1%, p95 180ms          [grafana]
TRIGGER           14:00:12  deploy v2.14.0 completes on all pods        [deploy log]
FAILURE BEGINS    14:02:13  first KeyError: PAYMENT_TIMEOUT             [app log 8841]
PROPAGATION       14:02-14:09  checkout error rate 0.1% → 92%           [grafana]
                  14:04:40  payment queue depth begins climbing         [prometheus]
DETECTION         14:09:02  PagerDuty fires (error-rate > 5% for 5m)    [alert log]
RESPONSE          14:14     on-call confirms, starts rollback           [incident channel]
RECOVERY          14:31:20  rollback complete, error rate normal        [grafana]
CURRENT           14:45     queue drained; 214 orders need reconciliation
```

Rules that keep it honest:

- **Every entry cites a source.** An event you can't source goes in as `(unverified — per on-call recollection)`.
- **Normalize timezones** first — mixed UTC/local timestamps create phantom causality. State the timezone once at the top.
- **Include non-events**: "14:00–14:02 — no errors yet" matters (see the gap analysis below). Include the *last known good* observation explicitly.
- **Mark clock-skew risk** when correlating across systems whose clocks you can't vouch for; a 30-second skew can invert apparent cause and effect.
- Unknown times are entries too: `??:?? — config change applied (no audit log — Unknown; observability gap)`.

## The three gaps — findings hiding in the timeline

1. **Trigger → failure gap.** Why 2 minutes and not instantly? The delay names the mechanism: first request on a cold path, cache TTL expiry, connection recycling, cron tick, queue backlog reaching the bad consumer, gradual resource exhaustion. If the failure was instant, the trigger is on the hot path; if delayed, something scheduled or accumulating sits between.
2. **Failure → detection gap** (14:02 → 14:09 = 7 minutes of silent failure). Why didn't we know sooner? Wrong threshold, missing signal, alert on the wrong metric, no synthetic check on the flow that broke. This gap *is* the Monitoring Improvements section.
3. **Detection → recovery gap** (14:09 → 14:31). What slowed response — unclear ownership, slow rollback path, missing runbook, hard-to-interpret dashboards? This gap feeds Process Findings. Also record what went *well* (rollback worked, one command) — postmortems that only list failures teach half the lesson.

Mark on the timeline **where intervention could have stopped escalation** — e.g., "a startup config check would have failed the deploy at 14:00:12, before any traffic saw an error."

## Failure propagation mapping

Trace how the fault *spread* from origin to impact — this is where containment findings come from:

- **Draw the chain:** origin component → what it returned/withheld → how each downstream consumer reacted (error? retry? hang? degrade?) → final user-visible impact. The order metrics moved (evidence.md) sketches this chain empirically.
- **At each hop, ask: why did the failure cross this boundary?** Missing timeout (caller hung), missing circuit breaker (caller kept hammering), retries amplifying load (thundering herd), shared resource (one tenant's failure exhausting a pool everyone uses), synchronous coupling where async would have absorbed it, missing fallback/degradation path.
- **Identify the blast radius boundary** — where it *stopped* spreading and why (a bulkhead that worked, a cache that served stale, an unrelated code path). What worked is a pattern to replicate; say so.
- Each hop the failure crossed uncontained is an **Architecture Finding**: the containment mechanism that was missing there (timeout, breaker, bulkhead, queue, fallback, isolation). These feed Phase 7 directly.

## Reconstruction under missing data

Real incidents have holes. Fill them honestly: bracket the unknown ("failure began between 14:01:30 — last success logged — and 14:02:13 — first error"), never interpolate a specific time you didn't observe; use indirect witnesses (a downstream service's logs to bound an upstream event); and record every hole as an observability gap with the specific log/metric/audit-trail that would have closed it. A timeline with honest brackets and named gaps is more credible — and more useful — than a smooth story.
