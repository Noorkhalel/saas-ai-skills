# API Architecture

Read this when defining the API style, contracts, and conventions (Phase 3 API boundaries, Phase 4 backend recommendation). The public API is a product contract: cheap to add to, expensive to change, nearly impossible to take back — design it with the same conservatism as the schema.

## Style decision

**Default: REST/JSON over HTTPS.** Universally consumable, cacheable, debuggable with curl, understood by every tool and developer. Choose something else only when its specific problem exists:

- **GraphQL** — when *many differently-shaped clients* (web + mobile + partners) each need different slices of a rich object graph, and you're prepared to own its costs: query cost-limiting/depth-limiting (an unbounded query is a DoS vector), cache complexity, N+1 resolution (dataloaders), and schema governance. One first-party web client is not a GraphQL justification.
- **gRPC** — internal service-to-service calls where you control both ends and want contract-first codegen + performance; pair with gateway translation if browsers must reach it. Rarely the public API.
- **Webhooks (outbound)** — whenever third parties need to know your events. Design requirements: signed payloads (HMAC), retries with backoff, per-endpoint failure isolation, event type versioning, and a redelivery/replay UI eventually. Deliver from a queue, never inline in the request that caused the event.
- **Realtime (WebSocket/SSE)** — when the product needs push (collab, chat, live dashboards). SSE for one-way feeds is far cheaper operationally than full WebSockets. Note the scaling shape: sticky/stateful connections change the deployment story (see `cloud.md`).

Hybrids are normal: REST public API + gRPC internal + webhooks outbound. Name each surface and its consumers in the plan.

## REST conventions

Fix these once, project-wide, in the plan — inconsistency here is death by a thousand cuts:

- **Resources, not verbs:** `GET/POST /orders`, `GET/PATCH/DELETE /orders/{id}`; sub-resources for containment (`/orders/{id}/items`); actions that aren't CRUD get an explicit action sub-resource (`POST /orders/{id}/cancel`) rather than pretending.
- **Status codes with conviction:** 200/201/204 success; 400 malformed; 401 unauthenticated; 403 forbidden; **404 for both "missing" and "not yours"** (403 on foreign resources confirms existence — enumeration leak); 409 conflict; 422 semantic validation; 429 rate limited; 5xx = our fault. Never 200-with-error-body.
- **One error envelope everywhere**, RFC 7807-style: `{ "type", "title", "detail", "status", "errors": [{field, message}] }`. Machine-readable `type`, human-readable `detail`, field-level validation errors. Internal exception text never leaks into `detail`.
- **Pagination: cursor-based by default** (stable under concurrent writes, no deep-offset cost); offset pagination only for small, admin-ish lists. Return `next_cursor` + `has_more`; document a max page size and enforce it.
- **Filtering/sorting** via query params with an allowlist — arbitrary field filtering is an accidental query-planner API and an index-miss generator.
- **Idempotency:** clients send `Idempotency-Key` on unsafe mutations (payments, order creation); server stores key → response for a window and replays it on retry. Non-negotiable for anything money-adjacent; cheap insurance everywhere else. PUT/DELETE should be naturally idempotent.
- **Rate limiting** at the edge, keyed per token *and* per tenant (see noisy neighbors, `saas.md`), returning 429 + `Retry-After`. Tiered limits are a plan entitlement.

## Contracts and versioning

- **Contract-first with OpenAPI** (or GraphQL SDL / proto files): the spec is reviewed like code, generates docs and clients, and drives contract tests. This is what keeps frontend/backend/partner teams unblocked and honest.
- **Versioning stance for the plan:** URL-path major versions (`/v1/`) for the public API — visible, cacheable, unambiguous. Inside a version, changes are **additive only**: new optional fields and endpoints are fine; removing/renaming/retyping is a new major version. Clients must ignore unknown fields (document it).
- Aim to never ship `/v2`. Version bumps are a migration campaign with deprecation headers, comms, and a sunset schedule (`Deprecation`/`Sunset` headers, dashboards of who's still on v1). The plan should state the deprecation policy *before* the first version ships.
- **Internal APIs** (module-to-module, service-to-service) don't need this ceremony — they need compatibility only across one deploy window; keep them coarse and few (see `styles.md` on chatty chains).

## Cross-cutting requirements

Name these in the plan's API section — they're where API designs actually fail in production:

- **AuthN/AuthZ on every endpoint by default** — auth middleware applied globally with explicit opt-*out* for public routes, never opt-in per route; object-level authorization inside handlers (`security.md`).
- **Validation at the boundary:** every request body/param validated against a schema before touching domain logic; unknown-field policy stated.
- **Timeouts, retries, and budgets for outbound calls** the API makes: every remote call has a timeout; retries only on idempotent operations, with backoff + jitter; a slow dependency must degrade (circuit-break, fallback) rather than exhaust your worker pool — one chatty upstream can take down the whole API.
- **Observability per request:** request id issued at the edge, propagated through logs and downstream calls, returned in error responses so support tickets can be traced.
- **Payload discipline:** response size limits, no unbounded arrays (paginate), no accidental serialization of internal fields (explicit response DTOs/serializers — ORM-model-to-JSON passthrough is how internal columns and other tenants' joins leak).
