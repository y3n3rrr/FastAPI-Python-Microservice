from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.entities.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository, db: Session) -> None:
        self.db = db
        self.repository = repository

    def list_users(self) -> list[User]:
        return self.repository.list()

    def get_user(self, user_id: int) -> User:
        user = self.repository.get(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return user

    def create_user(self, payload: UserCreate) -> User:
        user = User(
            name=payload.name,
            surname=payload.surname,
            email=payload.email,
            password_hash=hash_password(payload.password),
            is_active=payload.is_active,
        )
        self.repository.add(user)
        return self._commit_and_refresh(
            user=user,
            conflict_detail="The database rejected the new user record.",
        )

    def update_user(self, user_id: int, payload: UserUpdate) -> User:
        user = self.get_user(user_id)
        data = payload.model_dump(exclude_unset=True)

        password = data.pop("password", None)
        if password is not None:
            user.password_hash = hash_password(password)

        for field_name, field_value in data.items():
            setattr(user, field_name, field_value)

        return self._commit_and_refresh(
            user=user,
            conflict_detail="The database rejected the user update.",
        )

    def delete_user(self, user_id: int) -> None:
        user = self.get_user(user_id)
        self.repository.delete(user)
        self.db.commit()

    def _commit_and_refresh(self, user: User, conflict_detail: str) -> User:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=conflict_detail,
            ) from exc
        self.db.refresh(user)
        return user
