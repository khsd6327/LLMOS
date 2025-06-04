# src/llmos/ui/sidebar.py
"""
LLM OS - 사이드바 UI 컴포넌트
"""

import logging
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
        st.markdown(f"### 😽 {APP_NAME}")
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

        # 고정된 세션과 일반 세션 분리 조회
        pinned_sessions, unpinned_sessions = self.chat_manager.get_sessions_separated()
        
        # 세션이 없으면 새 세션 생성
        if not pinned_sessions and not unpinned_sessions and not st.session_state.current_session:
            self.app._create_and_set_new_session()
            st.rerun()

        # 고정된 채팅 섹션
        if pinned_sessions:
            st.markdown("#### 📌 고정된 채팅")
            for session in pinned_sessions:
                self._render_session_item(session, is_pinned=True)
            
            # 고정된 채팅과 일반 채팅 사이 구분선
            if unpinned_sessions:
                st.markdown("---")

        # 일반 채팅 섹션  
        if unpinned_sessions:
            if pinned_sessions:  # 고정된 채팅이 있으면 섹션 헤더 표시
                st.markdown("#### 📄 최근 채팅")
            
            # 표시할 일반 세션 수 계산 (고정된 세션 수를 고려)
            max_unpinned_to_show = SIDEBAR_MAX_SESSIONS - len(pinned_sessions)
            sessions_to_show = unpinned_sessions[:max_unpinned_to_show] if max_unpinned_to_show > 0 else []
            
            for session in sessions_to_show:
                self._render_session_item(session, is_pinned=False)
                
            # 더 많은 세션이 있는 경우
            total_remaining = len(unpinned_sessions) - len(sessions_to_show)
            if total_remaining > 0:
                st.caption(f"+ {total_remaining}개 더 있음")

    def _render_session_item(self, session, is_pinned: bool):
        """개별 세션 아이템 렌더링 (컨텍스트 메뉴 포함)"""
        is_current = st.session_state.current_session_id == session.id
        title_display = session.title[:SESSION_TITLE_MAX_LENGTH] + (
            "..." if len(session.title) > SESSION_TITLE_MAX_LENGTH else ""
        )
        
        # 고정된 채팅에 아이콘과 배경색 적용
        if is_pinned:
            title_display = f"📌 {title_display}"

        # 세션 아이템 컨테이너 (고정된 채팅은 연한 회색 배경)
        container_style = ""
        if is_pinned:
            container_style = "background-color: #F9F9F9; border-radius: 5px; padding: 5px;"
        
        # 세션 아이템 레이아웃
        col_btn, col_menu = st.columns([0.85, 0.15])

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
                st.session_state.current_session = self.chat_manager.get_session(session.id)

                # 이미지 상태 초기화
                st.session_state.chat_uploaded_image_bytes = None
                st.session_state.chat_uploaded_image_name = None
                st.session_state.last_uploaded_filename_integrated = None

                st.rerun()

        # 컨텍스트 메뉴 (세로 점 3개)
        if col_menu.button(
            "⋮", 
            key=f"menu_btn_{session.id}",
            help="메뉴",
        ):
            # 메뉴 상태 토글
            menu_key = f"show_menu_{session.id}"
            st.session_state[menu_key] = not st.session_state.get(menu_key, False)
            st.rerun()

        # 컨텍스트 메뉴가 열린 경우
        menu_key = f"show_menu_{session.id}"
        if st.session_state.get(menu_key, False):
            self._render_context_menu(session, is_pinned)

    def _render_context_menu(self, session, is_pinned: bool):
        """세션 컨텍스트 메뉴 렌더링"""
        with st.container():
            st.markdown("**메뉴:**")
            
            menu_col1, menu_col2 = st.columns(2)
            
            # 고정/고정 해제 버튼
            pin_text = "📌 고정 해제" if is_pinned else "📌 고정"
            if menu_col1.button(
                pin_text,
                key=f"pin_toggle_{session.id}",
                use_container_width=True,
            ):
                success = self.chat_manager.toggle_session_pin(session.id)
                menu_key = f"show_menu_{session.id}"
                st.session_state[menu_key] = False  # 메뉴 닫기
                
                if success:
                    if is_pinned:
                        st.toast("채팅 고정을 해제했습니다.", icon="📌")
                    else:
                        st.toast("채팅을 고정했습니다.", icon="📌")
                else:
                    if not is_pinned:  # 고정 시도했지만 실패 (7개 제한)
                        st.toast("최대 7개까지 고정할 수 있습니다.", icon="⚠️")
                
                st.rerun()

            # 제목 수정 버튼
            if menu_col2.button(
                "✏️ 제목 수정",
                key=f"edit_title_{session.id}",
                use_container_width=True,
            ):
                edit_key = f"editing_title_{session.id}"
                st.session_state[edit_key] = True
                menu_key = f"show_menu_{session.id}"
                st.session_state[menu_key] = False  # 메뉴 닫기
                st.rerun()

            # 삭제 버튼
            if st.button(
                "🗑️ 삭제",
                key=f"delete_session_{session.id}",
                use_container_width=True,
                type="secondary",
            ):
                self.chat_manager.delete_session(session.id)
                menu_key = f"show_menu_{session.id}"
                st.session_state[menu_key] = False  # 메뉴 닫기

                # 현재 세션이 삭제된 경우 새 세션 로드
                if st.session_state.current_session_id == session.id:
                    self.app._load_or_create_initial_session()

                st.toast("채팅을 삭제했습니다.", icon="🗑️")
                st.rerun()

        # 제목 수정 모드
        edit_key = f"editing_title_{session.id}"
        if st.session_state.get(edit_key, False):
            new_title = st.text_input(
                "새 제목:",
                value=session.title,
                key=f"title_input_{session.id}",
                max_chars=SESSION_TITLE_MAX_LENGTH,
            )
            
            edit_col1, edit_col2 = st.columns(2)
            
            if edit_col1.button(
                "💾 저장",
                key=f"save_title_{session.id}",
                use_container_width=True,
            ):
                if new_title.strip():
                    self.chat_manager.update_session_title(session.id, new_title.strip())
                    st.session_state[edit_key] = False
                    st.toast("제목을 수정했습니다.", icon="✏️")
                    st.rerun()
                else:
                    st.error("제목을 입력해주세요.")

            if edit_col2.button(
                "❌ 취소",
                key=f"cancel_title_{session.id}",
                use_container_width=True,
            ):
                st.session_state[edit_key] = False
                st.rerun()

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

        # 앱 새로고침 버튼 (개발 편의성을 위해 최상단 배치)
        if st.button("🔄 앱 새로고침", key="sidebar_refresh_btn", use_container_width=True, help="코드 변경사항을 바로 적용합니다."):
            st.toast("앱을 새로고침합니다! 🔄", icon="🔄")
            st.rerun()

        # 설정 페이지
        if st.button("⚙️ 앱 설정", key="sidebar_settings_btn", use_container_width=True):
            st.session_state.show_settings_page = True
            st.rerun()
            
        # API 대시보드 페이지
        if st.button("🔗 API 대시보드", key="sidebar_api_dashboard_btn", use_container_width=True):
            st.session_state.show_api_dashboard_page = True
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