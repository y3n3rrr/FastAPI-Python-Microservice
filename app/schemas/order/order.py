from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    user_id: int
    status: str = "pending"
    currency: str = "USD"
    total_amount: Decimal = Decimal("0.00")
    note: str | None = None


class OrderUpdate(BaseModel):
    user_id: int | None = None
    status: str | None = None
    currency: str | None = None
    total_amount: Decimal | None = None
    note: str | None = None


class OrderRead(BaseModel):
    id: int
    user_id: int
    status: str
    currency: str
    total_amount: Decimal
    note: str | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["OrderCreate", "OrderRead", "OrderUpdate"]
