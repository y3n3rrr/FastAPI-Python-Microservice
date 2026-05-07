from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import get_session_factory
from app.entities.card.card import Card
from app.entities.card.card_item import CardItem
from app.entities.catalog.product_variant import ProductVariant
from app.entities.user import User


def _get_or_create_user_1(db: Session) -> User:
    user = db.get(User, 1)
    if user is not None:
        return user

    user = User(
        id=1,
        name="Card",
        surname="Seeder",
        email="card.seed@example.com",
        password_hash=hash_password("seedpassword"),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def _upsert_card(db: Session, *, user_id: int, status: str, currency: str) -> Card:
    card = db.scalar(
        select(Card).where(
            Card.user_id == user_id,
            Card.status == status,
            Card.currency == currency,
        )
    )
    if card is None:
        card = Card(user_id=user_id, status=status, currency=currency)
        db.add(card)
        db.flush()
        return card

    card.status = status
    card.currency = currency
    return card


def _upsert_card_item(
    db: Session,
    *,
    card_id: int,
    product_variant_id: int,
    quantity: int,
    unit_price_snapshot: Decimal,
    currency: str,
    is_selected: bool,
) -> CardItem:
    card_item = db.scalar(
        select(CardItem).where(
            CardItem.card_id == card_id,
            CardItem.product_variant_id == product_variant_id,
        )
    )
    if card_item is None:
        card_item = CardItem(
            card_id=card_id,
            product_variant_id=product_variant_id,
            quantity=quantity,
            unit_price_snapshot=unit_price_snapshot,
            currency=currency,
            is_selected=is_selected,
        )
        db.add(card_item)
        db.flush()
        return card_item

    card_item.quantity = quantity
    card_item.unit_price_snapshot = unit_price_snapshot
    card_item.currency = currency
    card_item.is_selected = is_selected
    return card_item


def seed_card() -> None:
    session_factory = get_session_factory()
    db = session_factory()

    try:
        user = _get_or_create_user_1(db)

        variant = db.scalar(select(ProductVariant).order_by(ProductVariant.id))
        if variant is None:
            raise RuntimeError(
                "No product variant found. Run scripts/seed_catalog.py first to create catalog seed data."
            )

        card = _upsert_card(
            db,
            user_id=user.id,
            status="active",
            currency=variant.currency,
        )

        _upsert_card_item(
            db,
            card_id=card.id,
            product_variant_id=variant.id,
            quantity=2,
            unit_price_snapshot=variant.price,
            currency=variant.currency,
            is_selected=True,
        )

        db.commit()
        print("Card seed data upserted successfully.")
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError("Failed to seed card data. Ensure card migrations are applied first.") from exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_card()
