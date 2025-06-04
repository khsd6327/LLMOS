# src/llmos/ui/pages/chat_components/response_generator.py
"""
AI 응답 생성 담당 모듈
"""

import logging
from typing import Dict, List, Optional, Any

from ....managers.chat_sessions import ChatSessionManager
from ....managers.model_manager import EnhancedModelManager
from ....models.data_models import ChatSession

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """AI 응답 생성 데이터 전문가 (UI 렌더링 없음)"""

    def __init__(
        self,
        chat_manager: ChatSessionManager,
        model_manager: EnhancedModelManager,
        get_current_model_config_callback,
    ):
        self.chat_manager = chat_manager
        self.model_manager = model_manager
        self.get_current_model_config = get_current_model_config_callback

    def stream_response(self, session: ChatSession):
        """AI 응답을 스트림으로 생성하여 반환 (UI 렌더링 없음)"""
        api_messages = self._prepare_api_messages(session.messages)
        model_config = self.get_current_model_config()

        if not model_config:
            yield "오류: 현재 선택된 모델 설정을 찾을 수 없습니다.", None
            return

        try:
            if model_config.supports_streaming:
                yield from self.model_manager.stream_generate(api_messages)
            else:
                # 스트리밍을 지원하지 않는 모델을 위한 생성기 래퍼
                response, usage = self.model_manager.generate(api_messages)
                yield response, usage
        except Exception as e:
            logger.error(f"Error during response generation: {e}", exc_info=True)
            yield f"오류가 발생했습니다: {e}", None

    def _prepare_api_messages(
        self, messages: List[Dict[str, Any]], max_history: int = 10
    ) -> List[Dict[str, Any]]:
        """API 호출용 메시지 준비"""
        # ... (이 함수는 변경 없음) ...
        api_messages: List[Dict[str, Any]] = []
        recent_messages = messages[-max_history:]

        system_prompt: Optional[str] = None
        filtered_messages = []

        for msg in recent_messages:
            if msg["role"] == "system" and isinstance(msg["content"], str):
                system_prompt = msg["content"]
            elif msg.get("type") != "image_display":
                filtered_messages.append(msg)

        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})

        for msg in filtered_messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        return api_messages