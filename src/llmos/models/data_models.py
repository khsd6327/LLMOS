# src/llmos/models/data_models.py
"""
LLM OS - 데이터 모델 정의
"""

import base64
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any

from .enums import ModelProvider, ArtifactType

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """AI 모델 설정 정보"""
    provider: ModelProvider
    model_name: str
    display_name: str
    max_tokens: int
    supports_streaming: bool
    supports_functions: bool
    supports_vision: bool = False
    description: str = ""
    input_cost_per_1k: float = 0.0  # USD per 1K input tokens
    output_cost_per_1k: float = 0.0  # USD per 1K output tokens


@dataclass
class TokenUsage:
    """토큰 사용량 정보"""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model_name: str
    provider: str
    timestamp: datetime
    cost_usd: float = 0.0

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        data = asdict(self)
        if isinstance(self.timestamp, datetime):
            data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'TokenUsage':
        """딕셔너리에서 객체 생성"""
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class Artifact:
    """아티팩트 데이터 모델"""
    id: str
    type: ArtifactType
    title: str
    content: Any
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (직렬화용)"""
        content_data = self.content
        if self.type == ArtifactType.IMAGE and isinstance(self.content, bytes):
            try:
                content_data = base64.b64encode(self.content).decode('utf-8')
            except Exception as e:
                logger.warning(f"Failed to encode image content for artifact {self.id}: {e}")
                
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "content": content_data,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Artifact':
        """딕셔너리에서 객체 생성"""
        content_data = data["content"]
        artifact_type = ArtifactType(data["type"])
        
        if artifact_type == ArtifactType.IMAGE and isinstance(content_data, str):
            try:
                content_data = base64.b64decode(content_data)
            except Exception as e:
                logger.warning(f"Could not decode base64 content for image artifact {data['id']}: {e}")
        
        return cls(
            id=data["id"],
            type=artifact_type,
            title=data["title"],
            content=content_data,
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class ChatSession:
    """채팅 세션 데이터 모델"""
    id: str
    title: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "title": self.title,
            "messages": self.messages,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ChatSession':
        """딕셔너리에서 객체 생성"""
        return cls(
            id=data["id"],
            title=data["title"],
            messages=data.get("messages", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class AppState:
    """애플리케이션 상태 정보"""
    current_session_id: Optional[str] = None
    current_page: str = "chat"
    is_initialized: bool = False
    last_activity: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "current_session_id": self.current_session_id,
            "current_page": self.current_page,
            "is_initialized": self.is_initialized,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AppState':
        """딕셔너리에서 객체 생성"""
        last_activity = None
        if data.get("last_activity"):
            last_activity = datetime.fromisoformat(data["last_activity"])
            
        return cls(
            current_session_id=data.get("current_session_id"),
            current_page=data.get("current_page", "chat"),
            is_initialized=data.get("is_initialized", False),
            last_activity=last_activity
        )