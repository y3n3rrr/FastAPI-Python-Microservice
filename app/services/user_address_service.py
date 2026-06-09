from __future__ import annotations

from datetime import datetime
from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.entities.user_address import UserAddress
from app.repositories.user_address_repository import UserAddressRepository
from app.schemas.user_address import UserAddressCreate, UserAddressUpdate

TEntity = TypeVar("TEntity")


class UserAddressService:
    def __init__(self, repository: UserAddressRepository, db: Session) -> None:
        self.repository = repository
        self.db = db

    def list_addresses(self) -> list[UserAddress]:
        return self.repository.list()

    def list_user_addresses(self, user_id: int) -> list[UserAddress]:
        return self.repository.list_by_user(user_id)

    def get_address(self, address_id: int) -> UserAddress:
        address = self.repository.get(address_id)
        if address is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User address not found.")
        return address

    def get_default_user_address(self, user_id: int) -> UserAddress:
        address = self.repository.get_default_by_user(user_id)
        if address is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Default user address not found.")
        return address

    def create_address(self, payload: UserAddressCreate) -> UserAddress:
        data = payload.model_dump()
        if data.get("is_default"):
            self.repository.unset_default_for_user(data["user_id"])

        address = UserAddress(**data)
        self.repository.add(address)
        return self._commit_and_refresh(
            entity=address,
            conflict_detail="The database rejected the new user address record.",
        )

    def update_address(self, address_id: int, payload: UserAddressUpdate) -> UserAddress:
        address = self.get_address(address_id)
        data = payload.model_dump(exclude_unset=True)

        next_user_id = data.get("user_id", address.user_id)
        moves_default_address = "user_id" in data and data["user_id"] != address.user_id and address.is_default
        if data.get("is_default") is True or moves_default_address:
            self.repository.unset_default_for_user(next_user_id, exclude_address_id=address.id)

        self._set_updated_at(address)
        for field_name, field_value in data.items():
            setattr(address, field_name, field_value)

        return self._commit_and_refresh(
            entity=address,
            conflict_detail="The database rejected the user address update.",
        )

    def delete_address(self, address_id: int) -> None:
        address = self.get_address(address_id)
        self.repository.delete(address)
        self.db.commit()

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
