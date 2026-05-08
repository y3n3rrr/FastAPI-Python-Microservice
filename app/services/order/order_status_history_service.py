from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.order.order_status_history import OrderStatusHistory
from app.repositories.order.order_status_history_repository import OrderStatusHistoryRepository
from app.schemas.order.order_status_history import OrderStatusHistoryCreate, OrderStatusHistoryUpdate
from app.services.order.base import OrderServiceBase


class OrderStatusHistoryService(OrderServiceBase):
    def __init__(self, repository: OrderStatusHistoryRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_order_status_history(self) -> list[OrderStatusHistory]:
        return self.repository.list()

    def list_history_by_order(self, order_id: int) -> list[OrderStatusHistory]:
        return self.repository.list_by_order(order_id)

    def get_order_status_history(self, history_id: int) -> OrderStatusHistory:
        history = self.repository.get(history_id)
        if history is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order status history not found.")
        return history

    def create_order_status_history(self, payload: OrderStatusHistoryCreate) -> OrderStatusHistory:
        history = OrderStatusHistory(**payload.model_dump())
        self.repository.add(history)
        return self._commit_and_refresh(
            entity=history,
            conflict_detail="The database rejected the new order status history record.",
        )

    def update_order_status_history(self, history_id: int, payload: OrderStatusHistoryUpdate) -> OrderStatusHistory:
        history = self.get_order_status_history(history_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(history)

        for field_name, field_value in data.items():
            setattr(history, field_name, field_value)

        return self._commit_and_refresh(
            entity=history,
            conflict_detail="The database rejected the order status history update.",
        )

    def delete_order_status_history(self, history_id: int) -> None:
        history = self.get_order_status_history(history_id)
        self.repository.delete(history)
        self.db.commit()
