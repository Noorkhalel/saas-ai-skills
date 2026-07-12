# REST and OpenAPI review guide

## REST semantics

Use resource nouns and consistent plural paths. Nest only for meaningful containment or scoping; provide a canonical resource URL when it is independently addressed. `GET`/`HEAD` are safe; `PUT` replaces a known resource and must have defined full-representation semantics; `PATCH` needs an explicit patch format and concurrency semantics; `POST` may create or invoke an action; `DELETE` needs idempotent repeat behavior and a defined hard/soft/async outcome.

Use status semantics consistently: successful creation commonly `201` plus `Location`; accepted asynchronous work `202` plus status/callback contract; no body `204`; validation `400`/`422` according to documented convention; unauthenticated `401`; forbidden `403`; missing/not-disclosed resource behavior selected deliberately; conflict/precondition `409`/`412`; rate limit `429` plus retry guidance. Do not use status codes to smuggle ambiguous domain state.

## Collections and concurrency

Bound page size, filter vocabulary, sortable fields, expansion depth, and field selection. Cursor pagination needs a stable ordered key (usually tie-broken by ID), opaque cursor, direction, snapshot/freshness behavior, and malformed/expired-cursor error. Offset pagination may be acceptable for small stable admin lists but can be costly and duplicate/skip during writes.

For mutable representations, document `ETag`/`If-Match` or version preconditions and conflict response. For retried unsafe operations, accept an idempotency key scoped to tenant/principal/operation and payload fingerprint, retain it for a documented window, return the original compatible result, and define mismatch behavior.

## Problem Details and OpenAPI

Use a consistent error media type/shape, for example `application/problem+json`, with stable `type`/machine code, title/status, request ID, and safe field errors. Do not reveal stack traces, raw dependency errors, secrets, or resource existence where policy forbids it.

OpenAPI must specify paths/methods, operation IDs, security requirements, request/response schemas, required/nullability/default behavior, examples, all material statuses, reusable errors, pagination/filter/sort parameters, webhook callbacks, deprecation, rate limits, and version policy. Validate with a linter and contract tests. Generated SDKs require stable operation IDs, predictable names, precise schemas, and semantic versioning/release notes.
