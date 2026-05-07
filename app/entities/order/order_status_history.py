from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base, TimestampMixin
from app.entities.catalog.catalog import fk_table

if TYPE_CHECKING:
    from app.entities.order.order import Order
    from app.entities.user import User

_SETTINGS = get_settings()
_SCHEMA = None if _SETTINGS.database_url.startswith("sqlite") else _SETTINGS.database_schema


class OrderStatusHistory(TimestampMixin, Base):
    __tablename__ = "order_status_history"
    __table_args__ = (
        Index("ix_order_status_history_order_id", "order_id"),
        Index("ix_order_status_history_to_status", "to_status"),
        {"schema": _SCHEMA} if _SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey(fk_table("orders"), ondelete="CASCADE"),
        nullable=False,
    )

    from_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)

    changed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey(fk_table("users"), ondelete="SET NULL"),
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="status_history")
    changed_by_user: Mapped["User | None"] = relationship("User")
