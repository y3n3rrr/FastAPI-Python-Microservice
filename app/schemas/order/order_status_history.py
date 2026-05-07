from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrderStatusHistoryCreate(BaseModel):
    order_id: int
    from_status: str | None = None
    to_status: str
    changed_by_user_id: int | None = None
    note: str | None = None


class OrderStatusHistoryUpdate(BaseModel):
    order_id: int | None = None
    from_status: str | None = None
    to_status: str | None = None
    changed_by_user_id: int | None = None
    note: str | None = None


class OrderStatusHistoryRead(BaseModel):
    id: int
    order_id: int
    from_status: str | None
    to_status: str
    changed_by_user_id: int | None
    note: str | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["OrderStatusHistoryCreate", "OrderStatusHistoryRead", "OrderStatusHistoryUpdate"]
