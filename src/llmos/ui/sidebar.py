# src/llmos/ui/sidebar.py
"""
LLM OS - 사이드바 UI 컴포넌트
"""

import json
import logging
from datetime import datetime

import streamlit as st

from ..core.config import (
    APP_VERSION,
    APP_NAME,
    SIDEBAR_MAX_SESSIONS,
    SESSION_TITLE_MAX_LENGTH,
)

logger = logging.getLogger(__name__)


class Sidebar:
    """사이드바 UI 관리 클래스"""

    def __init__(self, app_instance):
        """
        사이드바 초기화

        Args:
            app_instance: EnhancedLLMOSApp 인스턴스
        """
        self.app = app_instance
        self.settings = app_instance.settings
        self.chat_manager = app_instance.chat_manager
        self.usage_tracker = app_instance.usage_tracker
        self.ui = app_instance.ui

    def render(self):
        """사이드바 전체 렌더링"""
        # 애플리케이션 헤더
        st.markdown(f"### 🧠 {APP_NAME}")
        st.caption(f"버전 {APP_VERSION}")

        # 채팅 세션 관리
        self._render_session_management()

        st.divider()

        # 모델 선택 및 설정
        self._render_model_configuration()

        st.divider()

        # 네비게이션 메뉴
        self._render_navigation_menu()

        st.divider()

        # 사용량 통계
        self.ui.render_usage_stats(self.usage_tracker)

    def _render_session_management(self):
        """세션 관리 섹션"""
        st.markdown("### 💬 채팅 기록")

        # 새 채팅 버튼
        if st.button(
            "➕ 새 채팅 시작", key="sidebar_new_chat_btn", use_container_width=True
        ):
            self.app._create_and_set_new_session()
            st.rerun()

        # 세션 목록
        all_sessions = self.chat_manager.get_all_sessions()

        if not all_sessions and not st.session_state.current_session:
            self.app._create_and_set_new_session()
            st.rerun()

        # 세션 리스트 렌더링
        for session in all_sessions[:SIDEBAR_MAX_SESSIONS]:  # 최대 설정된 개수만 표시
            if not session:
                continue

            is_current = st.session_state.current_session_id == session.id
            title_display = session.title[:SESSION_TITLE_MAX_LENGTH] + (
                "..." if len(session.title) > SESSION_TITLE_MAX_LENGTH else ""
            )

            col_btn, col_del = st.columns([0.85, 0.15])

            # 세션 선택 버튼
            button_type = "primary" if is_current else "secondary"
            if col_btn.button(
                title_display,
                key=f"select_session_btn_{session.id}",
                use_container_width=True,
                type=button_type,
            ):
                if not is_current:
                    st.session_state.current_session_id = session.id
                    st.session_state.current_session = self.chat_manager.get_session(
                        session.id
                    )

                    # 이미지 상태 초기화
                    st.session_state.chat_uploaded_image_bytes = None
                    st.session_state.chat_uploaded_image_name = None
                    st.session_state.last_uploaded_filename_integrated = None

                    st.rerun()

            # 삭제 버튼
            if col_del.button(
                "🗑️",
                key=f"delete_session_btn_{session.id}",
                help=f"{session.title} 삭제",
            ):
                self.chat_manager.delete_session(session.id)

                # 현재 세션이 삭제된 경우 새 세션 로드
                if is_current:
                    self.app._load_or_create_initial_session()

                st.rerun()

        # 더 많은 세션이 있는 경우
        if len(all_sessions) > SIDEBAR_MAX_SESSIONS:
            st.caption(f"+ {len(all_sessions) - SIDEBAR_MAX_SESSIONS}개 더 있음")

    def _render_model_configuration(self):
        """모델 설정 섹션"""
        st.markdown("### ⚙️ 모델 & 생성 설정")

        # 모델 선택기
        self.ui.render_model_selector(self.settings)

        st.divider()

        # 생성 매개변수
        self.ui.render_generation_params(self.settings)

    def _render_navigation_menu(self):
        """네비게이션 메뉴"""
        st.markdown("### 🛠️ 도구")

        # 설정 페이지
        if st.button("⚙️ 앱 설정", key="sidebar_settings_btn", use_container_width=True):
            st.session_state.show_settings_page = True
            st.rerun()

        # Spotify 페이지
        if st.button(
            "🎵 Spotify", key="sidebar_spotify_btn", use_container_width=True
        ):
            st.session_state.show_spotify_page = True
            st.rerun()
            
        # 즐겨찾기 페이지
        if st.button(
            "⭐ 즐겨찾기 모음", key="sidebar_favorites_btn", use_container_width=True
        ):
            st.session_state.show_favorites_page = True
            st.rerun()
        
        # 디버그 페이지
        if st.button(
            "🐛 디버그 정보", key="sidebar_debug_btn", use_container_width=True
        ):
            st.session_state.show_debug_page = True
            st.rerun()

        # 데이터 내보내기
        if st.button(
            "📤 데이터 내보내기", key="sidebar_export_btn", use_container_width=True
        ):
            self.app._export_data()