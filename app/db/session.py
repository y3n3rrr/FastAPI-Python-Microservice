from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_ENGINES: dict[str, Engine] = {}


def _build_connect_args(database_url: str) -> dict[str, bool]:
    return {"check_same_thread": False} if database_url.startswith("sqlite") else {}


@lru_cache
def get_engine(database_url: str | None = None) -> Engine:
    resolved_url = database_url or get_settings().database_url
    engine = create_engine(
        resolved_url,
        pool_pre_ping=True,
        connect_args=_build_connect_args(resolved_url),
    )
    _ENGINES[resolved_url] = engine
    return engine


@lru_cache
def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(database_url),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )


def reset_db_state() -> None:
    for engine in _ENGINES.values():
        engine.dispose()
    _ENGINES.clear()
    get_session_factory.cache_clear()
    get_engine.cache_clear()


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory(get_settings().database_url)()
    try:
        yield session
    finally:
        session.close()
