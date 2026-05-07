
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.base import TimestampMixin
from app.entities.catalog import fk_table
from app.entities.catalog.catalog import SCHEMA

if TYPE_CHECKING:
    from app.entities.catalog.inventory import Inventory
    from app.entities.catalog.product import Product

class ProductVariant(TimestampMixin, Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("sku", name="uq_product_variants_sku"),
        Index("ix_product_variants_product_id", "product_id"),
        Index("ix_product_variants_sku", "sku"),
        {"schema": SCHEMA} if SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey(fk_table("products"), ondelete="CASCADE"),
        nullable=False,
    )

    sku: Mapped[str] = mapped_column(String(100), nullable=False)

    barcode: Mapped[str | None] = mapped_column(String(100), nullable=True)

    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size: Mapped[str | None] = mapped_column(String(100), nullable=True)

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    compare_at_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        server_default="USD",
    )

    weight_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="variants",
    )

    inventory: Mapped["Inventory | None"] = relationship(
        "Inventory",
        back_populates="variant",
        cascade="all, delete-orphan",
        uselist=False,
    )
