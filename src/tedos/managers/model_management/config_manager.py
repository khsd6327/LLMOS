# ted-os-project/src/tedos/managers/model_management/config_manager.py
"""
Ted OS - 모델 설정 및 검증 관리자
"""

import logging
from typing import Dict, Any, Tuple, Optional

from ...models.enums import ModelProvider
from ...models.data_models import ModelConfig
from ...models.model_registry import ModelRegistry
from ...managers.settings import SettingsManager
from .interface_manager import InterfaceManager

logger = logging.getLogger(__name__)


class ConfigManager:
    """모델 설정 해결 및 검증 전담 클래스"""

    def __init__(self, interface_manager: InterfaceManager, settings_manager: SettingsManager):
        self.interface_manager = interface_manager
        self.settings = settings_manager

    def get_active_config(
        self, provider_display_name: Optional[str], model_id_key: Optional[str]
    ) -> Tuple[ModelProvider, ModelConfig, Any]:
        """활성 모델 설정 가져오기"""
        # Provider 이름 정규화 (enum 형태를 display name으로 변환)
        if provider_display_name:
            provider_mapping = {
                "OPENAI": "OpenAI",
                "GOOGLE": "Google",
                "ANTHROPIC": "Anthropic",
            }
            provider_display_name = provider_mapping.get(
                provider_display_name.upper(), provider_display_name
            )
        # === 디버그 정보 출력 ===
        logger.info("=== DEBUG _get_active_config ===")
        logger.info(f"Input - provider_display_name: {provider_display_name}")
        logger.info(f"Input - model_id_key: {model_id_key}")
        logger.info(
            f"Settings - ui.selected_provider: {self.settings.get('ui.selected_provider')}"
        )
        logger.info(
            f"Settings - all default models: {self.settings.get_all_default_models()}"
        )
        logger.info("================================")

        resolved_provider_display_name = provider_display_name or self.settings.get(
            "ui.selected_provider"
        )

        # 제공업체별 기본 모델 선택 (새로운 방식)
        if model_id_key:
            resolved_model_id_key = model_id_key
        else:
            # 제공업체별 기본 모델 가져오기
            if resolved_provider_display_name:
                resolved_model_id_key = self.settings.get_default_model_for_provider(
                    resolved_provider_display_name
                )
            else:
                resolved_model_id_key = None

            # 만약 제공업체별 기본 모델이 없으면 첫 번째 모델 사용
            if not resolved_model_id_key and resolved_provider_display_name:
                available_models = ModelRegistry.get_models_for_provider(
                    resolved_provider_display_name
                )
                if available_models:
                    resolved_model_id_key = list(available_models.keys())[0]
                    # 자동 선택된 모델을 설정에 저장
                    self.settings.set_default_model_for_provider(
                        resolved_provider_display_name, resolved_model_id_key
                    )
                    logger.info(
                        f"Auto-selected default model: {resolved_provider_display_name}/{resolved_model_id_key}"
                    )

        # 둘 다 없으면 첫 번째 사용 가능한 제공업체와 모델 사용
        if not resolved_provider_display_name or not resolved_model_id_key:
            logger.warning("Missing provider or model, attempting fallback...")
            available_providers = self.interface_manager.get_available_providers()
            if available_providers:
                first_provider_enum = available_providers[0]

                # Enum에서 올바른 display name으로 변환
                provider_mapping = {
                    "OPENAI": "OpenAI",
                    "GOOGLE": "Google",
                    "ANTHROPIC": "Anthropic",
                }
                resolved_provider_display_name = provider_mapping.get(
                    first_provider_enum.name, first_provider_enum.name.capitalize()
                )
                # 해당 제공업체의 기본 모델 가져오기
                resolved_model_id_key = self.settings.get_default_model_for_provider(
                    resolved_provider_display_name
                )

                # 기본 모델이 없으면 첫 번째 모델 사용
                if not resolved_model_id_key:
                    available_models = ModelRegistry.get_models_for_provider(
                        resolved_provider_display_name
                    )
                    if available_models:
                        resolved_model_id_key = list(available_models.keys())[0]
                        # 자동 선택된 값을 설정에 저장
                        self.settings.set_default_model_for_provider(
                            resolved_provider_display_name, resolved_model_id_key
                        )

                # UI 설정도 업데이트
                self.settings.set(
                    "ui.selected_provider", resolved_provider_display_name
                )
                logger.info(
                    f"Fallback selected: {resolved_provider_display_name}/{resolved_model_id_key}"
                )

        logger.info(
            f"Final resolved - provider: {resolved_provider_display_name}, model: {resolved_model_id_key}"
        )

        if not resolved_provider_display_name or not resolved_model_id_key:
            logger.error(
                f"Unable to resolve configuration - provider: {resolved_provider_display_name}, model: {resolved_model_id_key}"
            )
            raise ValueError(
                "AI Provider or Model not selected/configured in settings."
            )

        config = ModelRegistry.get_model_config(
            resolved_provider_display_name, resolved_model_id_key
        )
        if not config:
            raise ValueError(
                f"Model configuration not found for: {resolved_provider_display_name}/{resolved_model_id_key}"
            )

        provider_enum = ModelRegistry.get_provider_enum_by_display_name(
            resolved_provider_display_name
        )
        if not provider_enum or not self.interface_manager.is_provider_available(provider_enum):
            raise ValueError(
                f"API interface for '{resolved_provider_display_name}' not set up. "
                f"Ensure API key is valid, saved, and app restarted if changed."
            )

        interface = self.interface_manager.get_interface(provider_enum)
        return provider_enum, config, interface

    def get_model_info(
        self,
        provider_display_name: Optional[str] = None,
        model_id_key: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """모델 정보 가져오기"""
        try:
            _provider_enum, config, interface = self.get_active_config(
                provider_display_name, model_id_key
            )

            return {
                "config": {
                    "provider": config.provider.value,
                    "model_name": config.model_name,
                    "display_name": config.display_name,
                    "max_tokens": config.max_tokens,
                    "description": config.description,
                    "input_cost_per_1k": config.input_cost_per_1k,
                    "output_cost_per_1k": config.output_cost_per_1k,
                },
                "features": {
                    "supports_streaming": config.supports_streaming,
                    "supports_functions": config.supports_functions,
                    "supports_vision": config.supports_vision,
                },
                "interface_features": interface.get_supported_features(),
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return None

    def validate_configuration(self) -> Dict[str, Any]:
        """설정 유효성 검증"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "provider_status": {},
        }

        # 제공업체별 상태 확인
        for provider in ModelProvider:
            provider_key = provider.value
            api_key = self.settings.get_api_key(provider)

            # Provider 이름을 올바른 display name으로 변환
            provider_display_name = self._get_provider_display_name(provider)
            
            status = {
                "has_api_key": bool(api_key),
                "interface_initialized": self.interface_manager.is_provider_available(provider),
                "available_models": len(
                    ModelRegistry.get_models_for_provider(provider_display_name)
                ),
            }

            if not api_key:
                validation_result["warnings"].append(
                    f"{provider.name} API key not configured"
                )
            elif not self.interface_manager.is_provider_available(provider):
                validation_result["errors"].append(
                    f"{provider.name} interface failed to initialize"
                )
                validation_result["valid"] = False

            validation_result["provider_status"][provider_key] = status

        # 선택된 모델 확인 (새로운 제공업체별 기본 모델 방식)
        selected_provider = self.settings.get("ui.selected_provider")
        
        if not selected_provider:
            validation_result["warnings"].append("No provider selected")
        else:
            # 해당 제공업체의 기본 모델 확인
            selected_model = self.settings.get_default_model_for_provider(selected_provider)
            
            if not selected_model:
                validation_result["warnings"].append(f"No default model selected for {selected_provider}")
            else:
                try:
                    self.get_active_config(selected_provider, selected_model)
                except Exception as e:
                    validation_result["errors"].append(f"Invalid model configuration: {e}")
                    validation_result["valid"] = False

        return validation_result

    def _get_provider_display_name(self, provider: ModelProvider) -> str:
        """Provider enum을 올바른 display name으로 변환"""
        provider_mapping = {
            ModelProvider.OPENAI: "OpenAI",
            ModelProvider.ANTHROPIC: "Anthropic", 
            ModelProvider.GOOGLE: "Google",
        }
        return provider_mapping.get(provider, provider.name.capitalize())