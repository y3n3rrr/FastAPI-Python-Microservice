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
        # 12 brands
        brand_seeds = [
            ("migros", "Migros"),
            ("pinar", "Pinar"),
            ("ulker", "Ulker"),
            ("eti", "Eti"),
            ("dimes", "Dimes"),
            ("sutas", "Sutas"),
            ("ayaydin", "Ayaydin"),
            ("superfresh", "SuperFresh"),
            ("tadim", "Tadim"),
            ("komili", "Komili"),
            ("ipek", "Ipek"),
            ("dogadan", "Dogadan"),
        ]
        brands_by_slug: dict[str, Brand] = {}
        for slug, name in brand_seeds:
            brands_by_slug[slug] = _upsert_brand(
                db,
                slug=slug,
                name=name,
                description=f"{name} branded grocery products.",
                logo_url=f"https://example.com/brands/{slug}.png",
                is_active=True,
            )

        # 24 categories (8 parent + 16 child)
        parent_categories = [
            ("beverages", "Beverages"),
            ("dairy", "Dairy"),
            ("snacks", "Snacks"),
            ("frozen-food", "Frozen Food"),
            ("breakfast", "Breakfast"),
            ("household", "Household"),
            ("bakery", "Bakery"),
            ("personal-care", "Personal Care"),
        ]
        categories_by_slug: dict[str, Category] = {}
        for slug, name in parent_categories:
            categories_by_slug[slug] = _upsert_category(
                db,
                slug=slug,
                parent_id=None,
                name=name,
                description=f"{name} category.",
                is_active=True,
            )

        child_categories = [
            ("fruit-juice", "Fruit Juice", "beverages"),
            ("sparkling-water", "Sparkling Water", "beverages"),
            ("milk", "Milk", "dairy"),
            ("yogurt", "Yogurt", "dairy"),
            ("chips", "Chips", "snacks"),
            ("nuts", "Nuts", "snacks"),
            ("frozen-vegetables", "Frozen Vegetables", "frozen-food"),
            ("frozen-pizza", "Frozen Pizza", "frozen-food"),
            ("cereal", "Cereal", "breakfast"),
            ("jams", "Jams", "breakfast"),
            ("detergent", "Detergent", "household"),
            ("cleaners", "Cleaners", "household"),
            ("bread", "Bread", "bakery"),
            ("pastry", "Pastry", "bakery"),
            ("shampoo", "Shampoo", "personal-care"),
            ("soap", "Soap", "personal-care"),
        ]
        leaf_category_slugs: list[str] = []
        for slug, name, parent_slug in child_categories:
            categories_by_slug[slug] = _upsert_category(
                db,
                slug=slug,
                parent_id=categories_by_slug[parent_slug].id,
                name=name,
                description=f"{name} sub-category.",
                is_active=True,
            )
            leaf_category_slugs.append(slug)

        brand_slugs = list(brands_by_slug.keys())
        products_by_slug: dict[str, Product] = {}

        # 60 products
        for i in range(1, 61):
            brand_slug = brand_slugs[(i - 1) % len(brand_slugs)]
            category_slug = leaf_category_slugs[(i - 1) % len(leaf_category_slugs)]
            product_slug = f"{brand_slug}-product-{i:03d}"
            product = _upsert_product(
                db,
                slug=product_slug,
                category_id=categories_by_slug[category_slug].id,
                brand_id=brands_by_slug[brand_slug].id,
                name=f"{brands_by_slug[brand_slug].name} {categories_by_slug[category_slug].name} Item {i:03d}",
                description=f"Seeded product #{i:03d} for catalog testing.",
                is_active=True,
            )
            products_by_slug[product_slug] = product

            _upsert_image(
                db,
                product_id=product.id,
                image_url=f"https://example.com/products/{product_slug}/front.jpg",
                alt_text=f"{product.name} front view",
                sort_order=0,
                is_primary=True,
            )

        # 120 variants + 120 inventories (2 variants per product)
        variant_counter = 0
        for idx, (product_slug, product) in enumerate(products_by_slug.items(), start=1):
            for pack in ("S", "L"):
                variant_counter += 1
                sku = f"SKU-{idx:03d}-{pack}"
                base_price = Decimal("19.90") + Decimal(idx % 17) * Decimal("2.10")
                price = base_price if pack == "S" else base_price + Decimal("9.00")
                compare_at_price = price + Decimal("4.00")
                size = "500ml" if pack == "S" else "1L"
                weight = Decimal("0.550") if pack == "S" else Decimal("1.050")
                barcode = f"8699{variant_counter:08d}"

                variant = _upsert_variant(
                    db,
                    sku=sku,
                    product_id=product.id,
                    barcode=barcode,
                    name=f"{size} Pack",
                    color=None,
                    size=size,
                    price=price,
                    compare_at_price=compare_at_price,
                    currency="TRY",
                    weight_kg=weight,
                    is_active=True,
                )

                quantity = 80 + (variant_counter % 140)
                reserved = variant_counter % 10
                reorder = 20 + (variant_counter % 15)
                _upsert_inventory(
                    db,
                    variant_id=variant.id,
                    quantity=quantity,
                    reserved_quantity=reserved,
                    reorder_level=reorder,
                )

        db.commit()
        print("Catalog seed data upserted successfully (60 products, 120 variants, 120 inventories).")
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError("Failed to seed catalog data. Ensure catalog migrations are applied first.") from exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_catalog()
