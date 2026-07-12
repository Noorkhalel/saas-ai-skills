# Frontend performance playbook

Start with real-user metrics when available; lab tests explain, not replace, field behavior. Segment by route, device/CPU class, network, region, cache state, and release. Track LCP, INP, CLS, TTFB, FCP, transfer size, long tasks, JS execution/hydration, and request waterfall.

## Investigation order

1. Identify the user interaction/route and reproduce with production-like throttling/data.
2. Inspect network waterfall: document/TTFB, critical CSS/JS, render-blocking requests, images/fonts, third parties, cache/CDN headers, and duplicate requests.
3. Inspect main thread: hydration, parsing/evaluation, long tasks, layout/recalc, rendering, event handlers, and React/Vue/Angular/Svelte component updates.
4. Inspect bundle composition and route chunks before code splitting; verify an import is actually deferred and that split chunks do not create a waterfall.
5. Validate visually, functionally, and with keyboard/screen-reader behavior. Performance changes must not degrade accessibility or loading/error states.

## Remedies only after attribution

Use responsive image dimensions/formats/priorities when image transfer or discovery limits LCP. Use route/component lazy loading when noncritical code dominates initial work. Virtualize genuinely large lists when rendering/count is proven. Memoize only when profiling shows expensive, avoidable renders and stable props; indiscriminate memoization adds comparison/memory complexity. Stabilize state boundaries and avoid global updates that rerender unrelated UI. For SSR/Next.js, separate server data latency from client hydration; stream/suspend only with correct loading, cache, and SEO semantics.

Do not optimize CWV by hiding content, delaying required work past the measurement point, disabling analytics/error handling without replacement, or reducing quality without product approval.
