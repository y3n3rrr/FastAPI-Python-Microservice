from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.entities.assistant.chat_message import ChatMessage
from app.entities.assistant.chat_session import ChatSession
from app.repositories.assistant.chat_repository import ChatRepository
from app.repositories.user_repository import UserRepository
from app.schemas.assistant.chat import ChatRequest
from app.services.assistant.llm_client import LLMClient


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

        answer = self.llm_client.generate_answer(payload.message)
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=answer,
            model="mock-llm-v1",
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
