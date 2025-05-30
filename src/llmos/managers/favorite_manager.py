# src/llmos/managers/favorite_manager.py
import json
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

# 로깅 설정
import logging
logger = logging.getLogger(__name__)

# 현재 파일의 상위 디렉토리 (src/llmos/) 를 기준으로 import 경로 설정
# 이렇게 하면 LLMOS 프로젝트 루트에서 python -m src.llmos.main 등으로 실행될 때를 가정
try:
    from ..models.data_models import FavoriteMessage, ModelProvider
    from ..utils.helpers import ensure_directory_exists # 이 함수는 utils.helpers에 있다고 가정합니다.
                                                      # 만약 없다면, 직접 디렉토리 생성 코드를 사용하거나 추가해야 합니다.
except ImportError:
    # 스크립트가 다른 방식으로 실행될 경우 (예: 직접 managers 폴더에서 실행)
    # 또는 테스트 환경 등을 위한 상대 경로 처리
    logger.warning("Attempting relative import for FavoriteManager dependencies.")
    # 실제 프로젝트 구조와 실행 방식에 따라 이 부분은 조정이 필요할 수 있습니다.
    # 일반적으로는 최상위 패키지부터의 절대 경로 임포트가 권장됩니다.
    # 예: from src.llmos.models.data_models import FavoriteMessage
    # 여기서는 현재 파일 위치를 기준으로 한 상대 임포트를 사용합니다.
    import sys
    # 현재 파일의 디렉토리 (managers)의 부모 디렉토리 (llmos)를 경로에 추가
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from models.data_models import FavoriteMessage, ModelProvider
    from utils.helpers import ensure_directory_exists


FAVORITES_FILE_NAME = "favorites_data.json" # 즐겨찾기 데이터 저장 파일명

class FavoriteManager:
    """즐겨찾기 메시지를 관리하는 클래스"""

    def __init__(self, storage_dir: str):
        """
        FavoriteManager를 초기화합니다.

        :param storage_dir: 즐겨찾기 데이터 파일이 저장될 디렉토리 경로입니다.
        """
        ensure_directory_exists(storage_dir) # 저장 디렉토리 존재 확인 및 생성
        self.favorites_file_path = os.path.join(storage_dir, FAVORITES_FILE_NAME)
        self._favorites: Dict[str, FavoriteMessage] = self._load_favorites()
        logger.info(f"FavoriteManager initialized. Data file: {self.favorites_file_path}")

    def _load_favorites(self) -> Dict[str, FavoriteMessage]:
        """
        파일에서 즐겨찾기 목록을 불러옵니다.
        파일이 없거나 유효하지 않은 JSON인 경우, 빈 딕셔너리를 반환합니다.
        """
        if not os.path.exists(self.favorites_file_path):
            logger.info(f"Favorites file not found at {self.favorites_file_path}. Initializing with empty list.")
            return {}
        
        try:
            with open(self.favorites_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 키는 ID, 값은 FavoriteMessage 객체로 변환
                return {
                    fav_id: FavoriteMessage.from_dict(fav_data)
                    for fav_id, fav_data in data.items()
                }
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {self.favorites_file_path}. Initializing with empty list.")
            return {}
        except Exception as e:
            logger.error(f"Failed to load favorites from {self.favorites_file_path}: {e}")
            return {}

    def _save_favorites(self) -> None:
        """
        현재 즐겨찾기 목록을 파일에 저장합니다.
        """
        try:
            # FavoriteMessage 객체를 딕셔너리 형태로 변환하여 저장
            data_to_save = {
                fav_id: fav_obj.to_dict()
                for fav_id, fav_obj in self._favorites.items()
            }
            with open(self.favorites_file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            logger.debug(f"Favorites saved to {self.favorites_file_path}")
        except Exception as e:
            logger.error(f"Failed to save favorites to {self.favorites_file_path}: {e}")

    def add_favorite(self, session_id: str, message_id: str, role: str, content: str,
                     created_at: datetime, model_provider: Optional[ModelProvider] = None,
                     model_name: Optional[str] = None, context_messages: Optional[List[Dict[str, Any]]] = None,
                     tags: Optional[List[str]] = None, notes: Optional[str] = None) -> FavoriteMessage:
        """
        새로운 즐겨찾기 메시지를 추가합니다.

        :return: 추가된 FavoriteMessage 객체
        """
        new_id = str(uuid.uuid4())
        favorited_at = datetime.now()
        
        if tags is None:
            tags = []

        favorite = FavoriteMessage(
            id=new_id,
            session_id=session_id,
            message_id=message_id,
            role=role,
            content=content,
            favorited_at=favorited_at,
            created_at=created_at,
            model_provider=model_provider,
            model_name=model_name,
            context_messages=context_messages,
            tags=tags,
            notes=notes
        )
        self._favorites[new_id] = favorite
        self._save_favorites()
        logger.info(f"Added new favorite: {new_id} (Session: {session_id}, Message: {message_id})")
        return favorite

    def remove_favorite(self, favorite_id: str) -> bool:
        """
        ID를 사용하여 즐겨찾기 메시지를 삭제합니다.

        :param favorite_id: 삭제할 즐겨찾기의 ID
        :return: 삭제 성공 시 True, 해당 ID가 없으면 False
        """
        if favorite_id in self._favorites:
            del self._favorites[favorite_id]
            self._save_favorites()
            logger.info(f"Removed favorite: {favorite_id}")
            return True
        logger.warning(f"Attempted to remove non-existent favorite: {favorite_id}")
        return False

    def get_favorite_by_id(self, favorite_id: str) -> Optional[FavoriteMessage]:
        """
        ID로 특정 즐겨찾기 메시지를 가져옵니다.

        :param favorite_id: 가져올 즐겨찾기의 ID
        :return: FavoriteMessage 객체 또는 해당 ID가 없으면 None
        """
        return self._favorites.get(favorite_id)

    def list_all_favorites(self, sort_by_date: bool = True, ascending: bool = False) -> List[FavoriteMessage]:
        """
        모든 즐겨찾기 메시지 목록을 반환합니다.

        :param sort_by_date: True이면 즐겨찾기 시간(favorited_at)으로 정렬합니다.
        :param ascending: True이면 오름차순, False이면 내림차순으로 정렬합니다.
        :return: FavoriteMessage 객체의 리스트
        """
        favorites_list = list(self._favorites.values())
        if sort_by_date:
            favorites_list.sort(key=lambda fav: fav.favorited_at, reverse=not ascending)
        logger.debug(f"Listed {len(favorites_list)} favorites.")
        return favorites_list

    def update_favorite_details(self, favorite_id: str, tags: Optional[List[str]] = None, notes: Optional[str] = None) -> Optional[FavoriteMessage]:
        """
        기존 즐겨찾기 메시지의 태그나 노트를 업데이트합니다.
        tags나 notes 중 하나 이상이 제공되어야 합니다.

        :param favorite_id: 업데이트할 즐겨찾기의 ID
        :param tags: 새로운 태그 리스트. None이면 태그는 변경하지 않습니다.
        :param notes: 새로운 노트 문자열. None이면 노트는 변경하지 않습니다.
        :return: 업데이트된 FavoriteMessage 객체 또는 해당 ID가 없으면 None
        """
        favorite = self.get_favorite_by_id(favorite_id)
        if not favorite:
            logger.warning(f"Attempted to update non-existent favorite: {favorite_id}")
            return None

        updated = False
        if tags is not None:
            favorite.tags = tags
            updated = True
        
        if notes is not None: # 빈 문자열 ""도 유효한 값으로 간주하여 업데이트
            favorite.notes = notes
            updated = True
        
        if updated:
            self._save_favorites()
            logger.info(f"Updated details for favorite: {favorite_id}")
        else:
            logger.info(f"No details provided to update for favorite: {favorite_id}")
            
        return favorite

    def find_favorites(self, query: Optional[str] = None, tags: Optional[List[str]] = None) -> List[FavoriteMessage]:
        """
        내용 검색어(query)나 태그(tags)를 기준으로 즐겨찾기를 검색합니다.

        :param query: 메시지 내용(content) 또는 노트(notes)에서 검색할 문자열. 대소문자 구분 없음.
        :param tags: 포함되어야 하는 태그 리스트. 모든 태그를 만족해야 함 (AND 조건).
        :return: 조건에 맞는 FavoriteMessage 객체의 리스트
        """
        results = []
        
        for favorite in self._favorites.values():
            match = True
            
            # 태그 검색 (AND 조건)
            if tags:
                if not all(tag.lower() in [t.lower() for t in favorite.tags] for tag in tags):
                    match = False
            
            # 내용 검색 (OR 조건: content 또는 notes)
            if match and query:
                query_lower = query.lower()
                content_match = query_lower in favorite.content.lower()
                notes_match = favorite.notes and query_lower in favorite.notes.lower()
                if not (content_match or notes_match):
                    match = False
            
            if match:
                results.append(favorite)
        
        logger.debug(f"Found {len(results)} favorites matching query='{query}', tags={tags}")
        # 필요시 정렬 추가 가능
        results.sort(key=lambda fav: fav.favorited_at, reverse=True) # 기본적으로 최신순 정렬
        return results