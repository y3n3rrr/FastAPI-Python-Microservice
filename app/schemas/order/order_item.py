from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OrderItemCreate(BaseModel):
    order_id: int
    product_variant_id: int
    quantity: int = 1
    unit_price_snapshot: Decimal
    line_total: Decimal = Decimal("0.00")
    currency: str = "USD"


class OrderItemUpdate(BaseModel):
    order_id: int | None = None
    product_variant_id: int | None = None
    quantity: int | None = None
    unit_price_snapshot: Decimal | None = None
    line_total: Decimal | None = None
    currency: str | None = None


class OrderItemRead(BaseModel):
    id: int
    order_id: int
    product_variant_id: int
    quantity: int
    unit_price_snapshot: Decimal
    line_total: Decimal
    currency: str
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["OrderItemCreate", "OrderItemRead", "OrderItemUpdate"]
