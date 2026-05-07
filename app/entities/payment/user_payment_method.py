from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

from app.core.config import get_settings

_SETTINGS = get_settings()

_SCHEMA = getattr(_SETTINGS, "database_schema", None)


def fk_table(table_name: str, column: str = "id") -> str:
    return f"{_SCHEMA}.{table_name}.{column}" if _SCHEMA else f"{table_name}.{column}"


class UserPaymentMethod(TimestampMixin, Base):
    __tablename__ = "user_payment_methods"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_payment_method_id",
            name="uq_user_payment_methods_provider_payment_method",
        ),
        Index("ix_user_payment_methods_user_id", "user_id"),
        Index("ix_user_payment_methods_provider_customer_id", "provider_customer_id"),
        {"schema": _SCHEMA} if _SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey(fk_table("users"), ondelete="CASCADE"),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    # Example: "stripe", "iyzico"

    provider_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    # Example: Stripe customer id: cus_xxx

    provider_payment_method_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    # Example: Stripe payment method id: pm_xxx
    # Or iyzico card token/reference

    card_brand: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    # visa, mastercard, amex

    card_last4: Mapped[str | None] = mapped_column(
        String(4),
        nullable=True,
    )

    exp_month: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    exp_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    cardholder_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    user: Mapped[object] = relationship(
        "User",
        back_populates="payment_methods",
    )
