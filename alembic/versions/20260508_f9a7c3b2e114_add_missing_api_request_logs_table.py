"""add missing api_request_logs table

Revision ID: f9a7c3b2e114
Revises: d3f4e5a6b712
Create Date: 2026-05-08 11:05:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.core.config import get_settings


# revision identifiers, used by Alembic.
revision = "f9a7c3b2e114"
down_revision = "d3f4e5a6b712"
branch_labels = None
depends_on = None


def upgrade() -> None:
    settings = get_settings()
    is_sqlite = settings.database_url.startswith("sqlite")
    schema = None if is_sqlite else settings.database_schema

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("api_request_logs", schema=schema):
        if is_sqlite:
            request_id_type: sa.types.TypeEngine = sa.String(length=36)
            client_ip_type: sa.types.TypeEngine = sa.String(length=64)
            request_headers_type: sa.types.TypeEngine = sa.JSON()
            response_headers_type: sa.types.TypeEngine = sa.JSON()
        else:
            request_id_type = postgresql.UUID(as_uuid=False)
            client_ip_type = postgresql.INET()
            request_headers_type = postgresql.JSONB(astext_type=sa.Text())
            response_headers_type = postgresql.JSONB(astext_type=sa.Text())

        op.create_table(
            "api_request_logs",
            sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True, nullable=False),
            sa.Column("request_id", request_id_type, nullable=False),
            sa.Column("user_id", sa.String(length=255), nullable=True),
            sa.Column("method", sa.String(length=16), nullable=False),
            sa.Column("path", sa.String(length=2048), nullable=False),
            sa.Column("query_string", sa.Text(), nullable=True),
            sa.Column("route_template", sa.String(length=2048), nullable=True),
            sa.Column("client_ip", client_ip_type, nullable=True),
            sa.Column("user_agent", sa.Text(), nullable=True),
            sa.Column("request_headers", request_headers_type, nullable=True),
            sa.Column("request_body", sa.Text(), nullable=True),
            sa.Column("response_status_code", sa.Integer(), nullable=False),
            sa.Column("response_headers", response_headers_type, nullable=True),
            sa.Column("response_body", sa.Text(), nullable=True),
            sa.Column("duration_ms", sa.Integer(), nullable=False),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            schema=schema,
        )

    index_names = {index["name"] for index in inspector.get_indexes("api_request_logs", schema=schema)}
    if "ix_api_request_logs_created_at" not in index_names:
        op.create_index(
            "ix_api_request_logs_created_at",
            "api_request_logs",
            ["created_at"],
            unique=False,
            schema=schema,
        )
    if "ix_api_request_logs_request_id" not in index_names:
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

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("api_request_logs", schema=schema):
        index_names = {index["name"] for index in inspector.get_indexes("api_request_logs", schema=schema)}
        if "ix_api_request_logs_request_id" in index_names:
            op.drop_index("ix_api_request_logs_request_id", table_name="api_request_logs", schema=schema)
        if "ix_api_request_logs_created_at" in index_names:
            op.drop_index("ix_api_request_logs_created_at", table_name="api_request_logs", schema=schema)
        op.drop_table("api_request_logs", schema=schema)
