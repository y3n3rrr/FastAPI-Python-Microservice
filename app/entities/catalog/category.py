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
    from app.entities.catalog.product import Product

class Category(TimestampMixin, Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_categories_slug"),
        Index("ix_categories_name", "name"),
        {"schema": SCHEMA} if SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey(fk_table("categories"), ondelete="SET NULL"),
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

    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children",
    )

    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
    )
