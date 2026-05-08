"""enforce single default payment method per user

Revision ID: f2a1b6c9d001
Revises: c6b571a34159
Create Date: 2026-05-07 22:10:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.core.config import get_settings


# revision identifiers, used by Alembic.
revision = "f2a1b6c9d001"
down_revision = "c6b571a34159"
branch_labels = None
depends_on = None


def upgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema
    table_name = "user_payment_methods"

    qualified_table = f'"{schema}".{table_name}' if schema else table_name

    # Keep only the newest default payment method per user, clear older duplicates.
    op.execute(
        sa.text(
            f"""
            UPDATE {qualified_table}
            SET is_default = false
            WHERE is_default = true
              AND id NOT IN (
                SELECT MAX(id)
                FROM {qualified_table}
                WHERE is_default = true
                GROUP BY user_id
              )
            """
        )
    )

    if settings.database_url.startswith("sqlite"):
        op.create_index(
            "uq_user_payment_methods_user_default_true",
            table_name,
            ["user_id"],
            unique=True,
            sqlite_where=sa.text("is_default = 1"),
            schema=schema,
        )
    else:
        op.create_index(
            "uq_user_payment_methods_user_default_true",
            table_name,
            ["user_id"],
            unique=True,
            postgresql_where=sa.text("is_default = true"),
            schema=schema,
        )


def downgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    op.drop_index(
        "uq_user_payment_methods_user_default_true",
        table_name="user_payment_methods",
        schema=schema,
    )
