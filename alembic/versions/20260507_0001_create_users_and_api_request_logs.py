"""create users and api_request_logs tables

Revision ID: 20260507_0001
Revises:
Create Date: 2026-05-07 10:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.core.config import get_settings

# revision identifiers, used by Alembic.
revision = "20260507_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    settings = get_settings()
    is_sqlite = settings.database_url.startswith("sqlite")
    schema = None if is_sqlite else settings.database_schema

    if schema:
        op.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{schema.replace(chr(34), chr(34) * 2)}"'))

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("surname", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("isactive", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_users_email"),
        schema=schema,
    )

    op.create_table(
        "api_request_logs",
        sa.Column("id", postgresql.BIGINT(), primary_key=True, autoincrement=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=True),
        sa.Column("method", sa.String(length=16), nullable=False),
        sa.Column("path", sa.String(length=2048), nullable=False),
        sa.Column("query_string", sa.Text(), nullable=True),
        sa.Column("route_template", sa.String(length=2048), nullable=True),
        sa.Column("client_ip", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("request_headers", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("request_body", sa.Text(), nullable=True),
        sa.Column("response_status_code", sa.Integer(), nullable=False),
        sa.Column("response_headers", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=schema,
    )

    if schema:
        op.create_index(
            "ix_api_request_logs_created_at",
            "api_request_logs",
            ["created_at"],
            unique=False,
            schema=schema,
        )
        op.create_index(
            "ix_api_request_logs_request_id",
            "api_request_logs",
            ["request_id"],
            unique=False,
            schema=schema,
        )


def downgrade() -> None:
    settings = get_settings()
    schema = None if settings.database_url.startswith("sqlite") else settings.database_schema

    if schema:
        op.drop_index("ix_api_request_logs_request_id", table_name="api_request_logs", schema=schema)
        op.drop_index("ix_api_request_logs_created_at", table_name="api_request_logs", schema=schema)
    op.drop_table("api_request_logs", schema=schema)
    op.drop_table("users", schema=schema)
