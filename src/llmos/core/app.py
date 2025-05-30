# src/llmos/core/app.py
"""
LLM OS - 메인 애플리케이션 클래스
"""

import json
import logging
import time
from datetime import datetime

import streamlit as st

from .config import (
    APP_VERSION, APP_NAME, PAGE_ICON, PAGE_LAYOUT, INITIAL_SIDEBAR_STATE,
    SIDEBAR_MAX_SESSIONS, SESSION_TITLE_MAX_LENGTH, KEYBOARD_SHORTCUT_DEBOUNCE_TIME,
    DATA_CLEANUP_KEEP_DAYS
)
from ..managers.settings import SettingsManager
from ..managers.chat_sessions import ChatSessionManager
from ..managers.artifacts import ArtifactManager
from ..managers.usage_tracker import UsageTracker
from ..managers.model_manager import EnhancedModelManager
from ..ui.components import EnhancedUI
from ..ui.styles import load_custom_css, apply_theme
from ..ui.pages.chat import ChatPage
from ..ui.pages.settings import SettingsPage
from ..ui.pages.artifacts import ArtifactsPage
from ..ui.pages.debug import DebugPage
from ..utils.logging_handler import setup_logging, get_log_handler

logger = logging.getLogger(__name__)


class EnhancedLLMOSApp:
    """향상된 LLM OS 애플리케이션 클래스"""

    def __init__(self):
        # 로깅 설정
        setup_logging()
        
        # 관리자들 초기화
        self.settings = SettingsManager()
        self.settings.ensure_paths_exist()
        
        self.usage_tracker = UsageTracker(self.settings.get("paths.usage_tracking"))
        self.model_manager = EnhancedModelManager(self.settings, self.usage_tracker)
        self.artifacts = ArtifactManager(self.settings.get("paths.artifacts"))
        self.chat_manager = ChatSessionManager(self.settings.get("paths.chat_sessions"))
        
        # UI 컴포넌트
        self.ui = EnhancedUI()
        
        # 페이지들
        self.chat_page = ChatPage(self.chat_manager, self.model_manager, self.ui)
        self.settings_page = SettingsPage(self.settings, self.model_manager, self.ui)
        self.artifacts_page = ArtifactsPage(self.artifacts, self.ui)
        self.debug_page = DebugPage(
            self.settings, self.chat_manager, self.model_manager, 
            self.usage_tracker, self.ui
        )
        
        # 세션 상태 초기화
        self._initialize_session_state()

    def _initialize_session_state(self):
        """세션 상태 초기화"""
        default_state = {
            # 현재 세션 정보
            "current_session_id": None,
            "current_session": None,
            
            # 이미지 업로드 상태
            "chat_uploaded_image_bytes": None,
            "chat_uploaded_image_name": None,
            "last_uploaded_filename_integrated": None,
            
            # 페이지 상태
            "show_settings_page": False,
            "show_artifacts_page": False,
            "show_debug_page": False,
            "show_export_page": False,
            
            # 편집 상태
            "editing_message_key": None,
            "edit_text_content": "",
            
            # 애플리케이션 상태
            "app_initialized": False,
            
            # UI 상태
            "pending_toast": None,
            
            # 모델 선택 상태 (새로 추가)
            "selected_provider": None,
            "selected_model": None,
            
            # 키보드 단축키 관련 상태 (추가)
            "keyboard_shortcut_action": None,
            "show_shortcuts_help": False,
            "last_shortcut_time": 0,
        }

        for key, default_value in default_state.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
        
        # 애플리케이션 초기화
        if not st.session_state.app_initialized:
            self._load_or_create_initial_session()
            st.session_state.app_initialized = True

    def _load_or_create_initial_session(self):
        """초기 세션 로드 또는 생성"""
        all_sessions = self.chat_manager.get_all_sessions()
        
        if all_sessions:
            # 가장 최근 세션 로드
            last_session = all_sessions[0]
            st.session_state.current_session_id = last_session.id
            st.session_state.current_session = last_session
            logger.info(f"Loaded last session: {last_session.id} - {last_session.title}")
        else:
            # 새 세션 생성
            self._create_and_set_new_session("첫 채팅")
            logger.info("No existing sessions. Created a new one.")

    def _create_and_set_new_session(self, title_prefix: str = "새 채팅"):
        """새 세션 생성 및 설정"""
        session_title = f"{title_prefix} {datetime.now().strftime('%Y/%m/%d %H:%M')}"
        new_session = self.chat_manager.create_session(title=session_title)
        
        st.session_state.current_session_id = new_session.id
        st.session_state.current_session = new_session
        
        # 이미지 상태 초기화
        st.session_state.chat_uploaded_image_bytes = None
        st.session_state.chat_uploaded_image_name = None
        st.session_state.last_uploaded_filename_integrated = None
        
        # 세션 사용량 통계 초기화
        self.usage_tracker.reset_session_usage()
        
        return new_session

    def run(self):
        """애플리케이션 실행"""
        # 페이지 설정
        st.set_page_config(
            page_title=f"{APP_NAME} v{APP_VERSION}",
            page_icon=PAGE_ICON,
            layout=PAGE_LAYOUT,
            initial_sidebar_state=INITIAL_SIDEBAR_STATE
        )        
        # 스타일 로드
        load_custom_css()
        
        # 테마 적용
        theme = self.settings.get("ui.theme", "auto")
        if theme != "auto":
            apply_theme(theme)
        
        # 키보드 핸들러 및 처리 로직 추가
        self.ui.render_keyboard_handler()
        self._handle_keyboard_shortcuts()
        
        # 토스트 메시지 표시
        if st.session_state.get("pending_toast"):
            msg, icon = st.session_state.pending_toast
            st.toast(msg, icon=icon)
            del st.session_state.pending_toast
        
        # 단축키 도움말 표시
        if st.session_state.get("show_shortcuts_help"):
            self.ui.render_shortcuts_help()
    
        
        # 페이지 라우팅
        if st.session_state.show_settings_page:
            self.settings_page.render()
        elif st.session_state.show_artifacts_page:
            self.artifacts_page.render()
        elif st.session_state.show_debug_page:
            self.debug_page.render()
        else:
            # 메인 채팅 페이지
            self._render_main_layout()

    def _render_main_layout(self):
        """메인 레이아웃 렌더링"""
        # 사이드바
        with st.sidebar:
            self._render_sidebar()
        
        # 메인 컨텐츠
        self.chat_page.render()

    def _render_sidebar(self):
        """사이드바 렌더링"""
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
        if st.button("➕ 새 채팅 시작", key="sidebar_new_chat_btn", use_container_width=True):
            self._create_and_set_new_session()
            st.rerun()
        
        # 세션 목록
        all_sessions = self.chat_manager.get_all_sessions()
        
        if not all_sessions and not st.session_state.current_session:
            self._create_and_set_new_session()
            st.rerun()
        
        # 세션 리스트 렌더링
        for session in all_sessions[:SIDEBAR_MAX_SESSIONS]:  # 최대 설정된 개수만 표시
            if not session:
                continue
            
            is_current = st.session_state.current_session_id == session.id
            title_display = session.title[:SESSION_TITLE_MAX_LENGTH] + ("..." if len(session.title) > SESSION_TITLE_MAX_LENGTH else "")
            
            col_btn, col_del = st.columns([0.85, 0.15])
            
            # 세션 선택 버튼
            button_type = "primary" if is_current else "secondary"
            if col_btn.button(
                title_display,
                key=f"select_session_btn_{session.id}",
                use_container_width=True,
                type=button_type
            ):
                if not is_current:
                    st.session_state.current_session_id = session.id
                    st.session_state.current_session = self.chat_manager.get_session(session.id)
                    
                    # 이미지 상태 초기화
                    st.session_state.chat_uploaded_image_bytes = None
                    st.session_state.chat_uploaded_image_name = None
                    st.session_state.last_uploaded_filename_integrated = None
                    
                    st.rerun()
            
            # 삭제 버튼
            if col_del.button("🗑️", key=f"delete_session_btn_{session.id}", help=f"{session.title} 삭제"):
                self.chat_manager.delete_session(session.id)
                
                # 현재 세션이 삭제된 경우 새 세션 로드
                if is_current:
                    self._load_or_create_initial_session()
                
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
        
        # 단축키 도움말 버튼 추가
        help_state = st.session_state.get("show_shortcuts_help", False)
        help_text = "단축키 숨기기" if help_state else "⌨️ 단축키 도움말"
        
        if st.button(help_text, key="sidebar_shortcuts_help_btn", use_container_width=True):
            st.session_state.show_shortcuts_help = not help_state
            st.rerun()
        
        # 설정 페이지
        if st.button("⚙️ 앱 설정", key="sidebar_settings_btn", use_container_width=True):
            st.session_state.show_settings_page = True
            st.rerun()
        
        # 아티팩트 페이지
        if st.button("📚 아티팩트", key="sidebar_artifacts_btn", use_container_width=True):
            st.session_state.show_artifacts_page = True
            st.rerun()
        
        # 디버그 페이지
        if st.button("🐛 디버그 정보", key="sidebar_debug_btn", use_container_width=True):
            st.session_state.show_debug_page = True
            st.rerun()
        
        # 데이터 내보내기
        if st.button("📤 데이터 내보내기", key="sidebar_export_btn", use_container_width=True):
            self._export_data()

    def _export_data(self):
        """데이터 내보내기"""
        try:
            # 모든 채팅 세션 내보내기
            all_sessions = self.chat_manager.get_all_sessions()
            
            export_data = {
                "app_name": APP_NAME,
                "app_version": APP_VERSION,
                "exported_at": datetime.now().isoformat(),
                "sessions": [session.to_dict() for session in all_sessions],
                "settings": self.settings.export_settings(),
                "usage_stats": self.usage_tracker.export_usage_data()
            }
            
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            filename = f"llmos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            st.download_button(
                label="💾 전체 데이터 다운로드",
                data=json_data,
                file_name=filename,
                mime="application/json",
                key="download_all_data_btn"
            )
            
            st.success("데이터 내보내기가 준비되었습니다!")
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            st.error(f"데이터 내보내기 중 오류가 발생했습니다: {e}")

    def _sync_model_selection(self):
        """모델 선택 상태 동기화"""
        try:
            # Settings에서 session_state로 동기화
            settings_provider = self.settings.get("ui.selected_provider")
            settings_model = self.settings.get("defaults.model")
            
            # session_state가 비어있으면 settings에서 가져오기
            if not st.session_state.get("selected_provider") and settings_provider:
                st.session_state.selected_provider = settings_provider
                
            if not st.session_state.get("selected_model") and settings_model:
                st.session_state.selected_model = settings_model
                
            # 둘 다 없으면 자동 선택
            if (not st.session_state.get("selected_provider") or 
                not st.session_state.get("selected_model")):
                self._auto_select_model()
                
        except Exception as e:
            logger.error(f"Error syncing model selection: {e}")
            self._auto_select_model()

    def _auto_select_model(self):
        """자동으로 모델 선택"""
        try:
            available_providers = self.model_manager.get_available_providers()
            if not available_providers:
                logger.warning("No available providers for auto model selection")
                return
                
            # 첫 번째 사용 가능한 제공업체 선택
            first_provider = available_providers[0]
            provider_display = first_provider.name.capitalize()
            
            from ..models.model_registry import ModelRegistry
            available_models = ModelRegistry.get_models_for_provider(provider_display)
            
            if available_models:
                model_key = list(available_models.keys())[0]
                
                # session_state와 settings에 저장
                st.session_state.selected_provider = provider_display
                st.session_state.selected_model = model_key
                self.settings.set("ui.selected_provider", provider_display)
                self.settings.set("defaults.model", model_key)
                
                logger.info(f"Auto-selected model: {provider_display}/{model_key}")
            else:
                logger.warning(f"No models available for provider: {provider_display}")
                
        except Exception as e:
            logger.error(f"Error in auto model selection: {e}")

    def cleanup(self):
        """애플리케이션 정리"""
        try:
            # 로그 정리
            log_handler = get_log_handler()
            if hasattr(log_handler, 'cleanup'):
                log_handler.cleanup()
            
            # 임시 파일 정리
            self.artifacts.cleanup_orphaned_files()
            
            # 오래된 사용량 데이터 정리 (90일 이상)
            self.usage_tracker.cleanup_old_data(keep_days=DATA_CLEANUP_KEEP_DAYS)
            
            logger.info("Application cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def get_app_info(self) -> dict:
        """애플리케이션 정보 반환"""
        return {
            "name": APP_NAME,
            "version": APP_VERSION,
            "total_sessions": len(self.chat_manager.get_all_sessions()),
            "total_artifacts": len(self.artifacts.get_all_artifacts()),
            "available_providers": len(self.model_manager.get_available_providers()),
            "current_session_id": st.session_state.get("current_session_id"),
            "settings_valid": self.model_manager.validate_configuration()["valid"]
        }


    def _handle_keyboard_shortcuts(self):
        """키보드 단축키 처리"""
        shortcut_action = st.session_state.get("keyboard_shortcut_action")
        if not shortcut_action:
            return
        
        # 중복 실행 방지 (0.5초 내 같은 액션 무시)
        current_time = time.time()
        last_time = st.session_state.get("last_shortcut_time", 0)
        
        if current_time - last_time < KEYBOARD_SHORTCUT_DEBOUNCE_TIME:
            st.session_state.keyboard_shortcut_action = None
            return
        
        # 단축키 액션 처리
        if self.ui.handle_keyboard_shortcut(shortcut_action, self):
            st.session_state.last_shortcut_time = current_time
            st.rerun()
        
        # 액션 처리 후 초기화
        st.session_state.keyboard_shortcut_action = None

def create_app() -> EnhancedLLMOSApp:
    """애플리케이션 인스턴스 생성"""
    return EnhancedLLMOSApp()


