# Security Review Checklist (Phase 4)

OWASP-driven review, organized by where vulnerabilities actually live in code. For each class: the pattern to hunt, how to verify it's real (trace source → sink), and the fix to recommend. Severity default: reachable-with-untrusted-input = CRITICAL; requires-authenticated-user or unclear reachability = HIGH with the uncertainty stated.

**First, map trust:** which values in this code originate outside (params, body, headers, cookies, file contents/names, webhook payloads, third-party API responses, DB values that users wrote earlier)? Every finding below is about an untrusted value reaching a sensitive sink. Second-order flows count: stored-then-rendered is still XSS; stored-then-queried is still injection.

## Injection

- **SQL injection:** untrusted input concatenated/interpolated into query strings — template literals with `${}`, `+`, `%s`/`format`, f-strings into `raw()`/`execute()`. ORMs don't save you at their escape hatches (`whereRaw`, `$queryRawUnsafe`, `extra()`, native `query()`). Dynamic identifiers (ORDER BY column, table names) can't be parameterized — require allowlists. Fix: parameterized queries everywhere; allowlist identifiers.
- **Command injection:** input reaching `exec`/`system`/`spawn`-with-`shell:true`/backticks/`os.system`. Fix: argument-array APIs, no shell, allowlist binaries. Also: input in `eval`, `Function()`, deserializers (`pickle`, `ObjectInputStream`, YAML full load) — untrusted deserialization is remote code execution.
- **Path traversal:** user input joined into filesystem paths (`path.join(base, req.params.name)` — `../../etc/passwd`) or archive entries extracted unchecked (zip-slip). Fix: canonicalize then verify the result is inside the base; treat uploaded filenames as hostile (generate your own).
- **SSRF:** server fetching a user-supplied URL (webhooks, importers, image proxies, PDF renderers). Verify: can it reach internal addresses/cloud metadata (`169.254.169.254`)? Fix: allowlist hosts/schemes, block private ranges *after* DNS resolution, don't follow redirects blindly.

## XSS & browser-side

- **Sinks:** `innerHTML`, `outerHTML`, `document.write`, `dangerouslySetInnerHTML`, `v-html`, Angular `bypassSecurityTrust*`, template-engine escape-off filters (`| safe`, `<%- %>`, `{{{ }}}`), attribute/URL contexts (`href={userUrl}` — `javascript:` URLs), and user HTML "sanitized" by regex (use a real sanitizer: DOMPurify-class).
- Framework auto-escaping covers the default path — the findings live at the escape hatches, so grep for them specifically.
- **CSRF:** cookie-authenticated state-changing endpoints without CSRF token/`SameSite` protection; GET handlers with side effects. Token-in-header APIs are inherently safer — but then check CORS config (`origin: *` with credentials, or reflecting the request origin).

## Authentication

- **Password handling:** anything but a slow adaptive hash (bcrypt/argon2id) is a finding — MD5/SHA-family = CRITICAL; plaintext comparisons; password/secret logged or in error payloads; missing rate limiting on login/reset endpoints (credential stuffing).
- **Session issues:** session id not regenerated on login (fixation); cookies missing `HttpOnly`/`Secure`/`SameSite`; sessions never expiring; session data trusted from the client (unsigned cookies/localStorage "session").
- **JWT problems:** `alg: none` or algorithm not pinned (`verify` accepting HS256 *and* RS256 — key-confusion); `decode()` used where `verify()` was meant (signature never checked — surprisingly common, always CRITICAL); no expiry or days-long tokens with no revocation story; secrets weak/hardcoded; sensitive data in the (readable) payload; tokens in localStorage when HttpOnly cookies were feasible (XSS → token theft).
- **Reset/signup flows:** predictable or non-expiring reset tokens; reset response revealing whether the email exists (enumeration); email change without confirming the old address; unverified email trusted for identity merging.

## Authorization

The highest-yield section of most reviews — authn tells you *who*, these bugs skip the *may they*:

- **Missing object-level checks (IDOR):** handler fetches by client-supplied id (`GET /invoices/:id`) with no ownership/tenancy predicate on the query. Verify by reading the actual query/ORM call — is there a `WHERE user_id/org_id = session...`? This is OWASP's #1 for a reason; check *every* endpoint that takes an id.
- **Missing function-level checks:** admin/mutation endpoints relying on the UI hiding the button; authz middleware applied per-route opt-in (one forgotten route = hole) instead of global-with-explicit-public-list.
- **Privilege escalation:** role/`is_admin`/`org_id` accepted from request bodies into updates (mass assignment — check what the update actually allows through); role checked from a client-controlled claim without server-side verification.
- **Tenant isolation:** see `data.md` — every tenant-scoped query filters by the *session's* tenant, never a client-supplied one; RLS or chokepoint enforcement, not per-endpoint discipline.
- 403 vs 404: returning 403 on others' resource ids confirms existence — prefer 404 parity.

## Data security

- **Secrets in code/config-in-repo:** API keys, DB URLs with passwords, JWT secrets, encryption keys — as literals, defaults (`process.env.SECRET || "dev-secret"` ships the fallback), or committed `.env`. Any secret that has ever been committed is burned: recommend rotation, not just removal.
- **Sensitive data leaks:** passwords/tokens/PII in logs; full user/ORM objects serialized to responses (password hash, internal flags along for the ride — require explicit response DTOs); verbose errors with stack traces/SQL to clients; sensitive data in URLs (logged everywhere).
- **Crypto misuse:** homemade crypto or ECB mode; static IVs/nonces; `Math.random()` for tokens (use CSPRNG); comparing secrets with `==` (timing — use constant-time compare); "encrypted" meaning base64.
- **Transport/storage:** HTTP for anything authenticated; TLS verification disabled (`rejectUnauthorized: false`, `verify=False`) — that's not a config nit, it's MITM-by-design.

## Reporting security findings

State the OWASP category, the source→sink trace as evidence, exploitability conditions, and the fix. If the code is clean in a category you checked, say so ("parameterized queries throughout; no injection surface found") — a security review's value includes what was *ruled out*. Uncertain reachability: report as HIGH with the open question, never silently drop.
