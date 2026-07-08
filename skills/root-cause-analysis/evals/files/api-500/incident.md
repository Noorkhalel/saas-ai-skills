# Incident: checkout API returning 500s after this afternoon's deploy

All times UTC. Status: recovered via rollback; RCA requested.

## Monitoring (Grafana, checkout service)

- Baseline all week: error rate ~0.2%, p95 210ms
- 14:00:41 — deploy of `checkout v3.9.0` completes on all 6 pods (deploy log)
- 14:03:12 — error rate starts climbing: 0.2% → 88% over ~90 seconds
- 14:11:29 — PagerDuty alert fires (rule: error rate > 10% sustained 5 min)
- 14:19:00 — on-call identifies the deploy as suspect, initiates rollback to v3.8.2
- 14:26:47 — rollback complete, error rate back to 0.2%
- Impact window: ~24 minutes; ~9,400 failed checkout attempts (payment provider shows no double charges)

## App logs (first errors, 14:03:12 onward, identical for all)

```
14:03:12.401 ERROR unhandled exception in POST /api/checkout
TypeError [ERR_INVALID_ARG_TYPE]: The "ms" argument must be of type number. Received undefined
    at Timeout.setTimeout (node:internal/timers:...)
    at applyPaymentTimeout (dist/payments/client.js:88)
    at processPayment (dist/payments/client.js:41)
```

Note: the first checkout request after deploy was at 14:03:12 (checkout traffic is bursty; nothing hit the payment path in the first ~2.5 minutes).

## The deploy diff (v3.8.2 → v3.9.0), relevant hunk in `src/payments/client.ts`

```diff
- const PAYMENT_TIMEOUT_MS = 30000; // hardcoded since 2023
+ // Make payment timeout tunable per environment (requested by ops)
+ const PAYMENT_TIMEOUT_MS = Number(process.env.PAYMENT_TIMEOUT_MS);
```

PR #2214, "Make payment timeout configurable", approved by one reviewer, all CI checks green
(unit tests mock the payments client entirely; no test boots the real module).

## Configuration state

- `PAYMENT_TIMEOUT_MS=45000` was added to the **staging** environment config (separate repo,
  `config-staging.yaml`, merged 3 days ago by the ops team).
- The **production** config repo has no `PAYMENT_TIMEOUT_MS` entry. Config repo changes are
  deployed independently of app deploys and are not linked in the PR template.
- Staging soak ran 48h clean before the prod deploy.

## Prior occurrences

In March a similar incident: new required env var `REDIS_TLS_MODE` missing in prod, 11-minute
outage. The postmortem action "add startup validation for required env vars" was written down
but never scheduled.
