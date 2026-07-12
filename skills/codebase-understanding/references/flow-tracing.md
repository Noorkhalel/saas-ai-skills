# Flow, data, auth, and integration tracing

For every edge, cite source/destination symbol/config or mark missing. A request trace should include transport entry, middleware, identity extraction, authorization enforcement, application/domain operation, transaction/persistence, async/event work, response/error mapping. A data trace includes source, validation, transform, serialization, cache, queue/event, persistence, external transmission, and retention/deletion for sensitive data.

Authentication identifies a principal; authorization grants action on resource/tenant. Map UI restriction, API policy/guard/middleware, and database RLS/ownership separately. Do not call a UI check secure without server/database evidence. For persistence map ORM/query, schema/migrations, tables/collections, transactions, constraints/indexes/RLS, ownership/read/write paths, cross-module access, cache/search/vector storage.

For integrations map adapter/client/config key/call sites/error-timeout-retry-fallback/secrets/test strategy. For external providers, record sync/async, data class, tenant scope, quota/cost, region, idempotency, observability, and failure ownership. Mermaid flow/sequence diagrams must use inspected edges; label inferred edges.
