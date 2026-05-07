import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.entities.assistant.chat_message import ChatMessage
from app.entities.assistant.chat_session import ChatSession


class ChatRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_session(self, session_id: int) -> ChatSession | None:
        return self.db.get(ChatSession, session_id)

    def add_session(self, session: ChatSession) -> ChatSession:
        self.db.add(session)
        return session

    def add_message(self, message: ChatMessage) -> ChatMessage:
        self.db.add(message)
        return message

    def list_messages_by_session(self, session_id: int) -> builtins.list[ChatMessage]:
        stmt = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.id)
        return list(self.db.scalars(stmt))
