from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.cart.cart import Cart
from app.repositories.cart.cart_repository import CartRepository
from app.schemas.cart.cart import CartCreate, CartUpdate
from app.services.cart.base import CartServiceBase


class CartService(CartServiceBase):
    def __init__(self, repository: CartRepository, db: Session) -> None:
        super().__init__(db)
        self.repository = repository

    def list_carts(self) -> list[Cart]:
        return self.repository.list()

    def list_user_carts(self, user_id: int) -> list[Cart]:
        return self.repository.list_by_user(user_id)

    def get_cart(self, cart_id: int) -> Cart:
        cart = self.repository.get(cart_id)
        if cart is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found.")
        return cart

    def create_cart(self, payload: CartCreate) -> Cart:
        cart = Cart(**payload.model_dump())
        self.repository.add(cart)
        return self._commit_and_refresh(
            entity=cart,
            conflict_detail="The database rejected the new cart record.",
        )

    def update_cart(self, cart_id: int, payload: CartUpdate) -> Cart:
        cart = self.get_cart(cart_id)
        data = payload.model_dump(exclude_unset=True)
        self._set_updated_at(cart)

        for field_name, field_value in data.items():
            setattr(cart, field_name, field_value)

        return self._commit_and_refresh(
            entity=cart,
            conflict_detail="The database rejected the cart update.",
        )

    def delete_cart(self, cart_id: int) -> None:
        cart = self.get_cart(cart_id)
        self.repository.delete(cart)
        self.db.commit()
