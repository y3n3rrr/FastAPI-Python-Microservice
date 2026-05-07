"""add assistant chat tables

Revision ID: b7f3e2d9c114
Revises: a91c2d4e7b11
Create Date: 2026-05-07 23:35:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.core.config import get_settings


# revision identifiers, used by Alembic.
revision = "b7f3e2d9c114"
down_revision = "a91c2d4e7b11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    def fk(table_name: str, column: str = "id") -> str:
        return f"{schema}.{table_name}.{column}" if schema else f"{table_name}.{column}"

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], [fk("users")], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"], unique=False, schema=schema)

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], [fk("chat_sessions")], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"], unique=False, schema=schema)
    op.create_index("ix_chat_messages_created_at", "chat_messages", ["created_at"], unique=False, schema=schema)


def downgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    op.drop_index("ix_chat_messages_created_at", table_name="chat_messages", schema=schema)
    op.drop_index("ix_chat_messages_session_id", table_name="chat_messages", schema=schema)
    op.drop_table("chat_messages", schema=schema)
    op.drop_index("ix_chat_sessions_user_id", table_name="chat_sessions", schema=schema)
    op.drop_table("chat_sessions", schema=schema)
