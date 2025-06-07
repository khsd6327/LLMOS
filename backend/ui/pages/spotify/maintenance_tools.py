# ted-os-project/src/tedos/ui/pages/spotify/maintenance_tools.py
"""
Ted OS - Spotify 라이브러리 정리 도구 담당 모듈
"""

import logging
from datetime import datetime

import streamlit as st

from ....managers.spotify_manager import SpotifyManager

logger = logging.getLogger(__name__)


class MaintenanceTools:
    """Spotify 라이브러리 정리 도구 전담 클래스"""

    def __init__(self, spotify_manager: SpotifyManager):
        self.spotify_manager = spotify_manager

    def render_duplicate_finder(self):
        """중복곡 찾기 UI"""
        st.markdown("### 👥 좋아요 목록 중복곡 찾기")
        st.markdown("곡 이름과 아티스트가 같은 중복된 트랙을 찾습니다.")
        
        if "duplicates" not in st.session_state:
            st.session_state.duplicates = []
        
        if st.button("🔍 중복곡 찾기", use_container_width=True):
            with st.spinner("중복곡 검색 중..."):
                duplicates = self.spotify_manager.find_duplicate_tracks()
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
                        self.spotify_manager.remove_tracks_from_liked(tracks_to_remove)
                        st.success(f"✅ {len(tracks_to_remove)}개의 중복 트랙을 삭제했습니다.")
                        st.session_state.duplicates = []
                        st.rerun()

    def render_old_songs_cleanup(self):
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
                candidates, total = self.spotify_manager.get_old_liked_songs(count)
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
                            self.spotify_manager.remove_tracks_from_liked(tracks_to_remove)
                            st.success(f"✅ {len(tracks_to_remove)}개의 트랙을 삭제했습니다.")
                            st.session_state.cleanup_candidates = []
                            st.rerun()
                    else:
                        st.error("삭제를 확인해주세요.")
            else:
                st.info("삭제할 트랙을 선택해주세요.")
