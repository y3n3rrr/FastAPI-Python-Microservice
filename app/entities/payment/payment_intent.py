from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base, TimestampMixin

_SETTINGS = get_settings()
_SCHEMA = None if _SETTINGS.database_url.startswith("sqlite") else _SETTINGS.database_schema


def fk_table(table_name: str, column: str = "id") -> str:
    return f"{_SCHEMA}.{table_name}.{column}" if _SCHEMA else f"{table_name}.{column}"


class PaymentIntent(TimestampMixin, Base):
    __tablename__ = "payment_intents"
    __table_args__ = (
        Index("ix_payment_intents_user_id", "user_id"),
        Index("ix_payment_intents_order_id", "order_id"),
        Index("ix_payment_intents_status", "status"),
        Index("uq_payment_intents_user_idempotency_key", "user_id", "idempotency_key", unique=True),
        {"schema": _SCHEMA} if _SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey(fk_table("users"), ondelete="CASCADE"),
        nullable=False,
    )

    payment_method_id: Mapped[int] = mapped_column(
        ForeignKey(fk_table("user_payment_methods"), ondelete="RESTRICT"),
        nullable=False,
    )

    order_id: Mapped[int | None] = mapped_column(
        ForeignKey(fk_table("orders"), ondelete="SET NULL"),
        nullable=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="requires_confirmation",
        server_default="requires_confirmation",
    )

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_payment_method_id: Mapped[str] = mapped_column(String(255), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[object] = relationship("User")
    payment_method: Mapped[object] = relationship("UserPaymentMethod")
    order: Mapped[object] = relationship("Order")
