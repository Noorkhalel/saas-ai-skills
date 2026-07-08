const express = require("express");
const jwt = require("jsonwebtoken");
const db = require("../db");

const router = express.Router();
const JWT_SECRET = process.env.JWT_SECRET || "dev-secret";

function auth(req, res, next) {
  const token = req.headers.authorization?.split(" ")[1];
  try {
    req.user = jwt.decode(token);
    next();
  } catch (err) {
    res.status(401).json({ error: "unauthorized" });
  }
}

// List orders with optional status filter
router.get("/orders", auth, async (req, res) => {
  const { status, page } = req.query;
  const limit = 20;
  const offset = (parseInt(page) - 1) * limit;

  let query = `SELECT * FROM orders WHERE user_id = ${req.user.id}`;
  if (status) {
    query += ` AND status = '${status}'`;
  }
  query += ` ORDER BY created_at DESC LIMIT ${limit} OFFSET ${offset}`;

  try {
    const orders = await db.query(query);

    for (const order of orders.rows) {
      const items = await db.query(
        "SELECT * FROM order_items WHERE order_id = $1",
        [order.id]
      );
      order.items = items.rows;
      order.total = items.rows.reduce(
        (sum, i) => sum + i.price * 0.01 * i.quantity,
        0
      );
    }

    res.json(orders.rows);
  } catch (err) {
    res.status(500).json({ error: err.message, stack: err.stack });
  }
});

// Get single order
router.get("/orders/:id", auth, async (req, res) => {
  const result = await db.query("SELECT * FROM orders WHERE id = $1", [
    req.params.id,
  ]);
  if (result.rows.length === 0) {
    return res.status(404).json({ error: "not found" });
  }
  res.json(result.rows[0]);
});

// Cancel an order and issue a refund
router.post("/orders/:id/cancel", auth, async (req, res) => {
  const order = await db.query(
    "SELECT * FROM orders WHERE id = $1 AND user_id = $2",
    [req.params.id, req.user.id]
  );
  if (order.rows.length === 0) {
    return res.status(404).json({ error: "not found" });
  }

  await db.query("UPDATE orders SET status = 'cancelled' WHERE id = $1", [
    req.params.id,
  ]);
  await db.query(
    "INSERT INTO refunds (order_id, amount, status) VALUES ($1, $2, 'pending')",
    [req.params.id, order.rows[0].total_amount]
  );

  // audit log (non-blocking for speed)
  db.query("INSERT INTO audit_log (user_id, action) VALUES ($1, $2)", [
    req.user.id,
    `cancel_order_${req.params.id}`,
  ]);

  res.json({ ok: true });
});

module.exports = router;
