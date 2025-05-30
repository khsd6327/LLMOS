# src/llmos/managers/artifacts.py
"""
LLM OS - 아티팩트 관리자
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..models.data_models import Artifact
from ..models.enums import ArtifactType

logger = logging.getLogger(__name__)


class ArtifactManager:
    """아티팩트 관리자"""

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_path / "artifacts_index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict[str, dict]:
        """아티팩트 인덱스 로드"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error decoding artifacts index: {self.index_file}. Creating new index.")
                return {}
        return {}

    def _save_index(self):
        """아티팩트 인덱스 저장"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving artifacts index: {e}")

    def create(
        self,
        type_val: ArtifactType,
        title: str,
        content: Any,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Artifact:
        """새 아티팩트 생성"""
        artifact_id = str(uuid.uuid4())
        now = datetime.now()
        
        artifact = Artifact(
            id=artifact_id,
            type=type_val,
            title=title,
            content=content,
            tags=tags or [],
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        # 파일로 저장
        artifact_file_path = self.storage_path / f"{artifact.id}.json"
        try:
            with open(artifact_file_path, 'w', encoding='utf-8') as f:
                json.dump(artifact.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving artifact file {artifact_file_path}: {e}")
            raise

        # 인덱스 업데이트
        self.index[artifact.id] = {
            "title": artifact.title,
            "type": artifact.type.value,
            "tags": artifact.tags,
            "created_at": artifact.created_at.isoformat(),
            "updated_at": artifact.updated_at.isoformat(),
            "file": f"{artifact.id}.json"
        }
        self._save_index()
        
        logger.info(f"Created artifact: {artifact.id} - {artifact.title}")
        return artifact

    def get(self, artifact_id: str) -> Optional[Artifact]:
        """아티팩트 ID로 조회"""
        if artifact_id not in self.index:
            logger.warning(f"Artifact ID {artifact_id} not found in index.")
            return None
        
        artifact_filename = self.index[artifact_id].get("file", f"{artifact_id}.json")
        artifact_file_path = self.storage_path / artifact_filename
        
        if artifact_file_path.exists():
            try:
                with open(artifact_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Artifact.from_dict(data)
            except Exception as e:
                logger.error(f"Error loading artifact {artifact_id} from {artifact_file_path}: {e}")
        else:
            logger.warning(f"Artifact file {artifact_file_path} not found for ID {artifact_id} in index.")
        
        return None

    def update(self, artifact_id: str, **updates: Any) -> Optional[Artifact]:
        """아티팩트 업데이트"""
        artifact = self.get(artifact_id)
        if not artifact:
            return None

        changed = False
        for key, value in updates.items():
            if hasattr(artifact, key) and getattr(artifact, key) != value:
                setattr(artifact, key, value)
                changed = True

        if changed:
            artifact.updated_at = datetime.now()
            
            # 파일 업데이트
            artifact_filename = self.index[artifact_id].get("file", f"{artifact.id}.json")
            artifact_file_path = self.storage_path / artifact_filename
            
            try:
                with open(artifact_file_path, 'w', encoding='utf-8') as f:
                    json.dump(artifact.to_dict(), f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Error updating artifact file {artifact_file_path}: {e}")
                return None

            # 인덱스 업데이트
            self.index[artifact_id].update({
                "title": artifact.title,
                "type": artifact.type.value,
                "tags": artifact.tags,
                "updated_at": artifact.updated_at.isoformat()
            })
            self._save_index()
            
            logger.info(f"Updated artifact: {artifact.id}")
        
        return artifact

    def delete(self, artifact_id: str) -> bool:
        """아티팩트 삭제"""
        if artifact_id in self.index:
            artifact_filename = self.index[artifact_id].get("file", f"{artifact_id}.json")
            artifact_file_path = self.storage_path / artifact_filename
            
            # 파일 삭제
            if artifact_file_path.exists():
                try:
                    artifact_file_path.unlink()
                except Exception as e:
                    logger.error(f"Error deleting artifact file {artifact_file_path}: {e}")
                    return False

            # 인덱스에서 삭제
            del self.index[artifact_id]
            self._save_index()
            
            logger.info(f"Deleted artifact: {artifact_id}")
            return True
        
        logger.warning(f"Attempted to delete non-existent artifact ID in index: {artifact_id}")
        return False

    def search(
        self,
        query: Optional[str] = None,
        type_val: Optional[ArtifactType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Artifact]:
        """아티팩트 검색"""
        results: List[Artifact] = []
        
        for artifact_id, info in self.index.items():
            match = True
            
            # 타입 필터
            if type_val and info.get("type") != type_val.value:
                match = False
                continue
            
            # 태그 필터
            if tags and not any(tag_filter in info.get("tags", []) for tag_filter in tags):
                match = False
                continue
            
            # 텍스트 검색
            if query:
                item_title = info.get("title", "")
                title_match = query.lower() in item_title.lower()
                
                content_match = False
                if not title_match and info.get("type") != ArtifactType.IMAGE.value:
                    # 내용에서도 검색
                    artifact_data = self.get(artifact_id)
                    if artifact_data and isinstance(artifact_data.content, str):
                        if query.lower() in artifact_data.content.lower():
                            content_match = True
                
                if not title_match and not content_match:
                    match = False
                    continue
            
            if match:
                artifact = self.get(artifact_id)
                if artifact:
                    results.append(artifact)
                    if len(results) >= limit:
                        break
        
        # 최신 업데이트 순으로 정렬
        results.sort(key=lambda a: a.updated_at, reverse=True)
        return results

    def get_all_artifacts(self, limit: int = 100) -> List[Artifact]:
        """모든 아티팩트 조회"""
        return self.search(limit=limit)

    def get_by_type(self, artifact_type: ArtifactType, limit: int = 50) -> List[Artifact]:
        """타입별 아티팩트 조회"""
        return self.search(type_val=artifact_type, limit=limit)

    def get_by_tags(self, tags: List[str], limit: int = 50) -> List[Artifact]:
        """태그별 아티팩트 조회"""
        return self.search(tags=tags, limit=limit)

    def add_tag(self, artifact_id: str, tag: str) -> bool:
        """아티팩트에 태그 추가"""
        artifact = self.get(artifact_id)
        if artifact and tag not in artifact.tags:
            artifact.tags.append(tag)
            return self.update(artifact_id, tags=artifact.tags) is not None
        return False

    def remove_tag(self, artifact_id: str, tag: str) -> bool:
        """아티팩트에서 태그 제거"""
        artifact = self.get(artifact_id)
        if artifact and tag in artifact.tags:
            artifact.tags.remove(tag)
            return self.update(artifact_id, tags=artifact.tags) is not None
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """아티팩트 통계 정보"""
        all_artifacts = self.get_all_artifacts()
        
        if not all_artifacts:
            return {
                "total_artifacts": 0,
                "by_type": {},
                "total_tags": 0,
                "most_common_tags": []
            }
        
        # 타입별 분류
        type_counts = {}
        all_tags = []
        
        for artifact in all_artifacts:
            type_key = artifact.type.value
            type_counts[type_key] = type_counts.get(type_key, 0) + 1
            all_tags.extend(artifact.tags)
        
        # 태그 빈도
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        most_common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_artifacts": len(all_artifacts),
            "by_type": type_counts,
            "total_tags": len(set(all_tags)),
            "most_common_tags": most_common_tags
        }

    def cleanup_orphaned_files(self) -> int:
        """고아 파일들 정리"""
        json_files = list(self.storage_path.glob("*.json"))
        orphaned_count = 0
        
        for file_path in json_files:
            if file_path.name == "artifacts_index.json":
                continue
            
            artifact_id = file_path.stem
            if artifact_id not in self.index:
                try:
                    file_path.unlink()
                    orphaned_count += 1
                    logger.info(f"Removed orphaned file: {file_path}")
                except Exception as e:
                    logger.error(f"Error removing orphaned file {file_path}: {e}")
        
        return orphaned_count