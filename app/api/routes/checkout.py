from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.checkout import CheckoutCreate, CheckoutRead
from app.services.checkout_service import CheckoutService


router = APIRouter(prefix="/checkout", tags=["checkout"])


def get_checkout_service(db: Session = Depends(get_db_session)) -> CheckoutService:
    return CheckoutService(db=db)


@router.post("", response_model=CheckoutRead)
def create_checkout(payload: CheckoutCreate, service: CheckoutService = Depends(get_checkout_service)) -> CheckoutRead:
    payment_intent, order, order_items = service.checkout(payload)
    return CheckoutRead(payment_intent=payment_intent, order=order, order_items=order_items)
