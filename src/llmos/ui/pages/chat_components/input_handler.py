# src/llmos/ui/pages/chat_components/input_handler.py
"""
사용자 입력 처리 담당 모듈
"""

import base64
import logging
from typing import Dict, List, Any, Union

import streamlit as st

from ....models.data_models import ChatSession
from ....managers.state_manager import get_state
from ....managers.chat_sessions import ChatSessionManager
from ....utils.helpers import detect_image_mime_type, trigger_autoscroll

logger = logging.getLogger(__name__)


class InputHandler:
    """사용자 입력 처리 전담 클래스"""

    def __init__(self, chat_manager: ChatSessionManager):
        self.chat_manager = chat_manager

    def handle_user_input(self, session: ChatSession, user_input: str):
        """사용자 입력 처리 (v4 - 스크롤 트리거 추가)"""
        # 사용자 메시지를 세션에 추가
        user_content = self._prepare_user_content(user_input)
        session.messages.append({"role": "user", "content": user_content, "model_display_name": user_input})
        self.chat_manager.update_session(session)
        st.session_state.current_session = session

        # 업로드된 이미지 상태 초기화
        self._clear_uploaded_image()

        # 렌더러가 AI 응답 생성을 시작하도록 플래그 설정
        state = get_state() # StateManager 인스턴스 가져오기
        state.generating_response = True # state 사용
        
        # 사용자 메시지가 추가된 직후 스크롤 실행
        trigger_autoscroll()
        
    def _prepare_user_content(
        self, text_input: str
    ) -> Union[str, List[Dict[str, Any]]]:
        """사용자 콘텐츠 준비 (텍스트 + 이미지) (StateManager 사용)"""
        state = get_state() # StateManager 인스턴스 가져오기
        uploaded_image_bytes = state.chat_uploaded_image_bytes # state 사용
        uploaded_image_name = state.chat_uploaded_image_name   # state 사용
        message_parts: List[Dict[str, Any]] = []
        
        if uploaded_image_bytes and uploaded_image_name:
            current_session = state.current_session # state에서 현재 세션 가져오기
            if current_session: # 현재 세션 객체가 있는지 확인
                current_session.messages.append(
                    {
                        "role": "user", "type": "image_display",
                        "content": uploaded_image_bytes, "caption": f"입력 이미지: {uploaded_image_name}",
                    }
                )
            else:
                logger.warning("No current_session found in state to append image display message.")

            mime_type = detect_image_mime_type(uploaded_image_bytes, uploaded_image_name)
            base64_image = base64.b64encode(uploaded_image_bytes).decode("utf-8")
            message_parts.append(
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
            )
        
        message_parts.append({"type": "text", "text": text_input})
        
        if len(message_parts) == 1 and message_parts[0]["type"] == "text":
            return text_input
        else:
            return message_parts

    def _clear_uploaded_image(self):
        """업로드된 이미지 상태 초기화 (StateManager 사용)"""
        state = get_state() # StateManager 인스턴스 가져오기
        state.chat_uploaded_image_bytes = None # state 사용
        state.chat_uploaded_image_name = None   # state 사용
        state.last_uploaded_filename_integrated = None # state 사용