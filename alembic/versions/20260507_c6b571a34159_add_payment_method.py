"""add payment method

Revision ID: c6b571a34159
Revises: 939944e00b75
Create Date: 2026-05-07 20:55:43.003409
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.core.config import get_settings

# revision identifiers, used by Alembic.
revision = 'c6b571a34159'
down_revision = '939944e00b75'
branch_labels = None
depends_on = None


def upgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    def fk(table_name: str, column: str = "id") -> str:
        return f"{schema}.{table_name}.{column}" if schema else f"{table_name}.{column}"

    op.create_table('user_payment_methods',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('provider_customer_id', sa.String(length=255), nullable=True),
    sa.Column('provider_payment_method_id', sa.String(length=255), nullable=False),
    sa.Column('card_brand', sa.String(length=50), nullable=True),
    sa.Column('card_last4', sa.String(length=4), nullable=True),
    sa.Column('exp_month', sa.Integer(), nullable=True),
    sa.Column('exp_year', sa.Integer(), nullable=True),
    sa.Column('cardholder_name', sa.String(length=255), nullable=True),
    sa.Column('is_default', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], [fk("users")], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('provider', 'provider_payment_method_id', name='uq_user_payment_methods_provider_payment_method'),
    schema=schema
    )
    op.create_index('ix_user_payment_methods_provider_customer_id', 'user_payment_methods', ['provider_customer_id'], unique=False, schema=schema)
    op.create_index('ix_user_payment_methods_user_id', 'user_payment_methods', ['user_id'], unique=False, schema=schema)


def downgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    op.drop_index('ix_user_payment_methods_user_id', table_name='user_payment_methods', schema=schema)
    op.drop_index('ix_user_payment_methods_provider_customer_id', table_name='user_payment_methods', schema=schema)
    op.drop_table('user_payment_methods', schema=schema)
