from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import get_session_factory
from app.entities.catalog.product_variant import ProductVariant
from app.entities.order.order import Order
from app.entities.order.order_item import OrderItem
from app.entities.order.order_status_history import OrderStatusHistory
from app.entities.user import User


def _get_or_create_user_1(db: Session) -> User:
    user = db.get(User, 1)
    if user is not None:
        return user

    user = User(
        id=1,
        name="Order",
        surname="Seeder",
        email="order.seed@example.com",
        password_hash=hash_password("seedpassword"),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def _upsert_order(
    db: Session,
    *,
    user_id: int,
    status: str,
    currency: str,
    total_amount: Decimal,
    note: str | None,
) -> Order:
    order = db.scalar(
        select(Order).where(
            Order.user_id == user_id,
            Order.status == status,
            Order.currency == currency,
        )
    )
    if order is None:
        order = Order(
            user_id=user_id,
            status=status,
            currency=currency,
            total_amount=total_amount,
            note=note,
        )
        db.add(order)
        db.flush()
        return order

    order.total_amount = total_amount
    order.note = note
    return order


def _upsert_order_item(
    db: Session,
    *,
    order_id: int,
    product_variant_id: int,
    quantity: int,
    unit_price_snapshot: Decimal,
    line_total: Decimal,
    currency: str,
) -> OrderItem:
    order_item = db.scalar(
        select(OrderItem).where(
            OrderItem.order_id == order_id,
            OrderItem.product_variant_id == product_variant_id,
        )
    )
    if order_item is None:
        order_item = OrderItem(
            order_id=order_id,
            product_variant_id=product_variant_id,
            quantity=quantity,
            unit_price_snapshot=unit_price_snapshot,
            line_total=line_total,
            currency=currency,
        )
        db.add(order_item)
        db.flush()
        return order_item

    order_item.quantity = quantity
    order_item.unit_price_snapshot = unit_price_snapshot
    order_item.line_total = line_total
    order_item.currency = currency
    return order_item


def _upsert_status_history(
    db: Session,
    *,
    order_id: int,
    from_status: str | None,
    to_status: str,
    changed_by_user_id: int | None,
    note: str | None,
) -> OrderStatusHistory:
    history = db.scalar(
        select(OrderStatusHistory).where(
            OrderStatusHistory.order_id == order_id,
            OrderStatusHistory.to_status == to_status,
        )
    )
    if history is None:
        history = OrderStatusHistory(
            order_id=order_id,
            from_status=from_status,
            to_status=to_status,
            changed_by_user_id=changed_by_user_id,
            note=note,
        )
        db.add(history)
        db.flush()
        return history

    history.from_status = from_status
    history.changed_by_user_id = changed_by_user_id
    history.note = note
    return history


def seed_order() -> None:
    session_factory = get_session_factory()
    db = session_factory()

    try:
        user = _get_or_create_user_1(db)

        variant = db.scalar(select(ProductVariant).order_by(ProductVariant.id))
        if variant is None:
            raise RuntimeError(
                "No product variant found. Run scripts/seed_catalog.py first to create catalog seed data."
            )

        quantity = 2
        line_total = (variant.price or Decimal("0.00")) * quantity

        order = _upsert_order(
            db,
            user_id=user.id,
            status="pending",
            currency=variant.currency,
            total_amount=line_total,
            note="Seed order for integration checks.",
        )

        _upsert_order_item(
            db,
            order_id=order.id,
            product_variant_id=variant.id,
            quantity=quantity,
            unit_price_snapshot=variant.price,
            line_total=line_total,
            currency=variant.currency,
        )

        _upsert_status_history(
            db,
            order_id=order.id,
            from_status=None,
            to_status="pending",
            changed_by_user_id=user.id,
            note="Order created.",
        )

        db.commit()
        print("Order seed data upserted successfully.")
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError("Failed to seed order data. Ensure order migrations are applied first.") from exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_order()
