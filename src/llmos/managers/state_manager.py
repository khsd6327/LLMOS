# src/llmos/managers/state_manager.py
"""
LLM OS - 상태 관리 매니저
이 모듈은 Streamlit의 session_state를 관리하는 중앙 클래스를 제공합니다.
이 클래스는 애플리케이션의 상태를 초기화하고, 상태 값을 설정 및 가져오는 기능을 제공합니다.
이 모듈은 애플리케이션의 상태를 중앙에서 관리하여, 다른 모듈에서 일관된 방식으로 상태에 접근할 수 있도록 합니다.
"""

import streamlit as st
from typing import Any

class StateManager:
    """
    Streamlit의 session_state를 관리하는 중앙 클래스.
    모든 상태 관련 접근은 이 클래스를 통해 이루어져야 합니다.
    """
    def __init__(self, session_state):
        # 'state_manager_initialized' 키를 사용하여 StateManager 자체의 초기화 여부 확인
        if 'state_manager_initialized' not in session_state:
            session_state['state_manager_initialized'] = True
            self._state = session_state
            self.initialize_default_states() # 모든 상태 초기화 호출
        else:
            self._state = session_state

    def initialize_default_states(self):
        """
        애플리케이션에서 사용될 모든 초기 상태 값을 정의합니다.
        기존 app.py의 _initialize_session_state에 있던 값들을 이곳으로 옮겼습니다.
        """
        defaults = {
            # 현재 세션 정보
            "current_session_id": None,
            "current_session": None, # ChatSession 객체가 될 예정
            # 이미지 업로드 상태
            "chat_uploaded_image_bytes": None,
            "chat_uploaded_image_name": None,
            "last_uploaded_filename_integrated": None,
            # 페이지 상태 (어떤 페이지를 보여줄지)
            "show_settings_page": False,
            "show_debug_page": False,
            "show_export_page": False, # 아키텍처 가이드에는 없지만, app.py에 있었음
            "show_spotify_page": False,
            "show_favorites_page": False,
            "show_api_dashboard_page": False,
            # 메시지 편집 상태
            "editing_message_key": None,
            "edit_text_content": "",
            # 애플리케이션 전체 상태
            "app_initialized": False, # 애플리케이션 로직 초기화 여부
            # UI 관련 임시 상태
            "pending_toast": None, # (메시지, 아이콘) 튜플 저장
            "show_shortcuts_help": False, # 단축키 도움말 표시 여부
            # 모델 선택 상태
            "selected_provider": None,
            "selected_model": None,
            # 스트리밍 응답 생성 중 플래그
            "generating_response": False,
            "should_stop_streaming": False,
        }

        for key, default_value in defaults.items():
            self.set_default(key, default_value)

    def get(self, key: str, default: Any = None) -> Any:
        """지정된 키의 상태 값을 가져옵니다."""
        return self._state.get(key, default)

    def set(self, key: str, value: Any):
        """상태 값을 설정합니다."""
        self._state[key] = value

    def set_default(self, key: str, value: Any):
        """키가 존재하지 않을 경우에만 기본값을 설정합니다."""
        if key not in self._state:
            self._state[key] = value

    def __getattr__(self, key: str) -> Any:
        """st.session_state.key 와 같은 형태로 접근할 수 있도록 합니다."""
        # 내부 _state 속성에 대한 접근은 __getattribute__를 통하도록 명시적 처리
        if key == '_state':
            return super().__getattribute__(key)
        try:
            return self.get(key)
        except KeyError: # 실제로 get에서 KeyError가 발생하진 않지만, 명시적으로 AttributeError 발생
            raise AttributeError(f"'StateManager' object has no attribute '{key}' (via __getattr__)")

    def __setattr__(self, key: str, value: Any):
        """st.session_state.key = value 와 같은 형태로 값을 설정할 수 있도록 합니다."""
        if key == '_state': # _state는 내부 속성이므로 직접 설정
            super().__setattr__(key, value)
        else:
            self.set(key, value)

    def __delattr__(self, key: str):
        """키를 상태에서 삭제합니다 (st.session_state에서 del 하는 것과 동일)."""
        if key in self._state:
            del self._state[key]
        else:
            raise AttributeError(f"'StateManager' object has no attribute '{key}' (via __delattr__)")

    def get_all_state(self) -> dict:
        """현재 st.session_state의 모든 내용을 복사하여 반환합니다."""
        return dict(self._state)

def get_state() -> StateManager:
    """StateManager 인스턴스를 반환하는 헬퍼 함수"""
    if 'global_state_manager' not in st.session_state:
        st.session_state.global_state_manager = StateManager(st.session_state)
    return st.session_state.global_state_manager