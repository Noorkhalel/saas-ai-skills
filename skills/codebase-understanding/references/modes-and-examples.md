# Modes and examples

## Focused and legacy modes

For "where implement subscription cancellation?", trace route/component, API client, backend handler/use case, subscription model/migration, payment integration/webhook, authorization, and tests. Return exact likely files and explicitly non-target files; do not change billing UI just because it is nearby. For an HTTP 500, trace frontend request through handler, logs/errors, database query/transaction, and response mapping; identify owner and tests, not a symptom-only layer.

For legacy MVC, trace routes/controllers/models/templates/jobs/tests and Git history where available; label inferred responsibilities, separate active/obsolete paths, and add characterization tests before change.

## General cases

- React + Node.js login flow: verify login form/client, backend login route/middleware, session or JWT storage, refresh behavior, and tests; mark any missing edge UNKNOWN.
- React + FastAPI + PostgreSQL: verify client bootstrap/routes/API client; FastAPI app/router/dependencies; ORM/migrations/db connection; auth session/JWT and tests.
- Supabase multi-tenant: map client/Edge Functions/RPC/schema/migrations/RLS; distinguish `auth.uid()`/policy/database enforcement from UI role rendering.
- Microservices: map gateway, service entrypoints, contracts, queues/workers, data ownership, traces/deploy units; do not assume service names prove ownership.
- Serverless: find every handler/config trigger, shared middleware, cold-start config, IAM/event source, and deployment mapping.
- AI agent: map prompt/context/RAG/embedding/vector/model/tool/MCP/validation/approval/output with permission, data retention, egress, failure, and hallucination points.
- Docs conflict: cite the README/doc claim and the contradictory source/config/test evidence; label intended versus actual, avoid choosing without owner confirmation.
- Large TypeScript monorepo: inventory applications, packages, shared libraries, workspace graph, public exports, deployment units, and package ownership before explaining architecture.
- Legacy Python application: use routes, imports, tests, and call sites to distinguish active behavior from inference; add characterization tests for unclear paths.
- Production bug: trace the failing request through each layer until the owning module is evidenced; avoid fixing an HTTP 500 in a frontend symptom layer when the failure occurs later.

## Reading order

For onboarding a new senior engineer, recommend root manifest/workspace and README, bootstrap/routes, one critical workflow end-to-end, schema/migrations/auth, tests, deployment/CI, integrations, then modules by roadmap/risk. Adjust to goal; do not prescribe every file.
