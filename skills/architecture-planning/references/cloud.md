# Cloud & Deployment Architecture

Read this for hosting recommendations, provider service mapping, and the Deployment Architecture section of every plan. Guiding rule: **operational capability is a requirement like any other** — recommend infrastructure the actual team can run at 3 a.m., not the infrastructure a conference talk would admire.

## Twelve-Factor, the parts that shape architecture

Design the app so the deployment story stays simple; these factors are the load-bearing ones:

- **Config in the environment** — one build artifact promoted through dev→staging→prod; environments differ only in env vars/secrets. No environment-specific builds or config files baked into images.
- **Stateless processes** — no session or file state on instance disk; sessions in DB/Redis, files in object storage. This single property is what makes horizontal scaling, zero-downtime deploys, and instance replacement trivial. Stateful needs (WebSockets, in-memory caches) are called out explicitly in the plan because they bend it.
- **Backing services as attached resources** — DB, cache, queue, mail are URLs in config, swappable per environment.
- **Disposability & dev/prod parity** — fast start, graceful shutdown (finish in-flight, stop accepting), and the same containers/services locally (docker compose) as in prod.
- **Logs as event streams** — write structured logs to stdout; the platform ships them. No log files to rotate, no in-app log routing.

## Hosting decision ladder

Each rung buys flexibility with operational load. **Start at the top; earn each step down.** The plan states the rung, why it suffices, and the trigger to move down a rung.

1. **PaaS** (Render, Railway, Fly.io, Heroku, AWS App Runner, Azure App Service): push container/repo, get TLS, deploys, scaling, logs. Right answer for most products until traffic or architecture outgrows it. Weakness: cost at high sustained scale, less network/topology control.
2. **Managed containers** (AWS ECS/Fargate, Google Cloud Run, Azure Container Apps): containers without cluster management; VPC control, scale-to-zero (Cloud Run), spot pricing. Right when you need private networking, multiple services, or PaaS pricing breaks down.
3. **Kubernetes** (EKS/AKS/GKE): maximum control and portability; a part-to-full-time platform responsibility. Justified by many services, a platform team, or org standardization — *not* by resume-driven design. A 4-person product team on K8s is an anti-pattern the plan should reject explicitly.

**Serverless functions** (Lambda / Cloud Functions / Azure Functions) sit beside the ladder, not on it: right for event-shaped and spiky work (uploads processing, webhook handlers, scheduled jobs, glue) and for near-zero-baseline APIs. Watch: cold starts on latency-sensitive paths, execution limits, **DB connection exhaustion** (use a pooler/proxy — RDS Proxy, PgBouncer — or an HTTP-based DB client), and per-invocation cost curves that cross container cost at sustained load. Fine hybrid: containers for the product API, functions for the edges.

**Databases and stateful services: always managed** (RDS/Aurora, Cloud SQL, Azure Database, or Neon/Supabase/PlanetScale-class). Self-hosting the database to save $50/month trades away backups, PITR, failover, and patching — reject it in the plan unless compliance genuinely forces self-managed.

## Provider mapping

Recommend **one** provider (multi-cloud is a cost, not a virtue, for product teams — portability comes from containers + Terraform + managed-Postgres, not from abstraction layers). Choose on: existing team skills, existing org commitments/credits, region/residency needs, and required managed services. Equivalents:

| Need | AWS | Azure | GCP |
|------|-----|-------|-----|
| Containers (managed) | ECS/Fargate, App Runner | Container Apps, App Service | Cloud Run |
| Kubernetes | EKS | AKS | GKE |
| Functions | Lambda | Functions | Cloud Functions |
| Relational DB | RDS / Aurora | Azure Database for PostgreSQL | Cloud SQL / AlloyDB |
| Cache | ElastiCache | Azure Cache for Redis | Memorystore |
| Queue / pub-sub | SQS / SNS / EventBridge | Storage Queues / Service Bus / Event Grid | Cloud Tasks / Pub/Sub |
| Object storage | S3 | Blob Storage | GCS |
| CDN + edge | CloudFront | Front Door / CDN | Cloud CDN |
| Identity (customer) | Cognito | Entra External ID | Identity Platform |
| Secrets | Secrets Manager / SSM | Key Vault | Secret Manager |
| Observability | CloudWatch | Monitor / App Insights | Cloud Monitoring/Logging |
| DNS | Route 53 | Azure DNS | Cloud DNS |

## Delivery pipeline and environments

State the shape in every plan:

- **Environments:** local (docker compose mirroring prod services) → staging (prod-shaped, smaller; migrations rehearse here) → production. Preview environments per PR if the platform makes them cheap. Staging holds no production data — synthetic or scrubbed only.
- **CI/CD:** every push → lint, tests, build image once; merge to main → deploy staging automatically; production via the same pipeline with a promotion step (auto or one-click, team's choice). Deployment strategy: rolling with health checks as the default; blue/green or canary when the traffic justifies it. **Rollback is redeploy-previous-image** — which requires migrations to be backward-compatible one release in each direction (expand→migrate→contract discipline, `data.md`).
- **IaC from day one** (Terraform/OpenTofu or the provider's native tooling): infrastructure is reviewable, reproducible, and staging can be rebuilt from code. Click-ops environments become unauditable snowflakes within a quarter.

## Observability

Minimum viable, named concretely in the plan: **structured logs** (JSON, request id + tenant id on every line) centralized with retention; **metrics** — the four golden signals (latency p50/p95/p99, traffic, errors, saturation) per service plus queue depths and DB connections; **tracing** with propagated request ids from day one (OpenTelemetry when service count > 1); **uptime checks + error tracker** (Sentry-class) wired to alerting a human actually receives. Define 2–3 SLOs for the core workflows (e.g., "p95 < 400ms, 99.9% availability on the API") — alerts derive from SLO burn, not from every blip. Dashboards for the golden signals exist before launch, not after the first incident.

## Cost architecture

Cost is a first-class constraint from Phase 1: give the plan a rough monthly run-cost for launch shape and for 10× — order-of-magnitude honesty beats silence. Structural cost notes: budget alerts on day one (the forgotten-resource bill is a rite of passage to design away); the big traps are **egress**, NAT gateway hours, cross-AZ chatter, over-provisioned databases, and unbounded log/metric retention; scale-to-zero (Cloud Run, serverless, Neon-class DBs) is a gift for staging/preview environments; reserved/committed pricing only after usage stabilizes.

## Resilience and recovery

Answer four questions in the Deployment section: **What fails first?** (usually the DB or a third party — timeouts + circuit breakers on every outbound call, `api.md`). **What's the blast radius?** (multi-AZ by default; multi-region only when the SLA genuinely demands it — it roughly doubles complexity and cost). **What data can we lose?** (RPO — backup cadence + PITR window). **How fast are we back?** (RTO — and the restore path is *tested*, on a schedule; an untested backup is a hope, not a plan).
