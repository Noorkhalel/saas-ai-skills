# Workload patterns: AI, events, social, healthcare, and commerce

## AI / RAG / vector retrieval

Keep document, chunk, embedding, model/index version, tenant/ACL, source/citation, and deletion lifecycle explicit. Retrieval must enforce tenant/permission filters before exposing content. Choose vector dimensions/distance/index parameters from recall-latency-cost evaluation, not defaults. Re-embedding and index rebuilds need versioned coexistence, backfill, cutover, quality evaluation, and deletion propagation. Cache only permission-safe/versioned results; retain prompts or derived data only under an approved privacy policy.

## Event-driven/background jobs

Model immutable event identity, producer, occurrence/ingestion times, schema version, aggregate/key, payload reference, status, retry/attempt history, idempotency/deduplication, ordering/partition key, and retention/dead-letter queue (DLQ). Do not make a database table an unbounded queue without ingestion, archival/partition, consumer, and backpressure strategy. Outbox records and consumed-message records must support replay safely.

## Social and commerce

For social graphs, model follows/blocks/privacy, comments, likes, and messaging separately; favor cursor pagination and derived feed fan-out/projection based on measured fan-out/read patterns, with rebuild/reconciliation. For commerce with millions of products and orders, preserve immutable order/line-item price/tax/discount snapshots, inventory reservation/adjustment rules, payment-provider references/idempotency, and customer/merchant access boundaries. Do not recalculate historical totals from mutable catalog prices.

## Healthcare and regulated data

Classify PHI/PII, minimize collection, enforce role/purpose/tenant access, audit accesses and changes, encrypt in transit/at rest according to provider controls, restrict break-glass access with auditing, and define retention, legal hold, export, correction, deletion, and residency with compliance owners. Never claim a schema alone makes a system HIPAA/GDPR compliant; compliance includes policies, contracts, operations, and verification.
