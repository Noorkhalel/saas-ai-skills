# Security Architecture

Read this for the Authentication & Authorization and Security Considerations sections of every plan, and in depth when the system holds sensitive data or the user asks for security architecture. Security designed in costs a meeting; security retrofitted costs a quarter — the plan is where it's cheap.

## Threat modeling (lightweight, always)

Every plan does at least this much — it takes ten minutes on paper:

1. **Crown jewels:** what data/capability would hurt most if stolen, altered, or destroyed? (Customer PII, credentials, payment data, tenant business data, the ability to send email as you…)
2. **Actors:** anonymous internet, authenticated users, *other tenants* (in SaaS the most important adversary class), malicious insiders / compromised support accounts, compromised dependencies.
3. **Walk the diagram:** for each trust boundary in the Phase 3 component diagram (internet→edge, app→DB, app→third parties, webhook receivers, admin panel), run the STRIDE prompts — spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege — and note what applies.
4. **Output:** the top 5 risks by likelihood × impact, each with a mitigation that appears somewhere concrete in the plan (a component, a control, a roadmap item). Generic risk lists that could describe any app signal that no modeling happened.

## Authentication

- **Buy or adopt, don't invent.** Managed identity (Auth0/Cognito/Entra/Firebase Auth) or a battle-tested framework library. Hand-rolled auth is the highest-frequency source of catastrophic bugs in small-team systems. The plan names the provider/library and what it covers.
- **Session model — pick deliberately:** server-side sessions (opaque cookie, revocable, simple — right default for first-party web apps) vs. short-lived JWT access token + rotating refresh token (right for mobile/SPA/third-party API access; JWTs are *not revocable* before expiry, so keep them short and plan a revocation path for logout/compromise). Cookies carrying sessions: `HttpOnly`, `Secure`, `SameSite` — which also largely answers CSRF; token-in-header APIs need CORS discipline instead.
- **Table stakes to state in the plan:** password hashing with argon2id/bcrypt (never fast hashes), MFA at least TOTP (mandatory for admin roles), OAuth/OIDC social/enterprise login where the market expects it, and **SSO/SAML flagged early for B2B** — enterprise deals require it and it touches the org model (`saas.md`).
- **The forgotten attack surface is account lifecycle:** password reset (single-use, expiring, no user enumeration in responses), email change (confirm both addresses), signup (rate-limited, verified), session invalidation on password change. These flows get breached more than login does — put them in scope explicitly.
- Service-to-service and machine auth: scoped API keys or client-credential tokens, rotatable, least-privilege, never a shared god-key.

## Authorization

- **One enforcement chokepoint** — middleware/policy layer where every request passes through membership + permission checks; deny by default; public endpoints are the explicit exceptions. "Each handler remembers to check" is the design that produces IDOR.
- **Object-level checks are the ones that matter:** role checks answer "may members do X?"; the breach happens at "may *this* member do X to *this* resource?" (`GET /invoices/812` — is 812 in your tenant? yours?). Every resource fetch by id carries an ownership/tenancy predicate — by construction (RLS, scoped repositories — `saas.md`), not by memory.
- **RBAC model:** roles on the membership (per-org), 3–4 fixed roles first, permission-set indirection so custom roles can come later (`saas.md`). ABAC (attribute rules) only when RBAC demonstrably can't express a requirement.
- Admin/support access: separate surface, strongest auth (MFA required), impersonation with audit trail rather than shared credentials.

## Secrets management

- No secrets in the repo, in images, or in client-delivered code — env-injected at runtime from a secrets manager (AWS Secrets Manager / Vault / platform equivalent, see `cloud.md`); `.env` files are a local-dev convenience only.
- Per-environment secrets (staging never holds prod credentials); least-privilege DB users and cloud roles per service; rotation is a *designed path* (dual-valid window) not an emergency procedure; anything ever committed to git history is burned — rotate, don't delete.
- Log/error-tracker hygiene: scrub tokens, passwords, PII from logs at the framework level; error trackers get sanitized payloads.

## OWASP-driven design controls

The Top 10, translated into architecture decisions (most are one deliberate choice, made once):

| Risk | Architectural control in the plan |
|------|-----------------------------------|
| Broken access control | Chokepoint authz + object-level predicates (above) — the #1 real-world risk |
| Injection | Parameterized queries only (ORM/query builder); schema validation at every boundary; no string-built shell/SQL |
| Cryptographic failures | TLS everywhere (edge + internal where feasible); at-rest encryption on DB, storage, backups; argon2id for passwords; no homemade crypto |
| Insecure design | The threat model above; abuse cases alongside use cases (what does a hostile user do with this feature?) |
| Security misconfiguration | IaC-defined infrastructure (reviewable), locked-down defaults, no debug endpoints in prod, security headers (CSP, HSTS) at the edge |
| Vulnerable components | Lockfiles + automated dependency scanning (Dependabot/renovate) in CI from day one |
| AuthN failures | Managed auth, MFA, rate-limited auth endpoints, breached-password checks |
| Data integrity failures | Signed webhooks (in *and* out), verified artifacts in CI/CD, no unsafe deserialization of untrusted input |
| Logging & monitoring failures | Auth events, permission denials, and admin actions audit-logged (append-only); alerting on anomalies (login-failure spikes) |
| SSRF | Any user-supplied URL fetch goes through an allowlisting proxy; block internal ranges/metadata endpoints |

## Data protection and compliance

- **PII inventory in the plan:** which tables/fields hold personal data — this drives encryption choices, access controls, retention, and residency. You can't protect what you haven't listed.
- Retention and deletion policy per data class; user data export + deletion flows (GDPR/CCPA make these product features, not afterthoughts — `saas.md` offboarding).
- Compliance flags to raise early because they bend the architecture: **HIPAA** (BAAs, encryption, audit trails), **PCI** (keep card data out of scope entirely — provider-hosted payment fields), **SOC 2** (audit logging, access reviews, change management — mostly process, but the logging is architectural), data residency (region pinning; may force the tenancy model, `saas.md`).
- Backups inherit the same protection as production data: encrypted, access-controlled, and included in the deletion story.
