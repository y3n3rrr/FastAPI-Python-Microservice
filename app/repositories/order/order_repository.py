import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.order.order import Order


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[Order]:
        return list(self.db.scalars(select(Order).order_by(Order.id)))

    def get(self, order_id: int) -> Order | None:
        return self.db.get(Order, order_id)

    def list_by_user(self, user_id: int) -> builtins.list[Order]:
        stmt = select(Order).where(Order.user_id == user_id).order_by(Order.id)
        return list(self.db.scalars(stmt))

    def list_recent_by_user(self, user_id: int, *, limit: int = 20) -> builtins.list[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc(), Order.id.desc())
            .limit(max(1, min(limit, 100)))
        )
        return list(self.db.scalars(stmt))

    def get_by_user(self, *, user_id: int, order_id: int) -> Order | None:
        stmt = select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        return self.db.scalar(stmt)

    def add(self, order: Order) -> Order:
        self.db.add(order)
        return order

    def delete(self, order: Order) -> None:
        self.db.delete(order)
