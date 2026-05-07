from decimal import Decimal
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
from app.entities.user import TimestampMixin
from app.core.config import get_settings


_SCHEMA = getattr(get_settings(), "DB_SCHEMA", None)


def fk_table(table_name: str, column: str = "id") -> str:
    """
    Helps create schema-aware foreign keys.

    If DB schema is configured:
        ecommerce.products.id

    Otherwise:
        products.id
    """
    return f"{_SCHEMA}.{table_name}.{column}" if _SCHEMA else f"{table_name}.{column}"