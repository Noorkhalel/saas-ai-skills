# SaaS Architecture

Read this for any multi-tenant product: tenancy model, organization/user model, RBAC, billing, and the SaaS-specific failure modes. The tenancy model is one of the most expensive decisions in the whole system to change — treat it with the same care as the data model, because it *is* the data model.

## Multi-tenancy models

| Model | How | Choose when | Costs |
|-------|-----|-------------|-------|
| **Pooled (shared schema + `tenant_id`)** | Every tenant-owned table carries `tenant_id`; every query filters by it | Default for B2B/B2C SaaS: thousands of tenants, self-serve, cost-sensitive | Isolation is only as strong as your enforcement; noisy neighbors share resources; per-tenant backup/restore is surgery |
| **Schema-per-tenant** | One DB, one schema per tenant | Hundreds (not tens of thousands) of tenants needing stronger isolation or per-tenant customization | Migrations × N schemas; connection/catalog bloat at scale; ops tooling becomes bespoke |
| **Database-per-tenant** | Separate DB (or cluster) per tenant | Few, large, high-value tenants; compliance demanding physical isolation; per-tenant residency/BYOK | Highest cost and ops load; fleet migration orchestration; only viable with strong automation |

Hybrid is legitimate and common: pooled for the long tail, dedicated DB for enterprise tier — but only build the hybrid when the first enterprise deal demands it, not speculatively. State in the plan which model, why, and the migration story to the next tier up.

**Enforcement is the design decision that matters.** `tenant_id` columns don't isolate anything; the *mechanism* does. In order of strength:

1. **Postgres Row-Level Security** — policies filter every query by the tenant set in session context (`SET app.tenant_id`). The DB enforces isolation even when application code forgets. Strongly recommended for the pooled model on Postgres.
2. **Repository/ORM chokepoint** — a tenant-scoped data access layer that injects the filter; raw query access is forbidden by convention + lint. Weaker (bypassable) but portable.
3. **Per-endpoint discipline** — every developer remembers every time. This is not a mechanism; reject it in the plan.

Resolve tenant context at the edge (subdomain, path, token claim), validate it against the authenticated user's memberships (never trust a client-supplied tenant id alone), propagate it in request context, and set it in the DB session. Write an automated cross-tenant isolation test (user A queries tenant B's resource ids → 404/403) — put it in the roadmap's first phase.

**Tenant leak surfaces beyond the DB** — enumerate these in any SaaS plan: caches (tenant id in every cache key), search indexes (tenant filter in every query, or index-per-tenant), file/object storage (tenant-prefixed paths + scoped signed URLs), background jobs (tenant context serialized into the job, re-asserted on execution), logs and error trackers (no cross-tenant data in shared views), and LLM/analytics pipelines.

## Organization and identity model

Model B2B SaaS as **user ↔ membership ↔ organization** from day one, even if v1 looks single-user:

- **Users** authenticate; they are global (one account, many orgs).
- **Organizations** are the tenant: subscription, settings, and all product data hang off the org.
- **Memberships** join the two and carry the role. Invitations are pending memberships (email + role + token).

The classic trap: hanging data off the *user*, then painfully migrating to orgs when the first team signs up. If v1 truly is personal, still create an implicit personal org per user — the cost is one join; the saved migration is enormous. Decide early: can a user belong to multiple orgs (usually yes for B2B)? Is there a personal workspace? Who is the org's last-admin failsafe?

## RBAC

- Roles attach to the **membership** (per-org), not the user globally.
- Start with 3–4 fixed roles (owner / admin / member / read-only). Custom roles and granular permission matrices are an enterprise-tier feature — design the *check* so it can grow (check permissions, map roles → permission sets), but don't build the matrix UI speculatively.
- Enforce server-side at a chokepoint (middleware/policy layer), deny by default, and always check **both** membership (is this user in this org?) and permission (may this role do this?) — plus object-level ownership where relevant (see `security.md` on IDOR).
- Support-staff access deserves design: impersonation with explicit audit trail beats shared god-credentials.

## Billing architecture

**Buy the payment/billing engine (Stripe or equivalent); own the entitlements.** Building payment processing is never the right call; but delegating *what the customer can do* to the payment provider couples product logic to a vendor and breaks the moment sales cuts a custom deal.

- **Plans** define price and limits (marketing-facing). **Entitlements** define what a tenant may actually do (`max_projects: 50`, `sso: true`) — stored on your side, derived from the plan by default, overridable per tenant (custom deals, grandfathering, comps). Product code checks entitlements only, never plan names.
- **Subscription state machine:** trialing → active → past_due (grace, degrade gently: warn → read-only → suspend; never delete on payment failure) → canceled. Handle upgrades (immediate, prorated) and downgrades (at period end) explicitly.
- **Webhooks drive state** — payment provider webhooks update local subscription state. Architectural requirements: verify signatures, process idempotently (event ids table), tolerate out-of-order delivery, and reconcile nightly against the provider API (webhooks *will* be missed).
- **Usage-based components** need a metering pipeline: emit usage events → aggregate → report to billing. Decide early what is metered; retrofitting metering is painful.
- Tax (Stripe Tax/Paddle as merchant-of-record), invoices, and dunning: delegate to the provider; note the decision.

## SaaS operational table stakes

Address in the plan (a sentence each is fine, silence is not): tenant onboarding flow (self-serve signup → org creation → first-value moment), tenant offboarding (data export format, deletion with retention window — GDPR requires both), per-tenant rate limiting (one tenant must not exhaust shared capacity — the noisy-neighbor mitigation for pooled tenancy), per-tenant observability (tenant id as a dimension in logs/metrics so "it's slow for customer X" is answerable), and admin backoffice (support needs to see subscription state and impersonate safely from week one).
