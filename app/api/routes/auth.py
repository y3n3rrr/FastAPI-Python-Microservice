from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import AuthService
from app.services.user_service import UserService


router = APIRouter(tags=["auth"])


def get_auth_service(db: Session = Depends(get_db_session)) -> AuthService:
    return AuthService(UserRepository(db))


def get_registration_service(db: Session = Depends(get_db_session)) -> UserService:
    return UserService(UserRepository(db), db)


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserCreate, service: UserService = Depends(get_registration_service)) -> UserRead:
    return service.create_user(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return service.login(payload)
