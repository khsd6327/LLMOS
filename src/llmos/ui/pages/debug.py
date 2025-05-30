# src/llmos/ui/pages/debug.py
"""
LLM OS - 디버그 페이지
"""

import importlib.metadata
import json
import logging
import platform
import sys
from datetime import datetime
from typing import Dict, Any, List

import streamlit as st

from ...managers.settings import SettingsManager
from ...managers.chat_sessions import ChatSessionManager
from ...managers.model_manager import EnhancedModelManager
from ...managers.usage_tracker import UsageTracker
from ...ui.components import EnhancedUI
from ...utils.logging_handler import get_log_handler
from ...core.config import APP_VERSION, APP_NAME

logger = logging.getLogger(__name__)


class DebugPage:
    """디버그 페이지 클래스"""

    def __init__(
        self,
        settings_manager: SettingsManager,
        chat_manager: ChatSessionManager,
        model_manager: EnhancedModelManager,
        usage_tracker: UsageTracker,
        ui: EnhancedUI,
    ):
        self.settings = settings_manager
        self.chat_manager = chat_manager
        self.model_manager = model_manager
        self.usage_tracker = usage_tracker
        self.ui = ui

    def render(self):
        """디버그 페이지 렌더링"""
        st.header("🐛 디버그 및 개발자 정보")

        # 뒤로가기 버튼
        if st.button("⬅️ 채팅으로 돌아가기", key="back_from_debug_page_btn"):
            st.session_state.show_debug_page = False
            st.rerun()

        # 탭으로 섹션 분리
        tabs = st.tabs(
            ["🔍 시스템 정보", "📋 로그", "⚙️ 설정", "💬 세션", "📊 성능", "🧪 테스트"]
        )

        with tabs[0]:
            self._render_system_info_section()

        with tabs[1]:
            self._render_logs_section()

        with tabs[2]:
            self._render_settings_section()

        with tabs[3]:
            self._render_sessions_section()

        with tabs[4]:
            self._render_performance_section()

        with tabs[5]:
            self._render_test_section()

    def _render_system_info_section(self):
        """시스템 정보 섹션"""
        st.subheader("시스템 정보")

        # 애플리케이션 정보
        st.subheader("애플리케이션")

        app_info = {
            "이름": APP_NAME,
            "버전": APP_VERSION,
            "시작 시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        for key, value in app_info.items():
            st.text(f"{key}: {value}")

        # 시스템 환경
        st.subheader("시스템 환경")

        system_info = {
            "운영체제": platform.platform(),
            "Python 버전": sys.version.split()[0],
            "아키텍처": platform.architecture()[0],
            "프로세서": platform.processor() or "Unknown",
            "호스트명": platform.node(),
        }

        for key, value in system_info.items():
            st.text(f"{key}: {value}")

        # 경로 정보
        st.subheader("경로 정보")

        paths = {
            "설정 파일": str(self.settings.config_file),
            "환경 변수 파일": str(self.settings.env_file),
            "채팅 세션": self.settings.get("paths.chat_sessions"),
            "아티팩트": self.settings.get("paths.artifacts"),
            "사용량 추적": self.settings.get("paths.usage_tracking"),
        }

        for key, value in paths.items():
            st.text(f"{key}: {value}")

        # 라이브러리 버전
        st.subheader("주요 라이브러리 버전")

        libraries = [
            "streamlit",
            "openai",
            "anthropic",
            "google-generativeai",
            "tiktoken",
            "Pillow",
            "python-dotenv",
        ]

        lib_versions = {}
        for lib in libraries:
            try:
                version = importlib.metadata.version(lib)
                lib_versions[lib] = version
            except importlib.metadata.PackageNotFoundError:
                lib_versions[lib] = "미설치"

        # 테이블로 표시
        import pandas as pd

        df = pd.DataFrame(list(lib_versions.items()), columns=["라이브러리", "버전"])
        st.dataframe(df, use_container_width=True)

    def _render_logs_section(self):
        """로그 섹션"""
        st.subheader("애플리케이션 로그")

        log_handler = get_log_handler()

        # 로그 컨트롤
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            log_count = st.number_input(
                "표시할 로그 수",
                min_value=10,
                max_value=500,
                value=50,
                key="log_count_input",
            )

        with col2:
            log_level_filter = st.selectbox(
                "레벨 필터",
                ["전체", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                key="log_level_filter",
            )

        with col3:
            if st.button("로그 새로고침", key="refresh_logs_btn"):
                st.rerun()

        with col4:
            if st.button("로그 지우기", key="clear_logs_btn"):
                log_handler.clear_logs()
                st.success("로그가 삭제되었습니다.")
                st.rerun()

        # 로그 검색
        log_search = st.text_input(
            "로그 검색",
            placeholder="검색할 키워드를 입력하세요...",
            key="log_search_input",
        )

        # 로그 가져오기
        if log_level_filter == "전체":
            logs = log_handler.get_recent_logs(log_count)
        else:
            logs = log_handler.get_logs_by_level(log_level_filter)[-log_count:]

        # 검색 필터 적용
        if log_search:
            logs = log_handler.search_logs(log_search)
            logs = logs[-log_count:]

        # 로그 표시
        if logs:
            st.info(f"{len(logs)}개의 로그 항목")

            # 역순으로 표시 (최신이 위에)
            log_text = "\n".join(reversed(logs))

            st.text_area(
                "로그 내용", value=log_text, height=400, key="logs_display_area"
            )

            # 다운로드 버튼
            log_filename = f"llmos_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button(
                "로그 다운로드",
                data=log_text,
                file_name=log_filename,
                mime="text/plain",
                key="download_logs_btn",
            )
        else:
            st.info("표시할 로그가 없습니다.")

    def _render_settings_section(self):
        """설정 섹션"""
        st.subheader("애플리케이션 설정")

        # 설정 검증
        validation_result = self.model_manager.validate_configuration()

        # 상태 표시
        if validation_result["valid"]:
            st.success("✅ 설정이 올바릅니다.")
        else:
            st.error("❌ 설정에 문제가 있습니다.")

            for error in validation_result["errors"]:
                st.error(f"• {error}")

        for warning in validation_result["warnings"]:
            st.warning(f"⚠️ {warning}")

        # 제공업체 상태
        st.subheader("AI 제공업체 상태")

        for provider, status in validation_result["provider_status"].items():
            with st.expander(f"{provider.upper()}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**상태**")
                    st.write(f"API 키: {'✅' if status['has_api_key'] else '❌'}")
                    st.write(
                        f"인터페이스: {'✅' if status['interface_initialized'] else '❌'}"
                    )

                with col2:
                    st.write("**정보**")
                    st.write(f"사용 가능한 모델: {status['available_models']}개")

                    # 인터페이스 기능
                    if status["interface_initialized"]:
                        interface = self.model_manager.get_interface(
                            next(
                                p
                                for p in self.model_manager.get_available_providers()
                                if p.value == provider
                            )
                        )
                        if interface:
                            features = interface.get_supported_features()
                            st.write("**지원 기능**")
                            for feature, supported in features.items():
                                st.write(f"- {feature}: {'✅' if supported else '❌'}")

        # 전체 설정 보기
        if st.button("전체 설정 보기 (JSON)", key="view_full_settings_btn"):
            st.session_state.show_full_settings = not st.session_state.get(
                "show_full_settings", False
            )

        if st.session_state.get("show_full_settings"):
            with st.expander("전체 설정 (settings.json 내용)", expanded=True):
                settings_data = self.settings.export_settings()
                st.json(settings_data)

    def _render_sessions_section(self):
        """세션 섹션"""
        st.subheader("채팅 세션 정보")

        # 세션 통계
        session_stats = self.chat_manager.get_session_statistics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("총 세션", session_stats["total_sessions"])

        with col2:
            st.metric("총 메시지", session_stats["total_messages"])

        with col3:
            avg_messages = session_stats.get("avg_messages_per_session", 0)
            st.metric("평균 메시지/세션", f"{avg_messages:.1f}")

        with col4:
            if st.button("빈 세션 정리", key="cleanup_empty_sessions_btn"):
                deleted = self.chat_manager.cleanup_empty_sessions()
                st.success(f"{deleted}개의 빈 세션을 정리했습니다.")
                st.rerun()

        # 현재 세션 상세 정보
        current_session = st.session_state.get("current_session")
        if current_session:
            st.subheader("현재 세션 상세")

            with st.expander(f"세션: {current_session.title}", expanded=False):
                session_info = {
                    "ID": current_session.id,
                    "제목": current_session.title,
                    "메시지 수": len(current_session.messages),
                    "생성일": current_session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "수정일": current_session.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                }

                for key, value in session_info.items():
                    st.text(f"{key}: {value}")

                # 메시지 분석
                if current_session.messages:
                    user_msgs = sum(
                        1 for m in current_session.messages if m["role"] == "user"
                    )
                    assistant_msgs = sum(
                        1 for m in current_session.messages if m["role"] == "assistant"
                    )

                    st.write(f"사용자 메시지: {user_msgs}개")
                    st.write(f"AI 응답: {assistant_msgs}개")

        # 전체 세션 목록
        st.subheader("전체 세션 목록")

        all_sessions = self.chat_manager.get_all_sessions()
        if all_sessions:
            session_data = []
            for session in all_sessions[:20]:  # 최대 20개만 표시
                session_data.append(
                    {
                        "ID": session.id[:8] + "...",
                        "제목": session.title[:30]
                        + ("..." if len(session.title) > 30 else ""),
                        "메시지": len(session.messages),
                        "수정일": session.updated_at.strftime("%Y-%m-%d %H:%M"),
                    }
                )

            import pandas as pd

            df = pd.DataFrame(session_data)
            st.dataframe(df, use_container_width=True)

            if len(all_sessions) > 20:
                st.info(f"+ {len(all_sessions) - 20}개 더 있음")
        else:
            st.info("저장된 세션이 없습니다.")

    def _render_performance_section(self):
        """성능 섹션"""
        st.subheader("성능 정보")

        # 사용량 통계
        usage_stats = {
            "오늘": self.usage_tracker.get_today_usage_from_summary(),
            "주간": self.usage_tracker.get_weekly_usage(),
            "월간": self.usage_tracker.get_monthly_usage(),
        }

        # 메트릭 표시
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("오늘")
            today = usage_stats["오늘"]
            st.metric("요청", f"{today['total_requests']:,}")
            st.metric("토큰", f"{today['total_tokens']:,}")
            st.metric("비용", f"${today['total_cost']:.4f}")

        with col2:
            st.subheader("이번 주")
            weekly = usage_stats["주간"]
            st.metric("요청", f"{weekly['total_requests']:,}")
            st.metric("토큰", f"{weekly['total_tokens']:,}")
            st.metric("비용", f"${weekly['total_cost']:.4f}")

        with col3:
            st.subheader("이번 달")
            monthly = usage_stats["월간"]
            st.metric("요청", f"{monthly['total_requests']:,}")
            st.metric("토큰", f"{monthly['total_tokens']:,}")
            st.metric("비용", f"${monthly['total_cost']:.4f}")

        # 모델별 사용량
        st.subheader("모델별 사용량 (최근 30일)")

        model_usage = self.usage_tracker.get_usage_by_model(30)
        if model_usage:
            model_data = []
            for model, stats in model_usage.items():
                model_data.append(
                    {
                        "모델": model,
                        "요청": stats["requests"],
                        "토큰": f"{stats['tokens']:,}",
                        "비용": f"${stats['cost']:.4f}",
                    }
                )

            import pandas as pd

            df = pd.DataFrame(model_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("모델 사용량 데이터가 없습니다.")

        # 메모리 사용량 (참고용)
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            st.subheader("메모리 사용량")
            st.text(f"RSS: {memory_info.rss / 1024 / 1024:.1f} MB")
            st.text(f"VMS: {memory_info.vms / 1024 / 1024:.1f} MB")

        except ImportError:
            st.info("메모리 정보를 보려면 psutil 패키지를 설치하세요.")

    def _render_test_section(self):
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

        # 스트리밍 테스트
        if st.button("스트리밍 테스트", key="test_streaming_btn"):
            try:
                test_messages = [
                    {"role": "user", "content": "1부터 10까지 세어주세요."}
                ]

                st.info(
                    "스트리밍 테스트 시작..."
                )  # ← placeholder.info가 아니라 st.info

                with st.empty() as placeholder:
                    accumulated_text = ""
                    final_usage = None
                    chunk_count = 0

                    # 현재 선택된 테스트 제공업체 사용
                    selected_test_provider = st.session_state.get(
                        "test_provider_selector", available_providers[0].name
                    )

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
                            continue

                    # 최종 결과 표시
                    if accumulated_text.strip():
                        success_msg = (
                            f"✅ 스트리밍 테스트 완료! 총 {chunk_count}개 청크 수신"
                        )
                        if final_usage:
                            success_msg += f" | 토큰: {final_usage.total_tokens}"
                        st.success(
                            success_msg
                        )  # ← placeholder.success가 아니라 st.success
                    else:
                        st.warning(
                            "⚠️ 스트리밍 테스트 완료되었지만 응답이 비어있습니다."
                        )

            except Exception as e:
                st.error(f"❌ 스트리밍 테스트 실패: {str(e)}")

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
