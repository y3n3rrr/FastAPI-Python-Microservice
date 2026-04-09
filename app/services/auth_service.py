from fastapi import HTTPException, status

from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        return TokenResponse(access_token=create_access_token(subject=str(user.id)))
