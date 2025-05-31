# src/llmos/ui/pages/settings.py
"""
LLM OS - 설정 페이지
"""

import logging
from typing import Dict, Any

import streamlit as st

from ...managers.spotify_manager import SpotifyManager
from ...managers.settings import SettingsManager
from ...managers.model_manager import EnhancedModelManager
from ...models.enums import ModelProvider
from ...ui.components import EnhancedUI

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


class SettingsPage:
    """설정 페이지 클래스"""

    def __init__(
        self,
        settings_manager: SettingsManager,
        model_manager: EnhancedModelManager,
        spotify_manager: SpotifyManager, # <--- spotify_manager 인자 추가
        ui: EnhancedUI,
    ):
        self.settings = settings_manager
        self.model_manager = model_manager
        self.spotify_manager = spotify_manager # <--- self.spotify_manager로 저장
        self.ui = ui
        
    def render(self):
        """설정 페이지 렌더링"""
        st.header("⚙️ 애플리케이션 설정")

        # 뒤로가기 버튼
        if st.button("⬅️ 채팅으로 돌아가기", key="back_from_settings_page_btn"):
            st.session_state.show_settings_page = False
            st.rerun()

        # 탭으로 설정 섹션 분리
        tab_titles = ["🔑 API 키", "🎛️ 기본 설정", "🎨 UI 설정", "🎵 Spotify API", "🔧 고급 설정"] # <--- "Spotify API" 탭 제목 추가
        tabs = st.tabs(tab_titles)

        with tabs[0]: # API 키
            self._render_api_keys_section()

        with tabs[1]: # 기본 설정
            self._render_default_settings_section()

        with tabs[2]: # UI 설정
            self._render_ui_settings_section()

        with tabs[3]: # Spotify API (새로운 탭)
            self._render_spotify_api_settings_section() # 이 메서드는 곧 만들 예정입니다.

        with tabs[4]: # 고급 설정 (인덱스가 하나씩 밀립니다)
            self._render_advanced_settings_section()

    def _render_api_keys_section(self):
        """API 키 설정 섹션"""
        st.subheader("API 키 관리")
        st.markdown("각 AI 제공업체의 API 키를 설정하세요.")

        api_key_changed = False

        for provider_enum in ModelProvider:
            provider_val = provider_enum.value
            provider_name = provider_enum.name.capitalize()

            with st.expander(f"{provider_name} API 키", expanded=False):
                current_key = self.settings.get(f"api_keys.{provider_val}", "")
                has_key = bool(current_key)

                # 상태 표시
                if has_key:
                    st.success(f"✅ {provider_name} API 키가 설정되어 있습니다.")
                else:
                    st.warning(f"⚠️ {provider_name} API 키가 설정되지 않았습니다.")

                # 키 입력
                new_key = st.text_input(
                    f"{provider_name} API Key",
                    value=current_key,
                    type="password",
                    key=f"apikey_input_{provider_val}",
                    help=f"{provider_name} 웹사이트에서 API 키를 발급받으세요.",
                )

                # 저장 버튼
                col1, col2 = st.columns([1, 3])
                if col1.button(f"저장", key=f"save_apikey_{provider_val}"):
                    if new_key != current_key:
                        self.settings.set_api_key(provider_val, new_key)
                        api_key_changed = True
                        st.success(f"{provider_name} API 키가 업데이트되었습니다.")
                        st.rerun()

                # 테스트 버튼
                if has_key and col2.button(
                    f"연결 테스트", key=f"test_apikey_{provider_val}"
                ):
                    self._test_api_connection(provider_enum)

        if api_key_changed:
            st.info("API 키가 변경되었습니다. 모델 인터페이스를 다시 초기화합니다.")
            self.model_manager.refresh_interfaces()

    def _test_api_connection(self, provider: ModelProvider):
        """API 연결 테스트"""
        try:
            interface = self.model_manager.get_interface(provider)
            if interface:
                # 간단한 테스트 메시지
                test_messages = [{"role": "user", "content": "Hello"}]

                with st.spinner(f"{provider.name} API 연결 테스트 중..."):
                    response, _ = interface.generate(
                        test_messages, "test-model", max_tokens=10
                    )
                    st.success(f"✅ {provider.name} API 연결 성공!")
            else:
                st.error(f"❌ {provider.name} 인터페이스를 찾을 수 없습니다.")

        except Exception as e:
            st.error(f"❌ {provider.name} API 연결 실패: {str(e)}")

    def _render_default_settings_section(self):
        """기본 설정 섹션"""
        st.subheader("기본 생성 매개변수")

        col1, col2 = st.columns(2)

        with col1:
            # Temperature
            default_temp = self.settings.get("defaults.temperature", 0.7)
            new_temp = st.slider(
                "Temperature (기본값)",
                0.0,
                2.0,
                default_temp,
                0.05,
                key="settings_page_temp_slider",
                help="창의성 조절. 높을수록 다양하고 낮을수록 일관적입니다.",
            )

            if new_temp != default_temp:
                self.settings.set("defaults.temperature", new_temp)

        with col2:
            # Max Tokens
            default_max_tokens = self.settings.get("defaults.max_tokens", 4096)
            new_max_tokens = st.number_input(
                "최대 토큰 (기본값)",
                100,
                100000,
                default_max_tokens,
                100,
                key="settings_page_max_tokens",
                help="AI 응답의 최대 길이입니다.",
            )

            if new_max_tokens != default_max_tokens:
                self.settings.set("defaults.max_tokens", new_max_tokens)

        # 기능 설정
        st.subheader("기능 설정")

        # 자동 제목 생성
        auto_title = st.checkbox(
            "자동 채팅 제목 생성",
            value=self.settings.get("features.auto_title_generation", True),
            key="auto_title_checkbox",
            help="첫 번째 응답 후 AI가 자동으로 채팅 제목을 생성합니다.",
        )
        self.settings.set("features.auto_title_generation", auto_title)

        # 사용량 추적
        usage_tracking = st.checkbox(
            "사용량 추적",
            value=self.settings.get("features.usage_tracking", True),
            key="usage_tracking_checkbox",
            help="토큰 사용량과 비용을 추적합니다.",
        )
        self.settings.set("features.usage_tracking", usage_tracking)

        # 디버그 모드
        debug_mode = st.checkbox(
            "디버그 모드",
            value=self.settings.get("features.debug_mode", False),
            key="debug_mode_checkbox",
            help="개발자를 위한 추가 로깅과 정보를 표시합니다.",
        )
        self.settings.set("features.debug_mode", debug_mode)

    def _render_spotify_api_settings_section(self):
        """Spotify API 설정 섹션 렌더링"""
        st.subheader("🎵 Spotify API 연동 설정")

        # 현재 저장된 Spotify 설정을 불러옵니다.
        saved_client_id = self.settings.get("spotify_client_id", "")
        saved_client_secret = self.settings.get("spotify_client_secret", "") # 비밀번호 필드이므로 값은 직접 보이지 않습니다.
        saved_redirect_uri = self.settings.get("spotify_redirect_uri", "http://127.0.0.1:8888/callback")
        saved_port_type = self.settings.get("spotify_port_type", "fixed")

        st.markdown(
            """
            LLMOS에서 Spotify 기능을 사용하려면, Spotify 개발자 대시보드에서 애플리케이션을 생성하고 다음 정보를 얻어야 합니다:
            1. **Client ID**
            2. **Client Secret**
            3. **Redirect URI 설정:** `http://127.0.0.1:8888/callback` (또는 아래 입력한 URI)을 Spotify 앱 설정에 추가해야 합니다.

            [Spotify Developer Dashboard 바로가기](https://developer.spotify.com/dashboard/)
            """
        )

        with st.form("spotify_api_settings_form"):
            client_id = st.text_input(
                "Spotify Client ID",
                value=saved_client_id,
                key="settings_page_spotify_client_id",
                help="Spotify 개발자 대시보드에서 발급받은 Client ID입니다."
            )
            client_secret = st.text_input(
                "Spotify Client Secret",
                value=saved_client_secret, # 입력 필드가 password 타입이므로 실제 값은 가려집니다.
                type="password",
                key="settings_page_spotify_client_secret",
                help="Spotify 개발자 대시보드에서 발급받은 Client Secret입니다."
            )
            redirect_uri = st.text_input(
                "Spotify Redirect URI",
                value=saved_redirect_uri,
                key="settings_page_spotify_redirect_uri",
                help="Spotify 앱 설정에 등록한 Redirect URI와 정확히 일치해야 합니다."
            )

            port_options = ["fixed", "dynamic"]
            try:
                # 저장된 값이 유효한 옵션 중 하나인지 확인하고, 아니면 기본값(fixed)의 인덱스 사용
                default_port_index = port_options.index(saved_port_type)
            except ValueError:
                default_port_index = 0 # 'fixed'

            port_type = st.radio(
                "인증 시 사용할 로컬 포트 타입",
                options=port_options,
                index=default_port_index,
                format_func=lambda x: "고정 포트 (예: 8888)" if x == "fixed" else "동적 포트 (자동 할당)",
                key="settings_page_spotify_port_type",
                help="대부분의 경우 기본값을 유지해도 괜찮습니다. 고정 포트 사용 시 다른 프로그램과의 충돌에 유의하세요."
            )

            submitted = st.form_submit_button("💾 Spotify 설정 저장", use_container_width=True)

            if submitted:
                if client_id and client_secret and redirect_uri:
                    # SettingsManager를 통해 설정 값을 저장
                    self.settings.set("spotify_client_id", client_id)
                    self.settings.set("spotify_client_secret", client_secret)
                    self.settings.set("spotify_redirect_uri", redirect_uri)
                    self.settings.set("spotify_port_type", port_type)
                    
                    # SpotifyManager의 내부 설정을 다시 로드하도록 강제
                    try:
                        self.spotify_manager._load_spotify_settings() # SpotifyManager 상태 업데이트
                        # session_state에 성공 상태 저장 (즉시 rerun하지 않음)
                        st.session_state['spotify_settings_saved'] = True
                    except Exception as e:
                        st.error(f"❌ Spotify 설정을 적용하는 중 오류가 발생했습니다: {str(e)}")
                        logger.error(f"Error reloading spotify_manager settings after save: {e}")
                else:
                    st.error("⚠️ Client ID, Client Secret, Redirect URI는 반드시 입력해야 합니다.")

        # 성공 메시지 표시 (session_state 기반)
        if st.session_state.get('spotify_settings_saved', False):
            st.success("✅ Spotify API 설정이 성공적으로 저장되었습니다!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 페이지 새로고침", key="spotify_settings_refresh"):
                    st.session_state['spotify_settings_saved'] = False
                    st.rerun()
            with col2:
                if st.button("❌ 메시지 닫기", key="spotify_settings_close"):
                    st.session_state['spotify_settings_saved'] = False
        
        st.markdown("---")
        st.markdown("#### 현재 Spotify 연동 상태")
        if self.spotify_manager.is_configured():
            st.success("✅ Spotify API 정보가 애플리케이션에 설정되어 있습니다.")
            # 인증 상태는 Spotify 페이지에서 직접 확인/진행하도록 유도
            st.info("ℹ️ 실제 Spotify 계정 인증은 Spotify 기능 페이지에서 진행할 수 있습니다.")
        else:
            st.error("❌ Spotify API 정보가 아직 설정되지 않았습니다. 위 양식을 작성하고 저장해주세요.")
            
    def _render_ui_settings_section(self):
        """UI 설정 섹션"""
        st.subheader("사용자 인터페이스 설정")

        col1, col2 = st.columns(2)

        with col1:
            # 테마 설정
            current_theme = self.settings.get("ui.theme", "auto")
            theme = st.selectbox(
                "테마",
                ["auto", "light", "dark"],
                index=["auto", "light", "dark"].index(current_theme),
                key="theme_selector",
                help="애플리케이션 테마를 선택합니다.",
            )

            if theme != current_theme:
                self.settings.set("ui.theme", theme)
                st.info("테마가 변경되었습니다. 페이지를 새로고침하면 적용됩니다.")

        with col2:
            # 언어 설정
            current_language = self.settings.get("ui.language", "ko")
            language = st.selectbox(
                "언어",
                ["ko", "en"],
                index=["ko", "en"].index(current_language),
                format_func=lambda x: "한국어" if x == "ko" else "English",
                key="language_selector",
                help="인터페이스 언어를 선택합니다.",
            )

            if language != current_language:
                self.settings.set("ui.language", language)
                st.info("언어가 변경되었습니다. 일부 텍스트는 재시작 후 적용됩니다.")

        # 채팅 설정
        st.subheader("채팅 설정")

        # 메시지 히스토리 길이
        history_length = st.slider(
            "컨텍스트 메시지 수",
            5,
            50,
            self.settings.get("chat.context_length", 10),
            key="context_length_slider",
            help="AI에게 전달할 최근 메시지 수입니다.",
        )
        self.settings.set("chat.context_length", history_length)

        # 스트리밍 설정
        enable_streaming = st.checkbox(
            "스트리밍 응답 활성화",
            value=self.settings.get("chat.enable_streaming", True),
            key="streaming_checkbox",
            help="AI 응답을 실시간으로 스트리밍합니다.",
        )
        self.settings.set("chat.enable_streaming", enable_streaming)

    def _render_advanced_settings_section(self):
        """고급 설정 섹션"""
        st.subheader("고급 설정")

        # 데이터 관리
        st.subheader("데이터 관리")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("설정 초기화", key="reset_settings_btn"):
                if st.session_state.get("confirm_reset"):
                    self.settings.reset_to_defaults()
                    st.success("설정이 초기화되었습니다.")
                    st.session_state.confirm_reset = False
                    st.rerun()
                else:
                    st.session_state.confirm_reset = True
                    st.warning(
                        "정말로 설정을 초기화하시겠습니까? 다시 한 번 클릭하세요."
                    )

        with col2:
            # 설정 내보내기
            settings_data = self.settings.export_settings()
            st.download_button(
                "설정 내보내기",
                data=str(settings_data),
                file_name="llmos_settings.json",
                mime="application/json",
                key="export_settings_btn",
            )

        with col3:
            # 설정 가져오기
            uploaded_settings = st.file_uploader(
                "설정 가져오기", type=["json"], key="import_settings_uploader"
            )

            if uploaded_settings:
                try:
                    import json

                    settings_data = json.load(uploaded_settings)
                    self.settings.import_settings(settings_data)
                    st.success("설정을 가져왔습니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"설정 가져오기 실패: {e}")

        # 성능 설정
        st.subheader("성능 설정")

        # 캐시 설정
        enable_cache = st.checkbox(
            "응답 캐싱 활성화",
            value=self.settings.get("performance.enable_cache", False),
            key="cache_checkbox",
            help="동일한 질문에 대한 응답을 캐시합니다.",
        )
        self.settings.set("performance.enable_cache", enable_cache)

        # 배치 처리
        batch_size = st.slider(
            "배치 처리 크기",
            1,
            10,
            self.settings.get("performance.batch_size", 1),
            key="batch_size_slider",
            help="한 번에 처리할 요청 수입니다.",
        )
        self.settings.set("performance.batch_size", batch_size)

        # 시스템 정보
        st.subheader("시스템 정보")

        # 모델 검증
        validation_result = self.model_manager.validate_configuration()

        if validation_result["valid"]:
            st.success("✅ 시스템 설정이 올바릅니다.")
        else:
            st.error("❌ 시스템 설정에 문제가 있습니다.")
            for error in validation_result["errors"]:
                st.error(f"• {error}")

        for warning in validation_result["warnings"]:
            st.warning(f"⚠️ {warning}")

        # 제공업체 상태
        with st.expander("제공업체 상태", expanded=False):
            for provider, status in validation_result["provider_status"].items():
                st.write(f"**{provider.upper()}**")
                st.write(f"- API 키: {'✅' if status['has_api_key'] else '❌'}")
                st.write(
                    f"- 인터페이스: {'✅' if status['interface_initialized'] else '❌'}"
                )
                st.write(f"- 사용 가능한 모델: {status['available_models']}개")
                st.divider()

    def _get_system_info(self) -> Dict[str, Any]:
        """시스템 정보 수집"""
        import platform
        import sys
        from pathlib import Path

        return {
            "platform": platform.platform(),
            "python_version": sys.version,
            "config_path": str(self.settings.config_path),
            "total_sessions": len(self.settings.get("paths.chat_sessions", "")),
            "available_providers": len(self.model_manager.get_available_providers()),
        }
