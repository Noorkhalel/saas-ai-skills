const db = require("../db"); // node-postgres pool

// Reserve `qty` units of a product for an order.
// Called from POST /api/orders during checkout.
async function reserveInventory(productId, qty) {
  const { rows } = await db.query(
    "SELECT quantity FROM inventory WHERE product_id = $1",
    [productId]
  );

  if (rows.length === 0) {
    throw new Error("unknown product");
  }

  const available = rows[0].quantity;

  if (available < qty) {
    throw new Error("out of stock");
  }

  // deduct the reserved units
  await db.query(
    "UPDATE inventory SET quantity = quantity - $1 WHERE product_id = $2",
    [qty, productId]
  );

  return { reserved: qty, remaining: available - qty };
}

module.exports = { reserveInventory };
