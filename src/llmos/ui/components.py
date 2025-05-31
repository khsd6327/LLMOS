# src/llmos/ui/components.py
"""
LLM OS - UI 컴포넌트
"""

import logging
from typing import Dict, List, Optional, Tuple, Any

import streamlit as st

from ..managers.settings import SettingsManager
from ..managers.usage_tracker import UsageTracker
from ..models.model_registry import ModelRegistry
from ..core.config import SUPPORTED_IMAGE_EXTENSIONS

logger = logging.getLogger(__name__)


class EnhancedUI:
    """향상된 UI 컴포넌트 모음"""

    @staticmethod
    def render_usage_stats(usage_tracker):
        """사용량 통계 렌더링 (세션 + 오늘 + 전체) - 2x2 레이아웃 적용"""
        st.markdown("### 📊 사용량 통계")

        try:
            session_stats = usage_tracker.get_session_usage()
            today_stats = usage_tracker.get_today_usage_from_summary()
            total_stats = usage_tracker.get_total_usage_from_history()

            # 세션 사용량 (현재 앱 실행 이후) - 2x2 레이아웃
            with st.expander("⚡ 현재 세션", expanded=True):
                # 상단 행: 요청 + 토큰
                col1, col2 = st.columns(2)
                col1.metric("요청", f"{session_stats['total_requests']:,}")
                col2.metric("토큰", f"{session_stats['total_tokens']:,}")
                
                # 하단 행: 비용 + 세션 시간
                col3, col4 = st.columns(2)
                session_cost_str = (
                    f"${session_stats['total_cost']:.4f}"
                    if session_stats["total_cost"] > 0.00001
                    else "$0.00"
                )
                col3.metric("비용 (USD)", session_cost_str)
                
                # 세션 지속 시간
                session_duration = session_stats.get("session_duration_minutes", 0)
                duration_str = f"{session_duration:.1f}분" if session_duration > 0 else "0분"
                col4.metric("세션 시간", duration_str)

            # 오늘 사용량 - 2x2 레이아웃
            with st.expander("📅 오늘 사용량", expanded=False):
                # 상단 행: 요청 + 토큰
                col1, col2 = st.columns(2)
                col1.metric("요청", f"{today_stats['total_requests']:,}")
                col2.metric("토큰", f"{today_stats['total_tokens']:,}")
                
                # 하단 행: 비용 (넓게)
                today_cost_str = (
                    f"${today_stats['total_cost']:.4f}"
                    if today_stats["total_cost"] > 0.00001
                    else "$0.00"
                )
                st.metric("비용 (USD)", today_cost_str)

            # 전체 사용량 - 2x2 레이아웃
            with st.expander("📈 전체 사용량 (기록 기반)", expanded=False):
                # 상단 행: 요청 + 토큰
                col1, col2 = st.columns(2)
                col1.metric("총 요청", f"{total_stats['total_requests']:,}")
                col2.metric("총 토큰", f"{total_stats['total_tokens']:,}")
                
                # 하단 행: 비용 (넓게)
                total_cost_str = (
                    f"${total_stats['total_cost']:.4f}"
                    if total_stats["total_cost"] > 0.00001
                    else "$0.00"
                )
                st.metric("총 비용 (USD)", total_cost_str)

        except Exception as e:
            st.error(f"사용량 통계 로드 중 오류: {e}")
            st.info("사용량 데이터를 불러올 수 없습니다.")

    @staticmethod
    def render_usage_trends(usage_tracker: UsageTracker, days: int = 7):
        """사용량 트렌드 차트"""
        trends = usage_tracker.get_usage_trends(days)

        if trends:
            import pandas as pd

            df = pd.DataFrame(trends)

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("일별 토큰 사용량")
                st.bar_chart(df.set_index("date")["tokens"])

            with col2:
                st.subheader("일별 비용")
                st.line_chart(df.set_index("date")["cost"])

    @staticmethod
    def render_integrated_chat_input() -> Optional[str]:
        """통합 채팅 입력 렌더링"""
        # 이미지 미리보기 및 제거 버튼
        if st.session_state.get("chat_uploaded_image_bytes"):
            col_preview, col_remove_btn = st.columns([0.8, 0.2])

            with col_preview:
                st.image(
                    st.session_state.chat_uploaded_image_bytes,
                    caption=st.session_state.get(
                        "chat_uploaded_image_name", "첨부 이미지"
                    ),
                    width=100,
                )

            if col_remove_btn.button(
                "이미지 제거 ❌", key="remove_chat_image_btn_main_chat_input"
            ):
                st.session_state.chat_uploaded_image_bytes = None
                st.session_state.chat_uploaded_image_name = None
                st.session_state.last_uploaded_filename_integrated = None
                st.rerun()

        # 파일 업로더
        uploaded_file = st.file_uploader(
            "이미지 첨부 (선택)",
            type=SUPPORTED_IMAGE_EXTENSIONS,
            key="chat_file_uploader_main_integrated_input",
            label_visibility="collapsed",
            help="채팅과 함께 이미지를 업로드합니다.",
        )

        if uploaded_file:
            if st.session_state.get(
                "last_uploaded_filename_integrated"
            ) != uploaded_file.name or not st.session_state.get(
                "chat_uploaded_image_bytes"
            ):

                st.session_state.chat_uploaded_image_bytes = uploaded_file.getvalue()
                st.session_state.chat_uploaded_image_name = uploaded_file.name
                st.session_state.last_uploaded_filename_integrated = uploaded_file.name

                logger.info(
                    f"Image '{uploaded_file.name}' staged for chat via integrated uploader."
                )
                st.rerun()

        # 채팅 입력
        prompt = st.chat_input("메시지를 입력하거나 이미지를 첨부하세요...")
        return prompt

    @staticmethod
    def render_model_selector(
        settings_manager: SettingsManager,
    ) -> Tuple[Optional[str], Optional[str]]:
        """모델 선택기 렌더링"""
        all_provider_names = ModelRegistry.get_all_provider_display_names()

        if not all_provider_names:
            st.error("등록된 AI 제공자가 없습니다. ModelRegistry를 확인해주세요.")
            return None, None

        # 제공업체 선택
        selected_provider_name = settings_manager.get(
            "ui.selected_provider", all_provider_names[0]
        )
        if selected_provider_name not in all_provider_names:
            selected_provider_name = all_provider_names[0]
            settings_manager.set("ui.selected_provider", selected_provider_name)

        provider_idx = all_provider_names.index(selected_provider_name)

        new_selected_provider_name = st.selectbox(
            "🤖 AI 제공자",
            all_provider_names,
            index=provider_idx,
            key="main_ui_provider_selector",
        )

        # 제공업체가 변경된 경우
        if new_selected_provider_name != selected_provider_name:
            settings_manager.set("ui.selected_provider", new_selected_provider_name)

            # 새 제공업체의 기본 모델을 가져와서 설정 (제공업체별 기본 모델 사용)
            default_model_for_provider = (
                settings_manager.get_default_model_for_provider(
                    new_selected_provider_name
                )
            )

            if not default_model_for_provider:
                # 기본 모델이 설정되지 않은 경우 첫 번째 모델로 설정
                models_for_new_provider = ModelRegistry.get_models_for_provider(
                    new_selected_provider_name
                )
                if models_for_new_provider:
                    default_model_for_provider = list(models_for_new_provider.keys())[0]
                    settings_manager.set_default_model_for_provider(
                        new_selected_provider_name, default_model_for_provider
                    )

            st.rerun()

        # 모델 선택
        models_dict = ModelRegistry.get_models_for_provider(new_selected_provider_name)
        if not models_dict:
            st.warning(f"'{new_selected_provider_name}' 제공자를 위한 모델이 없습니다.")
            return new_selected_provider_name, None

        model_keys = list(models_dict.keys())

        # 현재 제공업체의 기본 모델 가져오기 (새로운 방식)
        selected_model_key = settings_manager.get_default_model_for_provider(
            new_selected_provider_name
        )

        # 기본 모델이 없거나 유효하지 않은 경우 첫 번째 모델로 설정
        if selected_model_key not in model_keys:
            selected_model_key = model_keys[0] if model_keys else None
            if selected_model_key:
                settings_manager.set_default_model_for_provider(
                    new_selected_provider_name, selected_model_key
                )

        model_idx = (
            model_keys.index(selected_model_key)
            if selected_model_key and selected_model_key in model_keys
            else 0
        )

        new_selected_model_key = st.selectbox(
            "🧠 모델 선택",
            model_keys,
            index=model_idx,
            format_func=lambda k: (
                models_dict[k].display_name if k in models_dict else "알 수 없음"
            ),
            key="main_ui_model_selector",
            help=(
                models_dict[selected_model_key].description
                if selected_model_key and selected_model_key in models_dict
                else "모델 설명을 보려면 선택하세요."
            ),
        )

        # 모델이 변경된 경우 해당 제공업체의 기본 모델로 저장
        if new_selected_model_key != selected_model_key:
            settings_manager.set_default_model_for_provider(
                new_selected_provider_name, new_selected_model_key
            )
            st.rerun()

        # 모델 정보 표시
        if new_selected_model_key and new_selected_model_key in models_dict:
            cfg = models_dict[new_selected_model_key]
            with st.expander(f"모델 정보: {cfg.display_name}", expanded=False):
                st.markdown(f"**API ID:** `{cfg.model_name}`")
                st.markdown(f"**최대 토큰:** {cfg.max_tokens:,}")
                st.markdown(
                    f"**스트리밍:** {'✅' if cfg.supports_streaming else '❌'}  "
                    f"**함수호출:** {'✅' if cfg.supports_functions else '❌'}  "
                    f"**비전:** {'✅' if cfg.supports_vision else '❌'}"
                )
                st.markdown(f"**입력 비용:** ${cfg.input_cost_per_1k:.5f} / 1K 토큰")
                st.markdown(f"**출력 비용:** ${cfg.output_cost_per_1k:.5f} / 1K 토큰")
                st.caption(cfg.description)

        return new_selected_provider_name, new_selected_model_key

    @staticmethod
    def render_generation_params(settings_manager: SettingsManager):
        """생성 매개변수 렌더링"""
        st.markdown("### ⚙️ 생성 매개변수")

        # Temperature
        temp = st.slider(
            "Temperature",
            0.0,
            2.0,
            settings_manager.get("defaults.temperature", 0.7),
            0.05,
            key="param_temp_slider_sidebar_config",
            help="창의성 조절. 높을수록 다양, 낮을수록 일관적.",
        )

        if temp != settings_manager.get("defaults.temperature"):
            settings_manager.set("defaults.temperature", temp)

        # Max Tokens
        max_tokens = st.number_input(
            "최대 토큰 (응답 길이)",
            100,
            100000,
            settings_manager.get("defaults.max_tokens", 4096),
            100,
            key="param_max_tokens_input_sidebar_config",
            help="AI 응답의 최대 길이.",
        )

        if max_tokens != settings_manager.get("defaults.max_tokens"):
            settings_manager.set("defaults.max_tokens", max_tokens)

    @staticmethod
    def render_loading_spinner(text: str = "처리 중..."):
        """로딩 스피너 렌더링"""
        return st.spinner(text)

    @staticmethod
    def render_progress_bar(progress: float, text: str = ""):
        """진행률 표시줄 렌더링"""
        st.progress(progress, text=text)

    @staticmethod
    def render_status_indicator(status: str, message: str = ""):
        """상태 표시기 렌더링"""
        status_icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "loading": "⏳",
        }

        icon = status_icons.get(status, "•")
        st.markdown(f"{icon} {message}")

    @staticmethod
    def render_expandable_section(title: str, content: Any, expanded: bool = False):
        """확장 가능한 섹션 렌더링"""
        with st.expander(title, expanded=expanded):
            if callable(content):
                content()
            else:
                st.write(content)

    @staticmethod
    def render_tabs(tab_names: List[str], contents: List[Any]):
        """탭 렌더링"""
        tabs = st.tabs(tab_names)

        for i, (tab, content) in enumerate(zip(tabs, contents)):
            with tab:
                if callable(content):
                    content()
                else:
                    st.write(content)

    @staticmethod
    def render_metric_card(title: str, value: str, delta: Optional[str] = None):
        """메트릭 카드 렌더링"""
        st.metric(title, value, delta)

    @staticmethod
    def render_info_box(message: str, type: str = "info"):
        """정보 박스 렌더링"""
        if type == "success":
            st.success(message)
        elif type == "error":
            st.error(message)
        elif type == "warning":
            st.warning(message)
        else:
            st.info(message)

    @staticmethod
    def render_confirmation_dialog(message: str, key: str) -> Optional[bool]:
        """확인 대화상자 렌더링"""
        st.warning(message)

        col1, col2 = st.columns(2)

        confirm = col1.button("확인", key=f"confirm_{key}", type="primary")
        cancel = col2.button("취소", key=f"cancel_{key}")

        if confirm:
            return True
        elif cancel:
            return False

        return None