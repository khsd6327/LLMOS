# src/llmos/ui/pages/chat.py
"""
LLM OS - 채팅 페이지
"""

import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

import streamlit as st

from ...managers.chat_sessions import ChatSessionManager
from ...managers.model_manager import EnhancedModelManager
from ...models.data_models import ChatSession, TokenUsage
from ...models.model_registry import ModelRegistry
from ...ui.components import EnhancedUI
from ...utils.helpers import detect_image_mime_type, validate_image
from ...managers.favorite_manager import FavoriteManager

logger = logging.getLogger(__name__)


class ChatPage:
    """채팅 페이지 클래스"""

    def __init__(
        self,
        chat_manager: ChatSessionManager,
        model_manager: EnhancedModelManager,
        ui: EnhancedUI,
        favorite_manager: FavoriteManager,
    ):
        self.chat_manager = chat_manager
        self.model_manager = model_manager
        self.ui = ui
        self.favorite_manager = favorite_manager

    def render(self):
        """채팅 페이지 렌더링"""
        current_session = st.session_state.get("current_session")

        if not current_session:
            self._render_no_session()
            return

        # 세션 제목 표시
        st.subheader(f"💬 {current_session.title}")

        # 채팅 메시지 렌더링
        self._render_chat_messages(current_session)

        # 채팅 입력
        user_input = self.ui.render_integrated_chat_input()
        if user_input:
            self._handle_user_input(current_session, user_input)
            st.rerun()

    def _render_no_session(self):
        """세션이 없을 때 렌더링"""
        st.info("채팅 세션을 선택하거나 새 채팅을 시작하세요.")

        if st.button("새 채팅 시작", type="primary"):
            new_session = self.chat_manager.create_session("새 채팅")
            st.session_state.current_session_id = new_session.id
            st.session_state.current_session = new_session
            st.rerun()

    def _render_chat_messages(self, session: ChatSession):
        """채팅 메시지들 렌더링"""
        for i, msg_data in enumerate(session.messages):
            msg_key = f"msg_{session.id}_{i}"
            is_last_message = i == len(session.messages) - 1

            with st.chat_message(msg_data["role"]):
                # 이미지 표시 메시지
                if msg_data.get("type") == "image_display" and isinstance(
                    msg_data["content"], bytes
                ):
                    st.image(
                        msg_data["content"],
                        caption=msg_data.get("caption", "첨부 이미지"),
                        width=250,
                    )

                # 편집 모드
                elif (
                    st.session_state.get("editing_message_key") == msg_key
                    and msg_data["role"] == "user"
                ):
                    self._render_edit_mode(session, i, msg_key)

                # 일반 메시지 표시
                else:
                    self._render_message_content(msg_data)
                    self._render_message_actions(
                        session, i, msg_key, msg_data, is_last_message
                    )

    def _render_edit_mode(self, session: ChatSession, msg_index: int, msg_key: str):
        """메시지 편집 모드 렌더링"""
        edited_text = st.text_area(
            "메시지 수정:",
            value=st.session_state.get("edit_text_content", ""),
            key=f"edit_area_main_chat_{msg_key}",
            height=100,
        )

        btn_cols = st.columns(8)

        if btn_cols[0].button("💾 저장", key=f"save_edit_main_chat_{msg_key}"):
            session.messages[msg_index]["content"] = edited_text
            self.chat_manager.update_session(session)
            st.session_state.current_session = session
            st.session_state.editing_message_key = None
            st.rerun()

        if btn_cols[1].button("❌ 취소", key=f"cancel_edit_main_chat_{msg_key}"):
            st.session_state.editing_message_key = None
            st.rerun()

    def _render_message_content(self, msg_data: Dict[str, Any]):
        """메시지 내용 렌더링"""
        content = msg_data["content"]

        if isinstance(content, str):
            st.markdown(content, unsafe_allow_html=True)
        elif isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    st.markdown(part["text"], unsafe_allow_html=True)

    def _render_message_actions(
        self,
        session: ChatSession,
        msg_index: int,
        msg_key: str,
        msg_data: Dict[str, Any],
        is_last_message: bool,
    ):
        """메시지 액션 버튼들 렌더링"""
        action_cols = st.columns([1, 1, 1, 7])

        # 사용자 메시지 편집
        if msg_data["role"] == "user":
            if action_cols[0].button(
                "✏️", key=f"edit_btn_main_chat_area_{msg_key}", help="메시지 수정"
            ):
                st.session_state.editing_message_key = msg_key

                # 편집할 텍스트 준비
                if isinstance(msg_data["content"], str):
                    st.session_state.edit_text_content = msg_data["content"]
                elif isinstance(msg_data["content"], list):
                    text_to_edit = ""
                    for part in msg_data["content"]:
                        if part.get("type") == "text":
                            text_to_edit = part["text"]
                            break
                    st.session_state.edit_text_content = text_to_edit
                else:
                    st.session_state.edit_text_content = ""

                st.rerun()

        # AI 응답 액션
        elif msg_data["role"] == "assistant":
            # 복사 버튼
            if isinstance(msg_data["content"], str):
                if action_cols[0].button(
                    "📋", key=f"copy_btn_main_chat_area_{msg_key}", help="응답 복사"
                ):
                    self._copy_to_clipboard(msg_data["content"])

            # 재시도 버튼 (마지막 메시지만)
            if is_last_message:
                if action_cols[1].button(
                    "🔄",
                    key=f"retry_btn_main_chat_area_{msg_key}",
                    help="AI 응답 재시도",
                ):
                    self._retry_last_response(session)
            
            # 즐겨찾기 버튼 (AI 응답에만)
            # msg_index는 _render_message_actions의 파라미터로 이미 존재합니다.
            if action_cols[2].button("⭐", key=f"fav_btn_{msg_key}", help="즐겨찾기에 추가/제거"):
                self._toggle_favorite_message(session, msg_data, msg_index) # msg_index 전달
                st.rerun()

    def _copy_to_clipboard(self, text: str):
        """클립보드 복사"""
        st.code(text, language=None)
        st.success("위 텍스트를 선택하여 복사하세요 (Ctrl+A, Ctrl+C).", icon="📋")
        st.session_state.pending_toast = (
            "내용이 복사 준비되었습니다 (위 박스에서 선택).",
            "📋",
        )

    def _handle_user_input(self, session: ChatSession, user_input: str):
        """사용자 입력 처리"""
        # 멀티모달 콘텐츠 준비
        user_content = self._prepare_user_content(user_input)

        # 사용자 메시지 추가
        session.messages.append({"role": "user", "content": user_content})
        self.chat_manager.update_session(session)
        st.session_state.current_session = session

        # 이미지 상태 초기화
        self._clear_uploaded_image()

        # AI 응답 생성
        self._generate_ai_response(session, user_input)

    def _prepare_user_content(
        self, text_input: str
    ) -> Union[str, List[Dict[str, Any]]]:
        """사용자 콘텐츠 준비 (텍스트 + 이미지)"""
        uploaded_image_bytes = st.session_state.get("chat_uploaded_image_bytes")
        uploaded_image_name = st.session_state.get("chat_uploaded_image_name")

        message_parts: List[Dict[str, Any]] = []

        # 이미지 처리
        if uploaded_image_bytes and uploaded_image_name:
            # 이미지 표시용 메시지 추가
            st.session_state.current_session.messages.append(
                {
                    "role": "user",
                    "type": "image_display",
                    "content": uploaded_image_bytes,
                    "caption": f"입력 이미지: {uploaded_image_name}",
                }
            )

            # API용 이미지 데이터 준비
            mime_type = detect_image_mime_type(
                uploaded_image_bytes, uploaded_image_name
            )
            base64_image = base64.b64encode(uploaded_image_bytes).decode("utf-8")

            message_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                }
            )

        # 텍스트 추가
        message_parts.append({"type": "text", "text": text_input})

        # 단일 텍스트인지 멀티모달인지 결정
        if len(message_parts) == 1 and message_parts[0]["type"] == "text":
            return text_input
        else:
            return message_parts

    def _clear_uploaded_image(self):
        """업로드된 이미지 상태 초기화"""
        st.session_state.chat_uploaded_image_bytes = None
        st.session_state.chat_uploaded_image_name = None
        st.session_state.last_uploaded_filename_integrated = None

    def _get_current_model_config(self):
        """현재 모델 설정 가져오기"""
        # 여러 소스에서 설정값 찾기 (우선순위: session_state → settings)
        provider = st.session_state.get(
            "selected_provider"
        ) or self.model_manager.settings.get("ui.selected_provider")

        # 제공업체별 기본 모델 사용 (새로운 방식)
        if provider and not st.session_state.get("selected_model"):
            model_key = self.model_manager.settings.get_default_model_for_provider(
                provider
            )
        else:
            model_key = st.session_state.get("selected_model")

        # 둘 다 없으면 기본값 사용
        if not provider or not model_key:
            # 사용 가능한 첫 번째 제공업체와 모델 사용
            available_providers = self.model_manager.get_available_providers()
            if available_providers:
                # 첫 번째 사용 가능한 제공업체 선택
                first_provider = available_providers[0]
                provider_display = first_provider.name.capitalize()

                # ModelRegistry는 이미 파일 상단에서 임포트됨 - 중복 임포트 제거
                available_models = ModelRegistry.get_models_for_provider(
                    provider_display
                )
                if available_models:
                    # 제공업체별 기본 모델 사용
                    model_key = (
                        self.model_manager.settings.get_default_model_for_provider(
                            provider_display
                        )
                    )
                    if not model_key or model_key not in available_models:
                        model_key = list(available_models.keys())[0]

                    provider = provider_display

                    # 자동 선택된 값을 session_state와 settings에 저장
                    st.session_state.selected_provider = provider
                    st.session_state.selected_model = model_key
                    self.model_manager.settings.set("ui.selected_provider", provider)
                    self.model_manager.settings.set("defaults.model", model_key)

        if not provider or not model_key:
            return None

        return ModelRegistry.get_model_config(provider, model_key)

    def _generate_ai_response(self, session: ChatSession, user_prompt: str):
        """AI 응답 생성"""
        # API 호출용 메시지 준비
        api_messages = self._prepare_api_messages(session.messages)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            usage_info: Optional[TokenUsage] = None

            try:
                # 모델 설정 확인
                model_config = self._get_current_model_config()
                if not model_config:
                    error_msg = "오류: 현재 선택된 모델 설정을 찾을 수 없습니다."
                    response_placeholder.error(error_msg)
                    full_response = error_msg
                else:
                    # 비전 모델 확인
                    if (
                        st.session_state.get("chat_uploaded_image_bytes")
                        and not model_config.supports_vision
                    ):
                        response_placeholder.warning(
                            f"'{model_config.display_name}' 모델은 이미지 입력을 지원하지 않을 수 있습니다."
                        )

                    # 응답 생성
                    if model_config.supports_streaming:
                        full_response, usage_info = self._generate_streaming_response(
                            api_messages, response_placeholder
                        )
                    else:
                        full_response, usage_info = self._generate_sync_response(
                            api_messages, response_placeholder
                        )

                    # 사용량 정보 표시
                    if usage_info:
                        self._display_usage_info(usage_info)

            except Exception as e:
                logger.error(f"Error during AI response generation: {e}", exc_info=True)
                full_response = f"오류가 발생했습니다: {e}"
                response_placeholder.error(full_response)

            # 응답을 세션에 추가
            session.messages.append({"role": "assistant", "content": full_response})

            # 자동 제목 생성
            self._auto_generate_title(session, user_prompt, full_response)

            # 세션 업데이트
            self.chat_manager.update_session(session)

    def _prepare_api_messages(
        self, messages: List[Dict[str, Any]], max_history: int = 10
    ) -> List[Dict[str, Any]]:
        """API 호출용 메시지 준비"""
        api_messages: List[Dict[str, Any]] = []
        recent_messages = messages[-max_history:]

        system_prompt: Optional[str] = None
        filtered_messages = []

        for msg in recent_messages:
            if msg["role"] == "system" and isinstance(msg["content"], str):
                system_prompt = msg["content"]
            elif msg.get("type") != "image_display":
                filtered_messages.append(msg)

        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})

        for msg in filtered_messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        return api_messages

    def _generate_streaming_response(
        self, messages, placeholder
    ) -> tuple[str, Optional[TokenUsage]]:
        """스트리밍 응답 생성"""
        full_response = ""
        final_usage = None

        stream_gen = self.model_manager.stream_generate(messages)
        for response_chunk, usage in stream_gen:
            full_response = response_chunk
            placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
            if usage:
                final_usage = usage

        placeholder.markdown(full_response, unsafe_allow_html=True)
        return full_response, final_usage

    def _generate_sync_response(
        self, messages, placeholder
    ) -> tuple[str, Optional[TokenUsage]]:
        """동기 응답 생성"""
        with placeholder.container():
            with st.spinner("AI가 응답을 생성 중입니다..."):
                response, usage = self.model_manager.generate(messages)

        placeholder.markdown(response, unsafe_allow_html=True)
        return response, usage

    def _display_usage_info(self, usage: TokenUsage):
        """사용량 정보 표시"""
        with st.expander("📊 토큰 사용량 (이번 응답)", expanded=False):
            cost_display = (
                f"${usage.cost_usd:.5f}" if usage.cost_usd > 0.000001 else "$0.00"
            )

            col_i, col_o, col_c = st.columns(3)
            col_i.metric("입력 토큰", f"{usage.input_tokens:,}")
            col_o.metric("출력 토큰", f"{usage.output_tokens:,}")
            col_c.metric("예상 비용", cost_display)

    def _auto_generate_title(
        self, session: ChatSession, user_prompt: str, ai_response: str
    ):
        """자동 제목 생성"""
        # 새 채팅이고 첫 번째 AI 응답인 경우
        if session.title.startswith("새 채팅") or session.title.startswith("첫 채팅"):
            assistant_count = sum(
                1 for m in session.messages if m["role"] == "assistant"
            )

            if (
                assistant_count == 1
                and ai_response
                and not ai_response.lower().startswith("오류")
            ):
                self._generate_chat_title(session, user_prompt, ai_response)

    def _generate_chat_title(
        self, session: ChatSession, user_prompt: str, ai_response: str
    ):
        """채팅 제목 생성 (수정된 버전)"""
        try:
            # 프롬프트 생성: 사용자의 첫 메시지를 기반으로 명확한 지시를 내립니다.
            # 이 프롬프트는 모든 AI 제공업체에 대해 일관되게 작동하도록 설계되었습니다.
            prompt_template = f"""
다음은 사용자와 AI의 첫 대화입니다. 이 대화의 핵심 주제를 나타내는 간결한 한글 제목을 15자 이내로 만들어주세요.
다른 설명이나 인사말 없이, 오직 제목 텍스트만 응답해야 합니다.

사용자 질문: "{user_prompt[:200]}"

제목:
"""

            title_messages = [{"role": "user", "content": prompt_template}]

            # ModelManager를 통해 제목 생성 요청
            # 온도(temperature)를 낮춰 일관된 결과 유도, max_tokens를 적절히 설정
            generated_title, _ = self.model_manager.generate(
                messages=title_messages,
                temperature=0.0,
                max_tokens=30,  # 한글/영문 제목 길이를 고려해 약간 여유롭게 설정
            )

            if not generated_title:
                logger.warning(
                    "AI가 제목을 생성하지 못했습니다 (빈 응답). 백업 제목을 사용합니다."
                )
                raise ValueError("Generated title is empty")

            # AI가 생성한 제목 정리
            clean_title = generated_title.strip()

            # 불필요한 접두사 및 따옴표 제거
            prefixes_to_remove = ["제목:", "Title:"]
            for prefix in prefixes_to_remove:
                if clean_title.lower().startswith(prefix.lower()):
                    clean_title = clean_title[len(prefix) :].strip()

            clean_title = clean_title.strip("\"'“”" "")

            # 최종 제목 결정
            if 1 < len(clean_title) <= 25:
                final_title = clean_title
            else:
                logger.warning(
                    f"생성된 제목 '{clean_title}'이 유효하지 않아 백업 제목을 사용합니다."
                )
                # 백업: 사용자 입력의 첫 부분 사용
                final_title = user_prompt[:20] + (
                    "..." if len(user_prompt) > 20 else ""
                )

            # 세션 제목 업데이트
            session.title = final_title
            self.chat_manager.update_session_title(session.id, final_title)
            st.session_state.pending_toast = (
                f"채팅 제목 자동 생성: {final_title}",
                "✨",
            )
            logger.info(
                f"성공적으로 채팅 제목을 생성하고 업데이트했습니다: {final_title}"
            )

        except Exception as e:
            logger.error(f"채팅 제목 자동 생성 중 오류 발생: {e}", exc_info=True)

            # 실패 시 안전한 백업 제목 사용
            safe_title = user_prompt[:20] + ("..." if len(user_prompt) > 20 else "")
            if session.title != safe_title:
                session.title = safe_title
                self.chat_manager.update_session_title(session.id, safe_title)
                logger.info(f"오류 발생으로 백업 제목을 사용합니다: {safe_title}")

    def _retry_last_response(self, session: ChatSession):
        """마지막 AI 응답 재시도"""
        if not session.messages or session.messages[-1]["role"] != "assistant":
            st.session_state.pending_toast = ("재시도할 AI 응답이 없습니다.", "⚠️")
            st.rerun()
            return

        # 마지막 AI 응답 제거
        session.messages.pop()

        # API 메시지 준비
        api_messages = self._prepare_api_messages(session.messages)

        if not api_messages or api_messages[-1]["role"] != "user":
            error_msg = "재시도를 위한 유효한 사용자 컨텍스트가 없습니다."
            session.messages.append({"role": "assistant", "content": error_msg})
            self.chat_manager.update_session(session)
            st.session_state.current_session = session
            st.session_state.pending_toast = (error_msg, "❌")
            st.rerun()
            return

        # 새 응답 생성
        try:
            response, usage = self.model_manager.generate(api_messages)
            if usage:
                logger.info(
                    f"Retry successful - Tokens: {usage.total_tokens}, Cost: ${usage.cost_usd:.5f}"
                )
        except Exception as e:
            logger.error(f"Error during retry: {e}")
            response = f"재시도 중 오류 발생: {e}"

        session.messages.append({"role": "assistant", "content": response})
        self.chat_manager.update_session(session)
        st.session_state.current_session = session

        if "오류" not in response.lower():
            st.session_state.pending_toast = ("AI 응답을 다시 생성했습니다.", "🔄")
        else:
            st.session_state.pending_toast = (
                "응답 재시도 중 오류가 발생했습니다.",
                "⚠️",
            )

        st.rerun()

    def _toggle_favorite_message(self, session: ChatSession, msg_data: Dict[str, Any], msg_idx: int):
        """
        메시지를 즐겨찾기에 추가하거나 이미 있다면 제거합니다. (현재는 추가 기능만 구현)
        """
        # FavoriteMessage에 필요한 정보 추출 및 준비
        message_content_str = ""
        if isinstance(msg_data.get("content"), str):
            message_content_str = msg_data["content"]
        elif isinstance(msg_data.get("content"), list):  # 멀티모달 메시지의 텍스트 부분 처리
            for part in msg_data["content"]:
                if part.get("type") == "text":
                    message_content_str = part["text"]
                    break
        
        # 내용이 없는 경우 즐겨찾기 방지 (예: 이미지 표시용 메시지)
        if not message_content_str and msg_data.get("type") == "image_display":
            st.toast("텍스트 내용이 없는 이미지는 즐겨찾기할 수 없습니다.", icon="⚠️")
            return
        if not message_content_str: # 일반적인 빈 메시지
            st.toast("내용이 없는 메시지는 즐겨찾기할 수 없습니다.", icon="⚠️")
            return

        # 컨텍스트 메시지 준비 (예: 현재 메시지를 포함하여 이전 N개)
        # FavoriteMessage.context_messages는 List[Dict[str, Any]] 형식 (role, content)
        context_messages_for_favorite = []
        context_window_start = max(0, msg_idx - 4) # 현재 메시지 포함 최대 5개
        for i in range(context_window_start, msg_idx + 1):
            ctx_msg = session.messages[i]
            ctx_role = ctx_msg.get("role")
            ctx_content_value = ctx_msg.get("content")
            
            ctx_content_str = ""
            if isinstance(ctx_content_value, str):
                ctx_content_str = ctx_content_value
            elif isinstance(ctx_content_value, list):
                for part in ctx_content_value:
                    if part.get("type") == "text":
                        ctx_content_str = part["text"]
                        break
            
            # 이미지 표시용 메시지는 컨텍스트에서 제외 (텍스트가 있다면 포함)
            if ctx_msg.get("type") == "image_display" and not ctx_content_str:
                continue
                
            context_messages_for_favorite.append({
                "role": ctx_role,
                "content": ctx_content_str
            })

        # 원본 메시지 생성 시간 (ChatSession의 메시지에는 타임스탬프가 없어, 임시로 현재 시간 사용 또는 다른 방법 강구 필요)
        # FavoriteMessage의 created_at은 원본 메시지의 생성 시간이지만, 현재 msg_data에 없으므로 임시 처리
        original_message_created_at = msg_data.get("timestamp", datetime.now()) # msg_data에 'timestamp'가 있다면 사용

        # 모델 정보 (AI 메시지인 경우) - 이것도 msg_data에 명시적으로 없으면 현재 선택된 모델로 임시 처리
        model_provider_enum = None
        model_name_str = None
        if msg_data["role"] == "assistant":
            # 현재 선택된 모델 정보를 가져오려고 시도 (최선은 아니지만 차선책)
            current_model_config = self._get_current_model_config() # 이 메서드가 ChatPage에 이미 존재함
            if current_model_config:
                model_provider_enum = current_model_config.provider # ModelProvider Enum 값
                model_name_str = current_model_config.model_name

        # 메시지 고유 ID (세션 내에서 메시지를 식별할 방법. 인덱스는 불안정하므로 개선 필요)
        # 우선은 인덱스를 기반으로 한 식별자 사용.
        # TODO: ChatSession의 각 message에 고유 ID (UUID)를 부여하는 것이 장기적으로 더 좋음.
        message_identifier_in_session = f"message_index_{msg_idx}"

        try:
            # TODO: 즐겨찾기 여부 확인 후 토글 로직 구현 (FavoriteManager에 is_favorited(session_id, message_id) 같은 메서드 필요)
            # 현재는 단순 추가 로직만 구현
            
            # 기존에 동일한 session_id와 message_identifier_in_session으로 추가된 즐겨찾기가 있는지 확인
            # (이 부분은 FavoriteManager에 find_by_message_origin(session_id, message_id) 같은 메서드가 필요합니다.
            #  지금은 간단하게 중복 추가될 수 있도록 둡니다. FavoriteManager가 ID로만 관리하므로, 내용은 중복될 수 있습니다.)

            self.favorite_manager.add_favorite(
                session_id=session.id,
                message_id=message_identifier_in_session,
                role=msg_data["role"],
                content=message_content_str,
                created_at=original_message_created_at, 
                model_provider=model_provider_enum,
                model_name=model_name_str,
                context_messages=context_messages_for_favorite,
                # tags와 notes는 초기에는 비워둠
            )
            st.toast("메시지를 즐겨찾기에 추가했습니다!", icon="⭐")
        except Exception as e:
            logger.error(f"즐겨찾기 추가 중 오류 발생: {e}", exc_info=True)
            st.error(f"즐겨찾기를 추가하는 중 오류가 발생했습니다: {str(e)}")