import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.user_address import UserAddress


class UserAddressRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[UserAddress]:
        return list(self.db.scalars(select(UserAddress).order_by(UserAddress.id)))

    def list_by_user(self, user_id: int) -> builtins.list[UserAddress]:
        stmt = select(UserAddress).where(UserAddress.user_id == user_id).order_by(UserAddress.id)
        return list(self.db.scalars(stmt))

    def get(self, address_id: int) -> UserAddress | None:
        return self.db.get(UserAddress, address_id)

    def get_default_by_user(self, user_id: int) -> UserAddress | None:
        stmt = select(UserAddress).where(
            UserAddress.user_id == user_id,
            UserAddress.is_default.is_(True),
            UserAddress.is_active.is_(True),
        )
        return self.db.scalar(stmt)

    def unset_default_for_user(self, user_id: int, exclude_address_id: int | None = None) -> None:
        stmt = select(UserAddress).where(
            UserAddress.user_id == user_id,
            UserAddress.is_default.is_(True),
        )
        if exclude_address_id is not None:
            stmt = stmt.where(UserAddress.id != exclude_address_id)

        for address in self.db.scalars(stmt):
            address.is_default = False

    def add(self, address: UserAddress) -> UserAddress:
        self.db.add(address)
        return address

    def delete(self, address: UserAddress) -> None:
        self.db.delete(address)
