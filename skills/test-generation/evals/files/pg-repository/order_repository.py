"""
PostgreSQL Repository for Order Management.

Handles order CRUD with transaction support, foreign key constraints,
and optimistic locking via version column.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import uuid4


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal = field(init=False)

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.unit_price <= 0:
            raise ValueError("Unit price must be positive")
        self.line_total = self.unit_price * self.quantity


@dataclass
class Order:
    customer_id: str
    items: list[OrderItem]
    id: str = field(default_factory=lambda: str(uuid4()))
    status: OrderStatus = OrderStatus.PENDING
    total: Decimal = Decimal("0")
    version: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


class OptimisticLockError(Exception):
    """Raised when a concurrent modification is detected."""
    pass


class OrderRepository:
    """
    Repository for order persistence.

    Assumes a PostgreSQL database with tables:
    - orders (id, customer_id, status, total, version, notes, created_at, updated_at)
    - order_items (id, order_id FK, product_id, product_name, quantity, unit_price, line_total)

    Indexes:
    - orders.customer_id
    - orders.status
    - orders.created_at
    - order_items.order_id
    """

    def __init__(self, connection):
        self._conn = connection

    def create(self, order: Order) -> Order:
        """
        Insert an order and its items in a single transaction.
        Calculates total from items. Rolls back if any insert fails.
        """
        order.total = sum(item.line_total for item in order.items)

        with self._conn.begin():
            self._conn.execute(
                """
                INSERT INTO orders (id, customer_id, status, total, version, notes, created_at, updated_at)
                VALUES (%(id)s, %(customer_id)s, %(status)s, %(total)s, %(version)s, %(notes)s, %(created_at)s, %(updated_at)s)
                """,
                {
                    "id": order.id,
                    "customer_id": order.customer_id,
                    "status": order.status.value,
                    "total": order.total,
                    "version": order.version,
                    "notes": order.notes,
                    "created_at": order.created_at,
                    "updated_at": order.updated_at,
                },
            )

            for item in order.items:
                self._conn.execute(
                    """
                    INSERT INTO order_items (id, order_id, product_id, product_name, quantity, unit_price, line_total)
                    VALUES (%(id)s, %(order_id)s, %(product_id)s, %(product_name)s, %(quantity)s, %(unit_price)s, %(line_total)s)
                    """,
                    {
                        "id": str(uuid4()),
                        "order_id": order.id,
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "line_total": item.line_total,
                    },
                )

        return order

    def find_by_id(self, order_id: str) -> Optional[Order]:
        """Fetch an order with its items by ID."""
        row = self._conn.execute(
            "SELECT * FROM orders WHERE id = %(id)s", {"id": order_id}
        ).fetchone()

        if not row:
            return None

        items_rows = self._conn.execute(
            "SELECT * FROM order_items WHERE order_id = %(order_id)s",
            {"order_id": order_id},
        ).fetchall()

        items = [
            OrderItem(
                product_id=r["product_id"],
                product_name=r["product_name"],
                quantity=r["quantity"],
                unit_price=r["unit_price"],
            )
            for r in items_rows
        ]

        return Order(
            id=row["id"],
            customer_id=row["customer_id"],
            items=items,
            status=OrderStatus(row["status"]),
            total=row["total"],
            version=row["version"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            notes=row["notes"],
        )

    def update_status(self, order_id: str, new_status: OrderStatus, expected_version: int) -> Order:
        """
        Update order status with optimistic locking.
        Raises OptimisticLockError if version doesn't match (concurrent modification).
        """
        now = datetime.utcnow()

        result = self._conn.execute(
            """
            UPDATE orders
            SET status = %(status)s, version = version + 1, updated_at = %(now)s
            WHERE id = %(id)s AND version = %(version)s
            """,
            {
                "status": new_status.value,
                "now": now,
                "id": order_id,
                "version": expected_version,
            },
        )

        if result.rowcount == 0:
            existing = self.find_by_id(order_id)
            if existing is None:
                raise ValueError(f"Order {order_id} not found")
            raise OptimisticLockError(
                f"Order {order_id} was modified by another process "
                f"(expected version {expected_version}, current {existing.version})"
            )

        return self.find_by_id(order_id)

    def find_by_customer(self, customer_id: str, status: Optional[OrderStatus] = None) -> list[Order]:
        """Find all orders for a customer, optionally filtered by status."""
        if status:
            rows = self._conn.execute(
                "SELECT id FROM orders WHERE customer_id = %(cid)s AND status = %(status)s ORDER BY created_at DESC",
                {"cid": customer_id, "status": status.value},
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id FROM orders WHERE customer_id = %(cid)s ORDER BY created_at DESC",
                {"cid": customer_id},
            ).fetchall()

        return [self.find_by_id(r["id"]) for r in rows]

    def delete(self, order_id: str) -> bool:
        """Delete an order and its items. Returns True if found and deleted."""
        with self._conn.begin():
            self._conn.execute(
                "DELETE FROM order_items WHERE order_id = %(id)s", {"id": order_id}
            )
            result = self._conn.execute(
                "DELETE FROM orders WHERE id = %(id)s", {"id": order_id}
            )
        return result.rowcount > 0
