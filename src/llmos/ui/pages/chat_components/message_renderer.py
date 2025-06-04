# src/llmos/ui/pages/chat_components/message_renderer.py
"""
채팅 메시지 렌더링 담당 모듈
"""

import logging
from typing import Dict, Any

import streamlit as st

from ....managers.chat_sessions import ChatSessionManager
from ....managers.model_manager import EnhancedModelManager
from ....models.data_models import ChatSession
from ....ui.components import EnhancedUI
from ....managers.favorite_manager import FavoriteManager
from ....utils.helpers import trigger_autoscroll

logger = logging.getLogger(__name__)


class MessageRenderer:
    """메시지 렌더링 총책임자"""

    def __init__(
        self,
        chat_manager: ChatSessionManager,
        model_manager: EnhancedModelManager,
        ui: EnhancedUI,
        favorite_manager: FavoriteManager,
        get_current_model_config_callback,
        retry_last_response_callback,
        response_generator, # ResponseGenerator 인스턴스 주입
        auto_generate_title_callback, # 제목 생성 콜백 주입
    ):
        self.chat_manager = chat_manager
        self.model_manager = model_manager
        self.ui = ui
        self.favorite_manager = favorite_manager
        self.get_current_model_config = get_current_model_config_callback
        self.retry_last_response = retry_last_response_callback
        self.response_generator = response_generator
        self.auto_generate_title = auto_generate_title_callback

    def render_chat_messages(self, session: ChatSession):
        """채팅 기록 렌더링 및 실시간 응답 스트리밍"""
        # 1. 기존 채팅 기록 렌더링
        for i, msg_data in enumerate(session.messages):
            # ... (이하 _render_message_content, _render_model_info 등 기존 함수들은 그대로 유지) ...
            self._render_single_message(session, i, msg_data)

        # 2. 새로운 AI 응답을 실시간으로 렌더링해야 하는 경우
        if st.session_state.get("generating_response"):
            self._render_streaming_response(session)

    def _render_single_message(self, session: ChatSession, msg_index: int, msg_data: Dict[str, Any]):
        """단일 메시지 렌더링 로직"""
        msg_key = f"msg_{session.id}_{msg_index}"
        is_last_message = msg_index == len(session.messages) - 1

        with st.chat_message(msg_data["role"]):
            if msg_data.get("type") == "image_display" and isinstance(msg_data["content"], bytes):
                st.image(msg_data["content"], caption=msg_data.get("caption", "첨부 이미지"), width=250)
            elif st.session_state.get("editing_message_key") == msg_key and msg_data["role"] == "user":
                self._render_edit_mode(session, msg_index, msg_key)
            else:
                self._render_message_content(msg_data)
                if msg_data["role"] == "assistant":
                    self._render_model_info(msg_data)
                self._render_message_actions(session, msg_index, msg_key, msg_data, is_last_message)

    def _render_streaming_response(self, session: ChatSession):
        """실시간 AI 응답 스트리밍 렌더링"""
        # ... (함수 앞부분의 with st.chat_message... 등은 동일) ...
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                stream_gen = self.response_generator.stream_response(session)
                for response_chunk, usage in stream_gen:
                    if st.session_state.get("should_stop_streaming"):
                        st.session_state.should_stop_streaming = False
                        break
                    full_response = response_chunk
                    response_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
            finally:
                st.session_state.generating_response = False

            response_placeholder.markdown(full_response, unsafe_allow_html=True)

            # 렌더링 완료 후 완성된 응답을 세션에 저장
            if full_response and not full_response.startswith("오류"):
                # ... (응답 저장 로직은 동일) ...
                model_config = self.get_current_model_config()
                model_info = {}
                if model_config:
                    model_info = {
                        "model_provider": model_config.provider.value,
                        "model_name": model_config.model_name,
                        "model_display_name": model_config.display_name,
                    }
                session.messages.append({
                    "role": "assistant", "content": full_response, **model_info
                })
                self.chat_manager.update_session(session)
                last_user_prompt = ""
                for msg in reversed(session.messages):
                    if msg["role"] == "user":
                        if isinstance(msg["content"], str):
                            last_user_prompt = msg["content"]
                        elif isinstance(msg["content"], list):
                             for part in msg["content"]:
                                if part.get("type") == "text":
                                    last_user_prompt = part["text"]
                                    break
                        break
                self.auto_generate_title(session, last_user_prompt, full_response)

                # AI 응답이 완료된 직후 스크롤 실행
                trigger_autoscroll()
                st.rerun()
                
    def _render_edit_mode(self, session: ChatSession, msg_index: int, msg_key: str):
        """메시지 편집 모드 렌더링"""
        edited_text = st.text_area("메시지 수정:", value=st.session_state.get("edit_text_content", ""), key=f"edit_area_main_chat_{msg_key}", height=100)
        btn_cols = st.columns(8)
        if btn_cols[0].button("💾 저장", key=f"save_edit_main_chat_{msg_key}"):
            session.messages[msg_index]["content"] = edited_text
            self.chat_manager.update_session(session)
            st.session_state.current_session = session
            st.session_state.editing_message_key = None
            st.rerun()
        if btn_cols[1].button("❌ 취소", key=f"cancel_edit_main_chat_{msg_key}"):
            st.session_state.editing_message_key = None
            st.rerun()

    def _render_message_content(self, msg_data: Dict[str, Any]):
        """메시지 내용 렌더링"""
        content = msg_data["content"]
        if isinstance(content, str):
            st.markdown(content, unsafe_allow_html=True)
        elif isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    st.markdown(part["text"], unsafe_allow_html=True)

    def _render_model_info(self, msg_data: Dict[str, Any]):
        """AI 메시지의 모델 정보 표시"""
        model_display_name = msg_data.get("model_display_name")
        model_name = msg_data.get("model_name") 
        model_provider = msg_data.get("model_provider")
        display_text = None
        if model_display_name:
            display_text = model_display_name
        elif model_name:
            display_text = model_name
        elif model_provider:
            display_text = f"{model_provider} 모델"
        if display_text:
            st.caption(f"🤖 {display_text}로 생성됨")
        else:
            current_model = self.get_current_model_config()
            if current_model:
                st.caption(f"🤖 {current_model.display_name}로 생성됨 (추정)")

    def _render_message_actions(self, session: ChatSession, msg_index: int, msg_key: str, msg_data: Dict[str, Any], is_last_message: bool):
        """메시지 액션 버튼들 렌더링"""
        action_cols = st.columns([1, 1, 1, 7])
        if msg_data["role"] == "user":
            if action_cols[0].button("✏️", key=f"edit_btn_main_chat_area_{msg_key}", help="메시지 수정"):
                st.session_state.editing_message_key = msg_key
                if isinstance(msg_data["content"], str):
                    st.session_state.edit_text_content = msg_data["content"]
                elif isinstance(msg_data["content"], list):
                    text_to_edit = ""
                    for part in msg_data["content"]:
                        if part.get("type") == "text":
                            text_to_edit = part["text"]
                            break
                    st.session_state.edit_text_content = text_to_edit
                else:
                    st.session_state.edit_text_content = ""
                st.rerun()
        elif msg_data["role"] == "assistant":
            if isinstance(msg_data["content"], str):
                if action_cols[0].button("📋", key=f"copy_btn_main_chat_area_{msg_key}", help="응답 복사"):
                    self._copy_to_clipboard(msg_data["content"])
            if is_last_message:
                if action_cols[1].button("🔄", key=f"retry_btn_main_chat_area_{msg_key}", help="AI 응답 재시도"):
                    self.retry_last_response(session)
                    st.rerun()
            if action_cols[2].button("⭐", key=f"fav_btn_{msg_key}", help="즐겨찾기에 추가/제거"):
                self._toggle_favorite_message(session, msg_data, msg_index)
                st.rerun()

    def _copy_to_clipboard(self, text: str):
        """클립보드 복사"""
        st.code(text, language=None)
        st.success("위 텍스트를 선택하여 복사하세요 (Ctrl+A, Ctrl+C).", icon="📋")
        st.session_state.pending_toast = ("내용이 복사 준비되었습니다 (위 박스에서 선택).", "📋")
        
    def _toggle_favorite_message(self, session: ChatSession, msg_data: Dict[str, Any], msg_idx: int):
        """메시지를 즐겨찾기에 추가하거나 이미 있다면 제거합니다."""
        from datetime import datetime
        message_content_str = ""
        if isinstance(msg_data.get("content"), str):
            message_content_str = msg_data["content"]
        elif isinstance(msg_data.get("content"), list):
            for part in msg_data["content"]:
                if part.get("type") == "text":
                    message_content_str = part["text"]
                    break
        if not message_content_str and msg_data.get("type") == "image_display":
            st.toast("텍스트 내용이 없는 이미지는 즐겨찾기할 수 없습니다.", icon="⚠️")
            return
        if not message_content_str:
            st.toast("내용이 없는 메시지는 즐겨찾기할 수 없습니다.", icon="⚠️")
            return
        context_messages_for_favorite = []
        context_window_start = max(0, msg_idx - 4)
        for i in range(context_window_start, msg_idx + 1):
            ctx_msg = session.messages[i]
            ctx_role = ctx_msg.get("role")
            ctx_content_value = ctx_msg.get("content")
            ctx_content_str = ""
            if isinstance(ctx_content_value, str):
                ctx_content_str = ctx_content_value
            elif isinstance(ctx_content_value, list):
                for part in ctx_content_value:
                    if part.get("type") == "text":
                        ctx_content_str = part["text"]
                        break
            if ctx_msg.get("type") == "image_display" and not ctx_content_str:
                continue
            context_messages_for_favorite.append({"role": ctx_role, "content": ctx_content_str})
        original_message_created_at = msg_data.get("timestamp", datetime.now())
        model_provider_enum = None
        model_name_str = None
        if msg_data["role"] == "assistant":
            current_model_config = self.get_current_model_config()
            if current_model_config:
                model_provider_enum = current_model_config.provider
                model_name_str = current_model_config.model_name
        message_identifier_in_session = f"message_index_{msg_idx}"
        try:
            self.favorite_manager.add_favorite(
                session_id=session.id, message_id=message_identifier_in_session,
                role=msg_data["role"], content=message_content_str, created_at=original_message_created_at, 
                model_provider=model_provider_enum, model_name=model_name_str,
                context_messages=context_messages_for_favorite,
            )
            st.toast("메시지를 즐겨찾기에 추가했습니다!", icon="⭐")
        except Exception as e:
            logger.error(f"즐겨찾기 추가 중 오류 발생: {e}", exc_info=True)
            st.error(f"즐겨찾기를 추가하는 중 오류가 발생했습니다: {str(e)}")