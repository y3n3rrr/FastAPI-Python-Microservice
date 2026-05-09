import builtins
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.cart.cart_item import CartItem


class CartItemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[CartItem]:
        return list(self.db.scalars(select(CartItem).order_by(CartItem.id)))

    def get(self, cart_item_id: int) -> CartItem | None:
        return self.db.get(CartItem, cart_item_id)

    def list_by_cart(self, cart_id: int) -> builtins.list[CartItem]:
        return list(self.db.scalars(select(CartItem).where(CartItem.cart_id == cart_id).order_by(CartItem.id)))

    def get_by_cart_and_variant(self, cart_id: int, product_variant_id: int) -> CartItem | None:
        stmt = select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_variant_id == product_variant_id,
        )
        return self.db.scalar(stmt)

    def add_or_increment(
        self,
        *,
        cart_id: int,
        product_variant_id: int,
        quantity: int,
        unit_price_snapshot: Decimal,
        currency: str,
    ) -> CartItem:
        existing = self.get_by_cart_and_variant(cart_id=cart_id, product_variant_id=product_variant_id)
        if existing is not None:
            existing.quantity += quantity
            existing.unit_price_snapshot = unit_price_snapshot
            existing.currency = currency.upper()
            return existing

        item = CartItem(
            cart_id=cart_id,
            product_variant_id=product_variant_id,
            quantity=quantity,
            unit_price_snapshot=unit_price_snapshot,
            currency=currency.upper(),
            is_selected=True,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def add(self, cart_item: CartItem) -> CartItem:
        self.db.add(cart_item)
        return cart_item

    def delete(self, cart_item: CartItem) -> None:
        self.db.delete(cart_item)
