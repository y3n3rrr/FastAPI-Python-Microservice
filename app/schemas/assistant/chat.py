from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    user_id: int
    message: str = Field(min_length=1)
    session_id: int | None = None


class ChatSessionRead(BaseModel):
    id: int
    user_id: int
    title: str | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ChatMessageRead(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    model: str | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ChatResponse(BaseModel):
    session: ChatSessionRead
    user_message: ChatMessageRead
    assistant_message: ChatMessageRead
