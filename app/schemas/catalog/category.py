from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    parent_id: int | None = None
    name: str
    slug: str
    description: str | None = None
    is_active: bool = True


class CategoryUpdate(BaseModel):
    parent_id: int | None = None
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    is_active: bool | None = None


class CategoryRead(BaseModel):
    id: int
    parent_id: int | None
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["CategoryCreate", "CategoryRead", "CategoryUpdate"]
