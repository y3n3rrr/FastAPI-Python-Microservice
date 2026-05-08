from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.checkout import CheckoutCreate, CheckoutRead, PaymentIntentRead, UserTransactionRead
from app.schemas.order import OrderItemRead, OrderRead
from app.services.checkout_service import CheckoutService


router = APIRouter(prefix="/checkout", tags=["checkout"])


def get_checkout_service(db: Session = Depends(get_db_session)) -> CheckoutService:
    return CheckoutService(db=db)


@router.post("", response_model=CheckoutRead)
def create_checkout(
    payload: CheckoutCreate,
    service: CheckoutService = Depends(get_checkout_service),
    idempotency_key: str = Header(alias="Idempotency-Key"),
) -> CheckoutRead:
    payment_intent, order, order_items = service.checkout(payload, idempotency_key=idempotency_key)
    payment_intent_read = PaymentIntentRead.model_validate(payment_intent)
    order_read = OrderRead.model_validate(order)
    order_items_read = [OrderItemRead.model_validate(item) for item in order_items]

    return CheckoutRead(
        payment_intent=payment_intent_read,
        order=order_read,
        order_items=order_items_read,
    )


@router.get("/users/{user_id}/transactions", response_model=list[UserTransactionRead])
def list_user_transactions(
    user_id: int,
    service: CheckoutService = Depends(get_checkout_service),
) -> list[UserTransactionRead]:
    transactions = service.list_user_transactions(user_id)
    return [
        UserTransactionRead(
            payment_intent=PaymentIntentRead.model_validate(payment_intent),
            order=OrderRead.model_validate(order) if order is not None else None,
            order_items=[OrderItemRead.model_validate(item) for item in order_items],
        )
        for payment_intent, order, order_items in transactions
    ]
