# Security, reliability, scale, and release

## Security review prompts

Build an auth matrix of principal, credential, tenant, resource, action, policy, and denied behavior. Test unauthenticated, wrong-tenant, wrong-role, revoked credential, resource-ID guessing, hidden-field mass assignment, forged webhook, malformed/oversized input, replay, and rate-limit cases. Enforce authorization server side for every object/function/property; expose only allowed fields. Validate structure, types, ranges, formats, and business state; parameterize data access; constrain outbound URLs and metadata access to mitigate SSRF.

Review JWT validation (issuer, audience, expiry/not-before, signature/key rotation, algorithm restrictions, claims) and OAuth2/OIDC flow, scopes, consent, redirect URIs, token audience, refresh/revocation, and client type. Use short-lived credentials/scopes, key rotation, TLS, secure secret storage, request IDs, redacted structured logs, and privacy-aware telemetry. CORS is a browser policy, not an API authorization mechanism; CSRF matters for browser cookie/session authentication. Rate limits need identity/key/IP/tenant dimensions, response headers/error semantics, fairness, and a load-shedding policy.

For a Supabase Edge Function API, verify JWT configuration and server-side authorization, RLS-enforced database paths, use of `auth.uid()`/claims, secret isolation, CORS/preflight policy, per-function input/output limits, safe service-role use, storage/object authorization, and tenant context in background work. An Edge Function can bypass RLS when it uses a service role; make that privilege narrow and explicit rather than assuming Supabase Auth protects every query.

## Reliability and performance

Use deadlines propagated to dependencies, bounded server/queue/pool concurrency, cancellation, circuit breaking/load shedding, and capped retries with jitter. Set retries from idempotency and downstream capacity, not hope. Define cache key scope (tenant/principal/roles/locale/version), TTL/freshness, invalidation, negative-cache policy, stampede protection, and fallback. Monitor p50/p95/p99, errors, saturation, request/response bytes, dependency time, cache behavior, queue depth/age, rate-limit outcomes, auth denies, and protocol-specific reconnect/retry/DLQ metrics.

For payment APIs, distinguish an accepted request from an authorized/captured/settled payment state. Require idempotency keys and payload fingerprints for create/confirm/refund operations; retain/replay compatible results, reject mismatched reuse, and make provider webhooks idempotent. Do not retry a payment request or webhook side effect until the provider contract and local state transition make double charge or double refund impossible.

## Compatibility and release gates

Classify changes: additive fields/operations may still break strict clients; behavior/default/enum/validation/auth/error changes are potentially breaking; removals/renames/type/semantic changes are breaking. Inventory consumers through gateway/SDK/operation telemetry. Publish changelog/migration examples, ship dual behavior or an adapter when needed, set deprecation/sunset dates, and measure adoption before removal.

Validate specs with Spectral/OpenAPI tooling or proto/AsyncAPI validators; contract-test providers and consumers; use Schemathesis/fuzzing for input safety; run authorization negatives, regression/integration, retry/idempotency, load/soak, fault-injection, and SDK-generation tests. Canary behind version/feature gates; predefine error/latency/security abort thresholds and a rollback or forward-repair path.
