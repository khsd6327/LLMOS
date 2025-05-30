# src/llmos/ui/pages/spotify.py
"""
Spotify 페이지 UI
"""

import streamlit as st
import threading
import logging
import traceback
from datetime import datetime
from typing import List, Dict, Optional

from ...models.enums import SpotifyTimeRange, SpotifySortKey
from ...models.data_models import SpotifyTrack, SpotifyPlaylist
from ...managers.spotify_manager import SpotifyManager
from ..components import EnhancedUI
from ..styles import apply_theme

logger = logging.getLogger(__name__)


def render_spotify_page(spotify_manager: SpotifyManager, ui_components: EnhancedUI):
    """Spotify 페이지 렌더링"""
    
    apply_theme() # 테마 적용은 그대로 유지합니다.
    
    st.markdown("# 🎵 Spotify 플레이리스트 관리")
    st.caption("Spotify 음악 라이브러리를 관리하고 새로운 음악을 발견하세요.")
    st.markdown("---")

    # 1. Spotify API 설정 확인
    if not spotify_manager.is_configured():
        st.warning("⚠️ Spotify 기능을 사용하려면 먼저 API 설정을 완료해야 합니다.")
        st.markdown(
            """
            애플리케이션의 **'앱 설정'** 페이지로 이동하여 **'🎵 Spotify API'** 탭에서 
            Client ID와 Client Secret 등 필요한 정보를 입력하고 저장해주세요.
            """
        )
        
        # '앱 설정' 페이지로 바로 이동하는 버튼
        if st.button("⚙️ 앱 설정 페이지로 이동하여 Spotify 설정하기", use_container_width=True):
            st.session_state.show_spotify_page = False # 현재 페이지 상태 끄고
            st.session_state.show_settings_page = True  # 설정 페이지 상태 켜기
            st.rerun()
        return # 설정이 안 되어 있으면 여기서 함수 실행 종료

    # 2. Spotify 계정 인증 확인 (API 설정이 완료된 경우)
    if not spotify_manager.is_authenticated():
        # 인증 UI는 그대로 사용합니다.
        render_authentication(spotify_manager) 
        return # 인증이 안 되어 있으면 여기서 함수 실행 종료
    
    # 3. 설정 및 인증이 모두 완료된 경우: Spotify 기능 UI 렌더링
    render_spotify_features(spotify_manager, ui_components)

def render_spotify_setup(spotify_manager: SpotifyManager):
    """Spotify 설정 UI"""
    st.warning("⚠️ Spotify API 설정이 필요합니다.")
    
def render_authentication(spotify_manager: SpotifyManager):
    """Spotify 인증 UI"""
    st.info("🔐 Spotify 인증이 필요합니다.")
    
    if st.button("🎵 Spotify 로그인", use_container_width=True):
        with st.spinner("인증 중..."):
            if spotify_manager.authenticate():
                st.success("✅ 인증 성공!")
                st.rerun()
            else:
                st.error("❌ 인증 실패. 설정을 확인해주세요.")


def render_spotify_features(spotify_manager: SpotifyManager, ui_components: EnhancedUI):
    """Spotify 기능 UI"""
    
    # 기능 탭
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Top 트랙 정리",
        "➕ 새 플레이리스트",
        "🔄 플레이리스트 정렬",
        "👥 중복곡 찾기",
        "🧹 오래된 곡 정리"
    ])
    
    with tab1:
        render_top_tracks_organizer(spotify_manager)
        
    with tab2:
        render_create_playlist(spotify_manager)
        
    with tab3:
        render_sort_playlist(spotify_manager)
        
    with tab4:
        render_duplicate_finder(spotify_manager)
        
    with tab5:
        render_old_songs_cleanup(spotify_manager)
    
    # 캐시 관리
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ 캐시 초기화", use_container_width=True):
            spotify_manager.clear_cache()
            st.success("캐시가 초기화되었습니다.")
            st.rerun()


def render_top_tracks_organizer(spotify_manager: SpotifyManager):
    """Top 트랙 정리 UI"""
    st.markdown("### 🎯 Top 트랙 플레이리스트 정리")
    st.markdown("자주 듣는 곡들을 자동으로 플레이리스트로 정리합니다.")
    
    # 플레이리스트 목록 가져오기
    playlists = spotify_manager.get_user_playlists()
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
            # progress_container.write(message) # <--- 이 줄을 주석 처리하거나 삭제하고
            logger.info(f"[Top 트랙 정리 진행] {message}") 
        
        def process_thread():
            try:
                spotify_manager.organize_top_tracks(tasks, clear_existing, progress_callback)
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

def render_create_playlist(spotify_manager: SpotifyManager):
    """새 플레이리스트 생성 UI"""
    st.markdown("### ➕ 새 플레이리스트 생성")
    
    with st.form("create_playlist_form"):
        name = st.text_input("플레이리스트 이름", key="new_playlist_name")
        description = st.text_area("설명 (선택사항)", key="new_playlist_desc")
        is_public = st.checkbox("공개 플레이리스트", key="new_playlist_public")
        
        submitted = st.form_submit_button("✨ 생성", use_container_width=True)
        
        if submitted:
            if name:
                playlist = spotify_manager.create_playlist(name, is_public, description)
                if playlist:
                    st.success(f"✅ 플레이리스트 '{playlist.name}'이(가) 생성되었습니다!")
                else:
                    st.error("❌ 플레이리스트 생성에 실패했습니다.")
            else:
                st.error("플레이리스트 이름을 입력해주세요.")


def render_sort_playlist(spotify_manager: SpotifyManager):
    """플레이리스트 정렬 UI"""
    st.markdown("### 🔄 플레이리스트 정렬")
    
    playlists = spotify_manager.get_user_playlists()
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
        
        success = spotify_manager.sort_playlist(
            playlist_id, sort_key, ascending, new_playlist_name, progress_callback
        )
        
        progress.progress(100)
        if success:
            st.success("✅ 플레이리스트 정렬 완료!")
        else:
            st.error("❌ 플레이리스트 정렬 실패")


def render_duplicate_finder(spotify_manager: SpotifyManager):
    """중복곡 찾기 UI"""
    st.markdown("### 👥 좋아요 목록 중복곡 찾기")
    st.markdown("곡 이름과 아티스트가 같은 중복된 트랙을 찾습니다.")
    
    if "duplicates" not in st.session_state:
        st.session_state.duplicates = []
    
    if st.button("🔍 중복곡 찾기", use_container_width=True):
        with st.spinner("중복곡 검색 중..."):
            duplicates = spotify_manager.find_duplicate_tracks()
            st.session_state.duplicates = duplicates
            
            if duplicates:
                st.success(f"✅ {len(duplicates)}개의 중복 그룹을 찾았습니다.")
            else:
                st.info("중복된 곡이 없습니다.")
    
    if st.session_state.duplicates:
        st.divider()
        
        # 삭제할 트랙 선택
        tracks_to_remove = []
        
        for i, dup_group in enumerate(st.session_state.duplicates):
            if len(dup_group) < 2:
                continue
                
            # 첫 번째 트랙 정보 표시
            first_track = dup_group[0]
            st.markdown(f"**{i+1}. {first_track.name} - {first_track.artists.split(',')[0]}** ({len(dup_group)}개)")
            
            # 추가된 날짜 기준 정렬
            sorted_tracks = sorted(dup_group, key=lambda x: x.added_at or '')
            
            for j, track in enumerate(sorted_tracks):
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    if j > 0:  # 첫 번째(가장 오래된) 트랙은 유지
                        if st.checkbox("삭제", key=f"dup_{track.id}"):
                            tracks_to_remove.append(track.id)
                    else:
                        st.markdown("**유지**")
                
                with col2:
                    added_date = "날짜 없음"
                    if track.added_at:
                        try:
                            added_date = datetime.fromisoformat(track.added_at.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                        except:
                            pass
                    st.caption(f"추가: {added_date}")
                
                with col3:
                    duration = f"{track.duration_ms // 60000}:{(track.duration_ms % 60000) // 1000:02d}"
                    st.caption(f"길이: {duration}")
            
            st.markdown("---")
        
        # 선택된 트랙 삭제
        if tracks_to_remove:
            if st.button(f"🗑️ 선택한 {len(tracks_to_remove)}개 트랙 삭제", type="primary", use_container_width=True):
                with st.spinner("삭제 중..."):
                    spotify_manager.remove_tracks_from_liked(tracks_to_remove)
                    st.success(f"✅ {len(tracks_to_remove)}개의 중복 트랙을 삭제했습니다.")
                    st.session_state.duplicates = []
                    st.rerun()


def render_old_songs_cleanup(spotify_manager: SpotifyManager):
    """오래된 곡 정리 UI"""
    st.markdown("### 🧹 오래된 좋아요 곡 정리")
    st.markdown("최근에 듣지 않는 오래된 곡들을 찾아 정리합니다.")
    
    # 조회할 곡 수 설정
    count = st.number_input(
        "조회할 후보 곡 수",
        min_value=10,
        max_value=200,
        value=50,
        step=10,
        key="cleanup_count"
    )
    
    if "cleanup_candidates" not in st.session_state:
        st.session_state.cleanup_candidates = []
        st.session_state.total_liked = 0
    
    if st.button("🔍 정리 후보 곡 찾기", use_container_width=True):
        with st.spinner("후보 곡 분석 중..."):
            candidates, total = spotify_manager.get_old_liked_songs(count)
            st.session_state.cleanup_candidates = candidates
            st.session_state.total_liked = total
            
            if candidates:
                st.success(f"✅ 총 {total}개 중 {len(candidates)}개의 정리 후보를 찾았습니다.")
            else:
                st.info("정리할 후보 곡이 없습니다.")
    
    if st.session_state.cleanup_candidates:
        st.divider()
        st.markdown(f"**정리 후보 곡** (총 좋아요: {st.session_state.total_liked}개)")
        
        # 삭제할 트랙 선택
        tracks_to_remove = []
        
        # 전체 선택/해제
        col1, col2 = st.columns([1, 4])
        with col1:
            select_all = st.checkbox("전체 선택", key="cleanup_select_all")
        
        for track in st.session_state.cleanup_candidates:
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                if st.checkbox("삭제", value=select_all, key=f"cleanup_{track.id}"):
                    tracks_to_remove.append(track.id)
            
            with col2:
                st.markdown(f"**{track.name}**")
                st.caption(f"{track.artists}")
            
            with col3:
                added_date = "날짜 없음"
                if track.added_at:
                    try:
                        added_date = datetime.fromisoformat(track.added_at.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                    except:
                        pass
                st.caption(f"추가: {added_date}")
        
        # 선택된 트랙 삭제
        st.divider()
        if tracks_to_remove:
            st.warning(f"⚠️ {len(tracks_to_remove)}개의 트랙이 선택되었습니다. 삭제하면 되돌릴 수 없습니다!")
            
            if st.button(f"🗑️ 선택한 {len(tracks_to_remove)}개 트랙 영구 삭제", type="primary", use_container_width=True):
                confirm = st.checkbox("정말로 삭제하시겠습니까?", key="cleanup_confirm")
                if confirm:
                    with st.spinner("삭제 중..."):
                        spotify_manager.remove_tracks_from_liked(tracks_to_remove)
                        st.success(f"✅ {len(tracks_to_remove)}개의 트랙을 삭제했습니다.")
                        st.session_state.cleanup_candidates = []
                        st.rerun()
                else:
                    st.error("삭제를 확인해주세요.")
        else:
            st.info("삭제할 트랙을 선택해주세요.")