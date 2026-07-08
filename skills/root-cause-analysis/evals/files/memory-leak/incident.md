# Incident: notifications service crashes nightly, now several times a day

All times UTC. Status: mitigated by a cron restart at 04:00; RCA requested.

## History

`notifications` is a long-running Node.js service (sends email/push, renders templates).
- **May:** stable for months, ~180MB RSS steady, zero OOM kills.
- **June 2 (v1.31.0 deployed):** memory now climbs continuously. First OOM kill June 9 (7 days).
- **June–July:** OOM interval shrinking as traffic grows: weekly → every ~2 days → since
  July 1, 2–4 OOM kills/day (limit 512Mi). Ops added the 04:00 cron restart on June 24 as a stopgap.
- Nobody was paged for any of this — there is no memory alert; OOM kills were discovered in
  the k8s restart counts during an unrelated review last week. User impact: notifications
  delayed 1–4 minutes around each crash (queue buffers them); ~40 nightly digest emails were
  sent twice after mid-render crashes (render side effect precedes send-ledger write).

## Metrics (Prometheus, RSS of one pod, typical day this week)

```
04:00 restart → 175MB | 08:00 → 240MB | 12:00 → 318MB | 16:00 → 402MB | 19:30 → 505MB → OOMKilled
```
Growth tracks request volume (flat overnight, steep during business hours). Heap snapshot
diff (taken 2h apart yesterday): the dominant growing retainer is a `Map` in
`dist/render/templates.js` — 1.9M entries, ~210MB retained, keys look like
`"digest:u_18422:2026-07-07"`, `"order-shipped:u_9911:en:dark"`.

## The June 2 diff (v1.31.0), `src/render/templates.ts` — PR #1789 "hotfix: template render perf"

```diff
+ // cache rendered templates — rendering is expensive (~40ms)
+ const renderCache = new Map<string, string>();
  export function renderTemplate(name: string, user: User, opts: Opts): string {
+   const key = `${name}:${user.id}:${opts.locale ?? "en"}:${opts.theme ?? "light"}`;
+   const hit = renderCache.get(key);
+   if (hit) return hit;
    const html = expensiveRender(name, user, opts);
+   renderCache.set(key, html);
    return html;
  }
```

PR #1789 was merged **without review** using the repo's `hotfix/*` branch bypass (created
for emergencies; this was a Friday perf complaint, not an emergency) 40 minutes after being
opened. The cache has no eviction, no TTL, no size bound; the key space includes user id ×
template × locale × theme × (for digests) the date — effectively unbounded. Cache hit rate
measured yesterday: **0.4%** (keys are nearly unique — per-user-per-day digests never repeat).

## Context

The perf complaint that motivated the hotfix was later traced (June 20, separate ticket) to
a slow DB query in the digest job, not to template rendering. The cache delivers ~no benefit.
No soak/endurance test exists in CI; the load test suite runs 5 minutes max.
