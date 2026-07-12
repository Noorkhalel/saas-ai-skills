# API Security (Phase 6)

Aligned to the OWASP API Security Top 10. APIs concentrate risk because they expose data and operations directly, often to authenticated clients that the server must not trust. Audit every endpoint, not a sample — one unprotected route is the breach.

## REST

**Authentication & authorization per endpoint** (API1 & API5)
- Every endpoint states its required auth. Deny-by-default: is there a global auth middleware with an explicit public allowlist, or is auth applied per-route (one forgotten route = open)?
- **BOLA / IDOR (API1, the top API risk):** object accessed by client-supplied id without an ownership/tenancy check on the query. Trace every `:id`, every nested resource, every batch endpoint. → `auth.md`
- **BFLA (API5):** function-level — a normal user reaching an admin/privileged operation because the check is only on the "admin" UI route, not the operation.

**Mass assignment (API6)**
- Endpoint binds the whole request body to a model (`update(req.body)`, `create({...req.body})`). Attacker adds `role`, `isAdmin`, `credits`, `org_id`, `verified`. Fix: explicit allowlist of writable fields (DTO / serializer / `pick`).

**Excessive data exposure (API3)**
- Response serializes the full ORM object — password hash, internal flags, other users' fields, PII — relying on the *client* to hide them. Fix: explicit response DTOs; never `return user` raw.
- Over-broad list endpoints returning more than the caller may see.

**Resource exhaustion & rate limiting (API4)**
- No rate limiting → credential stuffing, scraping, brute force, cost-amplification. No pagination caps (`?limit=100000`), no max page size, unbounded `include`/expansion, no request-size/upload limits, no query timeout. Each is a DoS or data-harvest lever.

**Input validation & injection (API8/A03)**
- Every parameter validated for type, range, format, and length at the boundary. Untrusted input into queries/commands → `secure-coding.md`, `database.md`.
- Filtering/sorting: `?sort=`, `?filter[field]=` reaching a query builder or ORDER BY needs an allowlist (injection + unintended-field exposure).

**Other**
- Verbose errors leaking stack traces/SQL (A05, A09) → `secure-coding.md`.
- CORS: `Access-Control-Allow-Origin: *` with credentials, or reflecting the request origin, defeats same-origin protection.
- Missing security headers on sensitive responses (HSTS, `X-Content-Type-Options`, CSP where HTML is served).
- HTTP methods: state-changing operations on GET (CSRF, caching, logging of parameters).
- Improper inventory (API9): undocumented/legacy/`/v1` endpoints and debug routes still live.

## GraphQL

- **Introspection** enabled in production — hands attackers the full schema. Disable or restrict.
- **Query depth / complexity** unbounded → a nested query is a DoS. Enforce depth and cost limits.
- **Batching abuse** → aliased/batched queries bypass per-request rate limits and enable brute force (many login mutations in one request). Rate-limit by operation cost, not request count.
- **Authorization at the resolver, not the gateway** — every field/resolver that returns sensitive data must check authz; a single global check misses field-level access. IDOR and over-exposure hide in individual resolvers.
- **Field-level data exposure:** the graph makes over-fetching easy — an authorized user traversing to another tenant's nodes.

## gRPC

- TLS/mTLS actually enforced (not `insecure` channel credentials in prod).
- Per-method authorization interceptor, deny-by-default; check every RPC, including reflection and health endpoints.
- Message size limits set (default-unbounded → DoS).
- Input validation on message fields as with REST.

## Webhooks (inbound)

- Signature verification on every inbound webhook (Stripe/GitHub/etc. sign payloads) — an unauthenticated webhook receiver that mutates state is an open endpoint. Verify the signature *before* processing, using the raw body and constant-time compare.
- Replay protection (timestamp + nonce); idempotency on side effects.

## Reporting

Per finding: the endpoint and method, the OWASP API category, the exact malicious request, the code path proving the gap, and the fix (add authz predicate, DTO allowlist, rate limit, depth cap). Because APIs reward completeness, state your coverage: "audited all 18 REST routes and 6 resolvers; BOLA check present on all but the two below."
