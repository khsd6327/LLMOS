# src/llmos/ui/pages/chat_components/message_actions.py
"""
메시지 액션 처리 담당 모듈 (복사, 편집, 재시도 등)
"""

import logging

import streamlit as st

from ....models.data_models import ChatSession
from ....managers.chat_sessions import ChatSessionManager

logger = logging.getLogger(__name__)


class MessageActions:
    """메시지 액션 처리 전담 클래스"""

    def __init__(self, chat_manager: ChatSessionManager, get_current_model_config_callback):
        self.chat_manager = chat_manager
        self.get_current_model_config = get_current_model_config_callback

    def retry_last_response(self, session: ChatSession):
        """마지막 AI 응답 재시도"""
        if not session.messages or session.messages[-1]["role"] != "assistant":
            st.session_state.pending_toast = ("재시도할 AI 응답이 없습니다.", "⚠️")
            st.rerun()
        
        session.messages.pop()
        self.chat_manager.update_session(session)
        st.session_state.current_session = session
        
        last_user_message = None
        for msg in reversed(session.messages):
            if msg["role"] == "user" and msg.get("type") != "image_display":
                if isinstance(msg["content"], str):
                    last_user_message = msg["content"]
                elif isinstance(msg["content"], list):
                    for part in msg["content"]:
                        if part.get("type") == "text":
                            last_user_message = part["text"]
                            break
                break
        
        if not last_user_message:
            error_msg = "재시도를 위한 유효한 사용자 메시지가 없습니다."
            session.messages.append({"role": "assistant", "content": error_msg})
            self.chat_manager.update_session(session)
            st.session_state.current_session = session
            st.session_state.pending_toast = (error_msg, "❌")
            st.rerun()
            return
        
        try:
            # 응답 생성은 이제 스트리밍을 직접 처리하지 않음
            st.session_state.generating_response = True
            st.rerun()
        except Exception as e:
            logger.error(f"Error during retry: {e}")
            error_response = f"재시도 중 오류 발생: {e}"
            model_config = self.get_current_model_config()
            model_info = {}
            if model_config:
                model_info = {
                    "model_provider": model_config.provider.value, 
                    "model_name": model_config.model_name, 
                    "model_display_name": model_config.display_name
                }
            session.messages.append({"role": "assistant", "content": error_response, **model_info})
            self.chat_manager.update_session(session)
            st.session_state.current_session = session
            st.session_state.pending_toast = ("응답 재시도 중 오류가 발생했습니다.", "⚠️")
            st.rerun()

    def copy_message_to_clipboard(self, content: str):
        """메시지 클립보드 복사"""
        st.code(content, language=None)
        st.success("위 텍스트를 선택하여 복사하세요 (Ctrl+A, Ctrl+C).", icon="📋")
        st.session_state.pending_toast = ("내용이 복사 준비되었습니다 (위 박스에서 선택).", "📋")

    def edit_message(self, session: ChatSession, msg_index: int, new_content: str):
        """메시지 편집"""
        try:
            session.messages[msg_index]["content"] = new_content
            self.chat_manager.update_session(session)
            st.session_state.current_session = session
            st.session_state.editing_message_key = None
            st.session_state.pending_toast = ("메시지가 수정되었습니다.", "✏️")
            return True
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            st.session_state.pending_toast = ("메시지 수정 중 오류가 발생했습니다.", "❌")
            return False

    def delete_message(self, session: ChatSession, msg_index: int):
        """메시지 삭제"""
        try:
            if 0 <= msg_index < len(session.messages):
                deleted_msg = session.messages.pop(msg_index)
                self.chat_manager.update_session(session)
                st.session_state.current_session = session
                st.session_state.pending_toast = ("메시지가 삭제되었습니다.", "🗑️")
                return True
            else:
                st.session_state.pending_toast = ("잘못된 메시지 인덱스입니다.", "❌")
                return False
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            st.session_state.pending_toast = ("메시지 삭제 중 오류가 발생했습니다.", "❌")
            return False