from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.entities.user_address import UserAddress
from app.repositories.user_address_repository import UserAddressRepository
from app.schemas.user_address import UserAddressCreate, UserAddressRead, UserAddressUpdate
from app.services.user_address_service import UserAddressService


router = APIRouter(prefix="/user-addresses", tags=["user-addresses"])


def get_user_address_service(db: Session = Depends(get_db_session)) -> UserAddressService:
    return UserAddressService(repository=UserAddressRepository(db), db=db)


@router.get("", response_model=list[UserAddressRead])
def list_addresses(service: UserAddressService = Depends(get_user_address_service)) -> list[UserAddress]:
    return service.list_addresses()


@router.get("/users/{user_id}", response_model=list[UserAddressRead])
def list_user_addresses(
    user_id: int, service: UserAddressService = Depends(get_user_address_service)
) -> list[UserAddress]:
    return service.list_user_addresses(user_id)


@router.get("/users/{user_id}/default", response_model=UserAddressRead)
def get_default_user_address(
    user_id: int, service: UserAddressService = Depends(get_user_address_service)
) -> UserAddress:
    return service.get_default_user_address(user_id)


@router.get("/{address_id}", response_model=UserAddressRead)
def get_address(address_id: int, service: UserAddressService = Depends(get_user_address_service)) -> UserAddress:
    return service.get_address(address_id)


@router.post("", response_model=UserAddressRead, status_code=status.HTTP_201_CREATED)
def create_address(
    payload: UserAddressCreate, service: UserAddressService = Depends(get_user_address_service)
) -> UserAddress:
    return service.create_address(payload)


@router.put("/{address_id}", response_model=UserAddressRead)
def update_address(
    address_id: int,
    payload: UserAddressUpdate,
    service: UserAddressService = Depends(get_user_address_service),
) -> UserAddress:
    return service.update_address(address_id, payload)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, service: UserAddressService = Depends(get_user_address_service)) -> Response:
    service.delete_address(address_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
