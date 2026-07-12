# Architectural, service, and AI/MCP dependencies

## Module and cycle analysis

Report a cycle as an exact ordered path and closing edge, classify compile-time/runtime/architectural, trace affected flow, and name the shared responsibility or ownership breach. Resolve by moving a cohesive contract lower, extracting a focused module, consumer-owned dependency inversion, adapter, event, application service, responsibility split, or ownership reassignment. Never move random files into `common` merely to hide a cycle.

Cross-feature/layer/workspace imports require intended-boundary and public-contract context. Check domain-to-infrastructure/UI/persistence leakage, deep imports, service locator/globals, shared database and bidirectional service calls, vendor SDK reach-through, and framework lock-in. A cross-module dependency can be a valid public API use; explain the impact before labeling it a violation.

## External runtime dependencies

For payment/email/SMS/cloud/storage/identity/webhook/queue/database/search/vector/AI model/MCP dependencies record owner, critical path, sync/async mode, data class and tenant scope, availability/region/latency, quota/rate/cost, authentication/secret rotation, timeout/deadline, retry/idempotency, fallback/degradation, circuit/load isolation, observability, vendor exit path, and recovery/runbook. Do not assume fallback is desirable if consistency/correctness requires fail-closed behavior.

## AI and MCP tools

Map provider SDKs, model endpoints, RAG/vector/search components, agent frameworks, MCP servers/tool manifests, permissions/scopes, credentials, tool input/output data flow, network egress, code execution/file/database access, version/provenance, rate/cost limits, retries, logging/retention, and human approval. Excessive MCP permissions are a trust-boundary finding; recommend least privilege, isolation, allowlists, tenant separation, auditability, and failure containment. Do not call a tool malicious without evidence.
