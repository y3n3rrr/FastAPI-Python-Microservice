from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.entities.payment.user_payment_method import UserPaymentMethod
from app.repositories.payment.user_payment_method_repository import UserPaymentMethodRepository
from app.schemas.payment import UserPaymentMethodCreate, UserPaymentMethodRead, UserPaymentMethodUpdate
from app.services.payment.user_payment_method_service import UserPaymentMethodService


router = APIRouter(prefix="/payment-methods", tags=["payment-methods"])


def get_payment_method_service(db: Session = Depends(get_db_session)) -> UserPaymentMethodService:
    return UserPaymentMethodService(repository=UserPaymentMethodRepository(db), db=db)


@router.get("", response_model=list[UserPaymentMethodRead])
def list_payment_methods(service: UserPaymentMethodService = Depends(get_payment_method_service)) -> list[UserPaymentMethod]:
    return service.list_payment_methods()


@router.get("/users/{user_id}", response_model=list[UserPaymentMethodRead])
def list_user_payment_methods(
    user_id: int, service: UserPaymentMethodService = Depends(get_payment_method_service)
) -> list[UserPaymentMethod]:
    return service.list_user_payment_methods(user_id)


@router.get("/{payment_method_id}", response_model=UserPaymentMethodRead)
def get_payment_method(
    payment_method_id: int, service: UserPaymentMethodService = Depends(get_payment_method_service)
) -> UserPaymentMethod:
    return service.get_payment_method(payment_method_id)


@router.post("", response_model=UserPaymentMethodRead, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payload: UserPaymentMethodCreate, service: UserPaymentMethodService = Depends(get_payment_method_service)
) -> UserPaymentMethod:
    return service.create_payment_method(payload)


@router.put("/{payment_method_id}", response_model=UserPaymentMethodRead)
def update_payment_method(
    payment_method_id: int,
    payload: UserPaymentMethodUpdate,
    service: UserPaymentMethodService = Depends(get_payment_method_service),
) -> UserPaymentMethod:
    return service.update_payment_method(payment_method_id, payload)


@router.delete("/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_method(payment_method_id: int, service: UserPaymentMethodService = Depends(get_payment_method_service)) -> Response:
    service.delete_payment_method(payment_method_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
