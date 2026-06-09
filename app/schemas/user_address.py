from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserAddressCreate(BaseModel):
    user_id: int
    label: str | None = Field(default=None, max_length=100)
    address_type: str = Field(default="shipping", min_length=1, max_length=30)
    recipient_name: str = Field(min_length=1, max_length=255)
    phone_number: str | None = Field(default=None, max_length=50)
    address_line1: str = Field(min_length=1, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=30)
    country: str = Field(min_length=1, max_length=100)
    delivery_instructions: str | None = None
    is_default: bool = False
    is_active: bool = True


class UserAddressUpdate(BaseModel):
    user_id: int | None = None
    label: str | None = Field(default=None, max_length=100)
    address_type: str | None = Field(default=None, min_length=1, max_length=30)
    recipient_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone_number: str | None = Field(default=None, max_length=50)
    address_line1: str | None = Field(default=None, min_length=1, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    postal_code: str | None = Field(default=None, max_length=30)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    delivery_instructions: str | None = None
    is_default: bool | None = None
    is_active: bool | None = None


class UserAddressRead(BaseModel):
    id: int
    user_id: int
    label: str | None
    address_type: str
    recipient_name: str
    phone_number: str | None
    address_line1: str
    address_line2: str | None
    city: str
    state: str | None
    postal_code: str | None
    country: str
    delivery_instructions: str | None
    is_default: bool
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["UserAddressCreate", "UserAddressRead", "UserAddressUpdate"]
