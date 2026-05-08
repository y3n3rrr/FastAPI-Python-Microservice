from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import get_session_factory
from app.entities.payment.user_payment_method import UserPaymentMethod
from app.entities.user import User


def _get_or_create_user_1(db: Session) -> User:
    user = db.get(User, 1)
    if user is not None:
        return user

    user = User(
        id=1,
        name="Payment",
        surname="Seeder",
        email="payment.seed@example.com",
        password_hash=hash_password("seedpassword"),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def _upsert_payment_method(
    db: Session,
    *,
    user_id: int,
    provider_payment_method_id: str,
    provider_customer_id: str,
    card_brand: str,
    card_last4: str,
    is_default: bool,
) -> UserPaymentMethod:
    payment_method = db.scalar(
        select(UserPaymentMethod).where(
            UserPaymentMethod.user_id == user_id,
            UserPaymentMethod.provider == "stripe",
            UserPaymentMethod.provider_payment_method_id == provider_payment_method_id,
        )
    )
    if payment_method is None:
        payment_method = UserPaymentMethod(
            user_id=user_id,
            provider="stripe",
            provider_customer_id=provider_customer_id,
            provider_payment_method_id=provider_payment_method_id,
            card_brand=card_brand,
            card_last4=card_last4,
            exp_month=12,
            exp_year=2030,
            cardholder_name="Payment Seeder",
            is_default=is_default,
            is_active=True,
        )
        db.add(payment_method)
        db.flush()
        return payment_method

    payment_method.provider_customer_id = provider_customer_id
    payment_method.card_brand = card_brand
    payment_method.card_last4 = card_last4
    payment_method.exp_month = 12
    payment_method.exp_year = 2030
    payment_method.cardholder_name = "Payment Seeder"
    payment_method.is_default = is_default
    payment_method.is_active = True
    return payment_method


def seed_payment_method() -> None:
    session_factory = get_session_factory()
    db = session_factory()

    try:
        user = _get_or_create_user_1(db)
        _upsert_payment_method(
            db,
            user_id=user.id,
            provider_payment_method_id="pm_seed_001",
            provider_customer_id="cus_seed_001",
            card_brand="visa",
            card_last4="4242",
            is_default=True,
        )
        _upsert_payment_method(
            db,
            user_id=user.id,
            provider_payment_method_id="pm_seed_002",
            provider_customer_id="cus_seed_001",
            card_brand="mastercard",
            card_last4="4444",
            is_default=False,
        )
        _upsert_payment_method(
            db,
            user_id=user.id,
            provider_payment_method_id="pm_seed_003",
            provider_customer_id="cus_seed_001",
            card_brand="amex",
            card_last4="0005",
            is_default=False,
        )
        db.commit()
        print("Payment method seed data upserted successfully (3 methods).")
    except SQLAlchemyError as exc:
        db.rollback()
        raise RuntimeError("Failed to seed payment method data. Ensure payment migrations are applied first.") from exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_payment_method()
