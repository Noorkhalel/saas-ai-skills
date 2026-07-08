# Frontend Debugging (Phase 5/6)

For crashes, blank screens, wrong UI state, stale data, and jank in browser apps. Frontend bugs split into: it *crashed* (threw), it *renders wrong* (state/props), it's *stale* (data/effect sync), or it's *slow* (render/bundle). Identify which before diving in.

## Crashes / blank screen / "white screen of death"

- **Read the browser console + the component stack**, not just the message. An unhandled error during render unmounts the tree (React) → blank page. The trace names the component; the *cause* is usually a bad assumption about data shape.
- **The classic post-login/post-fetch crash:** a component renders with data that isn't there yet (async not resolved) or came back a different shape than assumed — `user.profile.name` where `profile` is null, `.map` on `undefined`, destructuring a partial object. The render runs before/without the data. Verify the loading and error states exist, not just the success state; check what the API *actually* returned (shape drift, null fields, error body rendered as data).
- **Hydration mismatch (SSR/Next):** server and client render differently (using `window`/`Date`/`localStorage`/random during render, or different data) → hydration error, sometimes a wipe-and-remount flash. The console names the mismatch.
- Source maps: debug against mapped sources; a minified prod trace (`a.b is not a function`) needs the map to be actionable.

## State & rendering bugs (wrong UI)

- **Stale closure (React):** a callback/interval/effect captures state/props from the render it was created in and never sees updates — `setInterval(() => setN(n+1))` increments from the frozen `n` forever; an event handler reading old state. Fix: functional updates or refs; correct effect deps. A top source of "the value is wrong but the code looks right."
- **Effect dependency bugs:** missing deps → effect uses stale values / doesn't re-run when it should; extra/unstable deps (new object/array/function identity each render) → effect loops or over-fires. Check the dependency array against what the effect actually reads.
- **Direct state mutation:** `arr.push`/`obj.x=` then `setState(arr)` — same reference, no re-render, or torn UI (React/Vue/Redux all assume immutable updates). Sort/splice a copy.
- **Key bugs in lists:** array index as `key` on a reorderable/filterable list → state and DOM stick to the wrong item after reorder/delete (a *correctness* bug presenting as "the wrong row is selected/edited"). Use stable ids.
- **Derived state stored** in state (then desyncs from its source) instead of computed during render.
- **Race between fetches:** two in-flight requests resolve out of order, last-write-wins by luck → stale data shown; unmount during fetch → setState-after-unmount. Fix: abort/ignore-stale on cleanup, or a data lib that handles it.

## Stale / missing data

- Data-fetching layer caching (React Query/SWR/RSC, Next fetch cache): serving cached/stale data, or user-specific data cached where it's shared → cross-user leak (escalate — security). Check cache keys include the user/params; check revalidation.
- Next.js: `NEXT_PUBLIC_`-less env vars are undefined in the browser (a common "it's undefined on the client"); server/client component boundary — server-only data/secret imported into a client component; `use client` boundaries changing where code runs.
- Auth/session on the client: token expiry not handled (works until it silently expires → 401s that look "random" — see `references/security.md`); route guards being UX not security.

## Performance (jank, slow interaction)

- **Render storms:** state placed too high re-rendering the whole tree on every keystroke; new object/array/closure props defeating memoization; context value recreated each render re-rendering all consumers. Use the framework profiler (React DevTools Profiler) to *see* what re-rendered and why — don't guess.
- **Missing virtualization** for large lists (thousands of DOM nodes); **fetch waterfalls** (parent fetches, then child mounts and fetches — serialize into a request chain) — parallelize/lift; missing debounce on type-ahead.
- **Main-thread blocking:** heavy sync compute in an event handler/render (big sort/parse) freezing the UI; layout thrash (interleaved DOM read/write in a loop).
- Bundle: a huge dependency imported for one function; unoptimized/unsized images (layout shift). Measure with the network panel / bundle analyzer.

## Framework tells

- **React:** effect/deps and stale-closure bugs dominate; StrictMode double-invokes effects in dev (surfaces missing cleanup — a feature, not the bug).
- **Vue:** losing reactivity by destructuring reactive objects (`toRefs`); mutating props; `v-if`+`v-for` on one node; missing `:key`.
- **Angular:** subscriptions never unsubscribed (leak + ghost updates — `async` pipe / `takeUntilDestroyed`); expensive expressions in templates re-run every change-detection; zone/`OnPush` mismatches.
- **Svelte:** reactivity keyed to assignment (mutating without reassigning `arr = arr` doesn't trigger); store subscription leaks.

## Reporting

Name which category (crash/state/stale/perf), the specific mechanism (the stale closure, the shape drift, the missing dep, the render trigger), evidence (console trace, profiler flame, the actual API payload), confidence, and the minimal fix. For crashes, the fix includes handling the real absent/error state — not just a `?.` that turns a crash into a silently broken UI.
