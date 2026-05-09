from __future__ import annotations

import re
from typing import Any

from app.services.assistant.agents.models import (
    PlannerOutput,
    PlannerStep,
    ToolExecutionResult,
    ValidationOutput,
)
from app.services.assistant.agents.tool_registry import ToolRegistry
from app.services.assistant.llm_client import LLMClient


class OrchestratorAgent:
    def __init__(
        self,
        *,
        planner: "PlannerAgent",
        retriever: "RetrieverAgent",
        validator: "ValidationAgent",
        answerer: "AnswerAgent",
    ) -> None:
        self.planner = planner
        self.retriever = retriever
        self.validator = validator
        self.answerer = answerer

    def run(self, *, user_message: str, conversation_context: str, tool_registry: ToolRegistry) -> str:
        plan = self.planner.create_plan(
            user_message=user_message,
            conversation_context=conversation_context,
            tool_registry=tool_registry,
        )
        retrieval_results = self.retriever.execute(plan=plan, tool_registry=tool_registry)
        validation = self.validator.validate(plan=plan, results=retrieval_results)
        return self.answerer.build_answer(
            user_message=user_message,
            plan=plan,
            validation=validation,
        )


class PlannerAgent:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def create_plan(
        self,
        *,
        user_message: str,
        conversation_context: str,
        tool_registry: ToolRegistry,
    ) -> PlannerOutput:
        llm_plan = self.llm_client.generate_tool_plan(
            user_prompt=user_message,
            conversation_context=conversation_context,
            tool_definitions=tool_registry.list_for_planner(),
        )
        parsed = _parse_plan(llm_plan, tool_registry) if llm_plan is not None else None
        if parsed is not None and parsed.steps:
            return parsed
        return _heuristic_plan(user_message)


class RetrieverAgent:
    def execute(self, *, plan: PlannerOutput, tool_registry: ToolRegistry) -> list[ToolExecutionResult]:
        results: list[ToolExecutionResult] = []
        for step in plan.steps:
            arguments = step.arguments if isinstance(step.arguments, dict) else {}
            try:
                data = tool_registry.execute(step.tool, arguments)
                results.append(
                    ToolExecutionResult(
                        tool=step.tool,
                        arguments=arguments,
                        success=True,
                        data=data,
                        error=None,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                results.append(
                    ToolExecutionResult(
                        tool=step.tool,
                        arguments=arguments,
                        success=False,
                        data=None,
                        error=str(exc),
                    )
                )
        return results


class ValidationAgent:
    def validate(self, *, plan: PlannerOutput, results: list[ToolExecutionResult]) -> ValidationOutput:
        issues: list[str] = []
        for index, result in enumerate(results):
            if not result.success:
                issues.append(f"Step {index + 1} '{result.tool}' failed: {result.error}")
                continue
            self._validate_tool_result(plan_step=plan.steps[index], result=result, issues=issues)

        is_valid = len(issues) == 0
        return ValidationOutput(is_valid=is_valid, issues=issues, results=results)

    def _validate_tool_result(self, *, plan_step: PlannerStep, result: ToolExecutionResult, issues: list[str]) -> None:
        data = result.data
        if not isinstance(data, dict):
            return

        if result.tool == "catalog.search_products":
            items = data.get("items")
            if not isinstance(items, list):
                issues.append("catalog.search_products returned invalid 'items' payload.")
                return
            max_price = _as_float(plan_step.arguments.get("max_price"))
            min_price = _as_float(plan_step.arguments.get("min_price"))
            requested_currency = _as_upper(plan_step.arguments.get("currency"))
            for item in items:
                if not isinstance(item, dict):
                    issues.append("catalog.search_products returned non-object item.")
                    continue
                if not bool(item.get("is_active", False)):
                    issues.append("catalog.search_products returned an inactive item.")
                price = _as_float(item.get("price"))
                if max_price is not None and price is not None and price > max_price:
                    issues.append("catalog.search_products returned item above max_price filter.")
                if min_price is not None and price is not None and price < min_price:
                    issues.append("catalog.search_products returned item below min_price filter.")
                item_currency = _as_upper(item.get("currency"))
                if requested_currency and item_currency and item_currency != requested_currency:
                    issues.append("catalog.search_products returned item with unexpected currency.")

        if result.tool == "catalog.get_product_by_id":
            found = data.get("found")
            if found is True:
                product = data.get("product")
                if not isinstance(product, dict) or not bool(product.get("is_active", False)):
                    issues.append("catalog.get_product_by_id returned non-active or invalid product.")


class AnswerAgent:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def build_answer(self, *, user_message: str, plan: PlannerOutput, validation: ValidationOutput) -> str:
        llm_answer = self.llm_client.generate_answer_from_tool_results(
            user_prompt=user_message,
            plan=plan.model_dump(),
            results=[item.model_dump() for item in validation.results],
            validation_issues=validation.issues,
        )
        if llm_answer:
            return llm_answer

        if not plan.steps:
            return (
                "I could not map your request to an available tool yet. "
                "Please share a bit more detail, for example product/order/cart/payment intent."
            )

        lines: list[str] = []
        if validation.issues:
            lines.append("I found data, but some checks failed:")
            for issue in validation.issues[:5]:
                lines.append(f"- {issue}")

        for result in validation.results:
            lines.extend(self._render_tool_result(result))

        return "\n".join(lines).strip()

    def _render_tool_result(self, result: ToolExecutionResult) -> list[str]:
        if not result.success:
            return [f"{result.tool}: failed ({result.error})"]

        data = result.data if isinstance(result.data, dict) else {}
        if result.tool == "catalog.search_products":
            items = data.get("items") if isinstance(data.get("items"), list) else []
            if not items:
                return ["No matching products were found."]
            lines = ["Matching products:"]
            for item in items[:10]:
                if not isinstance(item, dict):
                    continue
                product = item.get("product") if isinstance(item.get("product"), dict) else {}
                product_name = product.get("name") or item.get("name") or "Unknown"
                price = item.get("price")
                currency = item.get("currency") or "USD"
                sku = item.get("sku") or "-"
                available_units = item.get("available_units")
                lines.append(
                    f"- {product_name} ({sku}) - {price} {currency}, available units: {available_units}"
                )
            return lines

        if result.tool == "catalog.get_product_by_id":
            if not data.get("found"):
                return ["Product not found or inactive."]
            product = data.get("product") if isinstance(data.get("product"), dict) else {}
            lines = [f"Product: {product.get('name')} ({product.get('slug')})"]
            variants = product.get("variants") if isinstance(product.get("variants"), list) else []
            for variant in variants[:10]:
                if not isinstance(variant, dict):
                    continue
                lines.append(
                    f"- Variant {variant.get('id')} {variant.get('sku')}: {variant.get('price')} "
                    f"{variant.get('currency')} (available: {variant.get('available_units')})"
                )
            return lines

        if result.tool == "cart.get_active_cart":
            if not data.get("found"):
                return ["No active cart found."]
            cart = data.get("cart") if isinstance(data.get("cart"), dict) else {}
            items = cart.get("items") if isinstance(cart.get("items"), list) else []
            lines = [f"Active cart #{cart.get('id')} ({cart.get('currency')}), items: {len(items)}"]
            for item in items[:10]:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- Variant {item.get('product_variant_id')} x{item.get('quantity')} "
                    f"at {item.get('unit_price_snapshot')} {item.get('currency')}"
                )
            return lines

        if result.tool == "cart.add_item":
            item = data.get("item") if isinstance(data.get("item"), dict) else {}
            return [
                f"Added to cart #{data.get('cart_id')}: variant {item.get('product_variant_id')} "
                f"x{item.get('quantity')}."
            ]

        if result.tool == "orders.get_user_orders":
            items = data.get("items") if isinstance(data.get("items"), list) else []
            if not items:
                return ["No orders found for your filters."]
            if len(items) == 1:
                order = items[0] if isinstance(items[0], dict) else {}
                return [
                    f"Your last order total is {order.get('total_amount')} {order.get('currency')} "
                    f"(order #{order.get('order_id')}, status: {order.get('status')})."
                ]
            lines = ["Recent orders:"]
            for order in items[:10]:
                if not isinstance(order, dict):
                    continue
                lines.append(
                    f"- Order #{order.get('order_id')}: {order.get('status')}, "
                    f"{order.get('total_amount')} {order.get('currency')}"
                )
            return lines

        if result.tool == "orders.get_order_status":
            if not data.get("found"):
                return ["Order not found for this user."]
            order = data.get("order") if isinstance(data.get("order"), dict) else {}
            latest = data.get("latest_status_event") if isinstance(data.get("latest_status_event"), dict) else None
            lines = [
                f"Order #{order.get('id')} status: {order.get('status')} "
                f"({order.get('total_amount')} {order.get('currency')})."
            ]
            if latest:
                lines.append(
                    f"Latest status event: {latest.get('from_status')} -> {latest.get('to_status')}"
                )
            return lines

        if result.tool == "payments.get_default_payment_method":
            if not data.get("found"):
                return ["No default active payment method found."]
            method = data.get("payment_method") if isinstance(data.get("payment_method"), dict) else {}
            return [
                f"Default payment method: {method.get('provider')} "
                f"{method.get('card_brand')} ****{method.get('card_last4')} "
                f"(exp: {method.get('exp_month')}/{method.get('exp_year')})."
            ]

        return [f"{result.tool}: {data}"]


def _parse_plan(data: dict[str, Any] | None, tool_registry: ToolRegistry) -> PlannerOutput | None:
    if data is None:
        return None
    try:
        plan = PlannerOutput.model_validate(data)
    except Exception:  # noqa: BLE001
        return None

    normalized_steps: list[PlannerStep] = []
    for step in plan.steps:
        if tool_registry.has_tool(step.tool):
            normalized_steps.append(step)
    return PlannerOutput(intent=plan.intent or "unknown", steps=normalized_steps)


def _heuristic_plan(user_message: str) -> PlannerOutput:
    lower = user_message.lower()

    product_id = _extract_product_id(lower)
    if product_id is not None and any(token in lower for token in ("product", "detail", "details")):
        return PlannerOutput(
            intent="product_detail",
            steps=[PlannerStep(tool="catalog.get_product_by_id", arguments={"product_id": product_id})],
        )

    if "add" in lower and "cart" in lower:
        variant_id = _extract_variant_id(lower)
        quantity = _extract_quantity(lower) or 1
        if variant_id is not None:
            return PlannerOutput(
                intent="cart_add_item",
                steps=[
                    PlannerStep(
                        tool="cart.add_item",
                        arguments={"product_variant_id": variant_id, "quantity": quantity},
                    )
                ],
            )

    if "active cart" in lower or ("my cart" in lower and "add" not in lower):
        return PlannerOutput(intent="cart_view", steps=[PlannerStep(tool="cart.get_active_cart", arguments={})])

    if ("order status" in lower) or ("status of order" in lower):
        order_id = _extract_order_id(lower)
        if order_id is not None:
            return PlannerOutput(
                intent="order_status",
                steps=[PlannerStep(tool="orders.get_order_status", arguments={"order_id": order_id})],
            )

    if any(token in lower for token in ("last order", "latest order", "most recent order")):
        return PlannerOutput(
            intent="last_order_total",
            steps=[
                PlannerStep(
                    tool="orders.get_user_orders",
                    arguments={
                        "status": None,
                        "limit": 1,
                    },
                )
            ],
        )

    if any(token in lower for token in ("my orders", "order history", "list orders")):
        return PlannerOutput(
            intent="orders_list",
            steps=[
                PlannerStep(
                    tool="orders.get_user_orders",
                    arguments={
                        "status": _extract_status_filter(lower),
                        "limit": _extract_limit(lower) or 10,
                    },
                )
            ],
        )

    if any(token in lower for token in ("default payment", "payment method", "saved card")):
        return PlannerOutput(
            intent="default_payment_method",
            steps=[PlannerStep(tool="payments.get_default_payment_method", arguments={})],
        )

    if any(token in lower for token in ("product", "catalog", "item", "price", "buy", "need", "find", "search")):
        return PlannerOutput(
            intent="product_search",
            steps=[
                PlannerStep(
                    tool="catalog.search_products",
                    arguments={
                        "query": _extract_query_term(user_message),
                        "category_slug": _extract_slug_filter(lower, "category"),
                        "brand_slug": _extract_slug_filter(lower, "brand"),
                        "min_price": _extract_min_price(lower),
                        "max_price": _extract_max_price(lower),
                        "currency": _extract_currency(lower),
                        "only_available": True,
                        "limit": _extract_limit(lower) or 10,
                    },
                )
            ],
        )

    return PlannerOutput(intent="unknown", steps=[])


def _extract_variant_id(text: str) -> int | None:
    match = re.search(r"(?:variant|product[_ ]?variant|sku|id)\s*#?\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def _extract_product_id(text: str) -> int | None:
    match = re.search(r"(?:product)\s*#?\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def _extract_order_id(text: str) -> int | None:
    match = re.search(r"(?:order)\s*#?\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def _extract_quantity(text: str) -> int | None:
    patterns = [
        r"(?:qty|quantity)\s*[:=]?\s*(\d+)",
        r"add\s+(\d+)\s+(?:item|items|pcs|pieces)",
        r"(\d+)\s*x",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return None


def _extract_limit(text: str) -> int | None:
    match = re.search(r"(?:top|first|limit)\s+(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def _extract_status_filter(text: str) -> str | None:
    known_statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "failed"]
    for status in known_statuses:
        if status in text:
            return status
    return None


def _extract_currency(text: str) -> str | None:
    if "$" in text or "usd" in text:
        return "USD"
    if "eur" in text:
        return "EUR"
    if "try" in text or "tl" in text:
        return "TRY"
    return None


def _extract_min_price(text: str) -> float | None:
    match = re.search(r"(?:above|over|more than|>=)\s*\$?\s*(\d+(?:\.\d+)?)", text)
    if match:
        return float(match.group(1))
    return None


def _extract_max_price(text: str) -> float | None:
    match = re.search(
        r"(?:under|below|less than|lower than|lower then|cheaper than|at most|up to|upto|<=|max)\s*\$?\s*(\d+(?:\.\d+)?)",
        text,
    )
    if match:
        return float(match.group(1))
    return None


def _extract_query_term(message: str) -> str | None:
    stripped = message.strip()
    if not stripped:
        return None
    for token in ("need", "find", "search", "looking for", "show"):
        idx = stripped.lower().find(token)
        if idx >= 0:
            tail = stripped[idx + len(token) :].strip(" :,-.")
            if tail:
                cleaned = _strip_filter_phrases(tail)
                return cleaned or tail
    cleaned = _strip_filter_phrases(stripped)
    return cleaned or stripped


def _extract_slug_filter(text: str, field: str) -> str | None:
    match = re.search(rf"{field}\s*[:=]?\s*([a-z0-9-]+)", text)
    if match:
        return match.group(1).strip()
    return None


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_upper(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.upper()


def _strip_filter_phrases(text: str) -> str:
    cleaned = re.sub(
        r"\b(under|below|less than|lower than|lower then|cheaper than|at most|up to|upto|max|above|over|more than)\b.*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\b(usd|eur|try|tl)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(price|prices)\b", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip(" ,.-")
    return cleaned
