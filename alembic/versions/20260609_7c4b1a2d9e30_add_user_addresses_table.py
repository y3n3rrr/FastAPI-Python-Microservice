"""add user addresses table

Revision ID: 7c4b1a2d9e30
Revises: f9a7c3b2e114
Create Date: 2026-06-09 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.core.config import get_settings


# revision identifiers, used by Alembic.
revision = "7c4b1a2d9e30"
down_revision = "f9a7c3b2e114"
branch_labels = None
depends_on = None


def upgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    def fk(table_name: str, column: str = "id") -> str:
        return f"{schema}.{table_name}.{column}" if schema else f"{table_name}.{column}"

    op.create_table(
        "user_addresses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=True),
        sa.Column("address_type", sa.String(length=30), server_default="shipping", nullable=False),
        sa.Column("recipient_name", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=50), nullable=True),
        sa.Column("address_line1", sa.String(length=255), nullable=False),
        sa.Column("address_line2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("postal_code", sa.String(length=30), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("delivery_instructions", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], [fk("users")], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index("ix_user_addresses_address_type", "user_addresses", ["address_type"], unique=False, schema=schema)
    op.create_index("ix_user_addresses_user_id", "user_addresses", ["user_id"], unique=False, schema=schema)

    if settings.database_url.startswith("sqlite"):
        op.create_index(
            "uq_user_addresses_user_default_true",
            "user_addresses",
            ["user_id"],
            unique=True,
            sqlite_where=sa.text("is_default = 1"),
            schema=schema,
        )
    else:
        op.create_index(
            "uq_user_addresses_user_default_true",
            "user_addresses",
            ["user_id"],
            unique=True,
            postgresql_where=sa.text("is_default = true"),
            schema=schema,
        )


def downgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    op.drop_index("uq_user_addresses_user_default_true", table_name="user_addresses", schema=schema)
    op.drop_index("ix_user_addresses_user_id", table_name="user_addresses", schema=schema)
    op.drop_index("ix_user_addresses_address_type", table_name="user_addresses", schema=schema)
    op.drop_table("user_addresses", schema=schema)
