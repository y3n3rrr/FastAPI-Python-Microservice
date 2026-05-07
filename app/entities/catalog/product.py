from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
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
    from app.entities.catalog.brand import Brand
    from app.entities.catalog.category import Category
    from app.entities.catalog.product_image import ProductImage
    from app.entities.catalog.product_variant import ProductVariant

class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_products_slug"),
        Index("ix_products_name", "name"),
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_brand_id", "brand_id"),
        {"schema": SCHEMA} if SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey(fk_table("categories"), ondelete="SET NULL"),
        nullable=True,
    )

    brand_id: Mapped[int | None] = mapped_column(
        ForeignKey(fk_table("brands"), ondelete="SET NULL"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="products",
    )

    brand: Mapped["Brand | None"] = relationship(
        "Brand",
        back_populates="products",
    )

    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
    )
