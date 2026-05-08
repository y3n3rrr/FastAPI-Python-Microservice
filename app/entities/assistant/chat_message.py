from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base, TimestampMixin

_SETTINGS = get_settings()
_SCHEMA = None if _SETTINGS.database_url.startswith("sqlite") else _SETTINGS.database_schema


def fk_table(table_name: str, column: str = "id") -> str:
    return f"{_SCHEMA}.{table_name}.{column}" if _SCHEMA else f"{table_name}.{column}"


class ChatMessage(TimestampMixin, Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_session_id", "session_id"),
        Index("ix_chat_messages_created_at", "created_at"),
        {"schema": _SCHEMA} if _SCHEMA else {},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey(fk_table("chat_sessions"), ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
