from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.repositories.cart.cart_item_repository import CartItemRepository
from app.repositories.cart.cart_repository import CartRepository
from app.repositories.catalog.product_repository import ProductRepository
from app.repositories.catalog.product_variant_repository import ProductVariantRepository
from app.repositories.order.order_repository import OrderRepository
from app.repositories.order.order_status_history_repository import OrderStatusHistoryRepository
from app.repositories.payment.user_payment_method_repository import UserPaymentMethodRepository
from app.services.assistant.agents.tool_registry import ToolSpec


class AssistantToolset:
    def __init__(self, *, user_id: int, repositories: "AssistantToolRepositories") -> None:
        self.user_id = user_id
        self.repositories = repositories

    def to_specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(
                name="catalog.search_products",
                description=(
                    "Search active product variants by text, category, brand, "
                    "price range, currency and availability."
                ),
                parameters={
                    "query": "string | null",
                    "category_slug": "string | null",
                    "brand_slug": "string | null",
                    "min_price": "number | null",
                    "max_price": "number | null",
                    "currency": "string | null",
                    "only_available": "boolean",
                    "limit": "integer",
                },
                handler=self.catalog_search_products,
            ),
            ToolSpec(
                name="catalog.get_product_by_id",
                description="Get one active product with variants and inventory by product id.",
                parameters={
                    "product_id": "integer",
                },
                handler=self.catalog_get_product_by_id,
            ),
            ToolSpec(
                name="cart.get_active_cart",
                description="Get logged-in user's active cart with items.",
                parameters={},
                handler=self.cart_get_active_cart,
            ),
            ToolSpec(
                name="cart.add_item",
                description="Add a variant to logged-in user's active cart.",
                parameters={
                    "product_variant_id": "integer",
                    "quantity": "integer",
                },
                handler=self.cart_add_item,
            ),
            ToolSpec(
                name="orders.get_user_orders",
                description="List logged-in user's recent orders, optional status filter.",
                parameters={
                    "status": "string | null",
                    "limit": "integer",
                },
                handler=self.orders_get_user_orders,
            ),
            ToolSpec(
                name="orders.get_order_status",
                description="Get one logged-in user's order status and latest status event.",
                parameters={
                    "order_id": "integer",
                },
                handler=self.orders_get_order_status,
            ),
            ToolSpec(
                name="payments.get_default_payment_method",
                description="Get logged-in user's default active payment method.",
                parameters={},
                handler=self.payments_get_default_payment_method,
            ),
        ]

    def catalog_search_products(self, arguments: dict[str, Any]) -> dict[str, Any]:
        query = _as_optional_str(arguments.get("query"))
        category_slug = _as_optional_str(arguments.get("category_slug"))
        brand_slug = _as_optional_str(arguments.get("brand_slug"))
        min_price = _as_optional_float(arguments.get("min_price"))
        max_price = _as_optional_float(arguments.get("max_price"))
        currency = _as_optional_str(arguments.get("currency"))
        only_available = _as_bool(arguments.get("only_available"), default=True)
        limit = _as_int(arguments.get("limit"), default=10, min_value=1, max_value=100)

        variants = self.repositories.product_variant_repository.search_active(
            query=query,
            category_slug=category_slug,
            brand_slug=brand_slug,
            min_price=min_price,
            max_price=max_price,
            currency=currency,
            only_available=only_available,
            limit=limit,
        )
        items: list[dict[str, Any]] = []
        for variant in variants:
            inventory = variant.inventory
            available_units = 0
            if inventory is not None:
                available_units = max(inventory.quantity - inventory.reserved_quantity, 0)
            product = variant.product
            items.append(
                {
                    "variant_id": variant.id,
                    "sku": variant.sku,
                    "name": variant.name or product.name,
                    "price": float(variant.price),
                    "currency": variant.currency,
                    "is_active": variant.is_active and product.is_active,
                    "available_units": available_units,
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "slug": product.slug,
                        "category": product.category.name if product.category else None,
                        "brand": product.brand.name if product.brand else None,
                    },
                }
            )

        return {"count": len(items), "items": items}

    def catalog_get_product_by_id(self, arguments: dict[str, Any]) -> dict[str, Any]:
        product_id = _as_required_int(arguments.get("product_id"), field_name="product_id")
        product = self.repositories.product_repository.get_active_with_relations(product_id)
        if product is None:
            return {"found": False, "product": None}

        variants: list[dict[str, Any]] = []
        for variant in product.variants:
            inventory = variant.inventory
            available_units = 0
            if inventory is not None:
                available_units = max(inventory.quantity - inventory.reserved_quantity, 0)
            variants.append(
                {
                    "id": variant.id,
                    "sku": variant.sku,
                    "name": variant.name,
                    "price": float(variant.price),
                    "currency": variant.currency,
                    "is_active": variant.is_active,
                    "available_units": available_units,
                }
            )

        return {
            "found": True,
            "product": {
                "id": product.id,
                "name": product.name,
                "slug": product.slug,
                "description": product.description,
                "is_active": product.is_active,
                "category": product.category.name if product.category else None,
                "brand": product.brand.name if product.brand else None,
                "variants": variants,
            },
        }

    def cart_get_active_cart(self, arguments: dict[str, Any]) -> dict[str, Any]:
        del arguments
        cart = self.repositories.cart_repository.get_active_by_user(self.user_id)
        if cart is None:
            return {"found": False, "cart": None}

        items = self.repositories.cart_item_repository.list_by_cart(cart.id)
        rows: list[dict[str, Any]] = []
        for item in items:
            variant = self.repositories.product_variant_repository.get(item.product_variant_id)
            rows.append(
                {
                    "cart_item_id": item.id,
                    "product_variant_id": item.product_variant_id,
                    "quantity": item.quantity,
                    "unit_price_snapshot": float(item.unit_price_snapshot),
                    "currency": item.currency,
                    "is_selected": item.is_selected,
                    "variant_name": variant.name if variant is not None else None,
                    "sku": variant.sku if variant is not None else None,
                }
            )
        return {
            "found": True,
            "cart": {
                "id": cart.id,
                "status": cart.status,
                "currency": cart.currency,
                "items": rows,
            },
        }

    def cart_add_item(self, arguments: dict[str, Any]) -> dict[str, Any]:
        variant_id = _as_required_int(arguments.get("product_variant_id"), field_name="product_variant_id")
        quantity = _as_int(arguments.get("quantity"), default=1, min_value=1, max_value=999)

        variant = self.repositories.product_variant_repository.get_active_with_relations(variant_id)
        if variant is None:
            raise ValueError(f"Variant {variant_id} is not available.")

        inventory = variant.inventory
        available_units = 0 if inventory is None else max(inventory.quantity - inventory.reserved_quantity, 0)
        if available_units <= 0:
            raise ValueError(f"Variant {variant_id} is out of stock.")

        cart = self.repositories.cart_repository.get_or_create_active_by_user(
            self.user_id,
            currency=variant.currency,
        )
        if cart.currency != variant.currency:
            raise ValueError(
                f"Cart currency is {cart.currency}, variant currency is {variant.currency}. Mixed currencies are not supported."
            )

        existing = self.repositories.cart_item_repository.get_by_cart_and_variant(
            cart_id=cart.id,
            product_variant_id=variant.id,
        )
        existing_quantity = 0 if existing is None else existing.quantity
        target_quantity = existing_quantity + quantity
        if target_quantity > available_units:
            raise ValueError(
                f"Cannot add {quantity} units. Available stock is {available_units}, cart already has {existing_quantity}."
            )

        item = self.repositories.cart_item_repository.add_or_increment(
            cart_id=cart.id,
            product_variant_id=variant.id,
            quantity=quantity,
            unit_price_snapshot=Decimal(variant.price),
            currency=variant.currency,
        )
        return {
            "cart_id": cart.id,
            "cart_currency": cart.currency,
            "item": {
                "cart_item_id": item.id,
                "product_variant_id": item.product_variant_id,
                "quantity": item.quantity,
                "unit_price_snapshot": float(item.unit_price_snapshot),
                "currency": item.currency,
            },
        }

    def orders_get_user_orders(self, arguments: dict[str, Any]) -> dict[str, Any]:
        status_filter = _as_optional_str(arguments.get("status"))
        limit = _as_int(arguments.get("limit"), default=10, min_value=1, max_value=50)
        orders = self.repositories.order_repository.list_recent_by_user(self.user_id, limit=limit)
        items: list[dict[str, Any]] = []
        for order in orders:
            if status_filter and order.status.lower() != status_filter.lower():
                continue
            items.append(
                {
                    "order_id": order.id,
                    "status": order.status,
                    "total_amount": float(order.total_amount),
                    "currency": order.currency,
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                }
            )
        return {"count": len(items), "items": items}

    def orders_get_order_status(self, arguments: dict[str, Any]) -> dict[str, Any]:
        order_id = _as_required_int(arguments.get("order_id"), field_name="order_id")
        order = self.repositories.order_repository.get_by_user(user_id=self.user_id, order_id=order_id)
        if order is None:
            return {"found": False, "order": None}

        latest = self.repositories.order_status_history_repository.get_latest_by_order(order.id)
        return {
            "found": True,
            "order": {
                "id": order.id,
                "status": order.status,
                "total_amount": float(order.total_amount),
                "currency": order.currency,
                "created_at": order.created_at.isoformat() if order.created_at else None,
            },
            "latest_status_event": (
                {
                    "from_status": latest.from_status,
                    "to_status": latest.to_status,
                    "note": latest.note,
                    "created_at": latest.created_at.isoformat() if latest.created_at else None,
                }
                if latest is not None
                else None
            ),
        }

    def payments_get_default_payment_method(self, arguments: dict[str, Any]) -> dict[str, Any]:
        del arguments
        method = self.repositories.user_payment_method_repository.get_default_by_user(self.user_id)
        if method is None:
            return {"found": False, "payment_method": None}
        return {
            "found": True,
            "payment_method": {
                "id": method.id,
                "provider": method.provider,
                "card_brand": method.card_brand,
                "card_last4": method.card_last4,
                "exp_month": method.exp_month,
                "exp_year": method.exp_year,
                "is_default": method.is_default,
                "is_active": method.is_active,
            },
        }


class AssistantToolRepositories:
    def __init__(
        self,
        *,
        product_repository: ProductRepository,
        product_variant_repository: ProductVariantRepository,
        cart_repository: CartRepository,
        cart_item_repository: CartItemRepository,
        order_repository: OrderRepository,
        order_status_history_repository: OrderStatusHistoryRepository,
        user_payment_method_repository: UserPaymentMethodRepository,
    ) -> None:
        self.product_repository = product_repository
        self.product_variant_repository = product_variant_repository
        self.cart_repository = cart_repository
        self.cart_item_repository = cart_item_repository
        self.order_repository = order_repository
        self.order_status_history_repository = order_status_history_repository
        self.user_payment_method_repository = user_payment_method_repository


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _as_bool(value: Any, *, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y"}:
        return True
    if text in {"0", "false", "no", "n"}:
        return False
    return default


def _as_required_int(value: Any, *, field_name: str) -> int:
    if value is None or str(value).strip() == "":
        raise ValueError(f"'{field_name}' is required.")
    return int(value)


def _as_int(value: Any, *, default: int, min_value: int, max_value: int) -> int:
    if value is None or str(value).strip() == "":
        return default
    parsed = int(value)
    return max(min_value, min(parsed, max_value))
