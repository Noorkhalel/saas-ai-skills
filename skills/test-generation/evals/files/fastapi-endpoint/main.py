"""
FastAPI endpoint for managing product inventory.

Features:
- CRUD operations with validation
- Authentication via Bearer token
- Role-based access (admin can create/update/delete, viewer can only read)
- Pagination with cursor-based navigation
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query, Header
from pydantic import BaseModel, Field, field_validator

app = FastAPI()


class UserRole(str, Enum):
    admin = "admin"
    viewer = "viewer"


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., pattern=r"^[A-Z]{2,4}-\d{4,8}$")
    price: float = Field(..., gt=0, le=999999.99)
    quantity: int = Field(..., ge=0)
    category: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be blank")
        return v.strip()


class ProductResponse(BaseModel):
    id: str
    name: str
    sku: str
    price: float
    quantity: int
    category: str
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseModel):
    items: list[ProductResponse]
    next_cursor: Optional[str] = None
    total: int


# Simulated database
_products: dict[str, dict] = {}
_next_id = 1


# Simulated auth
VALID_TOKENS = {
    "admin-token-123": {"user_id": "user-1", "role": UserRole.admin},
    "viewer-token-456": {"user_id": "user-2", "role": UserRole.viewer},
}


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.replace("Bearer ", "")
    user = VALID_TOKENS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def require_admin(user: dict = Depends(get_current_user)):
    if user["role"] != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@app.get("/products", response_model=PaginatedResponse)
def list_products(
    category: Optional[str] = None,
    cursor: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    items = list(_products.values())

    if category:
        items = [p for p in items if p["category"] == category]

    items.sort(key=lambda p: p["created_at"])

    # Cursor-based pagination
    if cursor:
        cursor_index = next(
            (i for i, p in enumerate(items) if p["id"] == cursor), None
        )
        if cursor_index is not None:
            items = items[cursor_index + 1 :]

    page = items[:limit]
    next_cursor = page[-1]["id"] if len(items) > limit else None

    return PaginatedResponse(
        items=[ProductResponse(**p) for p in page],
        next_cursor=next_cursor,
        total=len(list(_products.values())),
    )


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(
    product: ProductCreate,
    user: dict = Depends(require_admin),
):
    global _next_id

    # Check SKU uniqueness
    for existing in _products.values():
        if existing["sku"] == product.sku:
            raise HTTPException(status_code=409, detail="SKU already exists")

    now = datetime.utcnow()
    product_data = {
        "id": f"prod-{_next_id}",
        "name": product.name,
        "sku": product.sku,
        "price": product.price,
        "quantity": product.quantity,
        "category": product.category,
        "created_at": now,
        "updated_at": now,
    }
    _products[product_data["id"]] = product_data
    _next_id += 1

    return ProductResponse(**product_data)


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, user: dict = Depends(get_current_user)):
    product = _products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(**product)


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str, user: dict = Depends(require_admin)):
    if product_id not in _products:
        raise HTTPException(status_code=404, detail="Product not found")
    del _products[product_id]
