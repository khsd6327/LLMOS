# ted-os-project/src/tedos/ui/pages/debug/logs_viewer.py
"""
Ted OS - 로그 관리 및 표시 담당 모듈
"""

import logging
from datetime import datetime

import streamlit as st

from ....utils.logging_handler import get_log_handler

logger = logging.getLogger(__name__)


class LogsViewer:
    """로그 관리 및 표시 전담 클래스"""

    def __init__(self):
        self.log_handler = get_log_handler()

    def render_logs_section(self):
        """로그 섹션"""
        st.subheader("애플리케이션 로그")

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
                self.log_handler.clear_logs()
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
            logs = self.log_handler.get_recent_logs(log_count)
        else:
            logs = self.log_handler.get_logs_by_level(log_level_filter)[-log_count:]

        # 검색 필터 적용
        if log_search:
            logs = self.log_handler.search_logs(log_search)
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
            log_filename = f"tedos_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            st.download_button(
                "로그 다운로드",
                data=log_text,
                file_name=log_filename,
                mime="text/plain",
                key="download_logs_btn",
            )
        else:
            st.info("표시할 로그가 없습니다.")