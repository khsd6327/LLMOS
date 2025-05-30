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
    def render_copy_button(text_to_copy: str, button_key: str, help_text: str = "복사"):
        """복사 버튼 렌더링"""
        if st.button("📋", key=f"copy_btn_{button_key}", help=help_text):
            st.code(text_to_copy, language=None)
            st.success("위 텍스트를 선택하여 복사하세요 (Ctrl+A, Ctrl+C).", icon="📋")

    @staticmethod
    def render_edit_button(button_key: str):
        """편집 버튼 렌더링"""
        return st.button("✏️", key=f"edit_btn_{button_key}", help="수정")

    @staticmethod
    def render_retry_button(button_key: str):
        """재시도 버튼 렌더링"""
        return st.button("🔄", key=f"retry_btn_{button_key}", help="다시 시도")

    @staticmethod
    def render_usage_stats(usage_tracker: UsageTracker):
        """사용량 통계 렌더링 (세션 + 오늘 + 전체)"""
        st.markdown("### 📊 사용량 통계")
        
        session_stats = usage_tracker.get_session_usage()
        today_stats = usage_tracker.get_today_usage_from_summary()
        total_stats = usage_tracker.get_total_usage_from_history()

        # 세션 사용량 (현재 앱 실행 이후)
        with st.expander("⚡ 현재 세션", expanded=True):
            col1, col2, col3 = st.columns(3)
            col1.metric("요청", f"{session_stats['total_requests']:,}")
            col2.metric("토큰", f"{session_stats['total_tokens']:,}")
            
            session_cost_str = f"${session_stats['total_cost']:.4f}" if session_stats['total_cost'] > 0.00001 else "$0.00"
            col3.metric("비용 (USD)", session_cost_str)
            
            # 세션 지속 시간 표시
            session_duration = session_stats.get('session_duration_minutes', 0)
            if session_duration > 0:
                st.caption(f"세션 시간: {session_duration:.1f}분")

        # 오늘 사용량
        with st.expander("📅 오늘 사용량", expanded=False):
            col1, col2, col3 = st.columns(3)
            col1.metric("요청", f"{today_stats['total_requests']:,}")
            col2.metric("토큰", f"{today_stats['total_tokens']:,}")
            
            cost_str = f"${today_stats['total_cost']:.4f}" if today_stats['total_cost'] > 0.00001 else "$0.00"
            col3.metric("비용 (USD)", cost_str)

        # 전체 사용량
        with st.expander("📈 전체 사용량 (기록 기반)", expanded=False):
            col1, col2, col3 = st.columns(3)
            col1.metric("총 요청", f"{total_stats['total_requests']:,}")
            col2.metric("총 토큰", f"{total_stats['total_tokens']:,}")
            
            total_cost_str = f"${total_stats['total_cost']:.4f}" if total_stats['total_cost'] > 0.00001 else "$0.00"
            col3.metric("총 비용 (USD)", total_cost_str)
            
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
                st.bar_chart(df.set_index('date')['tokens'])
            
            with col2:
                st.subheader("일별 비용")
                st.line_chart(df.set_index('date')['cost'])

    @staticmethod
    def render_integrated_chat_input() -> Optional[str]:
        """통합 채팅 입력 렌더링"""
        # 이미지 미리보기 및 제거 버튼
        if st.session_state.get("chat_uploaded_image_bytes"):
            col_preview, col_remove_btn = st.columns([0.8, 0.2])
            
            with col_preview:
                st.image(
                    st.session_state.chat_uploaded_image_bytes,
                    caption=st.session_state.get("chat_uploaded_image_name", "첨부 이미지"),
                    width=100
                )
            
            if col_remove_btn.button("이미지 제거 ❌", key="remove_chat_image_btn_main_chat_input"):
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
            help="채팅과 함께 이미지를 업로드합니다."
        )
        
        if uploaded_file:
            if (st.session_state.get("last_uploaded_filename_integrated") != uploaded_file.name or
                not st.session_state.get("chat_uploaded_image_bytes")):
                
                st.session_state.chat_uploaded_image_bytes = uploaded_file.getvalue()
                st.session_state.chat_uploaded_image_name = uploaded_file.name
                st.session_state.last_uploaded_filename_integrated = uploaded_file.name
                
                logger.info(f"Image '{uploaded_file.name}' staged for chat via integrated uploader.")
                st.rerun()

        # 채팅 입력
        prompt = st.chat_input("메시지를 입력하거나 이미지를 첨부하세요...")
        return prompt

    @staticmethod
    def render_model_selector(settings_manager: SettingsManager) -> Tuple[Optional[str], Optional[str]]:
        """모델 선택기 렌더링"""
        all_provider_names = ModelRegistry.get_all_provider_display_names()
        
        if not all_provider_names:
            st.error("등록된 AI 제공자가 없습니다. ModelRegistry를 확인해주세요.")
            return None, None

        # 제공업체 선택
        selected_provider_name = settings_manager.get("ui.selected_provider", all_provider_names[0])
        if selected_provider_name not in all_provider_names:
            selected_provider_name = all_provider_names[0]
            settings_manager.set("ui.selected_provider", selected_provider_name)

        provider_idx = all_provider_names.index(selected_provider_name)
        
        new_selected_provider_name = st.selectbox(
            "🤖 AI 제공자",
            all_provider_names,
            index=provider_idx,
            key="main_ui_provider_selector"
        )
        
        # 제공업체가 변경된 경우
        if new_selected_provider_name != selected_provider_name:
            settings_manager.set("ui.selected_provider", new_selected_provider_name)
            
            # 새 제공업체의 기본 모델을 가져와서 설정 (제공업체별 기본 모델 사용)
            default_model_for_provider = settings_manager.get_default_model_for_provider(new_selected_provider_name)
            
            if not default_model_for_provider:
                # 기본 모델이 설정되지 않은 경우 첫 번째 모델로 설정
                models_for_new_provider = ModelRegistry.get_models_for_provider(new_selected_provider_name)
                if models_for_new_provider:
                    default_model_for_provider = list(models_for_new_provider.keys())[0]
                    settings_manager.set_default_model_for_provider(new_selected_provider_name, default_model_for_provider)
            
            st.rerun()

        # 모델 선택
        models_dict = ModelRegistry.get_models_for_provider(new_selected_provider_name)
        if not models_dict:
            st.warning(f"'{new_selected_provider_name}' 제공자를 위한 모델이 없습니다.")
            return new_selected_provider_name, None

        model_keys = list(models_dict.keys())
        
        # 현재 제공업체의 기본 모델 가져오기 (새로운 방식)
        selected_model_key = settings_manager.get_default_model_for_provider(new_selected_provider_name)

        # 기본 모델이 없거나 유효하지 않은 경우 첫 번째 모델로 설정
        if selected_model_key not in model_keys:
            selected_model_key = model_keys[0] if model_keys else None
            if selected_model_key:
                settings_manager.set_default_model_for_provider(new_selected_provider_name, selected_model_key)

        model_idx = model_keys.index(selected_model_key) if selected_model_key and selected_model_key in model_keys else 0

        new_selected_model_key = st.selectbox(
            "🧠 모델 선택",
            model_keys,
            index=model_idx,
            format_func=lambda k: models_dict[k].display_name if k in models_dict else "알 수 없음",
            key="main_ui_model_selector",
            help=models_dict[selected_model_key].description if selected_model_key and selected_model_key in models_dict else "모델 설명을 보려면 선택하세요."
        )
        
        # 모델이 변경된 경우 해당 제공업체의 기본 모델로 저장
        if new_selected_model_key != selected_model_key:
            settings_manager.set_default_model_for_provider(new_selected_provider_name, new_selected_model_key)
            st.rerun()

        # 모델 정보 표시
        if new_selected_model_key and new_selected_model_key in models_dict:
            cfg = models_dict[new_selected_model_key]
            with st.expander(f"모델 정보: {cfg.display_name}", expanded=False):
                st.markdown(f"**API ID:** `{cfg.model_name}`")
                st.markdown(f"**최대 토큰:** {cfg.max_tokens:,}")
                st.markdown(f"**스트리밍:** {'✅' if cfg.supports_streaming else '❌'}  "
                           f"**함수호출:** {'✅' if cfg.supports_functions else '❌'}  "
                           f"**비전:** {'✅' if cfg.supports_vision else '❌'}")
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
            0.0, 2.0,
            settings_manager.get("defaults.temperature", 0.7),
            0.05,
            key="param_temp_slider_sidebar_config",
            help="창의성 조절. 높을수록 다양, 낮을수록 일관적."
        )
        
        if temp != settings_manager.get("defaults.temperature"):
            settings_manager.set("defaults.temperature", temp)

        # Max Tokens
        max_tokens = st.number_input(
            "최대 토큰 (응답 길이)",
            100, 100000,
            settings_manager.get("defaults.max_tokens", 4096),
            100,
            key="param_max_tokens_input_sidebar_config",
            help="AI 응답의 최대 길이."
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
            "loading": "⏳"
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
    def render_keyboard_handler():
        """전역 키보드 단축키 핸들러"""
        st.markdown("""
        <script>
        // 키보드 이벤트 리스너 (전역)
        document.addEventListener('keydown', function(event) {
            // Streamlit의 input 요소들에서는 단축키 비활성화
            const activeElement = document.activeElement;
            const isInputActive = activeElement && (
                activeElement.tagName === 'INPUT' || 
                activeElement.tagName === 'TEXTAREA' ||
                activeElement.contentEditable === 'true'
            );
            
            // 채팅 입력창에서는 Enter, Shift+Enter만 허용
            if (isInputActive && activeElement.getAttribute('data-testid') === 'stChatInput') {
                if (event.key === 'Enter') {
                    if (event.shiftKey) {
                        // Shift + Enter: 줄바꿈 (기본 동작)
                        return;
                    } else {
                        // Enter: 메시지 전송 (기본 동작)
                        return;
                    }
                }
            }
            
            // 다른 입력 요소에서는 모든 단축키 비활성화
            if (isInputActive) {
                return;
            }
            
            // 키 조합 확인
            const key = event.key.toLowerCase();
            const ctrl = event.ctrlKey || event.metaKey; // Mac의 Cmd 키도 지원
            const shift = event.shiftKey;
            
            // 단축키 매핑
            if (ctrl && key === 'n') {
                event.preventDefault();
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'new_chat'}, '*');
            }
            else if (ctrl && key === 's') {
                event.preventDefault();
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'save_favorite'}, '*');
            }
            else if (ctrl && key === 'f') {
                event.preventDefault();
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'search_chat'}, '*');
            }
            else if (ctrl && key === 'd') {
                event.preventDefault();
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'debug_page'}, '*');
            }
            else if (ctrl && key === ',') {
                event.preventDefault();
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'settings_page'}, '*');
            }
            else if (ctrl && key === 'e') {
                event.preventDefault();
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'edit_last_message'}, '*');
            }
            else if (key === 'escape') {
                event.preventDefault();
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'cancel_action'}, '*');
            }
        });
        
        // 단축키 도움말 토글 (F1 또는 ?)
        document.addEventListener('keydown', function(event) {
            if (event.key === 'F1' || event.key === '?') {
                event.preventDefault();
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'show_shortcuts_help'}, '*');
            }
        });
        </script>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_shortcuts_help():
        """단축키 도움말 표시"""
        import platform
        
        # 운영체제에 따른 수식키 표시
        modifier_key = "Cmd" if platform.system() == "Darwin" else "Ctrl"
        
        with st.expander("⌨️ 키보드 단축키", expanded=False):
            st.markdown(f"""
            ### 📝 채팅 단축키
            - **Enter**: 메시지 전송
            - **Shift + Enter**: 줄바꿈
            - **{modifier_key} + E**: 마지막 메시지 편집
            
            ### ⚡ 빠른 액션
            - **{modifier_key} + N**: 새 채팅 시작
            - **{modifier_key} + S**: 현재 응답 즐겨찾기 저장
            - **{modifier_key} + F**: 채팅 내 검색
            
            ### 🛠️ 페이지 이동
            - **{modifier_key} + D**: 디버그 페이지
            - **{modifier_key} + ,**: 설정 페이지
            
            ### 🔧 기타
            - **ESC**: 현재 작업 취소
            - **F1 또는 ?**: 이 도움말 토글
            
            ---
            💡 **팁**: 텍스트 입력 중일 때는 단축키가 비활성화됩니다.
            
            🍎 **Mac 사용자**: Ctrl 대신 Cmd 키를 사용하세요!
            """)

    @staticmethod 
    def handle_keyboard_shortcut(shortcut_action: str, app_instance):
        """키보드 단축키 액션 처리"""
        if not shortcut_action:
            return False
        
        import platform
        modifier_key = "Cmd" if platform.system() == "Darwin" else "Ctrl"
            
        try:
            if shortcut_action == 'new_chat':
                # 새 채팅 시작
                app_instance._create_and_set_new_session()
                st.session_state.pending_toast = (f"새 채팅을 시작했습니다! ({modifier_key}+N)", "✨")
                return True
                
            elif shortcut_action == 'save_favorite':
                # 현재 응답 즐겨찾기 저장 (구현 예정)
                st.session_state.pending_toast = (f"즐겨찾기 기능은 곧 추가될 예정입니다. ({modifier_key}+S)", "🔖")
                return True
                
            elif shortcut_action == 'search_chat':
                # 채팅 검색 (구현 예정)
                st.session_state.pending_toast = (f"검색 기능은 곧 추가될 예정입니다. ({modifier_key}+F)", "🔍")
                return True
                
            elif shortcut_action == 'debug_page':
                # 디버그 페이지로 이동
                st.session_state.show_debug_page = True
                st.session_state.show_settings_page = False
                st.session_state.show_artifacts_page = False
                return True
                
            elif shortcut_action == 'settings_page':
                # 설정 페이지로 이동
                st.session_state.show_settings_page = True
                st.session_state.show_debug_page = False
                st.session_state.show_artifacts_page = False
                return True
                
            elif shortcut_action == 'edit_last_message':
                # 마지막 메시지 편집
                current_session = st.session_state.get("current_session")
                if current_session and current_session.messages:
                    # 마지막 사용자 메시지 찾기
                    for i in range(len(current_session.messages) - 1, -1, -1):
                        if current_session.messages[i]["role"] == "user":
                            msg_key = f"msg_{current_session.id}_{i}"
                            st.session_state.editing_message_key = msg_key
                            
                            # 편집할 텍스트 준비
                            content = current_session.messages[i]["content"]
                            if isinstance(content, str):
                                st.session_state.edit_text_content = content
                            elif isinstance(content, list):
                                text_to_edit = ""
                                for part in content:
                                    if part.get("type") == "text":
                                        text_to_edit = part["text"]
                                        break
                                st.session_state.edit_text_content = text_to_edit
                            else:
                                st.session_state.edit_text_content = ""
                            
                            st.session_state.pending_toast = (f"마지막 메시지 편집 모드가 활성화되었습니다. ({modifier_key}+E)", "✏️")
                            return True
                            
                st.session_state.pending_toast = ("편집할 사용자 메시지가 없습니다.", "⚠️")
                return True
                
            elif shortcut_action == 'cancel_action':
                # 현재 작업 취소
                if st.session_state.get("editing_message_key"):
                    st.session_state.editing_message_key = None
                    st.session_state.pending_toast = ("편집을 취소했습니다. (ESC)", "❌")
                    return True
                else:
                    # 페이지를 메인으로 돌리기
                    st.session_state.show_settings_page = False
                    st.session_state.show_debug_page = False
                    st.session_state.show_artifacts_page = False
                    return True
                    
            elif shortcut_action == 'show_shortcuts_help':
                # 도움말 표시 토글
                current_state = st.session_state.get("show_shortcuts_help", False)
                st.session_state.show_shortcuts_help = not current_state
                return True
                
        except Exception as e:
            st.session_state.pending_toast = (f"단축키 처리 중 오류: {e}", "❌")
            logger.error(f"Error handling keyboard shortcut '{shortcut_action}': {e}")
            
        return False