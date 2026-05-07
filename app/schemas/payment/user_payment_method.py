from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserPaymentMethodCreate(BaseModel):
    user_id: int
    provider: str = Field(min_length=1, max_length=50)
    provider_customer_id: str | None = Field(default=None, max_length=255)
    provider_payment_method_id: str = Field(min_length=1, max_length=255)
    card_brand: str | None = Field(default=None, max_length=50)
    card_last4: str | None = Field(default=None, min_length=4, max_length=4)
    exp_month: int | None = Field(default=None, ge=1, le=12)
    exp_year: int | None = None
    cardholder_name: str | None = Field(default=None, max_length=255)
    is_default: bool = False
    is_active: bool = True


class UserPaymentMethodUpdate(BaseModel):
    user_id: int | None = None
    provider: str | None = Field(default=None, min_length=1, max_length=50)
    provider_customer_id: str | None = Field(default=None, max_length=255)
    provider_payment_method_id: str | None = Field(default=None, min_length=1, max_length=255)
    card_brand: str | None = Field(default=None, max_length=50)
    card_last4: str | None = Field(default=None, min_length=4, max_length=4)
    exp_month: int | None = Field(default=None, ge=1, le=12)
    exp_year: int | None = None
    cardholder_name: str | None = Field(default=None, max_length=255)
    is_default: bool | None = None
    is_active: bool | None = None


class UserPaymentMethodRead(BaseModel):
    id: int
    user_id: int
    provider: str
    provider_customer_id: str | None
    provider_payment_method_id: str
    card_brand: str | None
    card_last4: str | None
    exp_month: int | None
    exp_year: int | None
    cardholder_name: str | None
    is_default: bool
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


__all__ = ["UserPaymentMethodCreate", "UserPaymentMethodRead", "UserPaymentMethodUpdate"]
