# ted-os-project/src/tedos/managers/model_manager.py
"""
Ted OS - 모델 관리자 (리팩토링됨)
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Generator

from ..models.data_models import TokenUsage
from ..managers.settings import SettingsManager
from ..managers.usage_tracker import UsageTracker
from .model_management import InterfaceManager, ResponseManager, ConfigManager

logger = logging.getLogger(__name__)


class ModelManager(InterfaceManager):
    """기본 모델 관리자 - InterfaceManager 상속"""

    def __init__(self, settings_manager: SettingsManager):
        super().__init__(settings_manager)


class EnhancedModelManager(ModelManager):
    """향상된 모델 관리자 - 분리된 클래스들을 조합"""

    def __init__(self, settings_manager: SettingsManager, usage_tracker: UsageTracker):
        super().__init__(settings_manager)
        
        # 분리된 관리자들 초기화
        self.config_manager = ConfigManager(self, settings_manager)
        self.response_manager = ResponseManager(
            self, settings_manager, usage_tracker, self.config_manager.get_active_config
        )

    def generate(
        self,
        messages: List[Dict[str, Any]],
        provider_display_name: Optional[str] = None,
        model_id_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[str, Optional[TokenUsage]]:
        """AI 응답 생성 - ResponseManager에 위임"""
        return self.response_manager.generate(
            messages, provider_display_name, model_id_key, **kwargs
        )

    def stream_generate(
        self,
        messages: List[Dict[str, Any]],
        provider_display_name: Optional[str] = None,
        model_id_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Generator[Tuple[str, Optional[TokenUsage]], None, None]:
        """AI 스트리밍 응답 생성 - ResponseManager에 위임"""
        yield from self.response_manager.stream_generate(
            messages, provider_display_name, model_id_key, **kwargs
        )

    def stop_generation(self):
        """현재 진행 중인 AI 응답 생성을 중단 - ResponseManager에 위임"""
        self.response_manager.stop_generation()

    def is_generating(self) -> bool:
        """현재 AI 응답 생성 중인지 확인 - ResponseManager에 위임"""
        return self.response_manager.is_generating()

    def get_model_info(
        self,
        provider_display_name: Optional[str] = None,
        model_id_key: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """모델 정보 가져오기 - ConfigManager에 위임"""
        return self.config_manager.get_model_info(provider_display_name, model_id_key)

    def validate_configuration(self) -> Dict[str, Any]:
        """설정 유효성 검증 - ConfigManager에 위임"""
        return self.config_manager.validate_configuration()

    # 하위 호환성을 위한 메서드들
    def _get_active_config(
        self, provider_display_name: Optional[str], model_id_key: Optional[str]
    ):
        """하위 호환성을 위한 메서드"""
        return self.config_manager.get_active_config(provider_display_name, model_id_key)
