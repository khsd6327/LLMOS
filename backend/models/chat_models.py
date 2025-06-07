from typing import Optional
from pydantic import BaseModel
from src.tedos.models.data_models import ChatSession


class ChatMessageRequest(BaseModel):
    prompt: str
    model_provider: Optional[str] = None
    model_name: Optional[str] = None


class SessionCreateRequest(BaseModel):
    title: Optional[str] = None


class SessionUpdateRequest(BaseModel):
    title: Optional[str] = None
    is_pinned: Optional[bool] = None


class SessionResponse(BaseModel):
    session: ChatSession
    message: str = "Session operation completed successfully"
