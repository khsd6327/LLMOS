# src/llmos/ui/pages/artifacts.py
"""
LLM OS - 아티팩트 페이지
"""

import json
import logging
from datetime import datetime
from typing import List, Optional

import streamlit as st

from ...managers.artifacts import ArtifactManager
from ...models.data_models import Artifact
from ...models.enums import ArtifactType
from ...ui.components import EnhancedUI
from ...utils.helpers import format_file_size, truncate_text

logger = logging.getLogger(__name__)


class ArtifactsPage:
    """아티팩트 페이지 클래스"""

    def __init__(self, artifact_manager: ArtifactManager, ui: EnhancedUI):
        self.artifact_manager = artifact_manager
        self.ui = ui

    def render(self):
        """아티팩트 페이지 렌더링"""
        st.header("📚 아티팩트 관리")
        
        # 뒤로가기 버튼
        if st.button("⬅️ 채팅으로 돌아가기", key="back_from_artifacts_page_btn"):
            st.session_state.show_artifacts_page = False
            st.rerun()

        # 탭으로 기능 분리
        tabs = st.tabs(["🔍 검색 & 보기", "➕ 새 아티팩트", "📊 통계", "🛠️ 관리"])
        
        with tabs[0]:
            self._render_search_view_section()
        
        with tabs[1]:
            self._render_create_artifact_section()
        
        with tabs[2]:
            self._render_statistics_section()
        
        with tabs[3]:
            self._render_management_section()

    def _render_search_view_section(self):
        """검색 및 보기 섹션"""
        st.subheader("아티팩트 검색")
        
        # 검색 컨트롤
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input(
                "검색어 (제목 또는 내용)",
                key="artifact_search_query",
                placeholder="검색할 키워드를 입력하세요..."
            )
        
        with col2:
            # 타입 필터
            type_options = ["전체"] + [t.value for t in ArtifactType]
            selected_type = st.selectbox(
                "타입 필터",
                type_options,
                key="artifact_type_filter"
            )
        
        with col3:
            # 정렬 옵션
            sort_options = ["최신순", "오래된순", "제목순"]
            sort_order = st.selectbox(
                "정렬",
                sort_options,
                key="artifact_sort_order"
            )
        
        # 태그 필터
        all_artifacts = self.artifact_manager.get_all_artifacts(limit=1000)
        all_tags = set()
        for artifact in all_artifacts:
            all_tags.update(artifact.tags)
        
        if all_tags:
            selected_tags = st.multiselect(
                "태그 필터",
                sorted(all_tags),
                key="artifact_tag_filter"
            )
        else:
            selected_tags = []
        
        # 검색 실행
        search_type = None if selected_type == "전체" else ArtifactType(selected_type)
        
        artifacts = self.artifact_manager.search(
            query=search_query if search_query else None,
            type_val=search_type,
            tags=selected_tags if selected_tags else None,
            limit=100
        )
        
        # 정렬 적용
        if sort_order == "오래된순":
            artifacts.sort(key=lambda a: a.created_at)
        elif sort_order == "제목순":
            artifacts.sort(key=lambda a: a.title.lower())
        # 기본은 최신순 (이미 정렬됨)
        
        # 결과 표시
        if not artifacts:
            st.info("검색 조건에 맞는 아티팩트가 없습니다.")
            return
        
        st.write(f"**{len(artifacts)}개의 아티팩트 발견**")
        
        # 아티팩트 목록 표시
        for artifact in artifacts:
            self._render_artifact_card(artifact)

    def _render_artifact_card(self, artifact: Artifact):
        """아티팩트 카드 렌더링"""
        with st.expander(
            f"{artifact.title} ({artifact.type.value}) - {artifact.updated_at.strftime('%Y-%m-%d %H:%M')}",
            expanded=False
        ):
            # 메타데이터
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.caption(f"**ID:** {artifact.id[:8]}...")
                st.caption(f"**생성일:** {artifact.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                st.caption(f"**타입:** {artifact.type.value}")
                if artifact.tags:
                    st.caption(f"**태그:** {', '.join(artifact.tags)}")
            
            with col3:
                if isinstance(artifact.content, str):
                    content_size = len(artifact.content.encode('utf-8'))
                    st.caption(f"**크기:** {format_file_size(content_size)}")
                elif isinstance(artifact.content, bytes):
                    st.caption(f"**크기:** {format_file_size(len(artifact.content))}")
            
            # 내용 표시
            if artifact.type == ArtifactType.IMAGE and isinstance(artifact.content, bytes):
                st.image(artifact.content, width=300, caption=artifact.title)
            
            elif isinstance(artifact.content, str):
                if artifact.type == ArtifactType.CODE:
                    # 언어 추론
                    language = self._detect_code_language(artifact.content)
                    st.code(artifact.content, language=language)
                elif artifact.type == ArtifactType.JSON:
                    try:
                        json_data = json.loads(artifact.content)
                        st.json(json_data)
                    except:
                        st.text_area(
                            "내용",
                            artifact.content,
                            height=150,
                            disabled=True,
                            key=f"artifact_content_{artifact.id}"
                        )
                else:
                    # 텍스트 내용
                    if len(artifact.content) > 1000:
                        with st.expander("전체 내용 보기", expanded=False):
                            st.text_area(
                                "내용",
                                artifact.content,
                                height=300,
                                disabled=True,
                                key=f"artifact_full_content_{artifact.id}"
                            )
                        st.text(truncate_text(artifact.content, 500))
                    else:
                        st.text_area(
                            "내용",
                            artifact.content,
                            height=150,
                            disabled=True,
                            key=f"artifact_content_{artifact.id}"
                        )
                
                # 복사 버튼
                self.ui.render_copy_button(
                    artifact.content,
                    f"artifact_{artifact.id}",
                    "내용 복사"
                )
            
            else:
                # 기타 타입
                try:
                    st.json(artifact.content)
                except:
                    st.text(str(artifact.content)[:500] + "...")
            
            # 메타데이터 표시
            if artifact.metadata:
                with st.expander("메타데이터", expanded=False):
                    st.json(artifact.metadata)
            
            # 액션 버튼
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("편집", key=f"edit_artifact_{artifact.id}"):
                    st.session_state.editing_artifact_id = artifact.id
                    st.rerun()
            
            with col2:
                if st.button("복제", key=f"clone_artifact_{artifact.id}"):
                    self._clone_artifact(artifact)
            
            with col3:
                if st.button("내보내기", key=f"export_artifact_{artifact.id}"):
                    self._export_artifact(artifact)
            
            with col4:
                if st.button("🗑️ 삭제", key=f"delete_artifact_{artifact.id}"):
                    if st.session_state.get(f"confirm_delete_{artifact.id}"):
                        self.artifact_manager.delete(artifact.id)
                        st.success(f"아티팩트 '{artifact.title}'가 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{artifact.id}"] = True
                        st.warning("정말로 삭제하시겠습니까? 다시 한 번 클릭하세요.")

    def _detect_code_language(self, code: str) -> str:
        """코드 언어 감지"""
        code_lower = code.lower()
        
        if 'def ' in code or 'import ' in code or 'print(' in code:
            return 'python'
        elif 'function ' in code or 'const ' in code or 'let ' in code:
            return 'javascript'
        elif '<html' in code_lower or '<div' in code_lower or '<!doctype' in code_lower:
            return 'html'
        elif 'background:' in code or 'color:' in code or 'margin:' in code:
            return 'css'
        elif '#include' in code or 'int main(' in code:
            return 'cpp'
        elif 'public class' in code or 'System.out.println' in code:
            return 'java'
        
        return 'text'

    def _render_create_artifact_section(self):
        """새 아티팩트 생성 섹션"""
        st.subheader("새 아티팩트 생성")
        
        with st.form("create_artifact_form"):
            # 기본 정보
            title = st.text_input("제목", placeholder="아티팩트 제목을 입력하세요")
            
            artifact_type = st.selectbox(
                "타입",
                [t.value for t in ArtifactType],
                key="new_artifact_type"
            )
            
            # 내용 입력
            if artifact_type == "image":
                uploaded_file = st.file_uploader(
                    "이미지 파일",
                    type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp']
                )
                content = uploaded_file.getvalue() if uploaded_file else None
            else:
                content = st.text_area(
                    "내용",
                    height=200,
                    placeholder="아티팩트 내용을 입력하세요"
                )
            
            # 태그
            tags_input = st.text_input(
                "태그",
                placeholder="태그를 쉼표로 구분해서 입력하세요 (예: 중요, 작업중, 완료)"
            )
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            
            # 메타데이터
            with st.expander("메타데이터 (선택사항)", expanded=False):
                metadata_json = st.text_area(
                    "JSON 형식의 메타데이터",
                    placeholder='{"key": "value"}',
                    height=100
                )
            
            # 생성 버튼
            submitted = st.form_submit_button("아티팩트 생성")
            
            if submitted:
                if not title:
                    st.error("제목을 입력해주세요.")
                elif not content:
                    st.error("내용을 입력해주세요.")
                else:
                    try:
                        # 메타데이터 파싱
                        metadata = {}
                        if metadata_json.strip():
                            metadata = json.loads(metadata_json)
                        
                        # 아티팩트 생성
                        artifact = self.artifact_manager.create(
                            type_val=ArtifactType(artifact_type),
                            title=title,
                            content=content,
                            tags=tags,
                            metadata=metadata
                        )
                        
                        st.success(f"아티팩트 '{title}'가 생성되었습니다!")
                        st.rerun()
                        
                    except json.JSONDecodeError:
                        st.error("메타데이터의 JSON 형식이 올바르지 않습니다.")
                    except Exception as e:
                        st.error(f"아티팩트 생성 중 오류가 발생했습니다: {e}")

    def _render_statistics_section(self):
        """통계 섹션"""
        st.subheader("아티팩트 통계")
        
        stats = self.artifact_manager.get_statistics()
        
        if stats["total_artifacts"] == 0:
            st.info("아직 아티팩트가 없습니다.")
            return
        
        # 전체 통계
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 아티팩트", stats["total_artifacts"])
        
        with col2:
            st.metric("총 태그", stats["total_tags"])
        
        with col3:
            if stats["most_common_tags"]:
                most_common = stats["most_common_tags"][0]
                st.metric("가장 많은 태그", f"{most_common[0]} ({most_common[1]}개)")
        
        # 타입별 분포
        if stats["by_type"]:
            st.subheader("타입별 분포")
            
            # 차트용 데이터 준비
            import pandas as pd
            
            type_df = pd.DataFrame(
                list(stats["by_type"].items()),
                columns=["타입", "개수"]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.bar_chart(type_df.set_index("타입"))
            
            with col2:
                for type_name, count in stats["by_type"].items():
                    percentage = (count / stats["total_artifacts"]) * 100
                    st.write(f"**{type_name}**: {count}개 ({percentage:.1f}%)")
        
        # 태그 클라우드
        if stats["most_common_tags"]:
            st.subheader("인기 태그")
            
            tag_cols = st.columns(5)
            for i, (tag, count) in enumerate(stats["most_common_tags"][:10]):
                col_idx = i % 5
                with tag_cols[col_idx]:
                    st.metric(tag, count)

    def _render_management_section(self):
        """관리 섹션"""
        st.subheader("아티팩트 관리")
        
        # 일괄 작업
        st.subheader("일괄 작업")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("미사용 파일 정리", key="cleanup_orphaned_btn"):
                with st.spinner("미사용 파일을 정리하는 중..."):
                    cleaned = self.artifact_manager.cleanup_orphaned_files()
                    st.success(f"{cleaned}개의 미사용 파일을 정리했습니다.")
        
        with col2:
            # 전체 아티팩트 내보내기
            if st.button("전체 내보내기", key="export_all_btn"):
                self._export_all_artifacts()
        
        with col3:
            # 아티팩트 가져오기
            uploaded_artifacts = st.file_uploader(
                "아티팩트 가져오기",
                type=['json'],
                key="import_artifacts_uploader"
            )
            
            if uploaded_artifacts:
                self._import_artifacts(uploaded_artifacts)
        
        # 검색 및 일괄 삭제
        st.subheader("고급 검색 및 관리")
        
        with st.expander("일괄 삭제", expanded=False):
            st.warning("⚠️ 주의: 이 작업은 되돌릴 수 없습니다.")
            
            # 삭제 조건
            delete_type = st.selectbox(
                "삭제할 아티팩트 타입",
                ["선택 안함"] + [t.value for t in ArtifactType],
                key="bulk_delete_type"
            )
            
            delete_tags = st.text_input(
                "삭제할 태그 (쉼표로 구분)",
                key="bulk_delete_tags",
                placeholder="태그1, 태그2"
            )
            
            if st.button("선택된 아티팩트 삭제", key="bulk_delete_btn"):
                if delete_type == "선택 안함" and not delete_tags:
                    st.error("삭제 조건을 선택해주세요.")
                else:
                    self._bulk_delete_artifacts(delete_type, delete_tags)

    def _clone_artifact(self, artifact: Artifact):
        """아티팩트 복제"""
        try:
            new_title = f"{artifact.title} (복사본)"
            cloned = self.artifact_manager.create(
                type_val=artifact.type,
                title=new_title,
                content=artifact.content,
                tags=artifact.tags.copy(),
                metadata=artifact.metadata.copy()
            )
            st.success(f"아티팩트가 복제되었습니다: {new_title}")
            st.rerun()
        except Exception as e:
            st.error(f"복제 중 오류가 발생했습니다: {e}")

    def _export_artifact(self, artifact: Artifact):
        """단일 아티팩트 내보내기"""
        try:
            export_data = {
                "artifact": artifact.to_dict(),
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            filename = f"artifact_{artifact.title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            st.download_button(
                "다운로드",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=filename,
                mime="application/json",
                key=f"download_artifact_{artifact.id}"
            )
        except Exception as e:
            st.error(f"내보내기 중 오류가 발생했습니다: {e}")

    def _export_all_artifacts(self):
        """전체 아티팩트 내보내기"""
        try:
            all_artifacts = self.artifact_manager.get_all_artifacts(limit=10000)
            
            export_data = {
                "artifacts": [artifact.to_dict() for artifact in all_artifacts],
                "exported_at": datetime.now().isoformat(),
                "total_count": len(all_artifacts),
                "version": "1.0"
            }
            
            filename = f"all_artifacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            st.download_button(
                "전체 아티팩트 다운로드",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name=filename,
                mime="application/json",
                key="download_all_artifacts"
            )
        except Exception as e:
            st.error(f"내보내기 중 오류가 발생했습니다: {e}")

    def _import_artifacts(self, uploaded_file):
        """아티팩트 가져오기"""
        try:
            import_data = json.load(uploaded_file)
            
            if "artifacts" in import_data:
                # 다중 아티팩트
                artifacts = import_data["artifacts"]
            elif "artifact" in import_data:
                # 단일 아티팩트
                artifacts = [import_data["artifact"]]
            else:
                st.error("올바르지 않은 아티팩트 파일 형식입니다.")
                return
            
            imported_count = 0
            error_count = 0
            
            for artifact_data in artifacts:
                try:
                    artifact = Artifact.from_dict(artifact_data)
                    # 새 ID 생성 (중복 방지)
                    artifact.id = self.artifact_manager.generate_id()
                    
                    self.artifact_manager.create(
                        type_val=artifact.type,
                        title=artifact.title,
                        content=artifact.content,
                        tags=artifact.tags,
                        metadata=artifact.metadata
                    )
                    imported_count += 1
                    
                except Exception as e:
                    logger.error(f"Error importing artifact: {e}")
                    error_count += 1
            
            if imported_count > 0:
                st.success(f"{imported_count}개의 아티팩트를 가져왔습니다.")
            
            if error_count > 0:
                st.warning(f"{error_count}개의 아티팩트 가져오기에 실패했습니다.")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"가져오기 중 오류가 발생했습니다: {e}")

    def _bulk_delete_artifacts(self, delete_type: str, delete_tags: str):
        """일괄 삭제"""
        try:
            # 삭제 조건에 맞는 아티팩트 검색
            search_type = None if delete_type == "선택 안함" else ArtifactType(delete_type)
            search_tags = [tag.strip() for tag in delete_tags.split(',') if tag.strip()] if delete_tags else None
            
            artifacts_to_delete = self.artifact_manager.search(
                type_val=search_type,
                tags=search_tags,
                limit=1000
            )
            
            if not artifacts_to_delete:
                st.info("삭제할 아티팩트가 없습니다.")
                return
            
            # 확인
            if st.session_state.get("confirm_bulk_delete"):
                deleted_count = 0
                for artifact in artifacts_to_delete:
                    if self.artifact_manager.delete(artifact.id):
                        deleted_count += 1
                
                st.success(f"{deleted_count}개의 아티팩트를 삭제했습니다.")
                st.session_state.confirm_bulk_delete = False
                st.rerun()
            else:
                st.warning(f"{len(artifacts_to_delete)}개의 아티팩트가 삭제됩니다. 계속하시겠습니까?")
                st.session_state.confirm_bulk_delete = True
                
        except Exception as e:
            st.error(f"일괄 삭제 중 오류가 발생했습니다: {e}")