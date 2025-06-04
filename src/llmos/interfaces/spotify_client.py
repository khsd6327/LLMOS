# src/llmos/interfaces/spotify_client.py
"""
Spotify API 클라이언트
"""

import logging
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict
from typing import List, Optional, Tuple, Callable

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from ..models.data_models import SpotifyTrack, SpotifyPlaylist, SpotifySettings
from ..models.enums import SpotifyTimeRange, SpotifySortKey

logger = logging.getLogger(__name__)


class SpotifyClient:
    """Spotify API 클라이언트"""
    
    def __init__(self, settings: SpotifySettings):
        """
        Args:
            settings: Spotify API 설정
        """
        self.settings = settings
        self.sp = None
        self.user_id = None
        self.scope = " ".join([
            "user-library-read",
            "user-library-modify", 
            "user-read-recently-played",
            "user-top-read",
            "playlist-read-private",
            "playlist-modify-public",
            "playlist-modify-private"
        ])
        
    def authenticate(self) -> bool:
        """Spotify 인증"""
        try:
            effective_redirect_uri = self.settings.redirect_uri
            open_browser = True
            
            # 동적 포트 설정 처리
            if self.settings.port_type == "dynamic" and (
                "127.0.0.1" in self.settings.redirect_uri or 
                "localhost" in self.settings.redirect_uri
            ):
                import socket
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.bind(('127.0.0.1', 0))
                    port = s.getsockname()[1]
                    s.close()
                    
                    uri_parts = self.settings.redirect_uri.split('/')
                    domain_part = uri_parts[2].split(':')[0]
                    path_part = "/".join(uri_parts[3:])
                    effective_redirect_uri = f"{uri_parts[0]}//{domain_part}:{port}/{path_part}"
                except Exception as e:
                    logger.error(f"동적 포트 설정 오류: {e}")
                    open_browser = False
                    
            auth_manager = SpotifyOAuth(
                client_id=self.settings.client_id,
                client_secret=self.settings.client_secret,
                redirect_uri=effective_redirect_uri,
                scope=self.scope,
                cache_path=self.settings.cache_path,
                show_dialog=True,
                open_browser=open_browser
            )
            
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            self.user_id = self.sp.current_user()["id"]
            logger.info(f"Spotify 인증 성공: {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Spotify 인증 오류: {e}")
            return False
            
    def is_authenticated(self) -> bool:
        """인증 상태 확인 (캐시된 토큰 또는 리디렉션 코드 자동 확인)"""
        # 1. 이미 self.sp 객체가 있고 현재 세션에서 유효한지 빠르게 확인
        if self.sp:
            try:
                self.sp.current_user() # API 호출로 실제 유효성 검사
                # logger.debug("Existing self.sp is valid.")
                return True
            except spotipy.exceptions.SpotifyException as e:
                if e.http_status == 401: # 토큰이 만료되었거나 유효하지 않음
                    logger.info("기존 Spotify 객체(self.sp)의 토큰이 유효하지 않습니다 (401). 캐시/재인증을 시도합니다.")
                    self.sp = None # 현재 self.sp 객체를 무효화하여 아래 로직에서 재시도하도록 함
                else: # 그 외 API 오류 (네트워크 문제 등일 수 있음)
                    logger.warning(f"기존 Spotify 객체(self.sp)로 API 호출 중 오류 발생: {e}")
                    return False # 현재로서는 인증 상태를 확인할 수 없으므로 False 반환
            except Exception as e: # 기타 예외 (네트워크 오류 등)
                logger.warning(f"기존 Spotify 객체(self.sp) 사용 중 네트워크 또는 기타 오류: {e}")
                return False

        # 2. self.sp가 없거나 위에서 무효화된 경우, SpotifyOAuth를 통해
        #    (브라우저를 새로 열지 않고) 토큰을 가져오거나 유효성을 확인하려고 시도합니다.
        #    이것은 스크립트가 다시 실행될 때 (예: OAuth 리디렉션 후 또는 새 페이지 로드 시)
        #    캐시된 토큰을 사용하거나 URL의 인증 코드를 처리하기 위함입니다.
        try:
            # open_browser=False 옵션으로 인증 상태 확인 중에는 브라우저가 열리지 않도록 합니다.
            # redirect_uri는 Spotify 앱 설정에 등록된 URI와 일치해야 하며,
            # 토큰 캐시를 찾거나 인증 코드를 처리할 때 사용될 수 있습니다.
            auth_manager = SpotifyOAuth(
                client_id=self.settings.client_id,
                client_secret=self.settings.client_secret,
                redirect_uri=self.settings.redirect_uri, # 설정 파일의 redirect_uri 사용
                scope=self.scope,
                cache_path=self.settings.cache_path,
                open_browser=False # 중요: 인증 상태 '확인' 중에는 브라우저를 열지 않음
            )
            
            # auth_manager를 사용하여 spotipy.Spotify 인스턴스 생성을 시도합니다.
            # 이 과정에서 auth_manager는 다음을 자동으로 시도합니다:
            # 1. 유효한 캐시된 토큰을 사용합니다.
            # 2. 현재 URL에 Spotify로부터 받은 authorization_code가 있다면, 그것을 사용하여 토큰과 교환합니다.
            # 위 두 가지가 모두 실패하면 (즉, 유효한 토큰이나 코드가 없으면), 이후 API 호출 시 오류가 발생합니다.
            temp_sp = spotipy.Spotify(auth_manager=auth_manager)
            
            # 실제로 API를 호출하여 토큰의 유효성을 최종 검증합니다.
            user_info = temp_sp.current_user() 
            
            if user_info and user_info.get("id"):
                self.sp = temp_sp # 유효한 경우, 현재 인스턴스의 self.sp를 이 객체로 업데이트합니다.
                if not self.user_id: # user_id가 아직 설정되지 않았다면 함께 설정합니다.
                    self.user_id = user_info["id"]
                # logger.info(f"Spotify 인증 상태 확인 성공 (사용자: {self.user_id})")
                return True
            else:
                # current_user()가 예외를 발생시키지 않았지만, 유효한 user_id를 반환하지 않은 드문 경우입니다.
                logger.warning("Spotify current_user() 호출은 성공했으나 유효한 사용자 정보를 얻지 못했습니다.")
                self.sp = None # 확실히 None으로 설정
                return False

        except spotipy.exceptions.SpotifyException as e:
            # Spotipy가 (캐시나 URL 코드를 통해) 유효한 토큰을 얻지 못했을 때 일반적으로 발생하는 예외입니다.
            # (예: 캐시된 토큰이 없거나 만료되었고, URL에 인증 코드도 없는 경우)
            # 이 경우는 아직 인증되지 않은 상태로 간주하는 것이 맞습니다.
            logger.debug(f"Spotify 인증 상태 확인 중 SpotifyException (토큰 얻기 실패 등): {e.msg} (HTTP 코드: {e.http_status})")
            self.sp = None 
            return False
        except Exception as e:
            # SpotifyOAuth 설정 오류, 네트워크 문제 등 기타 예기치 않은 예외 처리입니다.
            logger.error(f"Spotify 인증 상태 확인 중 예기치 않은 일반 오류 발생: {e}")
            self.sp = None
            return False
        
        
    def get_user_playlists(self) -> List[SpotifyPlaylist]:
        """사용자 플레이리스트 목록 가져오기"""
        if not self.is_authenticated():
            return []
            
        playlists = []
        results = self.sp.current_user_playlists(limit=50)
        
        while results:
            for playlist in results['items']:
                if playlist['owner']['id'] == self.user_id:
                    playlists.append(SpotifyPlaylist(
                        id=playlist['id'],
                        name=playlist['name'],
                        tracks_total=playlist['tracks']['total'],
                        owner_id=playlist['owner']['id'],
                        description=playlist.get('description', ''),
                        public=playlist.get('public', False)
                    ))
            
            if results['next']:
                try:
                    results = self.sp.next(results)
                except:
                    break
            else:
                break
                
        return playlists
        
    def get_saved_tracks(self, progress_callback: Optional[Callable] = None) -> List[SpotifyTrack]:
        """좋아요 표시한 트랙 목록 가져오기"""
        if not self.is_authenticated():
            return []
            
        all_tracks = []
        results = self.sp.current_user_saved_tracks(limit=50)
        total_tracks = results['total']
        processed_count = 0
        
        if progress_callback:
            progress_callback(f"'좋아요' 곡 로드 시작 (총 {total_tracks}곡)...")
            
        while results:
            for item in results['items']:
                track = item['track']
                if track and track['id']:
                    all_tracks.append(SpotifyTrack(
                        id=track['id'],
                        name=track['name'],
                        artists=', '.join([a['name'] for a in track.get('artists', [])]),
                        duration_ms=track.get('duration_ms', 0),
                        album_name=track.get('album', {}).get('name', 'N/A'),
                        release_date=track.get('album', {}).get('release_date', 'N/A'),
                        popularity=track.get('popularity', 0),
                        added_at=item['added_at']
                    ))
                    
            processed_count += len(results['items'])
            if progress_callback:
                progress_callback(f"'좋아요' 곡 로드 중... ({processed_count}/{total_tracks})")
                
            if results['next']:
                try:
                    results = self.sp.next(results)
                except Exception as e:
                    logger.error(f"페이지네이션 오류: {e}")
                    break
            else:
                break
                
        return all_tracks
        
    def get_top_tracks(self, time_range: SpotifyTimeRange, limit: int = 100) -> List[SpotifyTrack]:
        """Top 트랙 가져오기"""
        if not self.is_authenticated():
            return []
            
        tracks = []
        for offset in range(0, limit, 50):
            batch_limit = min(50, limit - offset)
            try:
                results = self.sp.current_user_top_tracks(
                    time_range=time_range.value,
                    limit=batch_limit,
                    offset=offset
                )
                
                for track in results['items']:
                    if track and track['id']:
                        tracks.append(SpotifyTrack(
                            id=track['id'],
                            name=track['name'],
                            artists=', '.join([a['name'] for a in track.get('artists', [])]),
                            duration_ms=track.get('duration_ms', 0),
                            album_name=track.get('album', {}).get('name', 'N/A'),
                            release_date=track.get('album', {}).get('release_date', 'N/A'),
                            popularity=track.get('popularity', 0)
                        ))
                        
            except Exception as e:
                logger.error(f"Top 트랙 ({time_range.value}) 오류: {e}")
                
        return tracks
        
    def get_recent_frequent_tracks(self, days: int = 30, limit: int = 100) -> List[SpotifyTrack]:
        """최근 자주 재생한 트랙 가져오기"""
        if not self.is_authenticated():
            return []
            
        played_tracks = []
        cutoff_timestamp = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000)
        
        results = self.sp.current_user_recently_played(limit=50)
        
        while results and results['items']:
            for item in results['items']:
                played_at = datetime.fromisoformat(item['played_at'].replace('Z', '+00:00'))
                if played_at.timestamp() * 1000 >= cutoff_timestamp:
                    track = item['track']
                    if track and track['id']:
                        played_tracks.append({
                            'id': track['id'],
                            'track_data': SpotifyTrack(
                                id=track['id'],
                                name=track['name'],
                                artists=', '.join([a['name'] for a in track.get('artists', [])]),
                                duration_ms=track.get('duration_ms', 0),
                                album_name=track.get('album', {}).get('name', 'N/A'),
                                release_date=track.get('album', {}).get('release_date', 'N/A'),
                                popularity=track.get('popularity', 0)
                            )
                        })
                else:
                    results = None
                    break
                    
            if results and results.get('cursors') and results['cursors'].get('before'):
                try:
                    results = self.sp.current_user_recently_played(
                        limit=50,
                        before=results['cursors']['before']
                    )
                except:
                    break
            else:
                break
                
        # 재생 횟수 계산 및 상위 트랙 선택
        play_counts = Counter(t['id'] for t in played_tracks)
        top_track_ids = [track_id for track_id, _ in play_counts.most_common(limit)]
        
        # 트랙 데이터 매핑
        track_map = {t['id']: t['track_data'] for t in played_tracks}
        return [track_map[track_id] for track_id in top_track_ids if track_id in track_map]
        
    def create_playlist(self, name: str, public: bool = False, collaborative: bool = False, description: str = '') -> Optional[SpotifyPlaylist]:
        """새 플레이리스트 생성"""
        if not self.is_authenticated():
            return None
            
        try:
            playlist = self.sp.user_playlist_create(
                self.user_id,
                name,
                public,
                collaborative,
                description
            )
            
            return SpotifyPlaylist(
                id=playlist['id'],
                name=playlist['name'],
                tracks_total=0,
                owner_id=self.user_id,
                description=description,
                public=public
            )
            
        except Exception as e:
            logger.error(f"플레이리스트 생성 오류 ('{name}'): {e}")
            return None
            
    def clear_playlist(self, playlist_id: str):
        """플레이리스트 비우기"""
        if not self.is_authenticated():
            return
            
        try:
            self.sp.playlist_replace_items(playlist_id, [])
        except Exception as e:
            logger.error(f"플레이리스트 비우기 오류 ({playlist_id}): {e}")
            
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str]):
        """플레이리스트에 트랙 추가"""
        if not self.is_authenticated() or not track_ids:
            return
            
        track_uris = [f"spotify:track:{track_id}" for track_id in track_ids]
        
        # 100개씩 배치 처리 (Spotify API 제한)
        for i in range(0, len(track_uris), 100):
            batch = track_uris[i:i+100]
            try:
                self.sp.playlist_add_items(playlist_id, batch)
            except Exception as e:
                logger.error(f"플레이리스트 곡 추가 오류 (배치 {i//100+1}): {e}")
                
    def get_playlist_tracks(self, playlist_id: str, progress_callback: Optional[Callable] = None) -> List[SpotifyTrack]:
        """플레이리스트의 트랙 목록 가져오기"""
        if not self.is_authenticated():
            return []
            
        tracks = []
        
        # 먼저 플레이리스트 정보 확인
        try:
            playlist_info = self.sp.playlist(playlist_id, fields="tracks(total)")
            total = playlist_info['tracks']['total'] if playlist_info else 0
        except:
            total = 0
            
        results = self.sp.playlist_items(
            playlist_id,
            fields="items(added_at,track(id,name,artists(name),album(name,release_date),duration_ms,popularity,is_local)),next",
            limit=100
        )
        
        processed_count = 0
        
        while results:
            for item in results['items']:
                if item and item['track'] and item['track']['id'] and not item['track']['is_local']:
                    track = item['track']
                    tracks.append(SpotifyTrack(
                        id=track['id'],
                        name=track['name'],
                        artists=', '.join([a['name'] for a in track.get('artists', [])]),
                        duration_ms=track.get('duration_ms', 0),
                        album_name=track.get('album', {}).get('name', 'N/A'),
                        release_date=track.get('album', {}).get('release_date', 'N/A'),
                        popularity=track.get('popularity', 0),
                        added_at=item['added_at']
                    ))
                    
                processed_count += 1
                if progress_callback and total > 0:
                    progress_callback(f"플레이리스트 트랙 로드 중... ({processed_count}/{total})")
                    
            if results['next']:
                try:
                    results = self.sp.next(results)
                except:
                    break
            else:
                break
                
        return tracks
        
    def remove_tracks_from_liked(self, track_ids: List[str]):
        """좋아요 목록에서 트랙 제거"""
        if not self.is_authenticated() or not track_ids:
            return
            
        # 50개씩 배치 처리
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i:i+50]
            try:
                self.sp.current_user_saved_tracks_delete(batch)
            except Exception as e:
                logger.error(f"좋아요 곡 삭제 오류: {e}")
                
    def find_duplicate_tracks_in_liked_songs(self, progress_callback: Optional[Callable] = None) -> List[List[SpotifyTrack]]:
        """좋아요 목록에서 중복 트랙 찾기"""
        if not self.is_authenticated():
            return []
            
        if progress_callback:
            progress_callback("'좋아요' 곡 중복 찾는 중...")
            
        liked_tracks = self.get_saved_tracks(progress_callback)
        
        # 곡 이름과 첫 번째 아티스트로 그룹화
        track_groups = defaultdict(list)
        for track in liked_tracks:
            # 키 생성: 소문자 변환 및 공백 제거
            track_key = (
                track.name.lower().strip(),
                track.artists.split(',')[0].lower().strip() if track.artists else ""
            )
            track_groups[track_key].append(track)
            
        # 중복 그룹 필터링 (2개 이상)
        duplicates = [group for group in track_groups.values() if len(group) > 1]
        
        if progress_callback:
            progress_callback(f"중복 찾기 완료. {len(duplicates)}개 세트 발견.")
            
        return duplicates
        
    def get_old_liked_songs(self, count: int = 50, progress_callback: Optional[Callable] = None) -> Tuple[List[SpotifyTrack], int]:
        """오래된 좋아요 곡 가져오기"""
        if not self.is_authenticated():
            return [], 0
            
        # 활발히 듣는 곡 ID 수집
        active_track_ids = set()
        
        if progress_callback:
            progress_callback("활성 청취 곡 분석 중...")
            
        for time_range in [SpotifyTimeRange.SHORT_TERM, SpotifyTimeRange.MEDIUM_TERM, SpotifyTimeRange.LONG_TERM]:
            try:
                tracks = self.get_top_tracks(time_range, 100)
                active_track_ids.update(track.id for track in tracks)
            except:
                continue
                
        # 모든 좋아요 곡 가져오기
        if progress_callback:
            progress_callback("'좋아요' 곡 목록 가져오는 중...")
            
        all_liked_tracks = self.get_saved_tracks(progress_callback)
        total_liked = len(all_liked_tracks)
        
        if progress_callback:
            progress_callback("정리 후보 곡 선정 중...")
            
        # 활발히 듣지 않는 곡 필터링
        cleanup_candidates = [
            track for track in all_liked_tracks 
            if track.id and track.id not in active_track_ids
        ]
        
        # 추가된 날짜 기준 정렬 (오래된 순)
        cleanup_candidates.sort(key=lambda x: x.added_at or '')
        
        if progress_callback:
            progress_callback(f"정리 후보 곡 {len(cleanup_candidates)}개 선정 완료.")
            
        return cleanup_candidates[:count], total_liked
        
    def sort_and_update_playlist(self, playlist_id: str, tracks: List[SpotifyTrack], 
                               sort_key: SpotifySortKey, ascending: bool = True,
                               new_playlist_name: Optional[str] = None) -> bool:
        """플레이리스트 정렬 및 업데이트"""
        if not self.is_authenticated():
            return False
            
        def get_sort_value(track: SpotifyTrack):
            """정렬 값 추출"""
            value = getattr(track, sort_key.value, None)
            if isinstance(value, str):
                return value.lower()
            if value is None:
                return float('-inf') if ascending else float('inf')
            return value
            
        # 트랙 정렬
        try:
            sorted_tracks = sorted(tracks, key=get_sort_value, reverse=not ascending)
        except TypeError:
            # 타입 에러 시 이름으로 정렬
            sorted_tracks = sorted(tracks, key=lambda t: t.name.lower())
            
        sorted_track_ids = [track.id for track in sorted_tracks if track.id]
        
        if not sorted_track_ids:
            return False
            
        # 새 플레이리스트 생성 또는 기존 사용
        target_playlist_id = playlist_id
        if new_playlist_name:
            new_playlist = self.create_playlist(new_playlist_name)
            if new_playlist:
                target_playlist_id = new_playlist.id
            else:
                return False
                
        # 플레이리스트 업데이트
        try:
            self.sp.playlist_replace_items(target_playlist_id, [])
            self.add_tracks_to_playlist(target_playlist_id, sorted_track_ids)
            return True
        except Exception as e:
            logger.error(f"플레이리스트 정렬 업데이트 오류: {e}")
            return False