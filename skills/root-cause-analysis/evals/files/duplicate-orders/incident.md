# Incident: duplicate orders created for some customers

All times UTC. Status: ongoing risk (happens a few times per week); RCA requested.

## Report

Support has 17 tickets over 3 weeks: customers charged once but receiving **two identical
order confirmations** and two shipments prepared. Ops manually cancels the duplicate when a
customer complains. First ticket: June 16 — three days after the June 13 release that moved
order creation from the HTTP request path to a queue consumer ("checkout latency project").

Duplicates cluster in time: 14 of 17 occurred during evening peak (18:00–21:00). We found 9
more duplicate pairs in the DB that nobody reported (28 total).

## Architecture (since June 13)

`POST /api/checkout` → validates + charges payment → publishes `order.create` message to
RabbitMQ → returns 202. `order-consumer` service consumes the message, creates the order
row + order items, calls the warehouse API, **then acks**. Prefetch 10, quorum queue,
default at-least-once delivery. 4 consumer replicas.

## Evidence from one confirmed duplicate (order pair #88231 / #88232, July 3)

RabbitMQ log:
```
19:42:07.114 deliver msg_id=ord-7f3a… ctag=consumer-2
19:42:09.876 channel closed unexpectedly (consumer-2) — connection reset
19:42:09.901 msg_id=ord-7f3a… redelivered=true → ctag=consumer-4
```

order-consumer-2 log (same window):
```
19:42:07.201 processing order.create ord-7f3a…
19:42:08.455 order row created id=88231
19:42:09.812 calling warehouse API…
19:42:09.874 FATAL: JavaScript heap out of memory      ← pod OOM-killed (memory limit 256Mi)
```

order-consumer-4 log:
```
19:42:09.933 processing order.create ord-7f3a…
19:42:10.671 order row created id=88232
19:42:11.560 warehouse reservation ok; ack
```

Consumer pods show 6–10 OOM restarts/day during evening peak (restart counts in k8s).
Nobody was alerted on these restarts; they were considered "self-healing."

## Code (order-consumer, `consumer.js`, trimmed)

```js
channel.consume("order.create", async (msg) => {
  const payload = JSON.parse(msg.content);
  const order = await db.orders.insert({          // plain INSERT, id auto-generated
    customerId: payload.customerId,
    items: payload.items,
    paymentRef: payload.paymentRef,
  });
  await warehouse.reserve(order.id, payload.items);
  channel.ack(msg);
});
```

There is no uniqueness constraint involving `paymentRef` or the message id; the `orders`
table PK is an auto-increment id. The message carries a stable `msg_id` and `paymentRef`.

## Prior discussion

The June 13 design doc says: "RabbitMQ guarantees each order message is processed once."
No reviewer challenged this line. There are no consumer-side integration tests involving
redelivery, and no duplicate-order monitor (the 9 unreported pairs were found only during
this investigation).
