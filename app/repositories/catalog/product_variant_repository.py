import builtins

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from app.entities.catalog.brand import Brand
from app.entities.catalog.category import Category
from app.entities.catalog.inventory import Inventory
from app.entities.catalog.product import Product
from app.entities.catalog.product_variant import ProductVariant


class ProductVariantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[ProductVariant]:
        return list(self.db.scalars(select(ProductVariant).order_by(ProductVariant.id)))

    def get(self, variant_id: int) -> ProductVariant | None:
        return self.db.get(ProductVariant, variant_id)

    def get_by_sku(self, sku: str) -> ProductVariant | None:
        return self.db.scalar(select(ProductVariant).where(ProductVariant.sku == sku))

    def get_active_with_relations(self, variant_id: int) -> ProductVariant | None:
        stmt = (
            select(ProductVariant)
            .join(Product, Product.id == ProductVariant.product_id)
            .outerjoin(Inventory, Inventory.variant_id == ProductVariant.id)
            .where(
                ProductVariant.id == variant_id,
                ProductVariant.is_active.is_(True),
                Product.is_active.is_(True),
            )
            .options(
                joinedload(ProductVariant.product).joinedload(Product.category),
                joinedload(ProductVariant.product).joinedload(Product.brand),
                joinedload(ProductVariant.inventory),
            )
        )
        return self.db.execute(stmt).scalars().unique().first()

    def list_by_product(self, product_id: int) -> builtins.list[ProductVariant]:
        return list(self.db.scalars(select(ProductVariant).where(ProductVariant.product_id == product_id).order_by(ProductVariant.id)))

    def add(self, variant: ProductVariant) -> ProductVariant:
        self.db.add(variant)
        return variant

    def delete(self, variant: ProductVariant) -> None:
        self.db.delete(variant)

    def search_active(
        self,
        *,
        query: str | None = None,
        category_slug: str | None = None,
        brand_slug: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        currency: str | None = None,
        only_available: bool = True,
        limit: int = 20,
    ) -> builtins.list[ProductVariant]:
        stmt = (
            select(ProductVariant)
            .join(Product, Product.id == ProductVariant.product_id)
            .outerjoin(Category, Category.id == Product.category_id)
            .outerjoin(Brand, Brand.id == Product.brand_id)
            .outerjoin(Inventory, Inventory.variant_id == ProductVariant.id)
            .where(
                ProductVariant.is_active.is_(True),
                Product.is_active.is_(True),
            )
            .options(
                joinedload(ProductVariant.product).joinedload(Product.category),
                joinedload(ProductVariant.product).joinedload(Product.brand),
                joinedload(ProductVariant.inventory),
            )
            .order_by(ProductVariant.id)
            .limit(max(1, min(limit, 100)))
        )

        if query:
            q = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(q),
                    Product.slug.ilike(q),
                    ProductVariant.name.ilike(q),
                    ProductVariant.sku.ilike(q),
                    Category.name.ilike(q),
                    Brand.name.ilike(q),
                )
            )

        if category_slug:
            stmt = stmt.where(Category.slug == category_slug)
        if brand_slug:
            stmt = stmt.where(Brand.slug == brand_slug)
        if currency:
            stmt = stmt.where(ProductVariant.currency == currency.upper())
        if min_price is not None:
            stmt = stmt.where(ProductVariant.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(ProductVariant.price <= max_price)
        if only_available:
            stmt = stmt.where(
                and_(
                    Inventory.id.is_not(None),
                    Inventory.quantity > Inventory.reserved_quantity,
                )
            )

        return list(self.db.scalars(stmt).unique())
