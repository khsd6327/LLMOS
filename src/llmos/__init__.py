# src/llmos/__init__.py
"""
LLM OS - 개인 맞춤형 AI 비서 시스템
"""

from .core.config import APP_VERSION, APP_NAME

__version__ = APP_VERSION
__title__ = APP_NAME
__author__ = "LLM OS Team"
__description__ = "개인 맞춤형 AI 비서 시스템"

# 주요 클래스들 노출
from .core.app import EnhancedLLMOSApp, create_app, run_app
from .managers.settings import SettingsManager
from .managers.chat_sessions import ChatSessionManager
from .managers.artifacts import ArtifactManager
from .managers.usage_tracker import UsageTracker
from .managers.model_manager import EnhancedModelManager

__all__ = [
    "EnhancedLLMOSApp",
    "create_app",
    "run_app",
    "SettingsManager",
    "ChatSessionManager", 
    "ArtifactManager",
    "UsageTracker",
    "EnhancedModelManager"
]