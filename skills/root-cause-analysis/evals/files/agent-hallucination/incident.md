# Incident: support AI agent confidently reports wrong order statuses

All times UTC. Status: ongoing; escalations rising; RCA requested.

## Report

Our customer-support AI agent (answers "where is my order" via an MCP tool that queries the
orders DB) has, over the past week, told ~30 customers their order "has shipped and is on its
way" when the order was actually **cancelled** or **payment-failed**. The agent states this
confidently with a tracking-style sentence. It began after we deployed a new version of the
`orders-mcp` server on Monday. Not every query is wrong — it's intermittent, and seems worse
during busy periods.

## Architecture

Support agent (LLM) → calls MCP tool `get_order_status(order_id)` exposed by our `orders-mcp`
server → server queries Postgres → returns status JSON. The agent composes the customer reply
from the tool result. Agent instructions: "Use get_order_status to answer order questions.
Be warm and reassuring."

## Evidence — one wrong interaction (transcript + server logs), order o_5521 (actually CANCELLED)

Agent tool call log:
```
10:41:22 tool_call get_order_status {"order_id":"o_5521"}
10:41:27 tool_result ""                       ← empty string returned
10:41:28 assistant: "Good news! Your order is on its way and should arrive soon. 📦"
```

orders-mcp server log (same request):
```
10:41:22 get_order_status order_id=o_5521
10:41:22 querying orders db…
10:41:27 ERROR query failed: timeout acquiring connection from pool (pool exhausted, size=5)
10:41:27 returning fallback response
```

`orders-mcp` handler (deployed Monday, `handler.ts`):
```ts
export async function getOrderStatus(orderId: string) {
  try {
    const row = await db.query("SELECT status FROM orders WHERE id = $1", [orderId]);
    return JSON.stringify({ status: row[0].status });
  } catch (e) {
    logger.error("query failed: " + e.message);
    return "";                       // <-- Monday's change: was `throw e` before
  }
}
```

Monday's PR #77 diff comment: "return empty instead of throwing so the agent doesn't crash on
DB blips." Connection pool size is 5; the agent runs up to 20 concurrent support sessions at
peak. There is no telemetry that records tool *errors* separately from tool *results* — the
agent platform only logs the final tool_result string. The agent has no instruction about what
to do if a tool returns empty/unknown, and no validation that the tool output contains a status.

## Correlation

The wrong answers cluster during peak concurrency (pool exhaustion is load-dependent). Off-peak,
the same agent answers correctly for the same orders. No evals or regression tests exist for the
agent's handling of tool failures; QA only tested the happy path with a warm pool.
