from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BrandCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None
    logo_url: str | None = None
    is_active: bool = True


class BrandUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    logo_url: str | None = None
    is_active: bool | None = None


class BrandRead(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    logo_url: str | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["BrandCreate", "BrandRead", "BrandUpdate"]
