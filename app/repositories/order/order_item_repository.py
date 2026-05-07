import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.order.order_item import OrderItem


class OrderItemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[OrderItem]:
        return list(self.db.scalars(select(OrderItem).order_by(OrderItem.id)))

    def get(self, order_item_id: int) -> OrderItem | None:
        return self.db.get(OrderItem, order_item_id)

    def list_by_order(self, order_id: int) -> builtins.list[OrderItem]:
        stmt = select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.id)
        return list(self.db.scalars(stmt))

    def add(self, order_item: OrderItem) -> OrderItem:
        self.db.add(order_item)
        return order_item

    def delete(self, order_item: OrderItem) -> None:
        self.db.delete(order_item)
