import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.order.order_status_history import OrderStatusHistory


class OrderStatusHistoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[OrderStatusHistory]:
        return list(self.db.scalars(select(OrderStatusHistory).order_by(OrderStatusHistory.id)))

    def get(self, history_id: int) -> OrderStatusHistory | None:
        return self.db.get(OrderStatusHistory, history_id)

    def list_by_order(self, order_id: int) -> builtins.list[OrderStatusHistory]:
        stmt = select(OrderStatusHistory).where(OrderStatusHistory.order_id == order_id).order_by(OrderStatusHistory.id)
        return list(self.db.scalars(stmt))

    def add(self, history: OrderStatusHistory) -> OrderStatusHistory:
        self.db.add(history)
        return history

    def delete(self, history: OrderStatusHistory) -> None:
        self.db.delete(history)
