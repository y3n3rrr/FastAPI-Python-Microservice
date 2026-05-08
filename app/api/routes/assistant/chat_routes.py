from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db_session
from app.entities.user import User
from app.repositories.assistant.chat_repository import ChatRepository
from app.repositories.user_repository import UserRepository
from app.schemas.assistant.chat import ChatMessageRead, ChatRequest, ChatResponse
from app.services.assistant.chat_service import ChatService
from app.services.assistant.llm_client import LLMClient


router = APIRouter(prefix="/assistant/chat", tags=["assistant"])


def get_chat_service(db: Session = Depends(get_db_session)) -> ChatService:
    return ChatService(
        repository=ChatRepository(db),
        user_repository=UserRepository(db),
        llm_client=LLMClient(),
        db=db,
    )


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    session, user_message, assistant_message = service.handle_chat(payload)
    return ChatResponse(session=session, user_message=user_message, assistant_message=assistant_message)


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageRead])
def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> list[ChatMessageRead]:
    return service.list_session_messages(session_id=session_id, user_id=current_user.id)
