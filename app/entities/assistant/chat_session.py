from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base, TimestampMixin

_SETTINGS = get_settings()
_SCHEMA = None if _SETTINGS.database_url.startswith("sqlite") else _SETTINGS.database_schema


def fk_table(table_name: str, column: str = "id") -> str:
    return f"{_SCHEMA}.{table_name}.{column}" if _SCHEMA else f"{table_name}.{column}"


class ChatSession(TimestampMixin, Base):
    __tablename__ = "chat_sessions"
    __table_args__ = (
        Index("ix_chat_sessions_user_id", "user_id"),
        {"schema": _SCHEMA} if _SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(fk_table("users"), ondelete="CASCADE"), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    user: Mapped[object] = relationship("User")
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )
