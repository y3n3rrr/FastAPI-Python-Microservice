from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.entities.cart.cart import Cart
from app.entities.cart.cart_item import CartItem
from app.repositories.cart.cart_item_repository import CartItemRepository
from app.repositories.cart.cart_repository import CartRepository
from app.schemas.cart import (
    CartCreate,
    CartItemCreate,
    CartItemRead,
    CartItemUpdate,
    CartRead,
    CartUpdate,
)
from app.services.cart.cart_item_service import CartItemService
from app.services.cart.cart_service import CartService


router = APIRouter(prefix="/carts", tags=["carts"])


def get_cart_service(db: Session = Depends(get_db_session)) -> CartService:
    return CartService(repository=CartRepository(db), db=db)


def get_cart_item_service(db: Session = Depends(get_db_session)) -> CartItemService:
    return CartItemService(repository=CartItemRepository(db), db=db)


@router.get("", response_model=list[CartRead])
def list_carts(service: CartService = Depends(get_cart_service)) -> list[Cart]:
    return service.list_carts()


@router.get("/users/{user_id}", response_model=list[CartRead])
def list_user_carts(user_id: int, service: CartService = Depends(get_cart_service)) -> list[Cart]:
    return service.list_user_carts(user_id)


@router.get("/items", response_model=list[CartItemRead])
def list_cart_items(service: CartItemService = Depends(get_cart_item_service)) -> list[CartItem]:
    return service.list_cart_items()


@router.get("/{cart_id}/items", response_model=list[CartItemRead])
def list_items_by_cart(cart_id: int, service: CartItemService = Depends(get_cart_item_service)) -> list[CartItem]:
    return service.list_items_by_cart(cart_id)


@router.get("/items/{cart_item_id}", response_model=CartItemRead)
def get_cart_item(cart_item_id: int, service: CartItemService = Depends(get_cart_item_service)) -> CartItem:
    return service.get_cart_item(cart_item_id)


@router.post("/items", response_model=CartItemRead, status_code=status.HTTP_201_CREATED)
def create_cart_item(payload: CartItemCreate, service: CartItemService = Depends(get_cart_item_service)) -> CartItem:
    return service.create_cart_item(payload)


@router.put("/items/{cart_item_id}", response_model=CartItemRead)
def update_cart_item(
    cart_item_id: int,
    payload: CartItemUpdate,
    service: CartItemService = Depends(get_cart_item_service),
) -> CartItem:
    return service.update_cart_item(cart_item_id, payload)


@router.delete("/items/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart_item(cart_item_id: int, service: CartItemService = Depends(get_cart_item_service)) -> Response:
    service.delete_cart_item(cart_item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{cart_id}", response_model=CartRead)
def get_cart(cart_id: int, service: CartService = Depends(get_cart_service)) -> Cart:
    return service.get_cart(cart_id)


@router.post("", response_model=CartRead, status_code=status.HTTP_201_CREATED)
def create_cart(payload: CartCreate, service: CartService = Depends(get_cart_service)) -> Cart:
    return service.create_cart(payload)


@router.put("/{cart_id}", response_model=CartRead)
def update_cart(cart_id: int, payload: CartUpdate, service: CartService = Depends(get_cart_service)) -> Cart:
    return service.update_cart(cart_id, payload)


@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(cart_id: int, service: CartService = Depends(get_cart_service)) -> Response:
    service.delete_cart(cart_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
