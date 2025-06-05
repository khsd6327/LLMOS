# ted-os-project/src/llmos/ui/pages/debug_page.py
# src/llmos/ui/pages/debug_page.py
"""
LLM OS - 디버그 페이지 (리팩토링됨)
"""

import logging

import streamlit as st

from ...managers.settings import SettingsManager
from ...managers.chat_sessions import ChatSessionManager
from ...managers.model_manager import EnhancedModelManager
from ...managers.usage_tracker import UsageTracker
from ...managers.favorite_manager import FavoriteManager
from .debug.system_info import SystemInfoRenderer
from .debug.logs_viewer import LogsViewer
from .debug.data_inspector import DataInspector
from .debug.api_tester import ApiTester

logger = logging.getLogger(__name__)


class DebugPage:
    """디버그 페이지 클래스 - 분리된 렌더러들을 조합"""

    def __init__(
        self,
        settings_manager: SettingsManager,
        chat_manager: ChatSessionManager,
        model_manager: EnhancedModelManager,
        usage_tracker: UsageTracker,
        favorite_manager: FavoriteManager,
        ui: EnhancedUI,
    ):
        self.settings = settings_manager
        self.chat_manager = chat_manager
        self.model_manager = model_manager
        self.usage_tracker = usage_tracker
        self.favorite_manager = favorite_manager
        self.ui = ui

        # 분리된 렌더러들 초기화
        self.system_info_renderer = SystemInfoRenderer(settings_manager)
        self.logs_viewer = LogsViewer()
        self.data_inspector = DataInspector(chat_manager, usage_tracker, favorite_manager)
        self.api_tester = ApiTester(model_manager)

    def render(self):
        """디버그 페이지 렌더링"""
        st.header("🐛 디버그 및 개발자 정보")

        # 뒤로가기 버튼
        if st.button("⬅️ 채팅으로 돌아가기", key="back_from_debug_page_btn"):
            st.session_state.show_debug_page = False
            st.rerun()

        # 탭으로 섹션 분리
        tabs = st.tabs(
            ["🔍 시스템 정보", "📋 로그", "⚙️ 설정", "💬 세션", "⭐ 즐겨찾기", "📊 성능", "🧪 테스트"]
        )

        with tabs[0]:
            self.system_info_renderer.render_system_info_section()
        with tabs[1]:
            self.logs_viewer.render_logs_section()
        with tabs[2]:
            self._render_settings_section()
        with tabs[3]:
            self.data_inspector.render_sessions_section()
        with tabs[4]:
            self.data_inspector.render_favorites_section()
        with tabs[5]:
            self.data_inspector.render_performance_section()
        with tabs[6]:
            self.api_tester.render_test_section()

    def _render_settings_section(self):
        """설정 섹션 (기존 유지)"""
        st.subheader("애플리케이션 설정")

        # 공통 컴포넌트를 사용한 AI 제공업체 상태 표시
        provider_status = self.ui.render_provider_status(
            model_manager=self.model_manager,
            settings_manager=self.settings,
            show_test_buttons=True,
            show_details=True,
            key_suffix="debug_page"
        )

        # 전체 설정 보기
        if st.button("전체 설정 보기 (JSON)", key="view_full_settings_btn"):
            st.session_state.show_full_settings = not st.session_state.get(
                "show_full_settings", False
            )

        if st.session_state.get("show_full_settings"):
            with st.expander("전체 설정 (settings.json 내용)", expanded=True):
                settings_data = self.settings.export_settings()
                st.json(settings_data)