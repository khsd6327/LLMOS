# src/llmos/interfaces/openai_client.py
"""
LLM OS - OpenAI 인터페이스
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Generator

import openai  # type: ignore

from .base import LLMInterface
from ..models.data_models import TokenUsage

logger = logging.getLogger(__name__)


class OpenAIInterface(LLMInterface):
    """OpenAI API 인터페이스"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is missing or empty.")

        try:
            self.client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            logger.error(f"OpenAI client initialization failed: {e}")
            raise

    def _get_model_params(self, model_id: str, **kwargs: Any) -> Dict[str, Any]:
        """모델 매개변수 준비 (o-series 모델 지원)"""
        params = {}

        # o-series 모델 감지
        is_o_series = (
            model_id.startswith("o4-mini")
            or model_id.startswith("o3-")
            or model_id.startswith("o1-")
            or "o4-mini" in model_id
            or "o3-mini" in model_id
            or "o1-preview" in model_id
            or "o1-mini" in model_id
        )

        # max_tokens 파라미터 처리
        if "max_tokens" in kwargs:
            if is_o_series:
                # o-series 모델은 max_completion_tokens 사용
                params["max_completion_tokens"] = kwargs["max_tokens"]
                logger.info(
                    f"o-series model detected ({model_id}): using max_completion_tokens={kwargs['max_tokens']}"
                )
            else:
                # 일반 모델은 max_tokens 사용
                params["max_tokens"] = kwargs["max_tokens"]

        # temperature 파라미터
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]

        # OpenAI 전용 매개변수
        valid_openai_params = [
            "top_p",
            "presence_penalty",
            "frequency_penalty",
            "stop",
            "seed",
            "logprobs",
            "top_logprobs",
        ]

        for k, v in kwargs.items():
            if k in valid_openai_params:
                params[k] = v

        return params

        # OpenAI 전용 매개변수
        valid_openai_params = [
            "top_p",
            "presence_penalty",
            "frequency_penalty",
            "stop",
            "seed",
            "logprobs",
            "top_logprobs",
        ]

        for k, v in kwargs.items():
            if k in valid_openai_params:
                params[k] = v

        return params

    def generate(
        self, messages: List[Dict[str, Any]], model: str, **kwargs: Any
    ) -> Tuple[str, Optional[TokenUsage]]:
        """OpenAI API로 응답 생성"""
        try:
            api_params = self._get_model_params(model, **kwargs)

            response = self.client.chat.completions.create(
                model=model, messages=messages, **api_params  # type: ignore
            )

            content = response.choices[0].message.content or ""

            # 토큰 사용량 정보 생성
            usage_data = None
            if response.usage:
                usage_data = TokenUsage(
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    model_name=model,
                    provider="openai",
                    timestamp=datetime.now(),
                )

            return content, usage_data

        except openai.APIConnectionError as e:  # type: ignore
            logger.error(f"OpenAI API Connection Error: {e}")
            raise ConnectionError(f"OpenAI API Connection Error: {e}")
        except openai.RateLimitError as e:  # type: ignore
            logger.error(f"OpenAI API Rate Limit Error: {e}")
            raise PermissionError(f"OpenAI API Rate Limit Error: {e}")
        except openai.APIStatusError as e:  # type: ignore
            logger.error(
                f"OpenAI API Status Error (code {e.status_code}): {e.response}"
            )
            raise ValueError(f"OpenAI API Status Error: {e.response}")
        except Exception as e:
            logger.error(f"OpenAI API error (generate): {e}")
            raise

    def stream(
        self, messages: List[Dict[str, Any]], model: str, **kwargs: Any
    ) -> Generator[str, None, None]:
        """OpenAI API로 스트리밍 응답 생성"""
        try:
            api_params = self._get_model_params(model, **kwargs)

            stream_response = self.client.chat.completions.create(
                model=model,
                messages=messages,  # type: ignore
                stream=True,
                **api_params,
            )

            for chunk in stream_response:
                if (
                    chunk.choices
                    and chunk.choices[0].delta
                    and chunk.choices[0].delta.content is not None
                ):
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content

        except Exception as e:
            logger.error(f"OpenAI API streaming error: {e}")
            raise

    def get_supported_features(self) -> Dict[str, bool]:
        """OpenAI 지원 기능"""
        return {
            "streaming": True,
            "vision": True,
            "functions": True,
            "system_messages": True,
            "logprobs": True,
            "seed": True,
        }

    def estimate_tokens(self, text: str) -> int:
        """OpenAI tiktoken을 이용한 토큰 수 추정"""
        try:
            import tiktoken

            # 기본 인코딩 사용
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except ImportError:
            logger.warning("tiktoken not installed, using basic estimation")
            return super().estimate_tokens(text)
        except Exception as e:
            logger.warning(f"Error estimating tokens: {e}")
            return super().estimate_tokens(text)