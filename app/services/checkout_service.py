from __future__ import annotations

from decimal import Decimal
from collections import defaultdict

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

    def checkout(self, payload: CheckoutCreate, idempotency_key: str) -> tuple[PaymentIntent, Order, list[OrderItem]]:
        if not payload.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one checkout item is required.")
        if not idempotency_key.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Idempotency-Key header is required.")

        user = self.user_repository.get(payload.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        existing_intent = self.payment_intent_repository.get_by_user_and_idempotency_key(payload.user_id, idempotency_key)
        if existing_intent is not None:
            if existing_intent.order_id is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Checkout request is already in progress for this Idempotency-Key.",
                )
            existing_order = self.db.get(Order, existing_intent.order_id)
            if existing_order is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Checkout result is inconsistent. Please retry with a new Idempotency-Key.",
                )
            existing_items_stmt = select(OrderItem).where(OrderItem.order_id == existing_order.id).order_by(OrderItem.id)
            existing_items = list(self.db.scalars(existing_items_stmt))
            return existing_intent, existing_order, existing_items

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
                idempotency_key=idempotency_key,
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

    def list_user_transactions(self, user_id: int) -> list[tuple[PaymentIntent, Order | None, list[OrderItem]]]:
        user = self.user_repository.get(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        payment_intents = self.payment_intent_repository.list_by_user(user_id)
        if not payment_intents:
            return []

        order_ids = [intent.order_id for intent in payment_intents if intent.order_id is not None]
        orders_by_id: dict[int, Order] = {}
        order_items_by_order_id: dict[int, list[OrderItem]] = defaultdict(list)

        if order_ids:
            orders_stmt = select(Order).where(Order.id.in_(order_ids))
            orders = list(self.db.scalars(orders_stmt))
            orders_by_id = {order.id: order for order in orders}

            order_items_stmt = select(OrderItem).where(OrderItem.order_id.in_(order_ids)).order_by(OrderItem.order_id, OrderItem.id)
            for order_item in self.db.scalars(order_items_stmt):
                order_items_by_order_id[order_item.order_id].append(order_item)

        transactions: list[tuple[PaymentIntent, Order | None, list[OrderItem]]] = []
        for payment_intent in payment_intents:
            order = orders_by_id.get(payment_intent.order_id) if payment_intent.order_id is not None else None
            order_items = order_items_by_order_id.get(order.id, []) if order is not None else []
            transactions.append((payment_intent, order, order_items))

        return transactions
