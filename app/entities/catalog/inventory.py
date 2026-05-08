
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.base import TimestampMixin
from app.entities.catalog.catalog import SCHEMA, fk_table

if TYPE_CHECKING:
    from app.entities.catalog.product_variant import ProductVariant

class Inventory(TimestampMixin, Base):
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("variant_id", name="uq_inventory_variant_id"),
        Index("ix_inventory_variant_id", "variant_id"),
        {"schema": SCHEMA} if SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    variant_id: Mapped[int] = mapped_column(
        ForeignKey(fk_table("product_variants"), ondelete="CASCADE"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    reserved_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    reorder_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    variant: Mapped["ProductVariant"] = relationship(
        "ProductVariant",
        back_populates="inventory",
    )
