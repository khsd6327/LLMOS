# src/llmos/ui/pages/chat_components/title_generator.py
"""
자동 제목 생성 담당 모듈
"""

import logging

import streamlit as st

from ....models.data_models import ChatSession
from ....managers.chat_sessions import ChatSessionManager
from ....managers.model_manager import EnhancedModelManager

logger = logging.getLogger(__name__)


class TitleGenerator:
    """자동 제목 생성 전담 클래스"""

    def __init__(self, chat_manager: ChatSessionManager, model_manager: EnhancedModelManager):
        self.chat_manager = chat_manager
        self.model_manager = model_manager

    def auto_generate_title(self, session: ChatSession, user_prompt: str, ai_response: str):
        """자동 제목 생성"""
        if session.title.startswith("새 채팅") or session.title.startswith("첫 채팅"):
            assistant_count = sum(1 for m in session.messages if m["role"] == "assistant")
            if assistant_count == 1 and ai_response and not ai_response.lower().startswith("오류"):
                self._generate_chat_title(session, user_prompt, ai_response)

    def _generate_chat_title(self, session: ChatSession, user_prompt: str, ai_response: str):
        """채팅 제목 생성 (수정된 버전)"""
        try:
            prompt_template = f"""
다음은 사용자와 AI의 첫 대화입니다. 이 대화의 핵심 주제를 나타내는 간결한 한글 제목을 15자 이내로 만들어주세요.
다른 설명이나 인사말 없이, 오직 제목 텍스트만 응답해야 합니다.
사용자 질문: "{user_prompt[:200]}"
제목:
"""
            title_messages = [{"role": "user", "content": prompt_template}]
            generated_title, _ = self.model_manager.generate(
                messages=title_messages, temperature=0.0, max_tokens=30
            )
            if not generated_title:
                logger.warning("AI가 제목을 생성하지 못했습니다 (빈 응답). 백업 제목을 사용합니다.")
                raise ValueError("Generated title is empty")
            
            clean_title = generated_title.strip()
            prefixes_to_remove = ["제목:", "Title:"]
            for prefix in prefixes_to_remove:
                if clean_title.lower().startswith(prefix.lower()):
                    clean_title = clean_title[len(prefix) :].strip()
            
            clean_title = clean_title.strip("\"'""" "")
            
            if 1 < len(clean_title) <= 25:
                final_title = clean_title
            else:
                logger.warning(f"생성된 제목 '{clean_title}'이 유효하지 않아 백업 제목을 사용합니다.")
                final_title = user_prompt[:20] + ("..." if len(user_prompt) > 20 else "")
            
            session.title = final_title
            self.chat_manager.update_session_title(session.id, final_title)
            st.session_state.pending_toast = (f"채팅 제목 자동 생성: {final_title}", "✨")
            logger.info(f"성공적으로 채팅 제목을 생성하고 업데이트했습니다: {final_title}")
            
        except Exception as e:
            logger.error(f"채팅 제목 자동 생성 중 오류 발생: {e}", exc_info=True)
            safe_title = user_prompt[:20] + ("..." if len(user_prompt) > 20 else "")
            if session.title != safe_title:
                session.title = safe_title
                self.chat_manager.update_session_title(session.id, safe_title)
                logger.info(f"오류 발생으로 백업 제목을 사용합니다: {safe_title}")