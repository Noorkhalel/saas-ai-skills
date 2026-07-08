# System Analysis: Propagation, SPOFs, Coupling, Debt (Phase 7)

The incident is a probe the system just ran on itself. Phase 7 reads the result: what structural properties turned a fault into an outage, and what would make the system fail *small* next time. These findings outlive the specific bug — they're often the most valuable part of the RCA.

## Failure propagation review

With the propagation chain mapped (`timeline.md`), extract the structural findings:

- **Every uncontained hop is a missing mechanism.** Fault crossed A→B because B had: no timeout (hung on A), no circuit breaker (kept hammering a dying A), no fallback (hard-failed instead of degrading), retries without backoff/jitter/budget (amplified the load — retry storms turn one slow dependency into a fleet-wide outage), no queue between them (sync coupling transmitted the failure instantly), or shared state with A (corruption traveled).
- **Asymmetry check:** did a *non-critical* dependency take down a *critical* path? (Analytics call blocking checkout; a logging endpoint's latency stalling requests.) Criticality inversion is a top systemic finding — the fix is isolation (async, fire-and-forget, bulkhead), not making the trivial dependency more reliable.
- **What contained it deserves equal analysis:** the hop where propagation *stopped* (a cache serving stale, a bulkhead, a degraded mode) is a working pattern — name it and recommend replicating it at the hops that failed.

## Single points of failure

The incident usually illuminates one; sweep for the rest of its kind while you're here:

- **Technical SPOFs:** the one DB/broker/gateway/cache everything shares; a single instance of anything stateful; one AZ/region; one certificate/credential everything uses (expiry = fleet outage); one config file/feature-flag service consulted on every request.
- **Logical SPOFs:** one shared library whose bug ships everywhere at once; one schema everyone reads directly; one cron job the business silently depends on.
- **Human SPOFs:** the one person who knows how to deploy/recover/interpret the dashboard (the incident's response delay often reveals this — it's a Process finding too).
- For each: is it *acceptable* (documented, monitored, with a recovery plan) or *unmanaged*? The finding isn't "SPOF exists" — most systems have them — it's "unmanaged SPOF with no detection and no runbook."

## Hidden coupling

Couplings that don't appear in any architecture diagram but transmitted or enabled the failure:

- **Shared infrastructure fate:** same node/pool/cluster, same connection pool, same rate limit, same disk — "unrelated" services failing together because they cohabit.
- **Temporal coupling:** deploy-order dependencies (code before migration or vice versa), cron jobs assuming other jobs finished, cache warmers racing traffic.
- **Data coupling:** two services reading the same table/topic with different assumptions about its shape or semantics; one writer's "harmless" format change breaking a reader nobody listed as a consumer.
- **Configuration coupling:** one env var/flag consumed by multiple components with different interpretations; a shared default that two systems assume differently.
- **Version coupling:** implicit contracts between services that only hold at specific version pairs, with nothing enforcing compatible rollout order.

The tell in the incident: something broke that "had nothing to do with" the change. Trace *why* it was affected — that path is the hidden coupling; the fix is making the coupling explicit (contract, schema, dependency declaration) or severing it.

## State, data and event flow findings

- Where does state live that shouldn't (in-process state preventing restart/scale — the incident where "restarting made it worse/lost data" reveals this)?
- Which data flows have no schema/contract enforcement at the boundary (the corruption path)?
- Which event flows assume exactly-once/ordered delivery on infrastructure that guarantees neither (`domains.md` races/queues)?
- Is there a **reconciliation path** for when the flow breaks — a way to detect and repair divergence after the fact? Incidents that end with "we manually fixed 214 rows" are naming the missing reconciler.

## Technical debt on the blast path

Scope the debt findings to what the incident touched (a full debt audit is a different engagement): the module everyone fears changing that sat in the causal chain; the TODO/`FIXME`/"temporary" hack from years ago that finally fired; the deprecated pattern that survived because nothing forced migration; test coverage holes exactly where the bug lived. For each: the debt item, its role in *this* incident (enabler? amplifier? detection-blocker?), and the paydown recommendation with that incident-derived justification — debt findings tied to a real outage get funded; generic debt lists don't.

## Writing the Architecture Findings section

Each finding: **property → role in this incident → recommendation → cost class (cheap guard / medium refactor / major change)**. Order by leverage, not grandeur — a timeout and an alert that contain the next incident beat a proposed re-architecture that won't ship. Recommend the major change only when the incident class genuinely cannot be contained without it, and say so explicitly ("third incident from this coupling; containment has failed twice").
