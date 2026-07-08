# Security-Related Bug Debugging (Phase 7)

Read when the bug touches authentication, authorization, input handling, or data boundaries — including bugs that don't *look* like security bugs. Two framings matter: some bugs *are* security vulnerabilities (fix carefully, they're high-severity), and some functional bugs ("login randomly fails," "user sees wrong data") are security mechanisms misbehaving. Treat "user sees another tenant's/user's data" as an incident until proven otherwise.

## "Authentication randomly fails" / JWT issues

A top intermittent-auth report; "random" usually means *time- or instance-dependent*, not truly random:
- **Token expiry:** works then fails after N minutes → short-lived token not refreshed; the failure correlates with token age, not load. Check `exp` and the refresh path.
- **Clock skew** across instances/services: a token "not yet valid" (`nbf`) or "expired" because one server's clock differs — fails only on some instances (`references/concurrency.md`). Tell: fails on some pods/hosts, not others.
- **Key rotation / multiple instances with different secrets:** behind a load balancer, one instance signs with key A, another verifies with key B → fails ~half the time, "randomly." Check that all instances share the signing key/JWKS and that rotation keeps old keys valid during overlap.
- **`verify` vs `decode`:** `decode` never checks the signature — if the code uses it, auth is *not enforced at all* (forged tokens pass); if it recently switched to `verify` with a wrong key/alg, real tokens now fail. Either way, read which is used.
- **Algorithm/secret config:** `alg` mismatch (token HS256, verifier expects RS256), wrong/rotated secret, `alg:none` accepted. **Stateful revocation:** a token invalidated server-side (logout/ban) still accepted, or a session store that's inconsistent across instances.
- **Cookie/session:** `SameSite`/`Secure`/domain scoping dropping the cookie on some flows (cross-site, subdomain); session id not regenerated (fixation); session store (Redis) eviction dropping sessions under memory pressure → "logged out randomly."

## Authorization bugs

- **Missing object-level check (IDOR):** an endpoint fetches by client-supplied id with no ownership/tenant predicate → users reach others' data (`references/data.md` multi-tenant). Presents as "user sees data they shouldn't" — verify the query has the `WHERE owner/tenant = session...` clause; its absence is the bug and it's high-severity.
- **Broken function-level auth:** a role/permission check missing on some routes (per-route opt-in with one forgotten route), or relying on the UI hiding the control. **Privilege escalation:** role/`org_id`/`is_admin` accepted from the request body into an update (mass assignment); a client-controlled claim trusted without server verification.
- **Tenant isolation** (`references/data.md`): the highest-severity class — a missing tenant filter, a client-supplied tenant id, an RLS policy gap, or a cache key without a tenant dimension leaks across customers.

## RLS blocks valid users (Supabase/Postgres)

The inverse of a leak — legitimate access denied — but debug the same policies:
- Is a policy defined for **this operation**? A `SELECT` policy doesn't cover `INSERT/UPDATE/DELETE`; the write silently returns zero rows or errors. Missing policy = default deny.
- Is the **tenant/user context set** at query time? `auth.uid()` null (unauthenticated request path, or the JWT not passed to PostgREST), or `app.current_tenant` never `SET`. On a **pooled connection**, a session `SET` doesn't persist per request — use transaction-scoped `SET LOCAL`, else context is missing/leaked ("works in one connection, fails under pooling").
- Does the **policy predicate match the data** (comparing `auth.uid()` to the right column; a join to membership that's empty because the membership row is missing)? Read the policy and the actual row together.
- Is the app connecting as a role **subject to RLS** vs accidentally `BYPASSRLS` (leak) or lacking needed grants (block)?

## Input-handling bugs (functional symptom, security cause)

- **Missing/incorrect validation** manifesting as a crash or wrong behavior on unusual input (empty, unicode, oversized, malformed) — the functional bug and the security gap are the same missing check.
- **Injection as a "weird data" bug:** SQL injection can present as corrupted/duplicated query results or errors on names with quotes; NoSQL/operator injection (`{$gt:""}` via a JSON body) as auth bypass or odd query behavior; command injection as unexpected side effects. If untrusted input reaches a query/shell/eval sink, that's the cause — not a coincidence.
- **SSRF** as "our server makes strange outbound requests" / reaches internal hosts; **XSS** as "the page breaks / runs odd script" when user content renders unescaped; **path traversal** as reading/writing unexpected files from a user-supplied name.

## Secrets and exposure

- Secrets in code/logs/error responses/client bundles (`NEXT_PUBLIC_`, committed `.env`, a fallback default secret shipped) — if found, it's exposed; recommend rotation (a committed secret is burned) plus removal.
- A "config bug" that's actually a secret missing in one environment (auth fails in prod because the key isn't set there — falls back to a default or empty).

## Reporting

For a security-related bug, state whether it's an exposure/vuln (and its severity and blast radius) or a mechanism malfunctioning, the evidence (the missing check, the policy gap, the token/clock/key mismatch), confidence, and a fix that **fails closed** (deny on error/ambiguity, never open). Flag when a naive functional fix would *widen* the hole — e.g., "making the RLS error go away" by disabling RLS, or "fixing" a 500 with `?.` that turns it into silent unauthorized access. Recommend the regression test that asserts the *denial* path, and prevention (centralized enforcement, a test that probes cross-tenant access, secret scanning in CI).
