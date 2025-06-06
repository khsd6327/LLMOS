# ted-os-project/src/tedos/interfaces/google_client.py
"""
Ted OS - Google 인터페이스
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Generator, Union

from google import generativeai as genai  # type: ignore

from .base import LLMInterface
from ..models.data_models import TokenUsage

logger = logging.getLogger(__name__)


class GoogleInterface(LLMInterface):
    """Google Gemini API 인터페이스"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Google API key is missing.")

        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            logger.error(f"Google genai.configure failed: {e}")
            raise

    def _prepare_google_args(
        self, messages: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Google Gemini API 형식에 맞게 메시지 준비"""
        gemini_contents: List[Dict[str, Any]] = []
        system_instruction_text: Optional[str] = None

        # 시스템 메시지 분리
        temp_msgs_for_processing = []
        for msg_data_item in messages:
            if msg_data_item["role"] == "system":
                content = msg_data_item["content"]
                system_instruction_text = (
                    content
                    if isinstance(content, str)
                    else (
                        content[0]["text"]
                        if isinstance(content, list)
                        and content
                        and "text" in content[0]
                        else None
                    )
                )
            else:
                temp_msgs_for_processing.append(msg_data_item)

        # 메시지를 Gemini 형식으로 변환
        for msg_item_to_process in temp_msgs_for_processing:
            role = msg_item_to_process["role"]
            if role == "assistant":
                role = "model"

            parts_for_gemini: List[Union[str, Dict[str, Any]]] = []
            content_data = msg_item_to_process["content"]

            if isinstance(content_data, str):
                parts_for_gemini.append(content_data)
            elif isinstance(content_data, list):
                current_text_parts_buffer = []

                for item_content_part in content_data:
                    if item_content_part["type"] == "text":
                        current_text_parts_buffer.append(item_content_part["text"])
                    elif (
                        item_content_part["type"] == "image_url"
                        and "image_url" in item_content_part
                    ):
                        # 텍스트 버퍼가 있으면 먼저 추가
                        if current_text_parts_buffer:
                            parts_for_gemini.append(" ".join(current_text_parts_buffer))
                            current_text_parts_buffer = []

                        # 이미지 처리
                        data_uri = item_content_part["image_url"]["url"]
                        try:
                            header, encoded_data = data_uri.split(",", 1)
                            mime_type = header.split(":")[1].split(";")[0]
                            parts_for_gemini.append(
                                {
                                    "inline_data": {
                                        "mime_type": mime_type,
                                        "data": encoded_data,
                                    }
                                }
                            )
                        except Exception as e_img:
                            logger.error(f"Google image_url processing error: {e_img}")

                # 남은 텍스트 버퍼 처리
                if current_text_parts_buffer:
                    parts_for_gemini.append(" ".join(current_text_parts_buffer))

            if parts_for_gemini:
                # 연속된 같은 역할 메시지 병합
                if gemini_contents and gemini_contents[-1]["role"] == role:
                    logger.warning(
                        f"Consecutive '{role}' messages for Gemini. Merging logic might be needed or API may reject."
                    )
                    if (
                        isinstance(parts_for_gemini[0], str)
                        and isinstance(gemini_contents[-1]["parts"][0], str)
                        and len(gemini_contents[-1]["parts"]) == 1
                        and len(parts_for_gemini) == 1
                    ):
                        gemini_contents[-1]["parts"][0] += f"\n{parts_for_gemini[0]}"  # type: ignore
                    else:
                        gemini_contents.append(
                            {"role": role, "parts": parts_for_gemini}
                        )
                else:
                    gemini_contents.append({"role": role, "parts": parts_for_gemini})

        return gemini_contents, system_instruction_text

    def generate(
        self, messages: List[Dict[str, Any]], model: str, **kwargs: Any
    ) -> Tuple[str, Optional[TokenUsage]]:
        """Google Gemini API로 응답 생성 (안전성 강화)"""
        try:
            gemini_contents, system_instruction = self._prepare_google_args(messages)

            # 모델 생성
            gen_model_args = {"model_name": model}
            if system_instruction:
                gen_model_args["system_instruction"] = system_instruction

            generative_model = genai.GenerativeModel(**gen_model_args)

            # 생성 설정
            gen_config_args = {}
            if "temperature" in kwargs:
                gen_config_args["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                gen_config_args["max_output_tokens"] = kwargs["max_tokens"]
            if "top_p" in kwargs:
                gen_config_args["top_p"] = kwargs["top_p"]

            generation_config = (
                genai.types.GenerationConfig(**gen_config_args)
                if gen_config_args
                else None
            )

            # 컨텐츠 생성
            response = generative_model.generate_content(
                contents=gemini_contents, generation_config=generation_config
            )

            # === 아래 부분이 핵심 수정 사항입니다 ===
            # 1. 응답 후보(candidates)가 없는 경우 확인
            if not response.candidates:
                logger.warning("Google API 응답에 후보(candidate)가 없습니다.")
                if hasattr(response, "prompt_feedback"):
                    logger.warning(f"차단 이유: {response.prompt_feedback}")
                return "", None

            candidate = response.candidates[0]

            # 2. 요청 종료 이유(finish_reason) 확인 (1이 'STOP', 즉 성공)
            if candidate.finish_reason != 1:
                # finish_reason의 이름과 안전 등급을 포함하여 상세한 로그 기록
                logger.warning(
                    f"Google API 호출이 정상적으로 완료되지 않았습니다. "
                    f"종료 이유: {candidate.finish_reason.name} ({candidate.finish_reason}), "
                    f"안전 등급: {candidate.safety_ratings}"
                )
                return "", None  # 차단 또는 오류 시 빈 문자열 반환

            # 3. 응답에 내용(content)이 있는지 확인
            if not candidate.content or not candidate.content.parts:
                logger.warning(
                    "Google API 응답이 정상 종료되었으나 내용(content)이 없습니다."
                )
                return "", None

            content = "".join(
                part.text for part in candidate.content.parts if hasattr(part, "text")
            )
            # === 수정 끝 ===

            # 토큰 사용량 정보 생성
            usage_data = None
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage_meta = response.usage_metadata
                usage_data = TokenUsage(
                    input_tokens=usage_meta.prompt_token_count,
                    output_tokens=usage_meta.candidates_token_count,
                    total_tokens=usage_meta.total_token_count,
                    model_name=model,
                    provider="google",
                    timestamp=datetime.now(),
                )

            return content, usage_data

        except Exception as e:
            # 예상치 못한 예외 발생 시, 상세한 오류 로그를 남기고 앱이 중단되지 않도록 함
            logger.error(
                f"Google API 'generate' 함수에서 심각한 오류 발생: {e}", exc_info=True
            )
            return "", None

    def stream(
        self, messages: List[Dict[str, Any]], model: str, **kwargs: Any
    ) -> Generator[Any, None, None]:
        """Google Gemini API로 스트리밍 응답 생성"""
        try:
            gemini_contents, system_instruction = self._prepare_google_args(messages)

            # 모델 생성
            gen_model_args = {"model_name": model}
            if system_instruction:
                gen_model_args["system_instruction"] = system_instruction  # type: ignore

            generative_model = genai.GenerativeModel(**gen_model_args)  # type: ignore

            # 생성 설정
            gen_config_args = {}
            if "temperature" in kwargs:
                gen_config_args["temperature"] = kwargs["temperature"]
            if "max_tokens" in kwargs:
                gen_config_args["max_output_tokens"] = kwargs["max_tokens"]

            generation_config = (
                genai.types.GenerationConfig(**gen_config_args)
                if gen_config_args
                else None
            )

            # 스트리밍 생성
            stream_response = generative_model.generate_content(
                contents=gemini_contents,
                stream=True,
                generation_config=generation_config,
            )  # type: ignore

            final_usage_data = None
            for chunk in stream_response:
                try:
                    # chunk와 chunk.text 존재 여부 확인  ← 이 부분들이 새로 추가된 부분!
                    if chunk and hasattr(chunk, "text"):
                        chunk_text = chunk.text
                        if (
                            chunk_text and chunk_text.strip()
                        ):  # None 체크와 빈 문자열 체크
                            yield chunk_text
                except ValueError as ve:
                    # 차단된 응답 등의 경우 - 로그만 남기고 계속 진행
                    logger.warning(f"Google streaming chunk blocked or invalid: {ve}")
                    continue
                except AttributeError as ae:
                    # chunk.text 속성이 없는 경우
                    logger.warning(
                        f"Google streaming chunk has no text attribute: {ae}"
                    )
                    continue

                # 사용량 정보 수집
                if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
                    um = chunk.usage_metadata
                    final_usage_data = TokenUsage(
                        input_tokens=um.prompt_token_count,
                        output_tokens=um.candidates_token_count,
                        total_tokens=um.total_token_count,
                        model_name=model,
                        provider="google",
                        timestamp=datetime.now(),
                    )

            if final_usage_data:
                yield ("__USAGE__", final_usage_data)

        except Exception as e:
            logger.error(f"Google API streaming error: {e}")
            raise

    def get_supported_features(self) -> Dict[str, bool]:
        """Google Gemini 지원 기능"""
        return {
            "streaming": True,
            "vision": True,
            "functions": True,
            "system_messages": True,
            "long_context": True,
            "multimodal": True,
        }