from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_session_factory
from app.entities.catalog.brand import Brand
from app.entities.catalog.category import Category
from app.entities.catalog.inventory import Inventory
from app.entities.catalog.product import Product
from app.entities.catalog.product_image import ProductImage
from app.entities.catalog.product_variant import ProductVariant


def _upsert_brand(db: Session, *, slug: str, **values: object) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.slug == slug))
    if brand is None:
        brand = Brand(slug=slug, **values)
        db.add(brand)
        db.flush()
        return brand

    for key, value in values.items():
        setattr(brand, key, value)
    return brand


def _upsert_category(db: Session, *, slug: str, **values: object) -> Category:
    category = db.scalar(select(Category).where(Category.slug == slug))
    if category is None:
        category = Category(slug=slug, **values)
        db.add(category)
        db.flush()
        return category

    for key, value in values.items():
        setattr(category, key, value)
    return category


def _upsert_product(db: Session, *, slug: str, **values: object) -> Product:
    product = db.scalar(select(Product).where(Product.slug == slug))
    if product is None:
        product = Product(slug=slug, **values)
        db.add(product)
        db.flush()
        return product

    for key, value in values.items():
        setattr(product, key, value)
    return product


def _upsert_variant(db: Session, *, sku: str, **values: object) -> ProductVariant:
    variant = db.scalar(select(ProductVariant).where(ProductVariant.sku == sku))
    if variant is None:
        variant = ProductVariant(sku=sku, **values)
        db.add(variant)
        db.flush()
        return variant

    for key, value in values.items():
        setattr(variant, key, value)
    return variant


def _upsert_image(db: Session, *, product_id: int, image_url: str, **values: object) -> ProductImage:
    image = db.scalar(
        select(ProductImage).where(
            ProductImage.product_id == product_id,
            ProductImage.image_url == image_url,
        )
    )
    if image is None:
        image = ProductImage(product_id=product_id, image_url=image_url, **values)
        db.add(image)
        db.flush()
        return image

    for key, value in values.items():
        setattr(image, key, value)
    return image


def _upsert_inventory(db: Session, *, variant_id: int, **values: object) -> Inventory:
    inventory = db.scalar(select(Inventory).where(Inventory.variant_id == variant_id))
    if inventory is None:
        inventory = Inventory(variant_id=variant_id, **values)
        db.add(inventory)
        db.flush()
        return inventory

    for key, value in values.items():
        setattr(inventory, key, value)
    return inventory


def seed_catalog() -> None:
    session_factory = get_session_factory()
    db = session_factory()

    try:
        # Brands
        migros = _upsert_brand(
            db,
            slug="migros",
            name="Migros",
            description="Migros private-label and curated brand portfolio.",
            logo_url="https://example.com/brands/migros.png",
            is_active=True,
        )
        pinar = _upsert_brand(
            db,
            slug="pinar",
            name="Pinar",
            description="Dairy and packaged food products.",
            logo_url="https://example.com/brands/pinar.png",
            is_active=True,
        )

        # Categories
        beverages = _upsert_category(
            db,
            slug="beverages",
            parent_id=None,
            name="Beverages",
            description="Soft drinks, juices, and water.",
            is_active=True,
        )
        dairy = _upsert_category(
            db,
            slug="dairy",
            parent_id=None,
            name="Dairy",
            description="Milk, cheese, and yogurt products.",
            is_active=True,
        )
        fruit_juice = _upsert_category(
            db,
            slug="fruit-juice",
            parent_id=beverages.id,
            name="Fruit Juice",
            description="Single and mixed fruit juices.",
            is_active=True,
        )

        # Products
        orange_juice = _upsert_product(
            db,
            slug="migros-orange-juice-1l",
            category_id=fruit_juice.id,
            brand_id=migros.id,
            name="Migros Orange Juice 1L",
            description="100% orange juice, no added sugar.",
            is_active=True,
        )
        whole_milk = _upsert_product(
            db,
            slug="pinar-whole-milk-1l",
            category_id=dairy.id,
            brand_id=pinar.id,
            name="Pinar Whole Milk 1L",
            description="Pasteurized whole milk.",
            is_active=True,
        )

        # Variants
        orange_juice_variant = _upsert_variant(
            db,
            sku="MIG-OJ-1L",
            product_id=orange_juice.id,
            barcode="8690504012345",
            name="1 Liter",
            color=None,
            size="1L",
            price=Decimal("59.90"),
            compare_at_price=Decimal("64.90"),
            currency="TRY",
            weight_kg=Decimal("1.050"),
            is_active=True,
        )
        milk_variant = _upsert_variant(
            db,
            sku="PIN-MILK-1L",
            product_id=whole_milk.id,
            barcode="8690565012345",
            name="1 Liter",
            color=None,
            size="1L",
            price=Decimal("44.90"),
            compare_at_price=Decimal("47.90"),
            currency="TRY",
            weight_kg=Decimal("1.040"),
            is_active=True,
        )

        # Images
        _upsert_image(
            db,
            product_id=orange_juice.id,
            image_url="https://example.com/products/migros-orange-juice-1l/front.jpg",
            alt_text="Migros Orange Juice 1L front view",
            sort_order=0,
            is_primary=True,
        )
        _upsert_image(
            db,
            product_id=whole_milk.id,
            image_url="https://example.com/products/pinar-whole-milk-1l/front.jpg",
            alt_text="Pinar Whole Milk 1L front view",
            sort_order=0,
            is_primary=True,
        )

        # Inventory
        _upsert_inventory(
            db,
            variant_id=orange_juice_variant.id,
            quantity=180,
            reserved_quantity=12,
            reorder_level=40,
        )
        _upsert_inventory(
            db,
            variant_id=milk_variant.id,
            quantity=260,
            reserved_quantity=18,
            reorder_level=60,
        )

        db.commit()
        print("Catalog seed data upserted successfully.")
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError("Failed to seed catalog data. Ensure catalog migrations are applied first.") from exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_catalog()
