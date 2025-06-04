# src/llmos/core/app.py
"""
LLM OS - 메인 애플리케이션 클래스 (수정됨)
"""

import json
import logging
from datetime import datetime

import streamlit as st

from .config import (
    APP_VERSION,
    APP_NAME,
    PAGE_ICON,
    PAGE_LAYOUT,
    INITIAL_SIDEBAR_STATE,
    DATA_CLEANUP_KEEP_DAYS,
)

from ..managers.settings import SettingsManager
from ..managers.state_manager import get_state
from ..managers.chat_sessions import ChatSessionManager
from ..managers.usage_tracker import UsageTracker
from ..managers.model_manager import EnhancedModelManager
from ..managers.spotify_manager import SpotifyManager
from ..managers.favorite_manager import FavoriteManager
from ..ui.pages.favorites import FavoritesPage
from ..ui.components import EnhancedUI
from ..ui.styles import load_custom_css, apply_theme
from ..ui.sidebar import Sidebar
from ..ui.pages.chat import ChatPage
from ..ui.pages.settings import SettingsPage
from ..ui.pages.debug_page import DebugPage
from ..ui.pages.spotify_page import render_spotify_page
from ..utils.logging_handler import setup_logging, get_log_handler
from ..ui.pages.api_dashboard import APIDashboardPage

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
        self.chat_manager = ChatSessionManager(self.settings.get("paths.chat_sessions"))
        self.spotify_manager = SpotifyManager(self.settings)
        self.favorite_manager = FavoriteManager(storage_dir=self.settings.get("paths.favorites"))

        # UI 컴포넌트
        self.ui = EnhancedUI()
        self.sidebar = Sidebar(self)

        # 페이지들
        self.chat_page = ChatPage(self.chat_manager, self.model_manager, self.ui, self.favorite_manager)
        self.settings_page = SettingsPage(self.settings, self.model_manager, self.spotify_manager, self.ui)
        self.debug_page = DebugPage(
            self.settings,
            self.chat_manager,
            self.model_manager,
            self.usage_tracker,
            self.favorite_manager,
            self.ui,
        )

        self.favorites_page = FavoritesPage(self.favorite_manager, self.ui)
        self.api_dashboard_page = APIDashboardPage(
            self.settings,
            self.model_manager,
            self.usage_tracker,
            self.ui
        )

        # 중앙 상태 관리자 초기화
        self.state = get_state()

        # 세션 상태 초기화
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """세션 상태 초기화 (StateManager 사용)"""
        if not self.state.get("app_initialized", False):
            self._load_or_create_initial_session()
            self.state.set("app_initialized", True)

    def _load_or_create_initial_session(self) -> None:
        """초기 세션 로드 또는 생성 (StateManager 사용)"""
        all_sessions = self.chat_manager.get_all_sessions()

        if all_sessions:
            last_session = all_sessions[0]
            self.state.current_session_id = last_session.id
            self.state.current_session = last_session
            logger.info(f"Loaded last session: {last_session.id} - {last_session.title}")
        else:
            self._create_and_set_new_session("첫 채팅")
            logger.info("No existing sessions. Created a new one.")

    def _create_and_set_new_session(self, title_prefix: str = "새 채팅"):
        """새 세션 생성 및 설정 (StateManager 사용)"""
        session_title = f"{title_prefix} {datetime.now().strftime('%Y/%m/%d %H:%M')}"
        new_session = self.chat_manager.create_session(title=session_title)

        self.state.current_session_id = new_session.id
        self.state.current_session = new_session

        # 이미지 상태 초기화
        self.state.chat_uploaded_image_bytes = None
        self.state.chat_uploaded_image_name = None
        self.state.last_uploaded_filename_integrated = None

        self.usage_tracker.reset_session_usage()
        return new_session

    def run(self) -> None:
        """애플리케이션 실행 (StateManager 사용)"""
        # 페이지 설정
        st.set_page_config(
            page_title=f"{APP_NAME} v{APP_VERSION}",
            page_icon=PAGE_ICON,
            layout=PAGE_LAYOUT,
            initial_sidebar_state=INITIAL_SIDEBAR_STATE,
        )

        # 스타일 로드
        load_custom_css()

        # 테마 적용
        theme = self.settings.get("ui.theme", "auto")
        if theme != "auto":
            apply_theme(theme)

        # 토스트 메시지 표시
        if self.state.pending_toast:
            msg, icon = self.state.pending_toast
            st.toast(msg, icon=icon)
            del self.state.pending_toast

        # 단축키 도움말 표시
        if self.state.show_shortcuts_help:
            self.ui.render_shortcuts_help()

        # 페이지 라우팅
        if self.state.show_settings_page:
            self.settings_page.render()
        elif self.state.show_debug_page:
            self.debug_page.render()
        elif self.state.show_spotify_page:
            render_spotify_page(self.spotify_manager, self.ui)
        elif self.state.show_favorites_page:
            self.favorites_page.render()
        elif self.state.show_api_dashboard_page:
            self.api_dashboard_page.render()
        else:
            self._render_main_layout()

    def _render_main_layout(self) -> None:
        """메인 레이아웃 렌더링"""
        with st.sidebar:
            self.sidebar.render()
        self.chat_page.render()

    def _export_data(self) -> None:
        """데이터 내보내기"""
        try:
            all_sessions = self.chat_manager.get_all_sessions()

            export_data = {
                "app_name": APP_NAME,
                "app_version": APP_VERSION,
                "exported_at": datetime.now().isoformat(),
                "sessions": [session.to_dict() for session in all_sessions],
                "settings": self.settings.export_settings(),
                "usage_stats": self.usage_tracker.export_usage_data(),
            }

            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            filename = f"llmos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            st.download_button(
                label="💾 전체 데이터 다운로드",
                data=json_data,
                file_name=filename,
                mime="application/json",
                key="download_all_data_btn",
            )

            st.success("데이터 내보내기가 준비되었습니다!")

        except (IOError, OSError, PermissionError) as e:
            logger.error(f"File operation error during data export: {e}")
            st.error(f"파일 처리 중 오류가 발생했습니다: {e}")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Data processing error during export: {e}")
            st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during data export: {e}")
            st.error(f"예상치 못한 오류가 발생했습니다: {e}")

    def cleanup(self) -> None:
        """애플리케이션 정리"""
        try:
            log_handler = get_log_handler()
            if hasattr(log_handler, "cleanup"):
                log_handler.cleanup()

            self.usage_tracker.cleanup_old_data(keep_days=DATA_CLEANUP_KEEP_DAYS)
            logger.info("Application cleanup completed")

        except (IOError, OSError, PermissionError) as e:
            logger.error(f"File operation error during cleanup: {e}")
        except (AttributeError, TypeError) as e:
            logger.error(f"Object access error during cleanup: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during cleanup: {e}")

    def get_app_info(self) -> dict:
        """애플리케이션 정보 반환 (StateManager 사용)"""
        return {
            "name": APP_NAME,
            "version": APP_VERSION,
            "total_sessions": len(self.chat_manager.get_all_sessions()),
            "available_providers": len(self.model_manager.get_available_providers()),
            "current_session_id": self.state.get("current_session_id"),
            "settings_valid": self.model_manager.validate_configuration()["valid"],
        }


def create_app() -> EnhancedLLMOSApp:
    """애플리케이션 인스턴스 생성"""
    return EnhancedLLMOSApp()


def run_app() -> None:
    """애플리케이션 실행 (스크립트용)"""
    app = create_app()

    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        st.error(f"예상치 못한 오류가 발생했습니다: {e}")