from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base, TimestampMixin
from app.entities.catalog.catalog import fk_table

if TYPE_CHECKING:
    from app.entities.card.card import Card
    from app.entities.catalog.product_variant import ProductVariant

_SETTINGS = get_settings()
_SCHEMA = None if _SETTINGS.database_url.startswith("sqlite") else _SETTINGS.database_schema


class CardItem(TimestampMixin, Base):
    __tablename__ = "card_items"
    __table_args__ = (
        UniqueConstraint("card_id", "product_variant_id", name="uq_card_items_card_variant"),
        Index("ix_card_items_card_id", "card_id"),
        Index("ix_card_items_product_variant_id", "product_variant_id"),
        {"schema": _SCHEMA} if _SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    card_id: Mapped[int] = mapped_column(
        ForeignKey(fk_table("cards"), ondelete="CASCADE"),
        nullable=False,
    )

    product_variant_id: Mapped[int] = mapped_column(
        ForeignKey(fk_table("product_variants"), ondelete="RESTRICT"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    unit_price_snapshot: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        server_default="USD",
    )

    is_selected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    card: Mapped["Card"] = relationship("Card", back_populates="items")

    product_variant: Mapped["ProductVariant"] = relationship("ProductVariant")
