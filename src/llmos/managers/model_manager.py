# src/llmos/managers/model_manager.py
"""
LLM OS - 모델 관리자
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Generator

from ..interfaces.base import LLMInterface
from ..interfaces.openai_client import OpenAIInterface
from ..interfaces.anthropic_client import AnthropicInterface
from ..interfaces.google_client import GoogleInterface
from ..models.enums import ModelProvider
from ..models.data_models import TokenUsage, ModelConfig
from ..models.model_registry import ModelRegistry
from ..managers.settings import SettingsManager
from ..managers.usage_tracker import UsageTracker
from ..utils.output_renderer import OutputRenderer

logger = logging.getLogger(__name__)


class ModelManager:
    """기본 모델 관리자"""

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


class EnhancedModelManager(ModelManager):
    """향상된 모델 관리자"""

    def __init__(self, settings_manager: SettingsManager, usage_tracker: UsageTracker):
        super().__init__(settings_manager)
        self.output_renderer = OutputRenderer()
        self.usage_tracker = usage_tracker

    def _get_active_config(
        self, provider_display_name: Optional[str], model_id_key: Optional[str]
    ) -> Tuple[ModelProvider, ModelConfig, LLMInterface]:
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
            available_providers = self.get_available_providers()
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
        if not provider_enum or provider_enum not in self.interfaces:
            raise ValueError(
                f"API interface for '{resolved_provider_display_name}' not set up. "
                f"Ensure API key is valid, saved, and app restarted if changed."
            )

        interface = self.interfaces[provider_enum]
        return provider_enum, config, interface

    def generate(
        self,
        messages: List[Dict[str, Any]],
        provider_display_name: Optional[str] = None,
        model_id_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[str, Optional[TokenUsage]]:
        """AI 응답 생성"""
        _provider_enum, config, interface = self._get_active_config(
            provider_display_name, model_id_key
        )

        # 매개변수 준비
        params = {
            "temperature": self.settings.get("defaults.temperature", 0.7),
            "max_tokens": min(
                self.settings.get("defaults.max_tokens", config.max_tokens),
                config.max_tokens,
            ),
        }
        params.update(kwargs)

        logger.info(
            f"Generating with {config.provider.value}/{config.model_name} "
            f"(Display: {config.display_name}). Messages: {len(messages)}. Params: {params}"
        )

        # API 호출
        response_text, usage = interface.generate(
            messages, model=config.model_name, **params
        )

        # 사용량 추적
        if usage and self.usage_tracker:
            input_cost = (usage.input_tokens / 1000) * config.input_cost_per_1k
            output_cost = (usage.output_tokens / 1000) * config.output_cost_per_1k
            usage.cost_usd = round(input_cost + output_cost, 6)
            self.usage_tracker.add_usage(usage)

        return self.output_renderer.process_output(response_text), usage

    def stream_generate(
        self,
        messages: List[Dict[str, Any]],
        provider_display_name: Optional[str] = None,
        model_id_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Generator[Tuple[str, Optional[TokenUsage]], None, None]:
        """AI 스트리밍 응답 생성"""
        _provider_enum, config, interface = self._get_active_config(
            provider_display_name, model_id_key
        )

        # 스트리밍 지원 확인
        if not config.supports_streaming:
            logger.info(
                f"Model {config.display_name} does not support streaming. Falling back to generate."
            )
            actual_provider_name = provider_display_name or self.settings.get(
                "ui.selected_provider"
            )
            actual_model_key = model_id_key or self.settings.get("defaults.model")
            response_text, usage = self.generate(
                messages, actual_provider_name, actual_model_key, **kwargs
            )
            yield response_text, usage
            return

        # 매개변수 준비
        params = {
            "temperature": self.settings.get("defaults.temperature", 0.7),
            "max_tokens": min(
                self.settings.get("defaults.max_tokens", config.max_tokens),
                config.max_tokens,
            ),
        }
        params.update(kwargs)

        logger.info(
            f"Streaming with {config.provider.value}/{config.model_name} "
            f"(Display: {config.display_name}). Messages: {len(messages)}. Params: {params}"
        )

        accumulated_response = ""
        final_usage_data: Optional[TokenUsage] = None

        # 스트리밍 호출
        stream_iterator = interface.stream(messages, model=config.model_name, **params)

        for chunk_data in stream_iterator:
            try:
                if (
                    isinstance(chunk_data, tuple)
                    and len(chunk_data) == 2
                    and chunk_data[0] == "__USAGE__"
                ):
                    # 사용량 정보
                    final_usage_data = chunk_data[1]
                    if final_usage_data and self.usage_tracker:
                        input_cost = (
                            final_usage_data.input_tokens / 1000
                        ) * config.input_cost_per_1k
                        output_cost = (
                            final_usage_data.output_tokens / 1000
                        ) * config.output_cost_per_1k
                        final_usage_data.cost_usd = round(input_cost + output_cost, 6)
                        self.usage_tracker.add_usage(final_usage_data)
                elif (
                    isinstance(chunk_data, str) and chunk_data.strip()
                ):  # ← 빈 문자열 체크 추가
                    # 텍스트 청크
                    accumulated_response += chunk_data
                    yield self.output_renderer.process_output(
                        accumulated_response
                    ), final_usage_data
                elif chunk_data is None:
                    # None 값은 무시하고 계속 진행
                    continue
                else:
                    # 예상치 못한 데이터 타입
                    continue
            except Exception as e:
                continue  # 개별 청크 오류 시 전체 스트리밍을 중단하지 않음

        # OpenAI의 경우 수동으로 토큰 사용량 계산
        if (
            not final_usage_data
            and accumulated_response
            and config.provider == ModelProvider.OPENAI
        ):
            final_usage_data = self._estimate_openai_usage(
                messages, accumulated_response, config
            )
            if final_usage_data and self.usage_tracker:
                input_cost = (
                    final_usage_data.input_tokens / 1000
                ) * config.input_cost_per_1k
                output_cost = (
                    final_usage_data.output_tokens / 1000
                ) * config.output_cost_per_1k
                final_usage_data.cost_usd = round(input_cost + output_cost, 6)
                self.usage_tracker.add_usage(final_usage_data)
            yield self.output_renderer.process_output(
                accumulated_response
            ), final_usage_data

        # 최종 응답이 없는 경우
        elif not accumulated_response and final_usage_data:
            yield "", final_usage_data

    def _estimate_openai_usage(
        self, messages: List[Dict[str, Any]], response_text: str, config: ModelConfig
    ) -> Optional[TokenUsage]:
        """OpenAI 토큰 사용량 추정"""
        try:
            import tiktoken

            # 모델명 매핑
            tiktoken_model_name = config.model_name
            if "gpt-4o-mini" in config.model_name:
                tiktoken_model_name = "gpt-4o-mini"
            elif "gpt-4-turbo" in config.model_name:
                tiktoken_model_name = "gpt-4-turbo"
            elif "gpt-4o" == config.model_name:
                tiktoken_model_name = "gpt-4o"
            elif "gpt-3.5-turbo" in config.model_name:
                tiktoken_model_name = "gpt-3.5-turbo"

            # 인코더 가져오기
            try:
                enc = tiktoken.encoding_for_model(tiktoken_model_name)
            except KeyError:
                logger.warning(
                    f"Tiktoken encoding for '{tiktoken_model_name}' not found, using 'cl100k_base'."
                )
                enc = tiktoken.get_encoding("cl100k_base")

            # 입력 토큰 계산
            num_input_tokens = 0
            for msg in messages:
                content_str = ""
                if isinstance(msg.get("content"), str):
                    content_str = msg.get("content", "")
                elif isinstance(msg.get("content"), list):
                    for part in msg.get("content", []):  # type: ignore
                        if part.get("type") == "text":
                            content_str += part.get("text", "") + "\n"
                num_input_tokens += (
                    len(enc.encode(content_str)) + 5
                )  # 메시지당 오버헤드

            # 출력 토큰 계산
            num_output_tokens = len(enc.encode(response_text))

            usage_data = TokenUsage(
                input_tokens=num_input_tokens,
                output_tokens=num_output_tokens,
                total_tokens=num_input_tokens + num_output_tokens,
                model_name=config.model_name,
                provider=config.provider.value,
                timestamp=datetime.now(),
            )

            logger.info(
                f"Manually constructed TokenUsage for OpenAI stream: {usage_data.to_dict()}"
            )
            return usage_data

        except ImportError:
            logger.warning(
                "tiktoken library not installed. Cannot calculate token usage for OpenAI streaming."
            )
            return None
        except Exception as e:
            logger.error(
                f"Error during manual TokenUsage construction for OpenAI stream: {e}"
            )
            return None

    def get_model_info(
        self,
        provider_display_name: Optional[str] = None,
        model_id_key: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """모델 정보 가져오기"""
        try:
            _provider_enum, config, interface = self._get_active_config(
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

            status = {
                "has_api_key": bool(api_key),
                "interface_initialized": provider in self.interfaces,
                "available_models": len(
                    ModelRegistry.get_models_for_provider(provider.name.capitalize())
                ),
            }

            if not api_key:
                validation_result["warnings"].append(
                    f"{provider.name} API key not configured"
                )
            elif provider not in self.interfaces:
                validation_result["errors"].append(
                    f"{provider.name} interface failed to initialize"
                )
                validation_result["valid"] = False

            validation_result["provider_status"][provider_key] = status

        # 선택된 모델 확인
        selected_provider = self.settings.get("ui.selected_provider")
        selected_model = self.settings.get("defaults.model")

        if not selected_provider:
            validation_result["warnings"].append("No provider selected")
        elif not selected_model:
            validation_result["warnings"].append("No model selected")
        else:
            try:
                self._get_active_config(selected_provider, selected_model)
            except Exception as e:
                validation_result["errors"].append(f"Invalid model configuration: {e}")
                validation_result["valid"] = False

        return validation_result
