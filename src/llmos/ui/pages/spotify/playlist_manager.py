# src/llmos/ui/pages/spotify/playlist_manager.py
"""
LLM OS - Spotify 플레이리스트 관리 담당 모듈
"""

import logging

import streamlit as st

from ....managers.spotify_manager import SpotifyManager
from ....models.enums import SpotifySortKey

logger = logging.getLogger(__name__)


class PlaylistManager:
    """플레이리스트 생성 및 정렬 전담 클래스"""

    def __init__(self, spotify_manager: SpotifyManager):
        self.spotify_manager = spotify_manager

    def render_create_playlist(self):
        """새 플레이리스트 생성 UI"""
        st.markdown("### ➕ 새 플레이리스트 생성")
        
        with st.form("create_playlist_form"):
            name = st.text_input("플레이리스트 이름", key="new_playlist_name")
            description = st.text_area("설명 (선택사항)", key="new_playlist_desc")
            is_public = st.checkbox("공개 플레이리스트", key="new_playlist_public")
            
            submitted = st.form_submit_button("✨ 생성", use_container_width=True)
            
            if submitted:
                if name:
                    playlist = self.spotify_manager.create_playlist(name, is_public, description)
                    if playlist:
                        st.success(f"✅ 플레이리스트 '{playlist.name}'이(가) 생성되었습니다!")
                    else:
                        st.error("❌ 플레이리스트 생성에 실패했습니다.")
                else:
                    st.error("플레이리스트 이름을 입력해주세요.")

    def render_sort_playlist(self):
        """플레이리스트 정렬 UI"""
        st.markdown("### 🔄 플레이리스트 정렬")
        
        playlists = self.spotify_manager.get_user_playlists()
        if not playlists:
            st.warning("정렬할 플레이리스트가 없습니다.")
            return
        
        playlist_options = {p.name: p.id for p in playlists}
        
        selected_playlist = st.selectbox(
            "정렬할 플레이리스트",
            list(playlist_options.keys()),
            key="sort_playlist_select"
        )
        
        sort_options = {
            "곡 제목": SpotifySortKey.NAME,
            "아티스트": SpotifySortKey.ARTISTS,
            "앨범": SpotifySortKey.ALBUM_NAME,
            "추가된 날짜": SpotifySortKey.ADDED_AT,
            "발매일": SpotifySortKey.RELEASE_DATE,
            "곡 길이": SpotifySortKey.DURATION_MS,
            "인기도": SpotifySortKey.POPULARITY
        }
        
        col1, col2 = st.columns(2)
        with col1:
            sort_by = st.selectbox(
                "정렬 기준",
                list(sort_options.keys()),
                key="sort_by"
            )
        with col2:
            sort_order = st.radio(
                "정렬 순서",
                ["오름차순", "내림차순"],
                key="sort_order"
            )
        
        output_option = st.radio(
            "출력 옵션",
            ["기존 플레이리스트 덮어쓰기", "새 플레이리스트로 저장"],
            key="sort_output"
        )
        
        new_playlist_name = None
        if output_option == "새 플레이리스트로 저장":
            new_playlist_name = st.text_input(
                "새 플레이리스트 이름",
                value=f"{selected_playlist} (정렬됨)",
                key="sort_new_name"
            )
        
        if st.button("🔄 정렬 시작", use_container_width=True):
            progress = st.progress(0)
            status = st.empty()
            
            def progress_callback(message):
                status.text(message)
            
            playlist_id = playlist_options[selected_playlist]
            sort_key = sort_options[sort_by]
            ascending = sort_order == "오름차순"
            
            success = self.spotify_manager.sort_playlist(
                playlist_id, sort_key, ascending, new_playlist_name, progress_callback
            )
            
            progress.progress(100)
            if success:
                st.success("✅ 플레이리스트 정렬 완료!")
            else:
                st.error("❌ 플레이리스트 정렬 실패")