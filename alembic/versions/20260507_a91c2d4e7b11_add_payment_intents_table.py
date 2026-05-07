"""add payment intents table

Revision ID: a91c2d4e7b11
Revises: f2a1b6c9d001
Create Date: 2026-05-07 23:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.core.config import get_settings


# revision identifiers, used by Alembic.
revision = "a91c2d4e7b11"
down_revision = "f2a1b6c9d001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    def fk(table_name: str, column: str = "id") -> str:
        return f"{schema}.{table_name}.{column}" if schema else f"{table_name}.{column}"

    op.create_table(
        "payment_intents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("payment_method_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="requires_confirmation", nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_payment_method_id", sa.String(length=255), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], [fk("users")], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payment_method_id"], [fk("user_payment_methods")], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_id"], [fk("orders")], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index("ix_payment_intents_user_id", "payment_intents", ["user_id"], unique=False, schema=schema)
    op.create_index("ix_payment_intents_order_id", "payment_intents", ["order_id"], unique=False, schema=schema)
    op.create_index("ix_payment_intents_status", "payment_intents", ["status"], unique=False, schema=schema)


def downgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    op.drop_index("ix_payment_intents_status", table_name="payment_intents", schema=schema)
    op.drop_index("ix_payment_intents_order_id", table_name="payment_intents", schema=schema)
    op.drop_index("ix_payment_intents_user_id", table_name="payment_intents", schema=schema)
    op.drop_table("payment_intents", schema=schema)
