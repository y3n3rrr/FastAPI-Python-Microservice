from __future__ import annotations

from datetime import datetime
from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

TEntity = TypeVar("TEntity")


class CartServiceBase:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _set_updated_at(self, entity: TEntity) -> None:
        if hasattr(entity, "updated_at"):
            setattr(entity, "updated_at", datetime.now())

    def _commit_and_refresh(self, entity: TEntity, conflict_detail: str) -> TEntity:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=conflict_detail,
            ) from exc
        self.db.refresh(entity)
        return entity
