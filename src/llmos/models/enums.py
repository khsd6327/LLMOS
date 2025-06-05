# ted-os-project/src/llmos/models/enums.py
# src/llmos/models/enums.py
"""
LLM OS - Enum 클래스 정의
"""

from enum import Enum


class ModelProvider(Enum):
    """AI 모델 제공업체 열거형"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class MessageRole(Enum):
    """메시지 역할 열거형"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class UIPage(Enum):
    """UI 페이지 타입 열거형"""

    CHAT = "chat"
    SETTINGS = "settings"
    DEBUG = "debug"
    EXPORT = "export"
    SPOTIFY = "spotify"



class LogLevel(Enum):
    """로그 레벨 열거형"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
class SpotifyTimeRange(Enum):
    """Spotify Top 트랙 시간 범위"""
    
    SHORT_TERM = "short_term"  # 약 4주
    MEDIUM_TERM = "medium_term"  # 약 6개월
    LONG_TERM = "long_term"  # 전체 기간


class SpotifySortKey(Enum):
    """Spotify 플레이리스트 정렬 기준"""
    
    NAME = "name"  # 곡 제목
    ARTISTS = "artists"  # 아티스트명
    ALBUM_NAME = "album_name"  # 앨범명
    ADDED_AT = "added_at"  # 추가된 날짜
    RELEASE_DATE = "release_date"  # 발매일
    DURATION_MS = "duration_ms"  # 곡 길이
    POPULARITY = "popularity"  # 인기도