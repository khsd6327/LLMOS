# ted-os-project/src/tedos/managers/model_management/interface_manager.py
"""
Ted OS - AI 인터페이스 관리자
"""

import logging
from typing import Dict, List, Optional

from ...interfaces.base import LLMInterface
from ...interfaces.openai_client import OpenAIInterface
from ...interfaces.anthropic_client import AnthropicInterface
from ...interfaces.google_client import GoogleInterface
from ...models.enums import ModelProvider
from ...managers.settings import SettingsManager

logger = logging.getLogger(__name__)


class InterfaceManager:
    """AI 인터페이스 초기화 및 관리 전담 클래스"""

    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self.interfaces: Dict[ModelProvider, LLMInterface] = {}
        self._initialize_interfaces()

    def _initialize_interfaces(self):
        """AI 인터페이스들 초기화"""
        self.interfaces.clear()
        api_keys = self.settings.get("api_keys", {})

        # OpenAI 인터페이스
        openai_key = api_keys.get(ModelProvider.OPENAI.value)
        if openai_key:
            try:
                self.interfaces[ModelProvider.OPENAI] = OpenAIInterface(openai_key)
                logger.info("OpenAI interface initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI interface: {e}")
        else:
            logger.info(
                "OpenAI API key not found/empty. OpenAI interface not initialized."
            )

        # Anthropic 인터페이스
        anthropic_key = api_keys.get(ModelProvider.ANTHROPIC.value)
        if anthropic_key:
            try:
                self.interfaces[ModelProvider.ANTHROPIC] = AnthropicInterface(
                    anthropic_key
                )
                logger.info("Anthropic interface initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic interface: {e}")
        else:
            logger.info(
                "Anthropic API key not found/empty. Anthropic interface not initialized."
            )

        # Google 인터페이스
        google_key = api_keys.get(ModelProvider.GOOGLE.value)
        if google_key:
            try:
                self.interfaces[ModelProvider.GOOGLE] = GoogleInterface(google_key)
                logger.info("Google interface initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Google interface: {e}")
        else:
            logger.info(
                "Google API key not found/empty. Google interface not initialized."
            )

    def get_available_providers(self) -> List[ModelProvider]:
        """사용 가능한 제공업체 목록"""
        return list(self.interfaces.keys())

    def is_provider_available(self, provider: ModelProvider) -> bool:
        """제공업체 사용 가능 여부"""
        return provider in self.interfaces

    def get_interface(self, provider: ModelProvider) -> Optional[LLMInterface]:
        """특정 제공업체 인터페이스 반환"""
        return self.interfaces.get(provider)

    def refresh_interfaces(self):
        """인터페이스들 새로고침"""
        self._initialize_interfaces()