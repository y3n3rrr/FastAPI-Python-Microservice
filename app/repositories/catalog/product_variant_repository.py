from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.catalog.product_variant import ProductVariant


class ProductVariantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[ProductVariant]:
        return list(self.db.scalars(select(ProductVariant).order_by(ProductVariant.id)))

    def get(self, variant_id: int) -> ProductVariant | None:
        return self.db.get(ProductVariant, variant_id)

    def get_by_sku(self, sku: str) -> ProductVariant | None:
        return self.db.scalar(select(ProductVariant).where(ProductVariant.sku == sku))

    def list_by_product(self, product_id: int) -> list[ProductVariant]:
        return list(self.db.scalars(select(ProductVariant).where(ProductVariant.product_id == product_id).order_by(ProductVariant.id)))

    def add(self, variant: ProductVariant) -> ProductVariant:
        self.db.add(variant)
        return variant

    def delete(self, variant: ProductVariant) -> None:
        self.db.delete(variant)
