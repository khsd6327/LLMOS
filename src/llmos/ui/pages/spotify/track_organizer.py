# src/llmos/ui/pages/spotify/track_organizer.py
"""
LLM OS - Spotify Top 트랙 정리 담당 모듈
"""

import logging
import threading
import traceback

import streamlit as st

from ....managers.spotify_manager import SpotifyManager
from ....models.enums import SpotifyTimeRange

logger = logging.getLogger(__name__)


class TrackOrganizer:
    """Top 트랙 정리 전담 클래스"""

    def __init__(self, spotify_manager: SpotifyManager):
        self.spotify_manager = spotify_manager

    def render_top_tracks_organizer(self):
        """Top 트랙 정리 UI"""
        st.markdown("### 🎯 Top 트랙 플레이리스트 정리")
        st.markdown("자주 듣는 곡들을 자동으로 플레이리스트로 정리합니다.")
        
        # 플레이리스트 목록 가져오기
        playlists = self.spotify_manager.get_user_playlists()
        playlist_options = {p.name: p.id for p in playlists}
        playlist_names = ["새 플레이리스트 생성"] + list(playlist_options.keys())
        
        # 정리 옵션
        st.markdown("#### 정리 옵션 선택")
        
        tasks = []
        
        # 절대적 최애곡
        col1, col2 = st.columns([1, 2])
        with col1:
            enable_long = st.checkbox("절대적 최애곡", value=True, key="top_long")
        with col2:
            if enable_long:
                long_playlist = st.selectbox(
                    "플레이리스트",
                    playlist_names,
                    key="top_long_playlist"
                )
                if long_playlist != "새 플레이리스트 생성":
                    tasks.append({
                        'type': SpotifyTimeRange.LONG_TERM.value,
                        'playlist_id': playlist_options.get(long_playlist),
                        'playlist_name': long_playlist,
                        'create_new': False
                    })
                else:
                    new_name = st.text_input("새 플레이리스트 이름", value="절대적 최애곡", key="top_long_new")
                    tasks.append({
                        'type': SpotifyTimeRange.LONG_TERM.value,
                        'playlist_id': None,
                        'playlist_name': new_name,
                        'create_new': True
                    })
        
        # 자주 듣는 곡
        col1, col2 = st.columns([1, 2])
        with col1:
            enable_frequent = st.checkbox("자주 듣는 곡", value=True, key="top_frequent")
        with col2:
            if enable_frequent:
                frequent_playlist = st.selectbox(
                    "플레이리스트",
                    playlist_names,
                    key="top_frequent_playlist"
                )
                if frequent_playlist != "새 플레이리스트 생성":
                    tasks.append({
                        'type': 'frequent',
                        'playlist_id': playlist_options.get(frequent_playlist),
                        'playlist_name': frequent_playlist,
                        'create_new': False
                    })
                else:
                    new_name = st.text_input("새 플레이리스트 이름", value="자주 듣는 곡", key="top_frequent_new")
                    tasks.append({
                        'type': 'frequent',
                        'playlist_id': None,
                        'playlist_name': new_name,
                        'create_new': True
                    })
        
        # 요즘 최고야
        col1, col2 = st.columns([1, 2])
        with col1:
            enable_short = st.checkbox("요즘 최고야!", value=True, key="top_short")
        with col2:
            if enable_short:
                short_playlist = st.selectbox(
                    "플레이리스트",
                    playlist_names,
                    key="top_short_playlist"
                )
                if short_playlist != "새 플레이리스트 생성":
                    tasks.append({
                        'type': SpotifyTimeRange.SHORT_TERM.value,
                        'playlist_id': playlist_options.get(short_playlist),
                        'playlist_name': short_playlist,
                        'create_new': False
                    })
                else:
                    new_name = st.text_input("새 플레이리스트 이름", value="요즘 최고야", key="top_short_new")
                    tasks.append({
                        'type': SpotifyTimeRange.SHORT_TERM.value,
                        'playlist_id': None,
                        'playlist_name': new_name,
                        'create_new': True
                    })
        
        clear_existing = st.checkbox("기존 곡 삭제 후 새로 채우기", value=True)
        
        # 작업 완료 상태를 session_state로 관리하기 위한 키
        TOP_TRACKS_ORGANIZER_DONE_KEY = "top_tracks_organizer_done"
        TOP_TRACKS_ORGANIZER_MESSAGE_KEY = "top_tracks_organizer_message"

        # 작업 완료 메시지가 있으면 표시
        if st.session_state.get(TOP_TRACKS_ORGANIZER_DONE_KEY):
            st.success(st.session_state.get(TOP_TRACKS_ORGANIZER_MESSAGE_KEY, "✅ Top 트랙 정리 완료!"))
            # 메시지 표시 후 상태 초기화
            st.session_state[TOP_TRACKS_ORGANIZER_DONE_KEY] = False
            st.session_state[TOP_TRACKS_ORGANIZER_MESSAGE_KEY] = ""

        if st.button("🚀 정리 시작", disabled=not tasks, use_container_width=True):
            progress_container = st.container() # 진행 메시지는 여기에 계속 표시됩니다.
            
            # 버튼 클릭 시 이전 완료 상태 초기화
            st.session_state[TOP_TRACKS_ORGANIZER_DONE_KEY] = False
            st.session_state[TOP_TRACKS_ORGANIZER_MESSAGE_KEY] = ""

            def progress_callback(message):
                logger.info(f"[Top 트랙 정리 진행] {message}") 
            
            def process_thread():
                try:
                    self.spotify_manager.organize_top_tracks(tasks, clear_existing, progress_callback)
                    # 작업 완료 후 session_state에 상태 저장
                    st.session_state[TOP_TRACKS_ORGANIZER_MESSAGE_KEY] = "✅ Top 트랙 정리 완료!"
                except Exception as e:
                    # --- 아래 로깅 부분을 수정합니다 ---
                    error_type = type(e).__name__
                    error_msg = str(e)
                    full_traceback = traceback.format_exc()
                    logger.error(f"Top 트랙 정리 중 오류 발생: TYPE={error_type}, MSG='{error_msg}'\nTRACEBACK:\n{full_traceback}")
                    st.session_state[TOP_TRACKS_ORGANIZER_MESSAGE_KEY] = f"❌ Top 트랙 정리 중 오류 발생: {error_type} - '{error_msg}'"
                    # --- 여기까지 수정 ---
                finally:
                    st.session_state[TOP_TRACKS_ORGANIZER_DONE_KEY] = True
                    st.rerun()
            
            thread = threading.Thread(target=process_thread)
            thread.start()
            st.info("Top 트랙 정리 작업이 백그라운드에서 시작되었습니다. 잠시 후 결과가 표시됩니다.")