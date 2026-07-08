# Bug Report: Duplicate Order Submissions

**Bug ID**: BUG-2024-0847
**Severity**: Critical
**Status**: Fixed (commit abc123f)
**Reporter**: Support team — multiple customer complaints
**Date found**: 2024-11-15
**Date fixed**: 2024-11-16

## Summary

Customers were being charged multiple times for the same order when they double-clicked the "Place Order" button or when network retries occurred. The system created duplicate orders with separate payment charges for each.

## Root Cause

The original `submitOrder` method had no idempotency check. Each call to `submitOrder` with the same items would:
1. Calculate the total
2. Charge the payment method
3. Save a new order

If the client retried (due to timeout, network error, or user double-click), a second order was created and a second charge was processed.

## Fix Applied

Added an `idempotencyKey` parameter to `OrderRequest`. The `submitOrder` method now:
1. Checks `store.findByIdempotencyKey(key)` before processing
2. If a previous result exists for that key, returns it without re-charging
3. Saves the result with the idempotency key for future deduplication

## Pre-Fix Behavior (the bug)

```
Client sends: submitOrder({ items: [...], paymentMethodId: "pm_123" })
Server: creates Order ORD-001, charges $99.99
Client timeout — retries same request
Server: creates Order ORD-002, charges $99.99 AGAIN
Customer charged $199.98 instead of $99.99
```

## Post-Fix Behavior (expected)

```
Client sends: submitOrder({ items: [...], idempotencyKey: "req-abc", paymentMethodId: "pm_123" })
Server: creates Order ORD-001, charges $99.99, saves with key "req-abc"
Client timeout — retries with same idempotencyKey
Server: finds existing result for "req-abc", returns ORD-001 without re-charging
Customer charged $99.99 once
```

## Regression Test Requirements

A proper regression test must:
1. Submit an order with an idempotency key → verify it succeeds
2. Submit again with the SAME idempotency key → verify it returns the original result
3. Verify the payment gateway was charged exactly ONCE (not twice)
4. Verify only ONE order exists in the store for that key
