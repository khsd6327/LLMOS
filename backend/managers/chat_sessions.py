# ted-os-project/src/tedos/managers/chat_sessions.py
"""
Ted OS - 채팅 세션 관리자
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..models.data_models import ChatSession

logger = logging.getLogger(__name__)


class ChatSessionManager:
    """채팅 세션 관리자"""

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_path / "chat_sessions.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, dict]:
        """세션 인덱스 로드"""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(
                    f"Error decoding index: {self.index_file}. Re-initializing."
                )
                return {}
        return {}

    def _save_index(self):
        """세션 인덱스 저장"""
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving index: {e}")

    def create_session(self, title: str = None) -> ChatSession:
        """새 채팅 세션 생성"""
        s_id = str(uuid.uuid4())
        s_title = title or f"새 채팅 {datetime.now().strftime('%Y/%m/%d %H:%M')}"

        session = ChatSession(
            id=s_id,
            title=s_title,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={},
        )

        self._save_session(session)
        logger.info(f"Created session: {s_id} - {s_title}")
        return session

    def _save_session(self, session: ChatSession):
        """세션을 파일로 저장"""
        s_file = self.storage_path / f"{session.id}.json"

        try:
            with open(s_file, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving session {s_file}: {e}")
            return

        # 인덱스 업데이트
        self.index[session.id] = {
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": len(session.messages),
        }
        self._save_index()

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """세션 ID로 세션 조회"""
        if not session_id or session_id not in self.index:
            return None

        s_file = self.storage_path / f"{session_id}.json"
        if s_file.exists():
            try:
                with open(s_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return ChatSession.from_dict(data)
            except Exception as e:
                logger.error(f"Error loading session {s_file}: {e}")

        return None

    def update_session(self, session: ChatSession):
        """세션 업데이트"""
        session.updated_at = datetime.now()
        self._save_session(session)

    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        s_file = self.storage_path / f"{session_id}.json"
        deleted_file, deleted_index = False, False

        # 파일 삭제
        if s_file.exists():
            try:
                s_file.unlink()
                deleted_file = True
            except Exception as e:
                logger.error(f"Error deleting file {s_file}: {e}")

        # 인덱스에서 삭제
        if session_id in self.index:
            del self.index[session_id]
            self._save_index()
            deleted_index = True

        if deleted_file or deleted_index:
            logger.info(f"Deleted session: {session_id}")
            return True

        return False

    def get_all_sessions(self) -> List[ChatSession]:
        """모든 세션 조회 (최신순 정렬)"""
        sessions = []

        for s_id in list(self.index.keys()):
            session = self.get_session(s_id)
            if session:
                sessions.append(session)

        # 최신 업데이트 순으로 정렬
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions

    def update_session_title(self, session_id: str, new_title: str):
        """세션 제목 업데이트"""
        session = self.get_session(session_id)
        if session:
            session.title = new_title
            self.update_session(session)

    def search_sessions(self, query: str, limit: int = 10) -> List[ChatSession]:
        """세션 검색 (제목 기준)"""
        all_sessions = self.get_all_sessions()

        if not query:
            return all_sessions[:limit]

        # 제목에서 검색
        matching_sessions = []
        query_lower = query.lower()

        for session in all_sessions:
            if query_lower in session.title.lower():
                matching_sessions.append(session)
                if len(matching_sessions) >= limit:
                    break

        return matching_sessions

    def get_session_statistics(self) -> Dict[str, Any]:
        """세션 통계 정보"""
        all_sessions = self.get_all_sessions()

        if not all_sessions:
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "avg_messages_per_session": 0,
                "oldest_session": None,
                "newest_session": None,
            }

        total_messages = sum(len(s.messages) for s in all_sessions)
        oldest_session = min(all_sessions, key=lambda s: s.created_at)
        newest_session = max(all_sessions, key=lambda s: s.created_at)

        return {
            "total_sessions": len(all_sessions),
            "total_messages": total_messages,
            "avg_messages_per_session": total_messages / len(all_sessions),
            "oldest_session": {
                "id": oldest_session.id,
                "title": oldest_session.title,
                "created_at": oldest_session.created_at.isoformat(),
            },
            "newest_session": {
                "id": newest_session.id,
                "title": newest_session.title,
                "created_at": newest_session.created_at.isoformat(),
            },
        }

    def cleanup_empty_sessions(self) -> int:
        """빈 세션들 정리"""
        empty_sessions = []
        all_sessions = self.get_all_sessions()

        for session in all_sessions:
            if not session.messages:
                empty_sessions.append(session.id)

        # 빈 세션들 삭제
        deleted_count = 0
        for session_id in empty_sessions:
            if self.delete_session(session_id):
                deleted_count += 1

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} empty sessions")

        return deleted_count

    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션을 내보내기용 딕셔너리로 변환"""
        session = self.get_session(session_id)
        if session:
            return session.to_dict()
        return None

    def import_session(self, session_data: Dict[str, Any]) -> Optional[ChatSession]:
        """딕셔너리에서 세션 가져오기"""
        try:
            session = ChatSession.from_dict(session_data)

            # ID 중복 확인
            if session.id in self.index:
                session.id = str(uuid.uuid4())

            self._save_session(session)
            return session
        except Exception as e:
            logger.error(f"Error importing session: {e}")
            return None
        
    # ===== 채팅 고정 관련 메서드들 =====
    
    def pin_session(self, session_id: str) -> bool:
        """세션을 고정 상태로 변경"""
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found for pinning: {session_id}")
            return False
            
        # 이미 고정된 상태인지 확인
        if session.is_pinned:
            logger.info(f"Session {session_id} is already pinned")
            return True
            
        # 고정 개수 제한 체크 (최대 7개)
        pinned_count = self.get_pinned_sessions_count()
        if pinned_count >= 7:
            logger.warning(f"Cannot pin session {session_id}: maximum 7 pinned sessions reached")
            return False
            
        session.is_pinned = True
        self.update_session(session)
        logger.info(f"Successfully pinned session: {session_id}")
        return True
    
    def unpin_session(self, session_id: str) -> bool:
        """세션의 고정 상태를 해제"""
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session not found for unpinning: {session_id}")
            return False
            
        session.is_pinned = False
        self.update_session(session)
        logger.info(f"Successfully unpinned session: {session_id}")
        return True
    
    def toggle_session_pin(self, session_id: str) -> bool:
        """세션의 고정 상태를 토글 (고정 ↔ 해제)"""
        session = self.get_session(session_id)
        if not session:
            return False
            
        if session.is_pinned:
            return self.unpin_session(session_id)
        else:
            return self.pin_session(session_id)
    
    def get_pinned_sessions(self) -> List[ChatSession]:
        """고정된 세션들만 조회 (최신순 정렬)"""
        all_sessions = self.get_all_sessions()
        pinned_sessions = [s for s in all_sessions if s.is_pinned]
        
        # 고정된 세션들도 최신 업데이트 순으로 정렬
        pinned_sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return pinned_sessions
    
    def get_unpinned_sessions(self) -> List[ChatSession]:
        """고정되지 않은 세션들만 조회 (최신순 정렬)"""
        all_sessions = self.get_all_sessions()
        unpinned_sessions = [s for s in all_sessions if not s.is_pinned]
        
        # 일반 세션들도 최신 업데이트 순으로 정렬  
        unpinned_sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return unpinned_sessions
    
    def get_pinned_sessions_count(self) -> int:
        """현재 고정된 세션의 개수를 반환"""
        all_sessions = self.get_all_sessions()
        return sum(1 for session in all_sessions if session.is_pinned)
    
    def get_sessions_separated(self) -> tuple[List[ChatSession], List[ChatSession]]:
        """고정된 세션과 일반 세션을 분리해서 반환
        
        Returns:
            tuple: (고정된_세션들, 일반_세션들) - 각각 최신순 정렬됨
        """
        pinned_sessions = self.get_pinned_sessions()
        unpinned_sessions = self.get_unpinned_sessions()
        return pinned_sessions, unpinned_sessions
