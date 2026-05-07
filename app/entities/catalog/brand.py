from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.base import TimestampMixin
from app.entities.catalog.catalog import SCHEMA, fk_table

if TYPE_CHECKING:
    from app.entities.catalog.product import Product

class Brand(TimestampMixin, Base):
    __tablename__ = "brands"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_brands_slug"),
        Index("ix_brands_name", "name"),
        {"schema": SCHEMA} if SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="brand",
    )
