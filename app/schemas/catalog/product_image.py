from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductImageCreate(BaseModel):
    product_id: int
    image_url: str
    alt_text: str | None = None
    sort_order: int = 0
    is_primary: bool = False


class ProductImageUpdate(BaseModel):
    product_id: int | None = None
    image_url: str | None = None
    alt_text: str | None = None
    sort_order: int | None = None
    is_primary: bool | None = None


class ProductImageRead(BaseModel):
    id: int
    product_id: int
    image_url: str
    alt_text: str | None
    sort_order: int
    is_primary: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["ProductImageCreate", "ProductImageRead", "ProductImageUpdate"]
