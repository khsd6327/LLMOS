# src/llmos/managers/spotify_manager.py
"""
Spotify 관리 매니저
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
from pathlib import Path

from ..models.data_models import SpotifyTrack, SpotifyPlaylist, SpotifySettings
from ..models.enums import SpotifyTimeRange, SpotifySortKey
from ..interfaces.spotify_client import SpotifyClient
from .settings import SettingsManager
from ..core.config import (
    SPOTIFY_DEFAULT_REDIRECT_URI,
    SPOTIFY_DEFAULT_PORT_TYPE,
    SPOTIFY_TOKEN_CACHE_FILENAME,
    SPOTIFY_CACHE_DIR_NAME,
    SPOTIFY_CONFIG_DIR_NAME,
    SPOTIFY_CACHE_EXPIRY_HOURS,
    SPOTIFY_CACHE_KEY_USER_PLAYLISTS,
    SPOTIFY_CACHE_KEY_SAVED_TRACKS,
    SPOTIFY_CACHE_KEY_TOP_TRACKS_PREFIX,
    SPOTIFY_CACHE_KEY_RECENT_FREQUENT_PREFIX,
    SPOTIFY_CACHE_KEY_PLAYLIST_TRACKS_PREFIX,
    SPOTIFY_SETTING_CLIENT_ID,
    SPOTIFY_SETTING_CLIENT_SECRET,
    SPOTIFY_SETTING_REDIRECT_URI,
    SPOTIFY_SETTING_PORT_TYPE,
)

logger = logging.getLogger(__name__)


class SpotifyManager:
    """Spotify 기능 관리 매니저"""
    
    def __init__(self, settings_manager: SettingsManager):
        """
        Args:
            settings_manager: 설정 관리자
        """
        self.settings_manager = settings_manager
        self.client: Optional[SpotifyClient] = None
        self._cache_dir = Path.home() / SPOTIFY_CONFIG_DIR_NAME / SPOTIFY_CACHE_DIR_NAME
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_expiry_hours = SPOTIFY_CACHE_EXPIRY_HOURS
        
        # Spotify 설정 로드
        self._load_spotify_settings()
        
    def _load_spotify_settings(self):
        """Spotify 설정 로드"""
        settings = self.settings_manager.settings
        
        # Spotify 설정 확인
        client_id = settings.get(SPOTIFY_SETTING_CLIENT_ID, "")
        client_secret = settings.get(SPOTIFY_SETTING_CLIENT_SECRET, "")
        redirect_uri = settings.get(SPOTIFY_SETTING_REDIRECT_URI, SPOTIFY_DEFAULT_REDIRECT_URI)
        port_type = settings.get(SPOTIFY_SETTING_PORT_TYPE, SPOTIFY_DEFAULT_PORT_TYPE)
        
        if client_id and client_secret:
            spotify_settings = SpotifySettings(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                port_type=port_type,
                cache_path=str(self._cache_dir / SPOTIFY_TOKEN_CACHE_FILENAME)
            )
            
            self.client = SpotifyClient(spotify_settings)
        else:
            self.client = None
            
    def is_configured(self) -> bool:
        """Spotify가 설정되었는지 확인"""
        return self.client is not None
        
    def authenticate(self) -> bool:
        """Spotify 인증"""
        if not self.client:
            logger.error("Spotify 클라이언트가 설정되지 않음")
            return False
            
        return self.client.authenticate()
        
    def is_authenticated(self) -> bool:
        """인증 상태 확인"""
        if not self.client:
            return False
        return self.client.is_authenticated()
        
    def save_spotify_settings(self, client_id: str, client_secret: str, 
                            redirect_uri: str = SPOTIFY_DEFAULT_REDIRECT_URI,
                            port_type: str = SPOTIFY_DEFAULT_PORT_TYPE) -> bool:
        """Spotify 설정 저장"""
        try:
            # 설정 저장 (개별 항목에 대해 set 메서드 사용)
            self.settings_manager.set(SPOTIFY_SETTING_CLIENT_ID, client_id)
            self.settings_manager.set(SPOTIFY_SETTING_CLIENT_SECRET, client_secret)
            self.settings_manager.set(SPOTIFY_SETTING_REDIRECT_URI, redirect_uri)
            self.settings_manager.set(SPOTIFY_SETTING_PORT_TYPE, port_type)
            # self.settings_manager.save_settings() # set 메서드 내에서 save_settings가 호출되므로 중복 호출 필요 없음

            # 클라이언트 재초기화
            self._load_spotify_settings()
            
            logger.info("Spotify 설정 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"Spotify 설정 저장 오류: {e}")
            return False
        
            
    def _get_cache_path(self, cache_key: str) -> Path:
        """캐시 파일 경로 반환"""
        return self._cache_dir / f"{cache_key}.json"
        
    def _load_from_cache(self, cache_key: str) -> Optional[any]:
        """캐시에서 데이터 로드"""
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 캐시 만료 확인
                cached_at = datetime.fromisoformat(data['cached_at'])
                if datetime.now() - cached_at < timedelta(hours=self._cache_expiry_hours):
                    return data['data']
                else:
                    logger.debug(f"캐시 만료: {cache_key}")
                    
            except Exception as e:
                logger.error(f"캐시 로드 오류 ({cache_key}): {e}")
                
        return None
        
    def _save_to_cache(self, cache_key: str, data: any):
        """캐시에 데이터 저장"""
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"캐시 저장 오류 ({cache_key}): {e}")
            
    def clear_cache(self):
        """모든 캐시 삭제"""
        try:
            for cache_file in self._cache_dir.glob("*.json"):
                if cache_file.name != SPOTIFY_TOKEN_CACHE_FILENAME:  # 토큰 캐시는 유지
                    cache_file.unlink()
            logger.info("Spotify 캐시 삭제 완료")
        except Exception as e:
            logger.error(f"캐시 삭제 오류: {e}")
            
    def get_user_playlists(self, use_cache: bool = True) -> List[SpotifyPlaylist]:
        """사용자 플레이리스트 목록 가져오기"""
        if not self.is_authenticated():
            return []
            
        cache_key = SPOTIFY_CACHE_KEY_USER_PLAYLISTS
        
        if use_cache:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return [SpotifyPlaylist.from_dict(p) for p in cached_data]
                
        # API 호출
        playlists = self.client.get_user_playlists()
        
        # 캐시 저장
        self._save_to_cache(cache_key, [p.to_dict() for p in playlists])
        
        return playlists
        
    def get_saved_tracks(self, progress_callback: Optional[Callable] = None,
                        use_cache: bool = True) -> List[SpotifyTrack]:
        """좋아요 표시한 트랙 목록 가져오기"""
        if not self.is_authenticated():
            return []
            
        cache_key = SPOTIFY_CACHE_KEY_SAVED_TRACKS
        
        if use_cache:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                if progress_callback:
                    progress_callback(f"캐시에서 {len(cached_data)}개 트랙 로드")
                return [SpotifyTrack.from_dict(t) for t in cached_data]
                
        # API 호출
        tracks = self.client.get_saved_tracks(progress_callback)
        
        # 캐시 저장
        self._save_to_cache(cache_key, [t.to_dict() for t in tracks])
        
        return tracks
        
    def get_top_tracks(self, time_range: SpotifyTimeRange, limit: int = 100,
                      use_cache: bool = True) -> List[SpotifyTrack]:
        """Top 트랙 가져오기"""
        if not self.is_authenticated():
            return []
            
        cache_key = f"{SPOTIFY_CACHE_KEY_TOP_TRACKS_PREFIX}_{time_range.value}_{limit}"
        
        if use_cache:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return [SpotifyTrack.from_dict(t) for t in cached_data]
                
        # API 호출
        tracks = self.client.get_top_tracks(time_range, limit)
        
        # 캐시 저장
        self._save_to_cache(cache_key, [t.to_dict() for t in tracks])
        
        return tracks
        
    def get_recent_frequent_tracks(self, days: int = 30, limit: int = 100,
                                 use_cache: bool = True) -> List[SpotifyTrack]:
        """최근 자주 재생한 트랙 가져오기"""
        if not self.is_authenticated():
            return []
            
        cache_key = f"{SPOTIFY_CACHE_KEY_RECENT_FREQUENT_PREFIX}_{days}_{limit}"
        
        if use_cache:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return [SpotifyTrack.from_dict(t) for t in cached_data]
                
        # API 호출
        tracks = self.client.get_recent_frequent_tracks(days, limit)
        
        # 캐시 저장
        self._save_to_cache(cache_key, [t.to_dict() for t in tracks])
        
        return tracks
        
    def create_playlist(self, name: str, public: bool = False,
                       description: str = '') -> Optional[SpotifyPlaylist]:
        """새 플레이리스트 생성"""
        if not self.is_authenticated():
            return None
            
        playlist = self.client.create_playlist(name, public, False, description)
        
        if playlist:
            # 플레이리스트 목록 캐시 무효화
            self._get_cache_path(SPOTIFY_CACHE_KEY_USER_PLAYLISTS).unlink(missing_ok=True)
            
        return playlist
        
    def organize_top_tracks(self, tasks: List[Dict], clear_existing: bool = True,
                          progress_callback: Optional[Callable] = None):
        """Top 트랙 플레이리스트 정리"""
        if not self.is_authenticated():
            return
            
        for task in tasks:
            playlist_id = task['playlist_id']
            playlist_name = task['playlist_name']
            
            if progress_callback:
                progress_callback(f"'{playlist_name}' 처리 중...")
                
            # 새 플레이리스트 생성 필요 시
            if task.get('create_new'):
                playlist = self.create_playlist(playlist_name)
                if playlist:
                    playlist_id = playlist.id
                    if progress_callback:
                        progress_callback(f"새 플레이리스트 '{playlist_name}' 생성됨")
                else:
                    if progress_callback:
                        progress_callback(f"플레이리스트 '{playlist_name}' 생성 실패")
                    continue
                    
            if not playlist_id:
                continue
                
            # 트랙 데이터 가져오기
            tracks = []
            if task['type'] == 'frequent':
                tracks = self.get_recent_frequent_tracks()
            elif task['type'] == SpotifyTimeRange.SHORT_TERM.value:
                tracks = self.get_top_tracks(SpotifyTimeRange.SHORT_TERM)
            elif task['type'] == SpotifyTimeRange.MEDIUM_TERM.value:
                tracks = self.get_top_tracks(SpotifyTimeRange.MEDIUM_TERM)
            elif task['type'] == SpotifyTimeRange.LONG_TERM.value:
                tracks = self.get_top_tracks(SpotifyTimeRange.LONG_TERM)
                
            track_ids = [t.id for t in tracks if t.id]
            
            if not track_ids:
                if progress_callback:
                    progress_callback(f"'{playlist_name}'에 추가할 트랙이 없음")
                continue
                
            # 플레이리스트 업데이트
            if clear_existing:
                self.client.clear_playlist(playlist_id)
                
            self.client.add_tracks_to_playlist(playlist_id, track_ids)
            
            if progress_callback:
                progress_callback(f"'{playlist_name}': {len(track_ids)}개 트랙 추가 완료")
                
    def find_duplicate_tracks(self, progress_callback: Optional[Callable] = None) -> List[List[SpotifyTrack]]:
        """좋아요 목록에서 중복 트랙 찾기"""
        if not self.is_authenticated():
            return []
            
        return self.client.find_duplicate_tracks_in_liked_songs(progress_callback)
        
    def remove_tracks_from_liked(self, track_ids: List[str]):
        """좋아요 목록에서 트랙 제거"""
        if not self.is_authenticated():
            return
            
        self.client.remove_tracks_from_liked(track_ids)
        
        # 좋아요 트랙 캐시 무효화
        self._get_cache_path(SPOTIFY_CACHE_KEY_SAVED_TRACKS).unlink(missing_ok=True)
        
    def get_old_liked_songs(self, count: int = 50,
                          progress_callback: Optional[Callable] = None) -> Tuple[List[SpotifyTrack], int]:
        """오래된 좋아요 곡 가져오기"""
        if not self.is_authenticated():
            return [], 0
            
        return self.client.get_old_liked_songs(count, progress_callback)
        
    def get_playlist_tracks(self, playlist_id: str,
                          progress_callback: Optional[Callable] = None,
                          use_cache: bool = True) -> List[SpotifyTrack]:
        """플레이리스트의 트랙 목록 가져오기"""
        if not self.is_authenticated():
            return []
            
        cache_key = f"{SPOTIFY_CACHE_KEY_PLAYLIST_TRACKS_PREFIX}_{playlist_id}"
        
        if use_cache:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                if progress_callback:
                    progress_callback(f"캐시에서 {len(cached_data)}개 트랙 로드")
                return [SpotifyTrack.from_dict(t) for t in cached_data]
                
        # API 호출
        tracks = self.client.get_playlist_tracks(playlist_id, progress_callback)
        
        # 캐시 저장
        self._save_to_cache(cache_key, [t.to_dict() for t in tracks])
        
        return tracks
        
    def sort_playlist(self, playlist_id: str, sort_key: SpotifySortKey,
                    ascending: bool = True, new_playlist_name: Optional[str] = None,
                    progress_callback: Optional[Callable] = None) -> bool:
        """플레이리스트 정렬"""
        if not self.is_authenticated():
            return False
            
        # 트랙 가져오기
        if progress_callback:
            progress_callback("플레이리스트 트랙 로드 중...")
            
        tracks = self.get_playlist_tracks(playlist_id, progress_callback, use_cache=False)
        
        if not tracks:
            if progress_callback:
                progress_callback("정렬할 트랙이 없음")
            return False
            
        # 정렬 및 업데이트
        success = self.client.sort_and_update_playlist(
            playlist_id, tracks, sort_key, ascending, new_playlist_name
        )
        
        if success:
            # 캐시 무효화
            if new_playlist_name:
                self._get_cache_path(SPOTIFY_CACHE_KEY_USER_PLAYLISTS).unlink(missing_ok=True)
            self._get_cache_path(f"{SPOTIFY_CACHE_KEY_PLAYLIST_TRACKS_PREFIX}_{playlist_id}").unlink(missing_ok=True)
            
            if progress_callback:
                progress_callback("플레이리스트 정렬 완료")
                
        return success