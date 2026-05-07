from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.entities.order.order import Order
from app.entities.order.order_item import OrderItem
from app.entities.order.order_status_history import OrderStatusHistory
from app.repositories.order.order_item_repository import OrderItemRepository
from app.repositories.order.order_repository import OrderRepository
from app.repositories.order.order_status_history_repository import OrderStatusHistoryRepository
from app.schemas.order import (
    OrderCreate,
    OrderItemCreate,
    OrderItemRead,
    OrderItemUpdate,
    OrderRead,
    OrderStatusHistoryCreate,
    OrderStatusHistoryRead,
    OrderStatusHistoryUpdate,
    OrderUpdate,
)
from app.services.order.order_item_service import OrderItemService
from app.services.order.order_service import OrderService
from app.services.order.order_status_history_service import OrderStatusHistoryService


router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(db: Session = Depends(get_db_session)) -> OrderService:
    return OrderService(repository=OrderRepository(db), db=db)


def get_order_item_service(db: Session = Depends(get_db_session)) -> OrderItemService:
    return OrderItemService(repository=OrderItemRepository(db), db=db)


def get_order_status_history_service(db: Session = Depends(get_db_session)) -> OrderStatusHistoryService:
    return OrderStatusHistoryService(repository=OrderStatusHistoryRepository(db), db=db)


@router.get("", response_model=list[OrderRead])
def list_orders(service: OrderService = Depends(get_order_service)) -> list[Order]:
    return service.list_orders()


@router.get("/users/{user_id}", response_model=list[OrderRead])
def list_user_orders(user_id: int, service: OrderService = Depends(get_order_service)) -> list[Order]:
    return service.list_user_orders(user_id)


@router.get("/items", response_model=list[OrderItemRead])
def list_order_items(service: OrderItemService = Depends(get_order_item_service)) -> list[OrderItem]:
    return service.list_order_items()


@router.get("/{order_id}/items", response_model=list[OrderItemRead])
def list_items_by_order(order_id: int, service: OrderItemService = Depends(get_order_item_service)) -> list[OrderItem]:
    return service.list_items_by_order(order_id)


@router.get("/items/{order_item_id}", response_model=OrderItemRead)
def get_order_item(order_item_id: int, service: OrderItemService = Depends(get_order_item_service)) -> OrderItem:
    return service.get_order_item(order_item_id)


@router.post("/items", response_model=OrderItemRead, status_code=status.HTTP_201_CREATED)
def create_order_item(payload: OrderItemCreate, service: OrderItemService = Depends(get_order_item_service)) -> OrderItem:
    return service.create_order_item(payload)


@router.put("/items/{order_item_id}", response_model=OrderItemRead)
def update_order_item(
    order_item_id: int,
    payload: OrderItemUpdate,
    service: OrderItemService = Depends(get_order_item_service),
) -> OrderItem:
    return service.update_order_item(order_item_id, payload)


@router.delete("/items/{order_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(order_item_id: int, service: OrderItemService = Depends(get_order_item_service)) -> Response:
    service.delete_order_item(order_item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/status-history", response_model=list[OrderStatusHistoryRead])
def list_order_status_history(
    service: OrderStatusHistoryService = Depends(get_order_status_history_service),
) -> list[OrderStatusHistory]:
    return service.list_order_status_history()


@router.get("/{order_id}/status-history", response_model=list[OrderStatusHistoryRead])
def list_history_by_order(
    order_id: int,
    service: OrderStatusHistoryService = Depends(get_order_status_history_service),
) -> list[OrderStatusHistory]:
    return service.list_history_by_order(order_id)


@router.get("/status-history/{history_id}", response_model=OrderStatusHistoryRead)
def get_order_status_history(
    history_id: int,
    service: OrderStatusHistoryService = Depends(get_order_status_history_service),
) -> OrderStatusHistory:
    return service.get_order_status_history(history_id)


@router.post("/status-history", response_model=OrderStatusHistoryRead, status_code=status.HTTP_201_CREATED)
def create_order_status_history(
    payload: OrderStatusHistoryCreate,
    service: OrderStatusHistoryService = Depends(get_order_status_history_service),
) -> OrderStatusHistory:
    return service.create_order_status_history(payload)


@router.put("/status-history/{history_id}", response_model=OrderStatusHistoryRead)
def update_order_status_history(
    history_id: int,
    payload: OrderStatusHistoryUpdate,
    service: OrderStatusHistoryService = Depends(get_order_status_history_service),
) -> OrderStatusHistory:
    return service.update_order_status_history(history_id, payload)


@router.delete("/status-history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_status_history(
    history_id: int,
    service: OrderStatusHistoryService = Depends(get_order_status_history_service),
) -> Response:
    service.delete_order_status_history(history_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, service: OrderService = Depends(get_order_service)) -> Order:
    return service.get_order(order_id)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, service: OrderService = Depends(get_order_service)) -> Order:
    return service.create_order(payload)


@router.put("/{order_id}", response_model=OrderRead)
def update_order(order_id: int, payload: OrderUpdate, service: OrderService = Depends(get_order_service)) -> Order:
    return service.update_order(order_id, payload)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, service: OrderService = Depends(get_order_service)) -> Response:
    service.delete_order(order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
