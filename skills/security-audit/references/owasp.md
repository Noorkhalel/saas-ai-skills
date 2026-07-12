# OWASP Top 10 Review (Phase 4)

Use the Top 10 as a coverage map — a checklist that every finding maps back to a named category, and a prompt to make sure you didn't skip a whole class. It's organized by prevalence and impact from real breach data, so working it top-to-bottom roughly tracks where risk actually concentrates. Cross-references point to the reference file where each class is hunted in depth.

## A01 — Broken Access Control (the #1 category)

The highest-yield area. Authentication tells you *who*; access control decides *whether they may* — and that check is what's usually missing.

- **Object-level (IDOR):** handler fetches by client-supplied id with no ownership/tenancy predicate. Check *every* endpoint that takes an id. → `auth.md`, `api.md`
- **Function-level:** admin/mutation endpoints protected only by the UI hiding the button; opt-in per-route middleware where one forgotten route is a hole.
- **Tenant isolation:** every tenant-scoped query filtered by the *session's* tenant. → `auth.md`, `database.md`
- **Other:** CORS misconfiguration allowing untrusted origins with credentials; force-browsing to authenticated pages; JWT/cookie tampering to change identity or role; 403-vs-404 leaking resource existence.

## A02 — Cryptographic Failures

Sensitive data exposed through weak or missing crypto. Password hashing (fast hash = finding), data in transit over HTTP, disabled TLS verification, weak ciphers/modes (ECB, static IV), hardcoded keys, `Math.random()` for tokens, secrets at rest unencrypted. → `secure-coding.md` (Cryptography), `database.md` (encryption at rest)

## A03 — Injection

SQL, NoSQL, command, LDAP, XPath, template (SSTI), and XSS (which OWASP folds here). Untrusted input reaching an interpreter without parameterization/escaping. → `secure-coding.md` (Injection, Output encoding), `database.md`

## A04 — Insecure Design

Flaws in the design, not the implementation — no fix at the code line because the *approach* is wrong. Missing rate limiting by design, no defense against automated abuse, trust in client-side controls, business-logic flaws (negative quantities, race on limited resource, workflow bypass), missing segmentation. Flag these as design findings with an architectural fix, and check the threat model (`threat-modeling.md`) — insecure design shows up as an unmitigated STRIDE threat.

## A05 — Security Misconfiguration

Default credentials, debug mode in production, unnecessary features/ports/services enabled, verbose errors, missing hardening headers, over-permissive cloud/container defaults, unpatched sample apps. → `secure-coding.md` (Secrets & configuration), `containers.md`, `cloud.md`

## A06 — Vulnerable & Outdated Components

Known-CVE dependencies, unmaintained/abandoned packages, outdated runtimes, and transitive risk. → `dependencies.md`

## A07 — Identification & Authentication Failures

Weak passwords permitted, credential stuffing (no rate limiting/lockout), session fixation, weak/absent MFA, insecure session tokens, JWT flaws (`decode` vs `verify`, `alg:none`, key confusion), predictable reset tokens, user enumeration. → `auth.md`

## A08 — Software & Data Integrity Failures

Untrusted deserialization; unsigned/unverified auto-updates; CI/CD pulling unpinned dependencies or actions; artifacts built from untrusted input without integrity verification. → `secure-coding.md` (deserialization), `cicd.md`, `dependencies.md`

## A09 — Security Logging & Monitoring Failures

Security events (login success/failure, access-control failures, high-value transactions, admin actions) not logged; logs without enough context to investigate; logs that leak sensitive data (a failure in both directions); no alerting on attack patterns; logs mutable by the app. Verify a breach would actually be *detectable* and *investigable*.

## A10 — Server-Side Request Forgery (SSRF)

Server fetches a user-controlled URL and can be steered at internal services or cloud metadata. → `secure-coding.md` (SSRF)

## Using this phase

Walk the ten categories against the target and, for each, either point to a finding you filed under it or record "checked — clean" with what you verified. This makes the audit's coverage legible: a reader can see you considered every class, not just the ones that happened to have bugs. Note the OWASP category tag on each finding in the report so remediation can be grouped and so the team can map to their own OWASP-based requirements.

For AI-integrated systems, also apply the **OWASP Top 10 for LLM Applications** — see `ai-security.md`. For APIs specifically, the **OWASP API Security Top 10** overlaps but adds API-specific classes (excessive data exposure, lack of resources & rate limiting, mass assignment) — see `api.md`.
