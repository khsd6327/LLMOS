# ted-os-project/src/tedos/ui/pages/spotify_page.py
"""
Ted OS - Spotify 페이지 (리팩토링됨)
"""

import streamlit as st
import logging

from ...managers.spotify_manager import SpotifyManager
from .spotify import SetupManager, TrackOrganizer, PlaylistManager, MaintenanceTools

logger = logging.getLogger(__name__)


def render_spotify_page(spotify_manager: SpotifyManager, ui_components: EnhancedUI):
    """Spotify 페이지 렌더링 (분리된 매니저들을 조합)"""
    
    apply_theme() # 테마 적용은 그대로 유지합니다.
    
    st.markdown("# 🎵 Spotify 플레이리스트 관리")
    st.caption("Spotify 음악 라이브러리를 관리하고 새로운 음악을 발견하세요.")
    
    # 뒤로가기 버튼 추가
    if st.button("⬅️ 채팅으로 돌아가기", key="back_from_spotify_page_btn"):
        st.session_state.show_spotify_page = False
        st.rerun()
    
    st.markdown("---")

    # 분리된 매니저들 초기화
    setup_manager = SetupManager(spotify_manager)
    track_organizer = TrackOrganizer(spotify_manager)
    playlist_manager = PlaylistManager(spotify_manager)
    maintenance_tools = MaintenanceTools(spotify_manager)

    # 1. Spotify API 설정 확인
    if not spotify_manager.is_configured():
        setup_manager.render_spotify_setup()
        return # 설정이 안 되어 있으면 여기서 함수 실행 종료

    # 2. Spotify 계정 인증 확인 (API 설정이 완료된 경우)
    if not spotify_manager.is_authenticated():
        setup_manager.render_authentication() 
        return # 인증이 안 되어 있으면 여기서 함수 실행 종료
    
    # 3. 설정 및 인증이 모두 완료된 경우: Spotify 기능 UI 렌더링
    render_spotify_features(track_organizer, playlist_manager, maintenance_tools, spotify_manager)


def render_spotify_features(
    track_organizer: TrackOrganizer, 
    playlist_manager: PlaylistManager, 
    maintenance_tools: MaintenanceTools,
    spotify_manager: SpotifyManager
):
    """Spotify 기능 UI (분리된 렌더러들 사용)"""
    
    # 기능 탭
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Top 트랙 정리",
        "➕ 새 플레이리스트",
        "🔄 플레이리스트 정렬",
        "👥 중복곡 찾기",
        "🧹 오래된 곡 정리"
    ])
    
    with tab1:
        track_organizer.render_top_tracks_organizer()
        
    with tab2:
        playlist_manager.render_create_playlist()
        
    with tab3:
        playlist_manager.render_sort_playlist()
        
    with tab4:
        maintenance_tools.render_duplicate_finder()
        
    with tab5:
        maintenance_tools.render_old_songs_cleanup()
    
    # 캐시 관리
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ 캐시 초기화", use_container_width=True):
            spotify_manager.clear_cache()
            st.success("캐시가 초기화되었습니다.")
            st.rerun()