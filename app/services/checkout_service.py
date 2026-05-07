from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.catalog.inventory import Inventory
from app.entities.catalog.product_variant import ProductVariant
from app.entities.order.order import Order
from app.entities.order.order_item import OrderItem
from app.entities.payment.payment_intent import PaymentIntent
from app.repositories.payment.payment_intent_repository import PaymentIntentRepository
from app.repositories.payment.user_payment_method_repository import UserPaymentMethodRepository
from app.repositories.user_repository import UserRepository
from app.schemas.checkout import CheckoutCreate


class CheckoutService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repository = UserRepository(db)
        self.payment_method_repository = UserPaymentMethodRepository(db)
        self.payment_intent_repository = PaymentIntentRepository(db)

    def checkout(self, payload: CheckoutCreate) -> tuple[PaymentIntent, Order, list[OrderItem]]:
        if not payload.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one checkout item is required.")

        user = self.user_repository.get(payload.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        default_payment_method = self.payment_method_repository.get_default_by_user(payload.user_id)
        if default_payment_method is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No default active payment method found for user.",
            )

        variant_rows: dict[int, ProductVariant] = {}
        for item in payload.items:
            variant = self.db.get(ProductVariant, item.product_variant_id)
            if variant is None or not variant.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product variant {item.product_variant_id} is unavailable.",
                )
            variant_rows[item.product_variant_id] = variant

        currencies = {variant_rows[item.product_variant_id].currency for item in payload.items}
        if len(currencies) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All checkout items must have the same currency.",
            )
        currency = next(iter(currencies))

        total_amount = Decimal("0.00")
        for item in payload.items:
            variant = variant_rows[item.product_variant_id]
            total_amount += variant.price * item.quantity

        try:
            payment_intent = PaymentIntent(
                user_id=payload.user_id,
                payment_method_id=default_payment_method.id,
                order_id=None,
                amount=total_amount,
                currency=currency,
                status="requires_confirmation",
                provider=default_payment_method.provider,
                provider_payment_method_id=default_payment_method.provider_payment_method_id,
                failure_reason=None,
            )
            self.payment_intent_repository.add(payment_intent)
            self.db.flush()

            order = Order(
                user_id=payload.user_id,
                status="pending",
                currency=currency,
                total_amount=total_amount,
                note=payload.note,
            )
            self.db.add(order)
            self.db.flush()

            order_items: list[OrderItem] = []
            for item in payload.items:
                variant = variant_rows[item.product_variant_id]
                inventory_stmt = (
                    select(Inventory)
                    .where(Inventory.variant_id == item.product_variant_id)
                    .with_for_update()
                )
                inventory = self.db.scalar(inventory_stmt)
                if inventory is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Inventory missing for variant {item.product_variant_id}.",
                    )

                if inventory.quantity < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Insufficient inventory for variant {item.product_variant_id}.",
                    )

                inventory.quantity -= item.quantity

                order_item = OrderItem(
                    order_id=order.id,
                    product_variant_id=item.product_variant_id,
                    quantity=item.quantity,
                    unit_price_snapshot=variant.price,
                    line_total=variant.price * item.quantity,
                    currency=variant.currency,
                )
                self.db.add(order_item)
                order_items.append(order_item)

            payment_intent.order_id = order.id
            payment_intent.status = "authorized"
            order.status = "confirmed"

            self.db.commit()

            self.db.refresh(payment_intent)
            self.db.refresh(order)
            for order_item in order_items:
                self.db.refresh(order_item)

            return payment_intent, order, order_items
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Checkout failed due to an unexpected error.",
            ) from exc
