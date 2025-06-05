# ted-os-project/src/llmos/interfaces/anthropic_client.py
# src/llmos/interfaces/anthropic_client.py
"""
LLM OS - Anthropic 인터페이스
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Generator

import anthropic  # type: ignore

from .base import LLMInterface
from ..models.data_models import TokenUsage

logger = logging.getLogger(__name__)


class AnthropicInterface(LLMInterface):
    """Anthropic Claude API 인터페이스"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Anthropic API key is missing.")

        try:
            self.client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            logger.error(f"Anthropic client init failed: {e}")
            raise

    def _prepare_anthropic_args(
        self, messages: List[Dict[str, Any]], kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Anthropic API 형식에 맞게 메시지와 매개변수 준비"""
        api_args = kwargs.copy()
        system_prompt_text = None

        # 시스템 메시지 분리
        processed_messages = []
        for msg in messages:
            if msg["role"] == "system":
                content = msg["content"]
                system_prompt_text = (
                    content
                    if isinstance(content, str)
                    else (
                        content[0]["text"]
                        if isinstance(content, list)
                        and content
                        and "text" in content[0]
                        else ""
                    )
                )
            else:
                processed_messages.append(msg)

        # 연속된 같은 역할 메시지 병합
        merged_messages = []
        for msg_item in processed_messages:
            current_role = msg_item["role"]
            current_content = msg_item["content"]

            # 같은 역할의 연속 메시지 병합
            if merged_messages and merged_messages[-1]["role"] == current_role:
                if isinstance(current_content, str) and isinstance(
                    merged_messages[-1]["content"], str
                ):
                    merged_messages[-1]["content"] += f"\n{current_content}"
                    continue
                elif isinstance(current_content, list) and isinstance(
                    merged_messages[-1]["content"], list
                ):
                    merged_messages[-1]["content"].extend(current_content)
                    continue
                else:
                    logger.warning(
                        f"Consecutive messages with role '{current_role}' and complex content for Anthropic. API might reject."
                    )

            # 이미지 URL을 Anthropic 형식으로 변환
            if isinstance(current_content, list):
                converted_content = []
                for item_part in current_content:
                    if item_part["type"] == "image_url" and "image_url" in item_part:
                        data_uri = item_part["image_url"]["url"]
                        try:
                            header, encoded = data_uri.split(",", 1)
                            mime_type = header.split(":", 1)[1].split(";", 1)[0]
                            converted_content.append(
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": mime_type,
                                        "data": encoded,
                                    },
                                }
                            )
                        except Exception as e_img:
                            logger.error(f"Anthropic image processing error: {e_img}")
                    elif item_part["type"] == "text":
                        converted_content.append(item_part)

                merged_messages.append(
                    {"role": current_role, "content": converted_content}
                )
            elif isinstance(current_content, str):
                merged_messages.append(
                    {"role": current_role, "content": current_content}
                )
            else:
                logger.warning(
                    f"Unsupported message content type for Anthropic: {type(current_content)}"
                )

        api_args["messages"] = merged_messages
        if system_prompt_text:
            api_args["system"] = system_prompt_text

        return api_args

    def generate(
        self, messages: List[Dict[str, Any]], model: str, **kwargs: Any
    ) -> Tuple[str, Optional[TokenUsage]]:
        """Anthropic API로 응답 생성"""
        try:
            max_tokens = kwargs.pop("max_tokens", 4096)
            api_args = self._prepare_anthropic_args(messages, kwargs)

            response = self.client.messages.create(
                model=model, max_tokens=max_tokens, **api_args
            )  # type: ignore

            content = "".join(
                [block.text for block in response.content if block.type == "text"]
            )

            # 토큰 사용량 정보 생성
            usage_data = None
            if response.usage:
                usage_data = TokenUsage(
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens
                    + response.usage.output_tokens,
                    model_name=model,
                    provider="anthropic",
                    timestamp=datetime.now(),
                )

            return content, usage_data

        except Exception as e:
            logger.error(f"Anthropic API error (generate): {e}")
            raise

    def stream(
        self, messages: List[Dict[str, Any]], model: str, **kwargs: Any
    ) -> Generator[Any, None, None]:
        """Anthropic API로 스트리밍 응답 생성"""
        try:
            max_tokens = kwargs.pop("max_tokens", 4096)
            api_args = self._prepare_anthropic_args(messages, kwargs)
            final_usage_data = None

            with self.client.messages.stream(
                model=model, max_tokens=max_tokens, **api_args
            ) as stream_obj:  # type: ignore
                for event in stream_obj:
                    if (
                        event  # ← 이 부분들이 새로 추가된 안전장치!
                        and event.type == "content_block_delta"
                        and hasattr(event, "delta")
                        and event.delta
                        and hasattr(event.delta, "type")
                        and event.delta.type == "text_delta"
                        and hasattr(event.delta, "text")
                        and event.delta.text
                    ):
                        text_content = event.delta.text
                        if text_content.strip():  # 빈 문자열 체크
                            yield text_content

                final_message = stream_obj.get_final_message()
                if final_message and final_message.usage:
                    final_usage_data = TokenUsage(
                        input_tokens=final_message.usage.input_tokens,
                        output_tokens=final_message.usage.output_tokens,
                        total_tokens=final_message.usage.input_tokens
                        + final_message.usage.output_tokens,
                        model_name=model,
                        provider="anthropic",
                        timestamp=datetime.now(),
                    )

            if final_usage_data:
                yield ("__USAGE__", final_usage_data)

        except Exception as e:
            logger.error(f"Anthropic API streaming error: {e}")
            raise

    def get_supported_features(self) -> Dict[str, bool]:
        """Anthropic 지원 기능"""
        return {
            "streaming": True,
            "vision": True,
            "functions": True,
            "system_messages": True,
            "long_context": True,
        }