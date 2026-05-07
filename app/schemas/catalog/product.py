from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    category_id: int | None = None
    brand_id: int | None = None
    name: str
    slug: str
    description: str | None = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    category_id: int | None = None
    brand_id: int | None = None
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    is_active: bool | None = None


class ProductRead(BaseModel):
    id: int
    category_id: int | None
    brand_id: int | None
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["ProductCreate", "ProductRead", "ProductUpdate"]
