from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.order.order import Order
from app.repositories.order.order_repository import OrderRepository
from app.schemas.order.order import OrderCreate, OrderUpdate
from app.services.order.base import OrderServiceBase


class OrderService(OrderServiceBase):
    def __init__(self, repository: OrderRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_orders(self) -> list[Order]:
        return self.repository.list()

    def list_user_orders(self, user_id: int) -> list[Order]:
        return self.repository.list_by_user(user_id)

    def get_order(self, order_id: int) -> Order:
        order = self.repository.get(order_id)
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
        return order

    def create_order(self, payload: OrderCreate) -> Order:
        order = Order(**payload.model_dump())
        self.repository.add(order)
        return self._commit_and_refresh(
            entity=order,
            conflict_detail="The database rejected the new order record.",
        )

    def update_order(self, order_id: int, payload: OrderUpdate) -> Order:
        order = self.get_order(order_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(order)

        for field_name, field_value in data.items():
            setattr(order, field_name, field_value)

        return self._commit_and_refresh(
            entity=order,
            conflict_detail="The database rejected the order update.",
        )

    def delete_order(self, order_id: int) -> None:
        order = self.get_order(order_id)
        self.repository.delete(order)
        self.db.commit()
