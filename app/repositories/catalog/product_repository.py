import builtins

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from app.entities.catalog.product import Product
from app.entities.catalog.product_variant import ProductVariant


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[Product]:
        return list(self.db.scalars(select(Product).order_by(Product.id)))

    def get(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def get_active_with_relations(self, product_id: int) -> Product | None:
        stmt = (
            select(Product)
            .where(
                Product.id == product_id,
                Product.is_active.is_(True),
            )
            .options(
                joinedload(Product.category),
                joinedload(Product.brand),
                joinedload(Product.variants.of_type(ProductVariant)).joinedload(ProductVariant.inventory),
            )
        )
        return self.db.execute(stmt).scalars().unique().first()

    def get_by_slug(self, slug: str) -> Product | None:
        return self.db.scalar(select(Product).where(Product.slug == slug))

    def list_by_category(self, category_id: int) -> builtins.list[Product]:
        return list(self.db.scalars(select(Product).where(Product.category_id == category_id).order_by(Product.id)))

    def list_by_brand(self, brand_id: int) -> builtins.list[Product]:
        return list(self.db.scalars(select(Product).where(Product.brand_id == brand_id).order_by(Product.id)))

    def add(self, product: Product) -> Product:
        self.db.add(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
