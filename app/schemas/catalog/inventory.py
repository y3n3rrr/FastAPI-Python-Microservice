from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InventoryCreate(BaseModel):
    variant_id: int
    quantity: int = 0
    reserved_quantity: int = 0
    reorder_level: int = 0


class InventoryUpdate(BaseModel):
    variant_id: int | None = None
    quantity: int | None = None
    reserved_quantity: int | None = None
    reorder_level: int | None = None


class InventoryRead(BaseModel):
    id: int
    variant_id: int
    quantity: int
    reserved_quantity: int
    reorder_level: int
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["InventoryCreate", "InventoryRead", "InventoryUpdate"]
