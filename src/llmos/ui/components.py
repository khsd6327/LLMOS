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
    def _render_stop_button(self):
        """AI 응답 중단 버튼 렌더링 (채팅 입력창 자리에 표시)"""
        # 중단 버튼을 채팅 입력창과 동일한 위치에 표시
        st.markdown("### 🤖 AI 응답 생성 중...")
        
        # 전체 너비로 중단 버튼 표시
        if st.button("🛑 응답 중단", key="stop_generation_btn", type="secondary", use_container_width=True):
            st.session_state.should_stop_streaming = True
            self.model_manager.stop_generation()
            st.toast("AI 응답을 중단했습니다.", icon="🛑")
            st.rerun()
            
        # 안내 메시지
        st.caption("💡 원하지 않는 응답이 생성되고 있다면 위 버튼을 눌러 중단할 수 있습니다.")
        st.caption("🔄 Enter: 전송 | Shift+Enter: 줄바꿈")

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
    def render_integrated_chat_input() -> Optional[str]:
        """통합 채팅 입력 v8: file_uploader on_change 콜백 사용 및 상태 관리 개선"""
        # 조건부 import: chat_input_advanced가 없으면 기본 streamlit 사용
        try:
            from chat_input_advanced import chat_input_avd
            chat_input_func = chat_input_avd
            logger.debug("Using advanced chat input (chat_input_avd)")
        except ImportError:
            chat_input_func = st.chat_input
            logger.warning("chat_input_advanced not available, using standard st.chat_input")

        from ..managers.state_manager import get_state  # get_state import 확인

        state = get_state()
        uploader_key = "chat_file_uploader_hidden"

        # --- 파일 업로드 처리 콜백 함수 ---
        def uploader_on_change_callback():
            _state = get_state() # 콜백 내에서 state 다시 가져오기
            uploaded_file_widget_value = st.session_state.get(uploader_key)

            if uploaded_file_widget_value is not None:
                try:
                    _state.chat_uploaded_image_bytes = uploaded_file_widget_value.getvalue()
                    _state.chat_uploaded_image_name = uploaded_file_widget_value.name
                    logger.info(f"Image '{_state.chat_uploaded_image_name}' processed by on_change and staged in StateManager.")
                    # on_change 콜백에 의해 자동으로 rerun이 발생하므로 명시적인 st.rerun() 호출은 대부분 필요 없습니다.
                    # 여기서 st.session_state[uploader_key] = None 을 호출하면 다음 업로드가 안될 수 있으므로 주의해야 합니다.
                    # Streamlit은 위젯 키를 내부적으로 관리하며, 사용자가 파일을 다시 올리면 on_change가 다시 트리거됩니다.
                    # 중요한 것은 이 콜백이 "파일이 새로 선택되었을 때만" 실행된다는 점입니다.
                except Exception as e:
                    logger.error(f"Error processing uploaded file in on_change_callback: {e}")
                    _state.chat_uploaded_image_bytes = None
                    _state.chat_uploaded_image_name = None
                    # 파일 처리 후 업로더 위젯의 상태를 명시적으로 초기화 시도
                    st.session_state[uploader_key] = None
            # else:
                # 파일이 제거된 경우 (clear 버튼 등) uploaded_file_widget_value가 None이 될 수 있습니다.
                # 이 경우, 이미 preview에서 state를 None으로 설정하므로 여기서 특별히 처리할 필요는 없을 수 있습니다.
                # logger.debug("File uploader value is None in on_change callback.")

        # --- 이미지 미리보기 및 제거 버튼 ---
        if state.chat_uploaded_image_bytes:
            col_preview, col_remove_btn = st.columns([0.8, 0.2])
            with col_preview:
                st.image(
                    state.chat_uploaded_image_bytes,
                    caption=state.chat_uploaded_image_name or "첨부 이미지",
                    width=100
                )
            if col_remove_btn.button("이미지 제거 ❌", key="remove_chat_image_btn"):
                state.chat_uploaded_image_bytes = None
                state.chat_uploaded_image_name = None
                state.just_removed_image_flag = True # 이미지 제거 플래그 설정
                # 파일 업로더 위젯 자체도 초기화 (uploader_key는 "chat_file_uploader_hidden")
                if uploader_key in st.session_state:
                    st.session_state[uploader_key] = None
                st.rerun()

        # --- 파일 업로더 위젯 ---
        st.file_uploader(
            "이미지 첨부",
            type=SUPPORTED_IMAGE_EXTENSIONS,
            key=uploader_key,
            label_visibility="collapsed",
            on_change=uploader_on_change_callback
        )

        # 이전의 무한 루프를 유발하던 로직은 제거되었습니다.
        # if uploaded_file: << 이 부분과 내부의 logger.info 및 st.rerun()이 문제의 원인이었습니다.
        # on_change 콜백이 이 역할을 대신합니다.

        # --- 채팅 입력창 ---
        if chat_input_func == st.chat_input:
            # 기본 streamlit chat_input 사용
            prompt = chat_input_func(
                placeholder="메시지를 입력하세요...",
                key="main_chat_input"
            )
        else:
            # 고급 chat_input_avd 사용
            prompt = chat_input_func(
                placeholder="메시지를 입력하세요..."
            )
        return prompt

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
    
    @staticmethod
    def render_provider_status(model_manager, show_test_buttons: bool = True,
                              show_details: bool = True, key_suffix: str = "") -> Dict[str, Any]:
        """
        AI 제공업체 상태 공통 컴포넌트
        
        Args:
            model_manager: EnhancedModelManager 인스턴스
            settings_manager: SettingsManager 인스턴스  
            show_test_buttons: API 연결 테스트 버튼 표시 여부
            show_details: 상세 정보 표시 여부
            key_suffix: Streamlit 키 충돌 방지용 접미사
            
        Returns:
            상태 정보 딕셔너리
        """
        st.subheader("🔌 AI 제공업체 상태")
        
        # 새로고침 버튼
        col_refresh, col_info = st.columns([1, 3])
        with col_refresh:
            if st.button("🔄 상태 새로고침", key=f"refresh_provider_status_{key_suffix}"):
                # 인터페이스 새로고침
                model_manager.refresh_interfaces()
                st.success("상태가 새로고침되었습니다!")
                st.rerun()
        
        with col_info:
            st.caption("각 AI 제공업체의 API 키 및 연결 상태를 확인합니다.")
        
        # 설정 검증 실행
        validation_result = model_manager.validate_configuration()
        status_summary = {"total_providers": 0, "active_providers": 0, "errors": 0, "warnings": 0}
        
        # 전체 상태 요약
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("총 제공업체", len(validation_result["provider_status"]))
        with col2:
            active_count = sum(1 for status in validation_result["provider_status"].values() 
                             if status["has_api_key"] and status["interface_initialized"])
            st.metric("활성 제공업체", active_count)
        with col3:
            st.metric("오류", len(validation_result["errors"]))
        with col4:
            st.metric("경고", len(validation_result["warnings"]))

        status_summary.update({
            "total_providers": len(validation_result["provider_status"]),
            "active_providers": active_count,
            "errors": len(validation_result["errors"]),
            "warnings": len(validation_result["warnings"])
        })
        
        # 전체 상태 표시
        if validation_result["valid"]:
            st.success("✅ 모든 설정이 올바릅니다.")
        else:
            st.error("❌ 설정에 문제가 있습니다.")
            for error in validation_result["errors"]:
                st.error(f"• {error}")
        
        for warning in validation_result["warnings"]:
            st.warning(f"⚠️ {warning}")
        
        # 각 제공업체별 상세 상태
        for provider_key, status in validation_result["provider_status"].items():
            provider_name = provider_key.upper()
            
            # 상태 아이콘 결정
            if status["has_api_key"] and status["interface_initialized"]:
                status_icon = "🟢"
                status_text = "정상"
            elif status["has_api_key"] and not status["interface_initialized"]:
                status_icon = "🔴"
                status_text = "인터페이스 오류"
            else:
                status_icon = "⚪"
                status_text = "미설정"
            
            with st.expander(f"{status_icon} {provider_name} - {status_text}", expanded=False):
                
                if show_details:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**기본 상태**")
                        st.write(f"API 키: {'✅ 설정됨' if status['has_api_key'] else '❌ 미설정'}")
                        st.write(f"인터페이스: {'✅ 초기화됨' if status['interface_initialized'] else '❌ 오류'}")
                    
                    with col2:
                        st.write("**모델 정보**")
                        st.write(f"사용 가능한 모델: {status['available_models']}개")
                        
                        # 인터페이스 기능 표시 (초기화된 경우에만)
                        if status["interface_initialized"]:
                            try:
                                from ..models.enums import ModelProvider
                                provider_enum = ModelProvider(provider_key)
                                interface = model_manager.get_interface(provider_enum)
                                if interface:
                                    features = interface.get_supported_features()
                                    st.write("**지원 기능**")
                                    feature_text = []
                                    for feature, supported in features.items():
                                        icon = "✅" if supported else "❌"
                                        feature_text.append(f"{icon} {feature}")
                                    st.write(" | ".join(feature_text))
                            except Exception as e:
                                logger.warning(f"Failed to get interface features for {provider_name}: {e}")
                
                # API 연결 테스트 버튼
                if show_test_buttons and status["has_api_key"] and status["interface_initialized"]:
                    if st.button(f"🔗 {provider_name} 연결 테스트", 
                               key=f"test_api_{provider_key}_{key_suffix}",
                               help=f"{provider_name} API와의 연결을 테스트합니다."):
                        
                        try:
                            from ..models.enums import ModelProvider
                            provider_enum = ModelProvider(provider_key)
                            
                            with st.spinner(f"{provider_name} API 테스트 중..."):
                                # 간단한 테스트 메시지
                                test_messages = [{"role": "user", "content": "Hello! This is a connection test."}]
                                
                                response, usage = model_manager.generate(
                                    test_messages,
                                    provider_display_name=provider_enum.name.capitalize(),
                                    max_tokens=50,
                                    temperature=0.1,
                                )
                                
                                st.success(f"✅ {provider_name} API 연결 성공!")
                                
                                # 응답 미리보기
                                with st.expander("테스트 응답 미리보기", expanded=False):
                                    st.text(f"응답: {response[:100]}{'...' if len(response) > 100 else ''}")
                                    if usage:
                                        st.text(f"토큰 사용량: {usage.total_tokens}")
                                        st.text(f"비용: ${usage.cost_usd:.6f}")
                                        
                        except Exception as e:
                            st.error(f"❌ {provider_name} API 테스트 실패:")
                            st.code(str(e))
                            logger.error(f"API test failed for {provider_name}: {e}")
                elif show_test_buttons and not status["has_api_key"]:
                    st.info(f"💡 {provider_name} API 키를 설정하면 연결 테스트를 할 수 있습니다.")
                elif show_test_buttons and not status["interface_initialized"]:
                    st.warning(f"⚠️ {provider_name} 인터페이스 초기화에 실패했습니다. API 키를 확인해주세요.")
        
        return status_summary