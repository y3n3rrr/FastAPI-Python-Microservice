"""add checkout idempotency key

Revision ID: d3f4e5a6b712
Revises: b7f3e2d9c114
Create Date: 2026-05-08 00:10:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.core.config import get_settings


# revision identifiers, used by Alembic.
revision = "d3f4e5a6b712"
down_revision = "b7f3e2d9c114"
branch_labels = None
depends_on = None


def upgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema
    qualified_table = f'"{schema}".payment_intents' if schema else "payment_intents"

    op.add_column(
        "payment_intents",
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        schema=schema,
    )

    # Backfill legacy rows to keep migration safe on non-empty databases.
    op.execute(sa.text(f"UPDATE {qualified_table} SET idempotency_key = 'legacy-' || id WHERE idempotency_key IS NULL"))

    with op.batch_alter_table("payment_intents", schema=schema) as batch_op:
        batch_op.alter_column("idempotency_key", existing_type=sa.String(length=128), nullable=False)

    op.create_index(
        "uq_payment_intents_user_idempotency_key",
        "payment_intents",
        ["user_id", "idempotency_key"],
        unique=True,
        schema=schema,
    )


def downgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    op.drop_index("uq_payment_intents_user_idempotency_key", table_name="payment_intents", schema=schema)
    op.drop_column("payment_intents", "idempotency_key", schema=schema)
