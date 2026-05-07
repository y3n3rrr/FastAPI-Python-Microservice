from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CartItemCreate(BaseModel):
    cart_id: int
    product_variant_id: int
    quantity: int = 1
    unit_price_snapshot: Decimal
    currency: str = "USD"
    is_selected: bool = True


class CartItemUpdate(BaseModel):
    cart_id: int | None = None
    product_variant_id: int | None = None
    quantity: int | None = None
    unit_price_snapshot: Decimal | None = None
    currency: str | None = None
    is_selected: bool | None = None


class CartItemRead(BaseModel):
    id: int
    cart_id: int
    product_variant_id: int
    quantity: int
    unit_price_snapshot: Decimal
    currency: str
    is_selected: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["CartItemCreate", "CartItemRead", "CartItemUpdate"]
