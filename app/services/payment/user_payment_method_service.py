from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.payment.user_payment_method import UserPaymentMethod
from app.repositories.payment.user_payment_method_repository import UserPaymentMethodRepository
from app.schemas.payment.user_payment_method import UserPaymentMethodCreate, UserPaymentMethodUpdate
from app.services.payment.base import PaymentServiceBase


class UserPaymentMethodService(PaymentServiceBase):
    def __init__(self, repository: UserPaymentMethodRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_payment_methods(self) -> list[UserPaymentMethod]:
        return self.repository.list()

    def list_user_payment_methods(self, user_id: int) -> list[UserPaymentMethod]:
        return self.repository.list_by_user(user_id)

    def get_payment_method(self, payment_method_id: int) -> UserPaymentMethod:
        payment_method = self.repository.get(payment_method_id)
        if payment_method is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User payment method not found.")
        return payment_method

    def create_payment_method(self, payload: UserPaymentMethodCreate) -> UserPaymentMethod:
        payment_method = UserPaymentMethod(**payload.model_dump())
        self.repository.add(payment_method)
        return self._commit_and_refresh(
            entity=payment_method,
            conflict_detail="The database rejected the new user payment method record.",
        )

    def update_payment_method(self, payment_method_id: int, payload: UserPaymentMethodUpdate) -> UserPaymentMethod:
        payment_method = self.get_payment_method(payment_method_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(payment_method)

        for field_name, field_value in data.items():
            setattr(payment_method, field_name, field_value)

        return self._commit_and_refresh(
            entity=payment_method,
            conflict_detail="The database rejected the user payment method update.",
        )

    def delete_payment_method(self, payment_method_id: int) -> None:
        payment_method = self.get_payment_method(payment_method_id)
        self.repository.delete(payment_method)
        self.db.commit()
