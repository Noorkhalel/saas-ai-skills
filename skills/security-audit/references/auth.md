# Authentication & Authorization (Phase 5)

The highest-yield phase of most audits. Authentication = *who you are*; authorization = *what you may do*. The severe, common bugs are in authorization — code that authenticates a user perfectly and then never checks whether *this* user may touch *this* object.

## Authentication (authn)

**Password handling**
- Storage: bcrypt/scrypt/argon2id only. MD5/SHA-* = CRITICAL, plaintext = CRITICAL, reversible "encryption" of passwords = CRITICAL. Fast hashes are crackable offline.
- Comparison: constant-time; never `==` on a hash or token (timing oracle).
- Policy: minimum length over complexity theater; check against breached-password lists ideally; no silent truncation.
- Rate limiting / lockout on login and reset — absence enables credential stuffing (MEDIUM–HIGH depending on exposure).

**Sessions**
- Session id regenerated on login (else session fixation) and invalidated on logout and password change.
- Cookies: `HttpOnly` (blocks JS theft), `Secure` (HTTPS only), `SameSite` (CSRF defense). Missing on a session cookie is a real finding.
- Expiry: idle and absolute timeouts; server-side revocation possible. Session data never trusted from an unsigned client cookie or localStorage.

**JWT** (a dense source of CRITICALs)
- `decode()` used where `verify()` was meant — signature never checked, any forged token accepted. **Always CRITICAL.**
- `alg:none` accepted, or algorithm not pinned (`verify` accepting both HS256 and RS256 → key-confusion attack using the public key as an HMAC secret).
- Weak/hardcoded/default signing secret; secret in code.
- No expiry, or multi-day tokens with no revocation story.
- Sensitive data in the payload (it's readable — base64, not encrypted).
- Token in localStorage where an HttpOnly cookie was feasible (XSS → token theft).

**MFA & reset/signup flows**
- MFA absent on high-value/admin accounts, or bypassable (recovery flow skips it).
- Reset tokens predictable, non-expiring, single-use not enforced, or reused across requests.
- Reset/login response reveals whether an email exists (user enumeration) — keep responses and timing uniform.
- Email change without confirming the old address; unverified email trusted to merge/claim an identity.

## Authorization (authz) — where the severe bugs are

**Object-level access control (IDOR)** — OWASP's #1
- Pattern: handler fetches by a client-supplied id (`GET /invoices/:id`, `GET /users/:id/documents`) with no ownership/tenancy predicate on the query.
- **Verify by reading the actual query/ORM call:** is there a `WHERE user_id = session.user` / `org_id = session.org`? A `findById(req.params.id)` with the id straight from the client and no scope is the bug. Check *every* endpoint that accepts an id — including nested ones and "internal" ones.
- Also applies to updates/deletes and to indirect references (a filename, an S3 key, a batch of ids).

**Function-level access control**
- Admin/privileged endpoints relying on the UI to hide them; authorization applied opt-in per route (one forgotten `@requires_admin` = hole) instead of deny-by-default with an explicit public allowlist.
- Vertical escalation: a normal user reaching an admin function. Horizontal: a user reaching a peer's data (IDOR).

**Privilege escalation & mass assignment**
- Role / `is_admin` / `org_id` / `verified` accepted from a request body into an update or create (`User.update(req.body)`, `Object.assign(user, req.body)`, Rails/Django/Laravel unguarded bulk assign). Check what the update *actually lets through* — an allowlist of updatable fields is the fix.
- Role read from a client-controlled claim (a header, a JWT the client can re-sign, a cookie) without server verification.

## Tenant isolation (multi-tenant SaaS)

Usually the highest-impact boundary in a SaaS audit — a miss leaks one customer's data to another.

- **Tenant id must come from the authenticated session, never from the request.** A `?org_id=` / `X-Org-Id` / body `org_id` that the server trusts is a cross-tenant read. The session's tenant is authoritative.
- **Every tenant-scoped query filters by the session's tenant.** Per-query `WHERE org_id = ?` discipline is fragile (one forgotten query = leak). Prefer a chokepoint (a scoped repository/base query) or database **RLS** (strongest — the DB enforces it even if app code forgets).
- **RLS correctness** (Postgres/Supabase): policies exist on *every* tenant table, `ENABLE ROW LEVEL SECURITY` *and* `FORCE` where needed, the tenant context (`SET app.current_org`) is set per-request and — critically — **reset on pooled connections** (a leaked `SET` bleeds one request's tenant into the next). `USING` vs `WITH CHECK` both present so writes can't escape the tenant. A `SECURITY DEFINER` function or a service-role key that bypasses RLS is a hole if reachable with user input.
- **Leak channels beyond the main query:** caches keyed without tenant, background jobs that lose tenant context, search/analytics indexes, aggregate/reporting queries, exports, file-storage paths, and webhooks. List and check each.

## Reporting

For each finding: the actor who exploits it (anonymous? peer user? any authenticated user?), the exact request, the code path proving the check is missing (quote the query/handler), and the smallest fix (add the predicate, move to deny-by-default, adopt RLS). For tenant isolation, state whether the mechanism is per-query discipline (call out the systemic fragility) or enforced (RLS/chokepoint). Rule-outs count: "checked all 12 object endpoints; ownership predicate present on each" is a valuable finding.
