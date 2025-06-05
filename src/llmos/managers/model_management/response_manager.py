# src/llmos/managers/model_management/response_manager.py
"""
LLM OS - AI 응답 생성 관리자
"""

import logging
from datetime import datetime
from typing import List, Optional, Any, Tuple, Generator, Dict

from ...models.enums import ModelProvider
from ...models.data_models import TokenUsage, ModelConfig
from ...managers.settings import SettingsManager
from ...managers.usage_tracker import UsageTracker
from ...utils.output_renderer import OutputRenderer
from .interface_manager import InterfaceManager

logger = logging.getLogger(__name__)


class ResponseManager:
    """AI 응답 생성 및 스트리밍 전담 클래스"""

    def __init__(
        self,
        interface_manager: InterfaceManager,
        settings_manager: SettingsManager,
        usage_tracker: UsageTracker,
        config_resolver_callback,
    ):
        self.interface_manager = interface_manager
        self.settings = settings_manager
        self.usage_tracker = usage_tracker
        self.output_renderer = OutputRenderer()
        self.get_active_config = config_resolver_callback
        self._should_stop_generation = False  # 출력 정지 플래그
        self._is_generating = False  # 생성 중 상태 플래그

    def generate(
        self,
        messages: List[Dict[str, Any]],
        provider_display_name: Optional[str] = None,
        model_id_key: Optional[str] = None,
        **kwargs: Any,
    ) -> Tuple[str, Optional[TokenUsage]]:
        """AI 응답 생성"""
        _provider_enum, config, interface = self.get_active_config(
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
        # 중단 플래그 초기화 및 생성 상태 설정
        self._should_stop_generation = False
        self._is_generating = True
        
        try:
            _provider_enum, config, interface = self.get_active_config(
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
                # 중단 요청 확인
                if self._should_stop_generation:
                    logger.info("Generation stopped by user request")
                    break
                    
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
                    elif isinstance(chunk_data, str):
                        # 새로운 청크만 yield (누적하지 않음)
                        if chunk_data:  # 빈 문자열이 아닌 경우만
                            accumulated_response += chunk_data
                            yield self.output_renderer.process_output(chunk_data), final_usage_data
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
                
        finally:
            # 생성 상태 플래그 리셋
            self._is_generating = False
            if self._should_stop_generation:
                logger.info("AI generation stopped by user request")

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

    def stop_generation(self):
        """현재 진행 중인 AI 응답 생성을 중단"""
        logger.info("User requested to stop AI generation")
        self._should_stop_generation = True

    def is_generating(self) -> bool:
        """현재 AI 응답 생성 중인지 확인"""
        return self._is_generating