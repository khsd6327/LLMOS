# src/llmos/ui/pages/settings.py
"""
LLM OS - 설정 페이지
"""

import logging
from typing import Dict, Any

import streamlit as st

from ...managers.settings import SettingsManager
from ...managers.model_manager import EnhancedModelManager
from ...models.enums import ModelProvider
from ...ui.components import EnhancedUI

logger = logging.getLogger(__name__)


class SettingsPage:
    """설정 페이지 클래스"""

    def __init__(
        self,
        settings_manager: SettingsManager,
        model_manager: EnhancedModelManager,
        ui: EnhancedUI,
    ):
        self.settings = settings_manager
        self.model_manager = model_manager
        self.ui = ui

    def render(self):
        """설정 페이지 렌더링"""
        st.header("⚙️ 애플리케이션 설정")

        # 뒒로가기 버튼
        if st.button("⬅️ 채팅으로 돌아가기", key="back_from_settings_page_btn"):
            st.session_state.show_settings_page = False
            st.rerun()

        # 탭으로 설정 섹션 분리
        tabs = st.tabs(["🔑 API 키", "🎛️ 기본 설정", "🎨 UI 설정", "🔧 고급 설정"])

        with tabs[0]:
            self._render_api_keys_section()

        with tabs[1]:
            self._render_default_settings_section()

        with tabs[2]:
            self._render_ui_settings_section()

        with tabs[3]:
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
