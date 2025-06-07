from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class FavoriteCreateRequest(BaseModel):
    session_id: str
    message_id: str
    role: str
    content: str
    created_at: str
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    context_messages: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class FavoriteUpdateRequest(BaseModel):
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class FavoriteSearchRequest(BaseModel):
    query: Optional[str] = None
    tags: Optional[List[str]] = None
