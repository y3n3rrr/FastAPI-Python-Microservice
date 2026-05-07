from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base, TimestampMixin
from app.entities.catalog.catalog import fk_table

if TYPE_CHECKING:
    from app.entities.cart.cart_item import CartItem
    from app.entities.user import User

_SETTINGS = get_settings()
_SCHEMA = None if _SETTINGS.database_url.startswith("sqlite") else _SETTINGS.database_schema


class Cart(TimestampMixin, Base):
    __tablename__ = "carts"
    __table_args__ = (
        Index("ix_carts_user_id", "user_id"),
        Index("ix_carts_status", "status"),
        {"schema": _SCHEMA} if _SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey(fk_table("users"), ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="active",
        server_default="active",
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        server_default="USD",
    )

    user: Mapped["User"] = relationship("User")

    items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
    )
