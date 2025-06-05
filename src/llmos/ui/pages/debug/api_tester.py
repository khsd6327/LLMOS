# ted-os-project/src/llmos/ui/pages/debug/api_tester.py
# src/llmos/ui/pages/debug/api_tester.py
"""
LLM OS - API 테스트 및 진단 담당 모듈
"""

import logging
import sys
import streamlit as st

from ....managers.model_manager import EnhancedModelManager

logger = logging.getLogger(__name__)


class ApiTester:
    """API 테스트 및 진단 전담 클래스"""

    def __init__(self, model_manager: EnhancedModelManager):
        self.model_manager = model_manager

    def render_test_section(self):
        """테스트 섹션"""
        st.subheader("시스템 테스트")

        # API 연결 테스트
        st.subheader("API 연결 테스트")

        available_providers = self.model_manager.get_available_providers()

        if not available_providers:
            st.warning("사용 가능한 AI 제공업체가 없습니다.")
            return

        selected_provider = st.selectbox(
            "테스트할 제공업체",
            [p.name for p in available_providers],
            key="test_provider_selector",
        )

        if st.button("API 연결 테스트", key="test_api_connection_btn"):
            provider_enum = next(
                p for p in available_providers if p.name == selected_provider
            )

            try:
                with st.spinner(f"{selected_provider} API 테스트 중..."):
                    test_messages = [
                        {"role": "user", "content": "안녕하세요! 연결 테스트입니다."}
                    ]

                    response, usage = self.model_manager.generate(
                        test_messages,
                        provider_display_name=provider_enum.name.capitalize(),
                        max_tokens=50,
                        temperature=0.1,
                    )

                    st.success(f"✅ {selected_provider} API 연결 성공!")
                    st.text(f"응답: {response[:100]}...")

                    if usage:
                        st.text(f"토큰 사용량: {usage.total_tokens}")
                        st.text(f"비용: ${usage.cost_usd:.6f}")

            except Exception as e:
                st.error(f"❌ {selected_provider} API 테스트 실패: {str(e)}")
                logger.error(f"API test failed for {selected_provider}: {e}", exc_info=True)

        # 스트리밍 테스트
        if st.button("스트리밍 테스트", key="test_streaming_btn"):
            try:
                test_messages = [
                    {"role": "user", "content": "1부터 10까지 세어주세요."}
                ]

                st.info("스트리밍 테스트 시작...")

                with st.empty() as placeholder:
                    accumulated_text = ""
                    final_usage = None
                    chunk_count = 0

                    # 현재 선택된 테스트 제공업체 사용
                    selected_test_provider = st.session_state.get(
                        "test_provider_selector", available_providers[0].name
                    )

                    try:
                        for chunk, usage in self.model_manager.stream_generate(
                            test_messages,
                            provider_display_name=selected_test_provider,
                            max_tokens=100,
                        ):
                            try:
                                # chunk가 None이거나 빈 문자열인지 확인
                                if chunk is None:
                                    continue

                                if not isinstance(chunk, str):
                                    continue

                                if not chunk.strip():
                                    continue

                                accumulated_text = chunk
                                chunk_count += 1

                                placeholder.text(
                                    f"스트리밍 응답 (청크 {chunk_count}개): {accumulated_text}"
                                )

                                if usage:
                                    final_usage = usage

                            except Exception as chunk_error:
                                logger.warning(f"Chunk processing error: {chunk_error}")
                                continue

                        # 최종 결과 표시
                        if accumulated_text.strip():
                            success_msg = (
                                f"✅ 스트리밍 테스트 완료! 총 {chunk_count}개 청크 수신"
                            )
                            if final_usage:
                                success_msg += f" | 토큰: {final_usage.total_tokens}"
                            st.success(success_msg)
                        else:
                            st.warning(
                                "⚠️ 스트리밍 테스트 완료되었지만 응답이 비어있습니다."
                            )

                    except Exception as stream_error:
                        st.error(f"❌ 스트리밍 테스트 실패: {str(stream_error)}")
                        logger.error(f"Streaming test failed: {stream_error}", exc_info=True)

            except Exception as e:
                st.error(f"❌ 스트리밍 테스트 초기화 실패: {str(e)}")
                logger.error(f"Streaming test initialization failed: {e}", exc_info=True)

        # Streamlit 세션 상태
        if st.button("Streamlit 세션 상태 보기", key="view_session_state_btn"):
            st.session_state.show_session_state = not st.session_state.get(
                "show_session_state", False
            )

        if st.session_state.get("show_session_state"):
            with st.expander("Streamlit 세션 상태", expanded=True):
                # 민감한 정보 제외하고 표시
                safe_state = {}
                for key, value in st.session_state.items():
                    if (
                        isinstance(value, (str, int, float, bool, list, dict))
                        and len(str(value)) < 1000
                    ):
                        safe_state[key] = value
                    else:
                        safe_state[key] = (
                            f"<{type(value).__name__}> (크기: {sys.getsizeof(value)} bytes)"
                        )

                st.json(safe_state)