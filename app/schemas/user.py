from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str | None = None
    surname: str | None = None
    email: EmailStr | None = None
    password: str = Field(min_length=6)
    is_active: bool = False


class UserUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6)
    is_active: bool | None = None


class UserRead(BaseModel):
    id: int
    name: str | None
    surname: str | None
    email: EmailStr | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["UserCreate", "UserRead", "UserUpdate"]
