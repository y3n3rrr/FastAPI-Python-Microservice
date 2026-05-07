from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.cart.cart_item import CartItem
from app.repositories.cart.cart_item_repository import CartItemRepository
from app.schemas.cart.cart_item import CartItemCreate, CartItemUpdate
from app.services.cart.base import CartServiceBase


class CartItemService(CartServiceBase):
    def __init__(self, repository: CartItemRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_cart_items(self) -> list[CartItem]:
        return self.repository.list()

    def list_items_by_cart(self, cart_id: int) -> list[CartItem]:
        return self.repository.list_by_cart(cart_id)

    def get_cart_item(self, cart_item_id: int) -> CartItem:
        cart_item = self.repository.get(cart_item_id)
        if cart_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found.")
        return cart_item

    def create_cart_item(self, payload: CartItemCreate) -> CartItem:
        cart_item = CartItem(**payload.model_dump())
        self.repository.add(cart_item)
        return self._commit_and_refresh(
            entity=cart_item,
            conflict_detail="The database rejected the new cart item record.",
        )

    def update_cart_item(self, cart_item_id: int, payload: CartItemUpdate) -> CartItem:
        cart_item = self.get_cart_item(cart_item_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(cart_item)

        for field_name, field_value in data.items():
            setattr(cart_item, field_name, field_value)

        return self._commit_and_refresh(
            entity=cart_item,
            conflict_detail="The database rejected the cart item update.",
        )

    def delete_cart_item(self, cart_item_id: int) -> None:
        cart_item = self.get_cart_item(cart_item_id)
        self.repository.delete(cart_item)
        self.db.commit()
