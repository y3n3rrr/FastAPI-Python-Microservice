import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.payment.user_payment_method import UserPaymentMethod


class UserPaymentMethodRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[UserPaymentMethod]:
        return list(self.db.scalars(select(UserPaymentMethod).order_by(UserPaymentMethod.id)))

    def list_by_user(self, user_id: int) -> builtins.list[UserPaymentMethod]:
        stmt = select(UserPaymentMethod).where(UserPaymentMethod.user_id == user_id).order_by(UserPaymentMethod.id)
        return list(self.db.scalars(stmt))

    def get(self, payment_method_id: int) -> UserPaymentMethod | None:
        return self.db.get(UserPaymentMethod, payment_method_id)

    def get_default_by_user(self, user_id: int) -> UserPaymentMethod | None:
        stmt = select(UserPaymentMethod).where(
            UserPaymentMethod.user_id == user_id,
            UserPaymentMethod.is_default.is_(True),
            UserPaymentMethod.is_active.is_(True),
        )
        return self.db.scalar(stmt)

    def add(self, payment_method: UserPaymentMethod) -> UserPaymentMethod:
        self.db.add(payment_method)
        return payment_method

    def delete(self, payment_method: UserPaymentMethod) -> None:
        self.db.delete(payment_method)
