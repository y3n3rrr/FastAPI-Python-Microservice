from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.id)))

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def add(self, user: User) -> User:
        self.db.add(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
