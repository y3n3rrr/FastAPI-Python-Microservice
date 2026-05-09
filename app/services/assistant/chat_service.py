from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.assistant.chat_message import ChatMessage
from app.entities.assistant.chat_session import ChatSession
from app.repositories.cart.cart_item_repository import CartItemRepository
from app.repositories.cart.cart_repository import CartRepository
from app.repositories.catalog.product_repository import ProductRepository
from app.repositories.catalog.product_variant_repository import ProductVariantRepository
from app.repositories.order.order_repository import OrderRepository
from app.repositories.order.order_status_history_repository import OrderStatusHistoryRepository
from app.repositories.payment.user_payment_method_repository import UserPaymentMethodRepository
from app.repositories.assistant.chat_repository import ChatRepository
from app.repositories.user_repository import UserRepository
from app.schemas.assistant.chat import ChatRequest
from app.services.assistant.agents import (
    AnswerAgent,
    AssistantToolRepositories,
    AssistantToolset,
    OrchestratorAgent,
    PlannerAgent,
    RetrieverAgent,
    ToolRegistry,
    ValidationAgent,
)
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
        orchestrator, tool_registry = self._build_orchestrator(user_id=payload.user_id)
        answer_text = orchestrator.run(
            user_message=payload.message,
            conversation_context=conversation_context,
            tool_registry=tool_registry,
        )
        llm_response: LLMResponse = LLMResponse(answer=answer_text, model=self._assistant_model_name())
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

    def list_available_tools(self, *, user_id: int) -> list[dict[str, Any]]:
        user = self.user_repository.get(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        _, tool_registry = self._build_orchestrator(user_id=user_id)
        return tool_registry.list_for_planner()

    def _build_conversation_context(self, session_id: int) -> str:
        messages = self.repository.list_messages_by_session(session_id)
        recent = messages[-8:]
        if not recent:
            return "No prior messages."
        lines = [f"{item.role}: {item.content}" for item in recent]
        return "\n".join(lines)

    def _build_orchestrator(self, *, user_id: int) -> tuple[OrchestratorAgent, ToolRegistry]:
        repositories = AssistantToolRepositories(
            product_repository=ProductRepository(self.db),
            product_variant_repository=ProductVariantRepository(self.db),
            cart_repository=CartRepository(self.db),
            cart_item_repository=CartItemRepository(self.db),
            order_repository=OrderRepository(self.db),
            order_status_history_repository=OrderStatusHistoryRepository(self.db),
            user_payment_method_repository=UserPaymentMethodRepository(self.db),
        )
        toolset = AssistantToolset(user_id=user_id, repositories=repositories)
        tool_registry = ToolRegistry(toolset.to_specs())
        orchestrator = OrchestratorAgent(
            planner=PlannerAgent(self.llm_client),
            retriever=RetrieverAgent(),
            validator=ValidationAgent(),
            answerer=AnswerAgent(self.llm_client),
        )
        return orchestrator, tool_registry

    def _assistant_model_name(self) -> str:
        provider = self.llm_client.settings.assistant_llm_provider.strip().lower()
        if provider == "ollama":
            return self.llm_client.settings.assistant_ollama_model
        return "agentic-mock-v1"
