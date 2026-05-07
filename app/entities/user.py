from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base, TimestampMixin
from app.entities.payment import UserPaymentMethod

_SETTINGS = get_settings()
_SCHEMA = None if _SETTINGS.database_url.startswith("sqlite") else _SETTINGS.database_schema


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = {"schema": _SCHEMA} if _SCHEMA else {}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    surname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column("password", String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column("isactive", Boolean, nullable=False, default=False)

    payment_methods: Mapped[list["UserPaymentMethod"]] = relationship(
        "UserPaymentMethod",
        back_populates="user",
        cascade="all, delete-orphan",
    )
