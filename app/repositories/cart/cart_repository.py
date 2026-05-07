import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.cart.cart import Cart


class CartRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[Cart]:
        return list(self.db.scalars(select(Cart).order_by(Cart.id)))

    def get(self, cart_id: int) -> Cart | None:
        return self.db.get(Cart, cart_id)

    def list_by_user(self, user_id: int) -> builtins.list[Cart]:
        return list(self.db.scalars(select(Cart).where(Cart.user_id == user_id).order_by(Cart.id)))

    def add(self, cart: Cart) -> Cart:
        self.db.add(cart)
        return cart

    def delete(self, cart: Cart) -> None:
        self.db.delete(cart)
