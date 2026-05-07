from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import get_session_factory
from app.entities.catalog.brand import Brand
from app.entities.catalog.category import Category
from app.entities.catalog.inventory import Inventory
from app.entities.catalog.product import Product
from app.entities.catalog.product_variant import ProductVariant
from app.entities.order.order import Order
from app.entities.order.order_item import OrderItem
from app.entities.payment.payment_intent import PaymentIntent
from app.entities.payment.user_payment_method import UserPaymentMethod
from app.entities.user import User


def _get_or_create_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.email == "payment.intent.seed@example.com"))
    if user is not None:
        return user

    user = User(
        name="PaymentIntent",
        surname="Seeder",
        email="payment.intent.seed@example.com",
        password_hash=hash_password("seedpassword"),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def _get_or_create_default_payment_method(db: Session, *, user_id: int) -> UserPaymentMethod:
    payment_method = db.scalar(
        select(UserPaymentMethod).where(
            UserPaymentMethod.user_id == user_id,
            UserPaymentMethod.provider == "stripe",
            UserPaymentMethod.provider_payment_method_id == "pm_intent_seed_001",
        )
    )
    if payment_method is not None:
        payment_method.is_default = True
        payment_method.is_active = True
        return payment_method

    payment_method = UserPaymentMethod(
        user_id=user_id,
        provider="stripe",
        provider_customer_id="cus_intent_seed_001",
        provider_payment_method_id="pm_intent_seed_001",
        card_brand="visa",
        card_last4="4242",
        exp_month=12,
        exp_year=2030,
        cardholder_name="Payment Intent Seeder",
        is_default=True,
        is_active=True,
    )
    db.add(payment_method)
    db.flush()
    return payment_method


def _get_or_create_catalog_and_variant(db: Session) -> ProductVariant:
    brand = db.scalar(select(Brand).where(Brand.slug == "payment-intent-seed-brand"))
    if brand is None:
        brand = Brand(
            name="Payment Intent Seed Brand",
            slug="payment-intent-seed-brand",
            description="Brand for payment intent seed data",
            logo_url="https://example.com/payment-intent-seed-brand.png",
            is_active=True,
        )
        db.add(brand)
        db.flush()

    category = db.scalar(select(Category).where(Category.slug == "payment-intent-seed-category"))
    if category is None:
        category = Category(
            parent_id=None,
            name="Payment Intent Seed Category",
            slug="payment-intent-seed-category",
            description="Category for payment intent seed data",
            is_active=True,
        )
        db.add(category)
        db.flush()

    product = db.scalar(select(Product).where(Product.slug == "payment-intent-seed-product-1l"))
    if product is None:
        product = Product(
            category_id=category.id,
            brand_id=brand.id,
            name="Payment Intent Seed Product 1L",
            slug="payment-intent-seed-product-1l",
            description="Product for payment intent seed data",
            is_active=True,
        )
        db.add(product)
        db.flush()

    variant = db.scalar(select(ProductVariant).where(ProductVariant.sku == "SKU-PAYMENT-INTENT-SEED-001"))
    if variant is None:
        variant = ProductVariant(
            product_id=product.id,
            sku="SKU-PAYMENT-INTENT-SEED-001",
            barcode="8690000000401",
            name="1L",
            color=None,
            size="1L",
            price=Decimal("49.90"),
            compare_at_price=Decimal("54.90"),
            currency="TRY",
            weight_kg=Decimal("1.050"),
            is_active=True,
        )
        db.add(variant)
        db.flush()

    inventory = db.scalar(select(Inventory).where(Inventory.variant_id == variant.id))
    if inventory is None:
        inventory = Inventory(
            variant_id=variant.id,
            quantity=20,
            reserved_quantity=0,
            reorder_level=3,
        )
        db.add(inventory)
        db.flush()

    return variant


def _get_or_create_order(db: Session, *, user_id: int, variant: ProductVariant) -> tuple[Order, OrderItem]:
    order = db.scalar(
        select(Order).where(
            Order.user_id == user_id,
            Order.note == "Payment intent seed order",
        )
    )
    if order is None:
        order = Order(
            user_id=user_id,
            status="confirmed",
            currency=variant.currency,
            total_amount=Decimal("99.80"),
            note="Payment intent seed order",
        )
        db.add(order)
        db.flush()

    order_item = db.scalar(
        select(OrderItem).where(
            OrderItem.order_id == order.id,
            OrderItem.product_variant_id == variant.id,
        )
    )
    if order_item is None:
        order_item = OrderItem(
            order_id=order.id,
            product_variant_id=variant.id,
            quantity=2,
            unit_price_snapshot=variant.price,
            line_total=Decimal("99.80"),
            currency=variant.currency,
        )
        db.add(order_item)
        db.flush()

    return order, order_item


def _upsert_payment_intent(
    db: Session,
    *,
    user_id: int,
    payment_method_id: int,
    order_id: int,
    currency: str,
) -> PaymentIntent:
    payment_intent = db.scalar(
        select(PaymentIntent).where(
            PaymentIntent.user_id == user_id,
            PaymentIntent.provider_payment_method_id == "pm_intent_seed_001",
            PaymentIntent.order_id == order_id,
        )
    )
    if payment_intent is None:
        payment_intent = PaymentIntent(
            user_id=user_id,
            payment_method_id=payment_method_id,
            order_id=order_id,
            amount=Decimal("99.80"),
            currency=currency,
            status="authorized",
            provider="stripe",
            provider_payment_method_id="pm_intent_seed_001",
            failure_reason=None,
        )
        db.add(payment_intent)
        db.flush()
        return payment_intent

    payment_intent.payment_method_id = payment_method_id
    payment_intent.amount = Decimal("99.80")
    payment_intent.currency = currency
    payment_intent.status = "authorized"
    payment_intent.provider = "stripe"
    payment_intent.failure_reason = None
    return payment_intent


def seed_payment_intent() -> None:
    session_factory = get_session_factory()
    db = session_factory()

    try:
        user = _get_or_create_user(db)
        payment_method = _get_or_create_default_payment_method(db, user_id=user.id)
        variant = _get_or_create_catalog_and_variant(db)
        order, _ = _get_or_create_order(db, user_id=user.id, variant=variant)
        _upsert_payment_intent(
            db,
            user_id=user.id,
            payment_method_id=payment_method.id,
            order_id=order.id,
            currency=variant.currency,
        )
        db.commit()
        print("Payment intent seed data upserted successfully.")
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError("Failed to seed payment intent data. Ensure migrations are applied first.") from exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_payment_intent()
