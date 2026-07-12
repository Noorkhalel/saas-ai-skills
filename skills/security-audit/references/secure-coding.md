# Secure Coding Review (Phase 3)

Organized by where vulnerabilities actually live: an untrusted value reaching a sensitive sink. For each class — the pattern to hunt, how to verify it's real (trace source→sink), and the fix. Severity default: reachable with untrusted input on an exposed path = CRITICAL; requires an authenticated user or unclear reachability = HIGH with the uncertainty stated.

**First, map trust.** Which values originate outside your control? Request params/body/query/headers/cookies, file contents and filenames, webhook payloads, third-party API responses, message-queue payloads, environment in shared runners, and DB values that a user wrote earlier (second-order). Every finding below is one of these reaching a sink. Stored-then-rendered is still XSS; stored-then-queried is still injection; stored-then-`exec`'d is still command injection.

## Injection

- **SQL injection:** untrusted input concatenated/interpolated into a query — template literals `${}`, string `+`, `%s`/`.format()`, f-strings into `raw()`/`execute()`. ORMs don't save you at escape hatches (`whereRaw`, `$queryRawUnsafe`, `.extra()`, `.raw()`, native `query()`). Dynamic identifiers (ORDER BY column, table name) can't be parameterized — require an allowlist. **Fix:** parameterized/prepared statements everywhere; allowlist identifiers.
- **NoSQL injection:** user object reaching a Mongo query enables operator injection (`{"$gt": ""}`, `{"$ne": null}`) — a login that does `find({user, pass: req.body.pass})` is bypassable when `pass` is an object. **Fix:** cast/validate types; disable operator interpretation on user input.
- **Command injection:** input reaching `exec`/`system`/`spawn` with `shell:true`/backticks/`os.system`/`subprocess(..., shell=True)`. **Fix:** argument-array APIs, no shell, allowlist binaries and args.
- **Code injection / unsafe deserialization:** input in `eval`, `Function()`, `pickle.loads`, `yaml.load` (full), Java `ObjectInputStream`, PHP `unserialize`, .NET `BinaryFormatter` — untrusted deserialization is remote code execution. **Fix:** safe formats (JSON), `yaml.safe_load`, signed/allowlisted types, never deserialize untrusted bytes into objects.
- **Template injection (SSTI):** user input rendered as a template (`render_template_string(user)`, Jinja/Freemarker/Velocity with user-controlled template) → RCE. **Fix:** never template user input; pass it as data to a fixed template.
- **Path traversal:** user input joined into a filesystem path (`path.join(base, req.params.name)` → `../../etc/passwd`) or archive entries extracted unchecked (zip-slip). **Fix:** canonicalize (`realpath`) then verify the result stays inside the base; generate your own filenames for uploads.
- **SSRF:** server fetching a user-supplied URL (webhooks, importers, image/PDF/link-preview fetchers). Verify it can reach internal addresses or cloud metadata (`169.254.169.254`, `metadata.google.internal`). **Fix:** allowlist hosts/schemes, resolve DNS then block private/link-local ranges, don't follow redirects blindly, drop the metadata endpoint.

## Output encoding & browser-side

- **XSS sinks:** `innerHTML`, `outerHTML`, `document.write`, `insertAdjacentHTML`, `dangerouslySetInnerHTML`, `v-html`, Angular `bypassSecurityTrust*`, template escape-off filters (`| safe`, `<%- %>`, `{{{ }}}`), attribute/URL contexts (`href={userUrl}` → `javascript:`), and "sanitized-by-regex" HTML (use a real sanitizer — DOMPurify-class). Framework auto-escaping covers the default path; findings live at the escape hatches, so grep for them.
- **CSRF:** cookie-authenticated state-changing endpoints without a CSRF token or `SameSite`; GET handlers with side effects. Header-token APIs are safer — but then check CORS (`origin: *` with credentials, or reflecting the request origin is a bypass).

## Cryptography

- **Password storage:** anything but a slow adaptive hash (bcrypt/scrypt/argon2id) is a finding — MD5/SHA-family = CRITICAL; plaintext = CRITICAL. Fast hashes crack offline in hours.
- **Weak crypto:** homemade crypto, ECB mode, static/reused IVs and nonces, hardcoded keys, `Math.random()`/`rand()` for tokens or secrets (use a CSPRNG), MD5/SHA-1 for integrity, `==` for secret comparison (timing — use constant-time compare), "encryption" that's actually base64/hex encoding.
- **TLS:** verification disabled (`rejectUnauthorized:false`, `verify=False`, `InsecureSkipVerify:true`) — MITM-by-design, not a config nit. HTTP for anything authenticated.

## Secrets & configuration

- **Secrets in code/repo:** API keys, DB URLs with passwords, JWT/signing secrets, cloud credentials as literals or defaults — `process.env.SECRET || "dev-secret"` *ships the fallback*. Committed `.env`, `terraform.tfstate` with secrets, private keys. **Any secret ever committed is burned — recommend rotation, not just removal.**
- **Unsafe defaults:** debug mode on in production (`DEBUG=True`, Flask/Django debug, verbose actuator endpoints), default/blank admin credentials, permissive CORS, directory listing, admin panels exposed, sample/test endpoints left enabled.
- **Config-driven exposure:** management ports open, cloud metadata reachable, `.git` served, source maps in prod exposing internals.

## Error handling & logging

- **Information leakage:** stack traces, SQL errors, internal paths, or framework versions returned to clients; verbose 500s. Return a generic error to the client, log detail server-side.
- **Sensitive data in logs:** passwords, tokens, full card numbers, PII, or full request bodies logged. This is a real breach vector (logs get shipped to third parties, indexed, and over-retained).
- **Swallowed security failures:** a `catch` that ignores an auth/validation error and continues; a failed signature check that logs-and-proceeds. Fail closed, not open.
- **Missing audit trail:** security-relevant events (login, privilege change, data export, admin action) not logged — see `owasp.md` A09.

## Reporting

State the class, the source→sink trace as evidence (quote the lines), the exploitability conditions, and the smallest fix. If a category is clean where you checked, say so ("parameterized queries throughout; no SQL injection surface found") — ruling things out is part of the audit's value. Uncertain reachability: report HIGH with the open question, never silently drop.
