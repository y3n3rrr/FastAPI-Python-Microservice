from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.order import OrderItemRead, OrderRead


class CheckoutItemCreate(BaseModel):
    product_variant_id: int
    quantity: int = Field(default=1, ge=1)


class CheckoutCreate(BaseModel):
    user_id: int
    items: list[CheckoutItemCreate]
    note: str | None = None


class PaymentIntentRead(BaseModel):
    id: int
    user_id: int
    payment_method_id: int
    order_id: int | None
    amount: Decimal
    currency: str
    status: str
    provider: str
    provider_payment_method_id: str
    idempotency_key: str
    failure_reason: str | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class CheckoutRead(BaseModel):
    payment_intent: PaymentIntentRead
    order: OrderRead
    order_items: list[OrderItemRead]


class UserTransactionRead(BaseModel):
    payment_intent: PaymentIntentRead
    order: OrderRead | None = None
    order_items: list[OrderItemRead] = Field(default_factory=list)
