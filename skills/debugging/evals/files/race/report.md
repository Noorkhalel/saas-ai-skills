# Bug report: inventory occasionally goes negative during flash sales

**Symptom:** During high-traffic flash sales, some products end up with **negative** `quantity` in the
`inventory` table, and we oversell — customers get order confirmations for items we don't have.

**Frequency:** Never reproducible in local testing or with a single user. Only happens under load,
and only for popular products (many people buying the same product at the same moment). Maybe a
few times per sale.

**Environment:** Node.js + node-postgres against PostgreSQL (default `READ COMMITTED` isolation).
Multiple app instances behind a load balancer; several worker processes each.

**Observed:** Two customers can both successfully reserve "the last unit" of a product within the
same few milliseconds; both get success responses; `quantity` ends at `-1`.

**Code:** `inventory.js` (same folder) — `reserveInventory()` is called during checkout.

No errors are thrown; both requests return `{ reserved: 1, remaining: 0 }`.
