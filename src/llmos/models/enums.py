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


class ArtifactType(Enum):
    """아티팩트 타입 열거형"""
    TEXT = "text"
    CODE = "code"
    MARKDOWN = "markdown"
    JSON = "json"
    PROMPT = "prompt"
    MEMORY = "memory"
    RESEARCH = "research"
    IMAGE = "image"


class MessageRole(Enum):
    """메시지 역할 열거형"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class UIPage(Enum):
    """UI 페이지 타입 열거형"""
    CHAT = "chat"
    SETTINGS = "settings"
    ARTIFACTS = "artifacts"
    DEBUG = "debug"
    EXPORT = "export"


class LogLevel(Enum):
    """로그 레벨 열거형"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"