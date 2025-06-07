# src/tedos/__init__.py
"""
Ted OS - 개인 맞춤형 AI 비서 시스템
"""

from .core.config import APP_VERSION, APP_NAME

__version__ = APP_VERSION
__title__ = APP_NAME
__author__ = "Ted OS Team"
__description__ = "개인 맞춤형 AI 비서 시스템"

# 주요 클래스들 노출
from .managers.settings import SettingsManager
from .managers.chat_sessions import ChatSessionManager
from .managers.usage_tracker import UsageTracker
from .managers.model_manager import EnhancedModelManager

__all__ = [
    "SettingsManager",
    "ChatSessionManager", 
    "UsageTracker",
    "EnhancedModelManager",
]
