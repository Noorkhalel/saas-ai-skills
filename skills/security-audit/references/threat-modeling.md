# Threat Modeling (Phase 2)

The threat model is not paperwork — it's how you decide *where to look hardest* in the phases that follow. A good model turns "audit everything" into "these three boundaries are where an attacker gets in, trace those first." Do it fast and use it to direct the deep review.

## The four questions

1. **What are we building?** — the system, its data, its actors. (Phase 1 gave you this.)
2. **What can go wrong?** — STRIDE per boundary, below.
3. **What are we going to do about it?** — becomes your findings and remediation.
4. **Did we do a good job?** — coverage statement in the report.

## Enumerate the model

**Assets** — what an attacker wants or what breaks the business: user PII, credentials/password hashes, payment data, session tokens, API keys, internal documents, the ability to act as another user/tenant, availability of the service, integrity of financial records. Rank them — the crown jewels focus the review.

**Actors and privilege levels** — anonymous internet user, authenticated user, tenant admin, platform admin, internal service/service-account, CI pipeline, third-party integration. For each finding, ask which actor can reach it; "unauthenticated" changes severity dramatically.

**Trust boundaries** — every place data crosses from less-trusted to more-trusted: internet→app, app→database, app→internal service, user-content→renderer, PR-author→CI-pipeline, tenant→tenant, LLM-output→tool/sink. Vulnerabilities cluster on these lines. Draw them (a data-flow diagram in text is fine).

**Entry points** — enumerate *every* one, not just the obvious HTTP routes: REST/GraphQL/gRPC endpoints, WebSocket handlers, webhook receivers, file/upload handlers, queue/topic consumers, scheduled jobs, admin interfaces, CLI/management commands, deserialization points, and any place that reads a header/cookie/env you don't fully control. An unlisted entry point is an unaudited one.

**Data flows** — follow untrusted input from each entry point inward until it hits a sink (query, command, filesystem, response, template, tool call). This trace *is* your evidence in later phases.

**External dependencies** — third-party APIs, identity providers, payment processors, object storage, message brokers, and the trust you place in each (do you validate their responses? is their webhook authenticated?).

**Sensitive-data locations** — where the crown jewels live at rest and in transit: DB columns, caches, logs, backups, object storage, LLM context windows, vector stores.

## STRIDE at each boundary

Apply per trust boundary to find threat classes, then verify in the code during the domain phases. STRIDE is a *prompt for where to look*, not a finding by itself.

| Threat | Question at this boundary | Where it's verified |
|--------|---------------------------|---------------------|
| **S**poofing | Can an attacker claim to be someone/something they aren't? | Authentication (`auth.md`): weak/absent authn, forgeable tokens, spoofable service identity |
| **T**ampering | Can they modify data, requests, or code in transit or at rest? | Integrity: mass assignment, unsigned tokens/webhooks, missing integrity checks (`secure-coding.md`, `cicd.md`) |
| **R**epudiation | Can they deny an action because nothing recorded it? | Logging/audit: missing security event logging, mutable logs (`owasp.md` A09) |
| **I**nformation disclosure | Can they read data they shouldn't? | Authorization/IDOR, verbose errors, over-fetching, secrets exposure (`auth.md`, `api.md`, `secure-coding.md`) |
| **D**enial of service | Can they exhaust resources or take it down? | Missing rate limits, unbounded queries/uploads, ReDoS, GraphQL depth (`api.md`) |
| **E**levation of privilege | Can they gain rights they shouldn't have? | Authz bypass, privilege escalation, container escape, over-broad IAM (`auth.md`, `containers.md`, `cloud.md`) |

## Multi-tenancy — model it explicitly

If the system is multi-tenant (SaaS with organizations/workspaces/accounts), tenant isolation is usually the highest-impact boundary. Record:

- **The tenant identifier** and where it comes from — it must derive from the *authenticated session*, never from a client-supplied parameter/body/header.
- **The isolation mechanism** — per-query `WHERE org_id = ?` discipline (fragile, one miss = leak), a shared query chokepoint, or database RLS (strongest). Note which, because it sets how you audit every query.
- **The leak channels** — cross-tenant leakage hides in caches keyed without tenant, background jobs that lose tenant context, search indexes, aggregate/reporting queries, file storage paths, and connection-pool RLS-context bleed. List them as things to check in Phase 5/7.

## Output of this phase

A compact model that feeds the report's Threat Model section and, more importantly, a *prioritized list of boundaries and entry points to audit deeply*. If you learned the system has one internet-facing GraphQL endpoint, a Stripe webhook, and an S3 upload path, those three are where you spend your attention — not evenly across 200 files.
