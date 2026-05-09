from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import get_session_factory
from app.entities.cart.cart import Cart
from app.entities.cart.cart_item import CartItem
from app.entities.catalog.product_variant import ProductVariant
from app.entities.user import User


def _get_or_create_user_1(db: Session) -> User:
    user = db.get(User, 1)
    if user is not None:
        return user

    user = User(
        id=1,
        name="Cart",
        surname="Seeder",
        email="cart.seed@example.com",
        password_hash=hash_password("seedpassword"),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def _upsert_cart(db: Session, *, user_id: int, status: str, currency: str) -> Cart:
    cart = db.scalar(
        select(Cart).where(
            Cart.user_id == user_id,
            Cart.status == status,
            Cart.currency == currency,
        )
    )
    if cart is None:
        cart = Cart(user_id=user_id, status=status, currency=currency)
        db.add(cart)
        db.flush()
        return cart

    cart.status = status
    cart.currency = currency
    return cart


def _upsert_cart_item(
    db: Session,
    *,
    cart_id: int,
    product_variant_id: int,
    quantity: int,
    unit_price_snapshot: Decimal,
    currency: str,
    is_selected: bool,
) -> CartItem:
    cart_item = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_variant_id == product_variant_id,
        )
    )
    if cart_item is None:
        cart_item = CartItem(
            cart_id=cart_id,
            product_variant_id=product_variant_id,
            quantity=quantity,
            unit_price_snapshot=unit_price_snapshot,
            currency=currency,
            is_selected=is_selected,
        )
        db.add(cart_item)
        db.flush()
        return cart_item

    cart_item.quantity = quantity
    cart_item.unit_price_snapshot = unit_price_snapshot
    cart_item.currency = currency
    cart_item.is_selected = is_selected
    return cart_item


def seed_cart() -> None:
    session_factory = get_session_factory()
    db = session_factory()

    try:
        user = _get_or_create_user_1(db)

        variants = list(
            db.scalars(
                select(ProductVariant)
                .where(ProductVariant.is_active.is_(True))
                .order_by(ProductVariant.id)
                .limit(8)
            )
        )
        if not variants:
            raise RuntimeError(
                "No product variant found. Run scripts/seed_catalog.py first to create catalog seed data."
            )

        cart = _upsert_cart(
            db,
            user_id=user.id,
            status="active",
            currency=variants[0].currency,
        )

        for index, variant in enumerate(variants, start=1):
            _upsert_cart_item(
                db,
                cart_id=cart.id,
                product_variant_id=variant.id,
                quantity=(index % 4) + 1,
                unit_price_snapshot=variant.price,
                currency=variant.currency,
                is_selected=(index % 3 != 0),
            )

        db.commit()
        print(f"Cart seed data upserted successfully ({len(variants)} cart items).")
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError("Failed to seed cart data. Ensure cart migrations are applied first.") from exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_cart()
