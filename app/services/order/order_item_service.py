from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.order.order_item import OrderItem
from app.repositories.order.order_item_repository import OrderItemRepository
from app.schemas.order.order_item import OrderItemCreate, OrderItemUpdate
from app.services.order.base import OrderServiceBase


class OrderItemService(OrderServiceBase):
    def __init__(self, repository: OrderItemRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_order_items(self) -> list[OrderItem]:
        return self.repository.list()

    def list_items_by_order(self, order_id: int) -> list[OrderItem]:
        return self.repository.list_by_order(order_id)

    def get_order_item(self, order_item_id: int) -> OrderItem:
        order_item = self.repository.get(order_item_id)
        if order_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found.")
        return order_item

    def create_order_item(self, payload: OrderItemCreate) -> OrderItem:
        order_item = OrderItem(**payload.model_dump())
        self.repository.add(order_item)
        return self._commit_and_refresh(
            entity=order_item,
            conflict_detail="The database rejected the new order item record.",
        )

    def update_order_item(self, order_item_id: int, payload: OrderItemUpdate) -> OrderItem:
        order_item = self.get_order_item(order_item_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(order_item)

        for field_name, field_value in data.items():
            setattr(order_item, field_name, field_value)

        return self._commit_and_refresh(
            entity=order_item,
            conflict_detail="The database rejected the order item update.",
        )

    def delete_order_item(self, order_item_id: int) -> None:
        order_item = self.get_order_item(order_item_id)
        self.repository.delete(order_item)
        self.db.commit()
