# GraphQL, gRPC, realtime, webhooks, and AI APIs

## GraphQL

Model a stable schema and explicit null/error semantics. Authorize at resolver/field level; apply tenant context to every resolver, DataLoader, cache, and subscription. Measure resolver-to-database calls and fix N+1 with request-scoped batching keyed by tenant/principal. Limit depth, complexity, aliases, result size, pagination, execution time, and introspection policy appropriate to exposure. Prefer persisted/allowlisted operations for public/high-scale APIs when governance benefits outweigh DX cost. Version by additive schema evolution and deprecate with usage telemetry.

## gRPC

Use `.proto` compatibility rules: never reuse field numbers; reserve removed names/numbers; add optional/new fields safely; do not change field type/meaning; version packages/services only for planned breaks. Define unary/streaming direction, deadlines, cancellation, metadata/auth propagation, error mapping/status details, retryability, flow control, max messages, and load balancing. Generated clients must not retry non-idempotent calls automatically.

## WebSocket and SSE

Specify authentication at connection and reauthorization/expiry behavior, origin policy, channel/topic authorization, message schema/version, sequencing/event ID, ordering and delivery guarantees, reconnect/resume cursor, duplicate handling, heartbeats, backpressure/buffer limits, presence semantics, rate limits, close/error codes, and observability. SSE is server-to-client HTTP streaming; state event names, IDs, `Last-Event-ID`, replay retention, keep-alive, and proxy timeout behavior. Never assume a live connection guarantees delivery.

## Webhooks and AsyncAPI

Treat callbacks as at-least-once unless a proven system says otherwise. Document event schema/version, event ID, occurrence time, ordering scope, delivery attempts, endpoint registration/verification, HMAC/signature, timestamp tolerance, replay defense, timeout, retry/backoff schedule, DLQ/failure visibility, and manual replay. Consumers must acknowledge fast, verify before processing, and be idempotent. Use AsyncAPI or equivalent to document channels, payloads, security, bindings, and consumer expectations.

## AI and streaming APIs

Bound input/context/token/output size, model/tool selection, concurrent requests, rate limits, and cost. Define cancellation, stream event schema/order (`start`, delta, tool call, completed, error), token/usage accounting, retry semantics, timeout/TTFT/total-latency SLOs, structured output validation, prompt/tool injection boundaries, tenant/privacy isolation, retention, and quality/safety regression metrics. Do not retry a request that can double bill or repeat a non-idempotent tool action without an idempotency design.
