from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.entities.catalog.product import Product
from app.entities.catalog.product_variant import ProductVariant
from app.entities.assistant.chat_message import ChatMessage
from app.entities.assistant.chat_session import ChatSession
from app.entities.order.order import Order
from app.entities.payment.payment_intent import PaymentIntent
from app.repositories.assistant.chat_repository import ChatRepository
from app.repositories.user_repository import UserRepository
from app.schemas.assistant.chat import ChatRequest
from app.services.assistant.llm_client import LLMClient, LLMResponse


class ChatService:
    def __init__(self, repository: ChatRepository, user_repository: UserRepository, llm_client: LLMClient, db: Session) -> None:
        self.repository = repository
        self.user_repository = user_repository
        self.llm_client = llm_client
        self.db = db

    def handle_chat(self, payload: ChatRequest) -> tuple[ChatSession, ChatMessage, ChatMessage]:
        user = self.user_repository.get(payload.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        session = self._get_or_create_session(payload.user_id, payload.session_id)

        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=payload.message,
            model=None,
        )
        self.repository.add_message(user_message)
        self.db.flush()

        conversation_context = self._build_conversation_context(session.id)
        database_context = self._build_database_context(payload.message, payload.user_id)
        llm_response: LLMResponse = self.llm_client.generate_answer(
            user_prompt=payload.message,
            database_context=database_context,
            conversation_context=conversation_context,
        )
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=llm_response.answer,
            model=llm_response.model,
        )
        self.repository.add_message(assistant_message)
        self.db.flush()

        self.db.commit()
        self.db.refresh(session)
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)

        return session, user_message, assistant_message

    def _get_or_create_session(self, user_id: int, session_id: int | None) -> ChatSession:
        if session_id is not None:
            existing = self.repository.get_session(session_id)
            if existing is None or existing.user_id != user_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
            return existing

        session = ChatSession(
            user_id=user_id,
            title=None,
            is_active=True,
        )
        self.repository.add_session(session)
        self.db.flush()
        return session

    def list_session_messages(self, *, session_id: int, user_id: int) -> list[ChatMessage]:
        session = self.repository.get_session(session_id)
        if session is None or session.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
        return self.repository.list_messages_by_session(session_id)

    def _build_conversation_context(self, session_id: int) -> str:
        messages = self.repository.list_messages_by_session(session_id)
        recent = messages[-8:]
        if not recent:
            return "No prior messages."
        lines = [f"{item.role}: {item.content}" for item in recent]
        return "\n".join(lines)

    def _build_database_context(self, question: str, user_id: int) -> str:
        lower = question.lower()
        lines: list[str] = []

        total_products = self.db.scalar(select(func.count()).select_from(Product)) or 0
        total_variants = self.db.scalar(select(func.count()).select_from(ProductVariant)) or 0
        lines.append(f"Catalog totals: products={total_products}, variants={total_variants}.")

        user_order_count = self.db.scalar(
            select(func.count()).select_from(Order).where(Order.user_id == user_id)
        ) or 0
        lines.append(f"User {user_id} total orders: {user_order_count}.")

        last_orders = list(
            self.db.scalars(
                select(Order)
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc(), Order.id.desc())
                .limit(5)
            )
        )
        if last_orders:
            order_bits = [
                f"(id={order.id}, status={order.status}, total={self._fmt_amount(order.total_amount)} {order.currency})"
                for order in last_orders
            ]
            lines.append("Recent user orders: " + ", ".join(order_bits))
        else:
            lines.append("Recent user orders: none.")

        last_intents = list(
            self.db.scalars(
                select(PaymentIntent)
                .where(PaymentIntent.user_id == user_id)
                .order_by(PaymentIntent.created_at.desc(), PaymentIntent.id.desc())
                .limit(5)
            )
        )
        if last_intents:
            intent_bits = [
                (
                    f"(id={intent.id}, status={intent.status}, amount={self._fmt_amount(intent.amount)} "
                    f"{intent.currency}, provider={intent.provider}, order_id={intent.order_id})"
                )
                for intent in last_intents
            ]
            lines.append("Recent payment intents: " + ", ".join(intent_bits))
        else:
            lines.append("Recent payment intents: none.")

        if any(keyword in lower for keyword in ("product", "catalog", "item", "price", "variant")):
            recent_variants = list(
                self.db.scalars(
                    select(ProductVariant)
                    .where(ProductVariant.is_active.is_(True))
                    .order_by(ProductVariant.updated_at.desc(), ProductVariant.id.desc())
                    .limit(10)
                )
            )
            if recent_variants:
                variant_bits = [
                    f"(id={v.id}, sku={v.sku}, name={v.name}, price={self._fmt_amount(v.price)} {v.currency})"
                    for v in recent_variants
                ]
                lines.append("Active variant sample: " + ", ".join(variant_bits))

        return "\n".join(lines)

    @staticmethod
    def _fmt_amount(value: Decimal | None) -> str:
        if value is None:
            return "0.00"
        return f"{value:.2f}"
