# Evidence Collection and Correlation (Phase 2)

An RCA is only as strong as its evidence chain. This file covers reading each artifact type, correlating across sources, and the fact discipline that keeps the report trustworthy.

## Fact classification — the discipline

Every statement that enters the report gets one of four labels, and the label is decided by *how you know it*:

| Label | How you know it | Example |
|-------|-----------------|---------|
| **Verified Fact** | Directly observed in an artifact you read (cite it) | "First 500 logged at 14:02:13 (app log line 8841)" |
| **Likely Cause** | Inference consistent with all evidence; one link unobserved | "The deploy introduced the read of the missing key (diff + error name match; not yet reproduced)" |
| **Possible Cause** | Plausible; not yet supported or excluded | "Cache poisoning could also produce stale reads" |
| **Unknown** | You looked and cannot determine it | "No metrics exist for connection-pool usage before 14:00" |

Two rules: never let a Likely Cause harden into a Verified Fact through repetition — it stays labeled until verified; and treat **Unknowns as findings** — "we cannot know X because no log/metric captures it" is an observability gap that belongs in Preventive Actions.

## Reading each artifact

**Logs.** Read *before* the first error, not just the error — the cause usually logs quietly (a WARN, a retry, an odd value) before the effect logs loudly. Identify the *first* anomalous line (one root failure emits cascades; the most frequent error is rarely the origin). Follow one failing request end-to-end by request/trace id rather than grepping the error string. Note what's *absent*: a log line that should appear and doesn't places the failure upstream of that point.

**Stack traces.** Top-to-bottom; first frame in first-party code is the entry point to the fault (not necessarily the origin — the bad value may be born elsewhere). Read every "Caused by"/nested cause to the deepest one. The exception *type* classifies the failure; the *message* often names the culprit (a key, a host, a column).

**Metrics and monitoring.** Find the *inflection points*: when did latency/errors/memory/CPU/queue-depth leave normal? The first metric to move points nearest the origin; the order in which metrics moved sketches the propagation path (DB latency rose → then app p95 → then error rate = downstream-up). Pull the same window for the previous day/week as the "normal" baseline — "high" means nothing without it.

**Git and deploy history.** The highest-yield correlation in RCA: **most incidents follow a change.** Line up incident start against: deploys (code), config changes, infra changes (IaC applies, scaling events), dependency updates (lockfile diffs), migrations, cron schedules, feature-flag flips, certificate/credential rotations, and *external* changes (provider incidents, API-partner deploys). A clean "nothing changed" is rare and is itself a finding (points to slow accumulation: growth, leak, expiry, data volume). For the suspect change: read the actual diff — including the parts that "couldn't be related."

**Configuration and environment.** Diff prod against the environment where it works. Check for the *absence* pattern: an unset variable silently falling back to a default. Verify what's actually deployed (image digest, resolved dependency versions) versus what the repo claims — drift between intended and actual state is a classic hidden cause.

**Crash/OOM artifacts.** Exit codes and signals classify (app error ≠ OOMKilled ≠ segfault ≠ SIGTERM). For memory: the *trend* diagnoses — gradual climb (leak) vs sudden spike (one allocation) vs sawtooth exceeding the ceiling (undersized). Restart history: increasing restart frequency over days is a leak signature.

**Database evidence.** Query plans (`EXPLAIN ANALYZE`) for degradation; lock/deadlock logs (the DB names both parties); replication lag; `pg_stat_statements`-class views for what changed in query mix; table/index bloat and autovacuum history for slow drifts; connection counts against the pool/max.

**API responses / external systems.** Capture the actual failing response (status, body, headers), not the client's summary of it. Check the provider's status/incident history for the window. Rate-limit headers and 429s hide inside generic "API errors."

## Correlation — where RCA conclusions actually come from

Single-source evidence produces hypotheses; **cross-source correlation produces conclusions**:

- **Logs ↔ code:** for the key log lines, open the code that emits them and read the surrounding logic — what state must be true for this line to print? The log tells you which branch ran; the code tells you what that implies.
- **Deploys ↔ incident onset:** exact timestamps, not "around 2pm." A 14:00:00 deploy and 14:02:13 first-error means the failure needed ~2 minutes — what runs then? (First request to a cold path, first cron tick, cache expiry, connection recycling.) The *gap* between change and failure is itself diagnostic.
- **Metrics ↔ logs:** the metric says *when and how much*; the log says *what and where*. An error-rate step at 14:02 + `KeyError` first logged 14:02:13 = same event, two witnesses. Disagreement between them is a finding (sampling, missing instrumentation, wrong dashboard).
- **Scope ↔ data:** failure limited to some users/tenants/regions → diff what's special about them (data shape, locale, plan, shard, node). The boundary of the blast radius traces the causal boundary.

## Collection checklist per incident window

Capture before it rots (logs rotate, metrics downsample, pods vanish): app + infra logs for the window (± the baseline before), deploy/change log with timestamps, the suspect diffs, metrics snapshots (error rate, latency, saturation, restarts), current + prior config, and any crash artifacts. In the report, list what you collected *and what was unavailable* — the unavailable list feeds Monitoring Improvements.
