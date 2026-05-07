from app.core.config import get_settings

_SETTINGS = get_settings()
SCHEMA = None if _SETTINGS.database_url.startswith("sqlite") else _SETTINGS.database_schema


def fk_table(table_name: str, column: str = "id") -> str:
    """
    Helps create schema-aware foreign keys.

    If DB schema is configured:
        ecommerce.products.id

    Otherwise:
        products.id
    """
    return f"{SCHEMA}.{table_name}.{column}" if SCHEMA else f"{table_name}.{column}"
