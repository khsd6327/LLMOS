# ted-os-project/src/tedos/models/data_models.py
"""
Ted OS - 데이터 모델 정의
"""

import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from .enums import ModelProvider

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
            data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "TokenUsage":
        """딕셔너리에서 객체 생성"""
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class ChatSession:
    """채팅 세션 데이터 모델"""

    id: str
    title: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    is_pinned: bool = False  # 채팅 고정 여부 (기본값: False)

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "ChatSession":
        """딕셔너리에서 객체 생성"""
        return cls(
            id=data["id"],
            title=data["title"],
            messages=data.get("messages", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
            is_pinned=data.get("is_pinned", False),
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
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppState":
        """딕셔너리에서 객체 생성"""
        last_activity = None
        if data.get("last_activity"):
            last_activity = datetime.fromisoformat(data["last_activity"])

        return cls(
            current_session_id=data.get("current_session_id"),
            current_page=data.get("current_page", "chat"),
            is_initialized=data.get("is_initialized", False),
            last_activity=last_activity,
        )
@dataclass
class SpotifyTrack:
    """Spotify 트랙 정보"""
    
    id: str
    name: str
    artists: str  # 쉼표로 구분된 아티스트 목록
    duration_ms: int
    album_name: str
    release_date: str
    popularity: int
    added_at: Optional[str] = None
    raw_genres: List[str] = None
    mapped_genre: str = "기타"
    
    def __post_init__(self):
        if self.raw_genres is None:
            self.raw_genres = []
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "artists": self.artists,
            "duration_ms": self.duration_ms,
            "album_name": self.album_name,
            "release_date": self.release_date,
            "popularity": self.popularity,
            "added_at": self.added_at,
            "raw_genres": self.raw_genres,
            "mapped_genre": self.mapped_genre,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SpotifyTrack":
        """딕셔너리에서 SpotifyTrack 객체 생성"""
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            artists=data.get("artists", ""),
            duration_ms=data.get("duration_ms", 0),
            album_name=data.get("album_name", ""),
            release_date=data.get("release_date", ""),
            popularity=data.get("popularity", 0),
            added_at=data.get("added_at"),
            raw_genres=data.get("raw_genres", []),
            mapped_genre=data.get("mapped_genre", "기타"),
        )

@dataclass
class SpotifyPlaylist:
    """Spotify 플레이리스트 정보"""
    
    id: str
    name: str
    tracks_total: int
    owner_id: Optional[str] = None
    description: Optional[str] = None
    public: bool = False
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "tracks_total": self.tracks_total,
            "owner_id": self.owner_id,
            "description": self.description,
            "public": self.public,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SpotifyPlaylist":
        """딕셔너리에서 객체 생성"""
        return cls(
            id=data["id"],
            name=data["name"],
            tracks_total=data.get("tracks_total", 0),
            owner_id=data.get("owner_id"),
            description=data.get("description"),
            public=data.get("public", False),
        )


@dataclass
class SpotifySettings:
    """Spotify API 설정"""
    
    client_id: str
    client_secret: str
    redirect_uri: str
    port_type: str = "fixed"  # "fixed" or "dynamic"
    cache_path: str = ".spotify_cache"
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환 (secret 제외)"""
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "port_type": self.port_type,
            "cache_path": self.cache_path,
            # client_secret은 보안상 제외
        }
    
    def is_valid(self) -> bool:
        """설정이 유효한지 확인"""
        return all([
            self.client_id,
            self.client_secret,
            self.redirect_uri
        ])
        
        
@dataclass
class FavoriteMessage:
    """즐겨찾기된 메시지 데이터 모델"""

    id: str  # 즐겨찾기 고유 ID
    session_id: str  # 원본 메시지가 속한 세션 ID
    message_id: str  # 원본 메시지의 고유 ID (ChatSession.messages 내 메시지 식별자 역할)
    role: str  # 메시지 역할 (예: "user", "assistant")
    content: str  # 메시지 본문
    favorited_at: datetime  # 즐겨찾기 지정 시간
    created_at: datetime # 원본 메시지 생성 시간 (메시지가 처음 기록된 시간)
    model_provider: Optional[ModelProvider] = None # 메시지 생성 시 사용된 모델 제공자 (AI 응답인 경우)
    model_name: Optional[str] = None # 메시지 생성 시 사용된 모델명 (AI 응답인 경우)
    context_messages: Optional[List[Dict[str, Any]]] = None  # 즐겨찾기 시점의 대화 문맥 (ChatSession.messages와 유사한 형식)
    tags: List[str] = field(default_factory=list) # 사용자가 추가할 수 있는 태그
    notes: Optional[str] = None # 사용자가 추가할 수 있는 간단한 메모

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (JSON 직렬화용)"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "message_id": self.message_id,
            "role": self.role,
            "content": self.content,
            "favorited_at": self.favorited_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "model_provider": self.model_provider.value if self.model_provider else None,
            "model_name": self.model_name,
            "context_messages": self.context_messages,
            "tags": self.tags,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FavoriteMessage":
        """딕셔너리에서 객체 생성"""
        provider_val = data.get("model_provider")
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            message_id=data["message_id"],
            role=data["role"],
            content=data["content"],
            favorited_at=datetime.fromisoformat(data["favorited_at"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            model_provider=ModelProvider(provider_val) if provider_val else None,
            model_name=data.get("model_name"),
            context_messages=data.get("context_messages"),
            tags=data.get("tags", []),
            notes=data.get("notes"),
        )
