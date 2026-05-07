from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CartCreate(BaseModel):
    user_id: int
    status: str = "active"
    currency: str = "USD"


class CartUpdate(BaseModel):
    user_id: int | None = None
    status: str | None = None
    currency: str | None = None


class CartRead(BaseModel):
    id: int
    user_id: int
    status: str
    currency: str
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["CartCreate", "CartRead", "CartUpdate"]
