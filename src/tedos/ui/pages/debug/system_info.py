# ted-os-project/src/tedos/ui/pages/debug/system_info.py
"""
Ted OS - 시스템 정보 렌더링 담당 모듈
"""

import importlib.metadata
import platform
import sys
from datetime import datetime
import streamlit as st

from ....core.config import APP_VERSION, APP_NAME
from ....managers.settings import SettingsManager


class SystemInfoRenderer:
    """시스템 정보 렌더링 전담 클래스"""

    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager

    def render_system_info_section(self):
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