from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductVariantCreate(BaseModel):
    product_id: int
    sku: str
    barcode: str | None = None
    name: str | None = None
    color: str | None = None
    size: str | None = None
    price: Decimal
    compare_at_price: Decimal | None = None
    currency: str = "USD"
    weight_kg: Decimal | None = None
    is_active: bool = True


class ProductVariantUpdate(BaseModel):
    product_id: int | None = None
    sku: str | None = None
    barcode: str | None = None
    name: str | None = None
    color: str | None = None
    size: str | None = None
    price: Decimal | None = None
    compare_at_price: Decimal | None = None
    currency: str | None = None
    weight_kg: Decimal | None = None
    is_active: bool | None = None


class ProductVariantRead(BaseModel):
    id: int
    product_id: int
    sku: str
    barcode: str | None
    name: str | None
    color: str | None
    size: str | None
    price: Decimal
    compare_at_price: Decimal | None
    currency: str
    weight_kg: Decimal | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["ProductVariantCreate", "ProductVariantRead", "ProductVariantUpdate"]
