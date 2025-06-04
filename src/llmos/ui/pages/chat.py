# src/llmos/ui/pages/chat.py
"""
LLM OS - 채팅 페이지 (리팩토링됨)
"""

import logging

import streamlit as st

from ...managers.chat_sessions import ChatSessionManager
from ...managers.model_manager import EnhancedModelManager
from ...models.data_models import ChatSession
from ...models.model_registry import ModelRegistry
from ...ui.components import EnhancedUI
from ...managers.state_manager import get_state
from ...managers.favorite_manager import FavoriteManager
from .chat_components.message_renderer import MessageRenderer
from .chat_components.response_generator import ResponseGenerator
from .chat_components.input_handler import InputHandler
from .chat_components.title_generator import TitleGenerator
from .chat_components.message_actions import MessageActions

logger = logging.getLogger(__name__)


class ChatPage:
    """채팅 페이지 클래스 - 분리된 클래스들을 조합"""

    def __init__(
        self,
        chat_manager: ChatSessionManager,
        model_manager: EnhancedModelManager,
        ui: EnhancedUI,
        favorite_manager: FavoriteManager,
    ):
        self.chat_manager = chat_manager
        self.model_manager = model_manager
        self.ui = ui
        self.favorite_manager = favorite_manager
        
        # 분리된 클래스들 초기화
        self.input_handler = InputHandler(chat_manager)
        self.title_generator = TitleGenerator(chat_manager, model_manager)
        self.message_actions = MessageActions(chat_manager, self._get_current_model_config)
        
        # ResponseGenerator와 MessageRenderer 초기화 (의존성 주입)
        self.response_generator = ResponseGenerator(
            chat_manager, model_manager, self._get_current_model_config
        )
        self.message_renderer = MessageRenderer(
            chat_manager,
            model_manager,
            ui,
            favorite_manager,
            self._get_current_model_config,
            self.message_actions.retry_last_response,
            self.response_generator,
            self.title_generator.auto_generate_title,
        )

    def render(self):
        """채팅 페이지 렌더링 (StateManager 사용)"""
        state = get_state() # StateManager 인스턴스 가져오기
        current_session = state.current_session # state에서 현재 세션 가져오기

        if not current_session:
            self._render_no_session()
            return

        st.subheader(f"💬 {current_session.title}")

        # message_renderer가 모든 메시지 렌더링을 담당
        self.message_renderer.render_chat_messages(current_session)

        # 채팅 입력창 UI 렌더링 및 입력 처리
        prompt = self.ui.render_integrated_chat_input()
        
        # 이미지 제거 플래그 확인
        just_removed_image = state.get("just_removed_image_flag", False)

        if just_removed_image:
            state.just_removed_image_flag = False # 플래그 사용 후 즉시 초기화
            # 이미지 제거 시에는 메시지 전송 로직을 건너뜁니다.
            # chat_input_avd에 남아있는 텍스트가 있다면, 그것도 비워주는 것이 이상적이나,
            # chat_input_avd 라이브러리가 외부에서 텍스트를 비우는 기능을 제공하는지 확인 필요.
            # 일단은 메시지 전송만 막습니다.
        elif prompt: # prompt가 있고, 이미지 제거 직후가 아닐 때만 처리
            self._handle_user_input(current_session, prompt)
            st.rerun()

    def _render_no_session(self):
        """세션이 없을 때 렌더링"""
        st.info("채팅 세션을 선택하거나 새 채팅을 시작하세요.")
        if st.button("새 채팅 시작", type="primary"):
            new_session = self.chat_manager.create_session("새 채팅")
            st.session_state.current_session_id = new_session.id
            st.session_state.current_session = new_session
            st.rerun()

    def _render_chat_input(self):
        """통합 채팅 입력 UI 렌더링"""
        self.ui.render_integrated_chat_input()

    def _handle_user_input(self, session: ChatSession, user_input: str):
        """사용자 입력 처리 - InputHandler에 위임"""
        self.input_handler.handle_user_input(session, user_input)

    def _get_current_model_config(self):
        """현재 모델 설정 가져오기"""
        provider = st.session_state.get("selected_provider") or self.model_manager.settings.get("ui.selected_provider")
        if provider and not st.session_state.get("selected_model"):
            model_key = self.model_manager.settings.get_default_model_for_provider(provider)
        else:
            model_key = st.session_state.get("selected_model")
        if not provider or not model_key:
            available_providers = self.model_manager.get_available_providers()
            if available_providers:
                first_provider = available_providers[0]
                provider_display = first_provider.name.capitalize()
                available_models = ModelRegistry.get_models_for_provider(provider_display)
                if available_models:
                    model_key = self.model_manager.settings.get_default_model_for_provider(provider_display)
                    if not model_key or model_key not in available_models:
                        model_key = list(available_models.keys())[0]
                    provider = provider_display
                    st.session_state.selected_provider = provider
                    st.session_state.selected_model = model_key
                    self.model_manager.settings.set("ui.selected_provider", provider)
                    self.model_manager.settings.set("defaults.model", model_key)
        if not provider or not model_key:
            return None
        return ModelRegistry.get_model_config(provider, model_key)