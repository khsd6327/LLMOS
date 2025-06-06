# ted-os-project/src/tedos/ui/pages/debug/data_inspector.py
"""
Ted OS - 데이터 검사 담당 모듈 (세션, 즐겨찾기, 성능)
"""

import logging
import streamlit as st

from ....managers.chat_sessions import ChatSessionManager
from ....managers.usage_tracker import UsageTracker
from ....managers.favorite_manager import FavoriteManager

logger = logging.getLogger(__name__)


class DataInspector:
    """데이터 검사 및 표시 전담 클래스"""

    def __init__(
        self,
        chat_manager: ChatSessionManager,
        usage_tracker: UsageTracker,
        favorite_manager: FavoriteManager,
    ):
        self.chat_manager = chat_manager
        self.usage_tracker = usage_tracker
        self.favorite_manager = favorite_manager

    def render_sessions_section(self):
        """세션 섹션"""
        st.subheader("채팅 세션 정보")

        # 세션 통계
        session_stats = self.chat_manager.get_session_statistics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("총 세션", session_stats["total_sessions"])

        with col2:
            st.metric("총 메시지", session_stats["total_messages"])

        with col3:
            avg_messages = session_stats.get("avg_messages_per_session", 0)
            st.metric("평균 메시지/세션", f"{avg_messages:.1f}")

        with col4:
            if st.button("빈 세션 정리", key="cleanup_empty_sessions_btn"):
                deleted = self.chat_manager.cleanup_empty_sessions()
                st.success(f"{deleted}개의 빈 세션을 정리했습니다.")
                st.rerun()

        # 현재 세션 상세 정보
        current_session = st.session_state.get("current_session")
        if current_session:
            st.subheader("현재 세션 상세")

            with st.expander(f"세션: {current_session.title}", expanded=False):
                session_info = {
                    "ID": current_session.id,
                    "제목": current_session.title,
                    "메시지 수": len(current_session.messages),
                    "생성일": current_session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "수정일": current_session.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                }

                for key, value in session_info.items():
                    st.text(f"{key}: {value}")

                # 메시지 분석
                if current_session.messages:
                    user_msgs = sum(
                        1 for m in current_session.messages if m["role"] == "user"
                    )
                    assistant_msgs = sum(
                        1 for m in current_session.messages if m["role"] == "assistant"
                    )

                    st.write(f"사용자 메시지: {user_msgs}개")
                    st.write(f"AI 응답: {assistant_msgs}개")

        # 전체 세션 목록
        st.subheader("전체 세션 목록")

        all_sessions = self.chat_manager.get_all_sessions()
        if all_sessions:
            session_data = []
            for session in all_sessions[:20]:  # 최대 20개만 표시
                session_data.append(
                    {
                        "ID": session.id[:8] + "...",
                        "제목": session.title[:30]
                        + ("..." if len(session.title) > 30 else ""),
                        "메시지": len(session.messages),
                        "수정일": session.updated_at.strftime("%Y-%m-%d %H:%M"),
                    }
                )

            import pandas as pd

            df = pd.DataFrame(session_data)
            st.dataframe(df, use_container_width=True)

            if len(all_sessions) > 20:
                st.info(f"+ {len(all_sessions) - 20}개 더 있음")
        else:
            st.info("저장된 세션이 없습니다.")

    def render_favorites_section(self):
        """즐겨찾기 정보 섹션 (디버그용)"""
        st.subheader("⭐ 저장된 즐겨찾기 메시지")

        if not hasattr(self, 'favorite_manager') or not self.favorite_manager:
            st.warning("FavoriteManager가 DebugPage에 제대로 전달되지 않았거나 초기화되지 않았습니다.")
            return

        try:
            if st.button("즐겨찾기 목록 새로고침", key="refresh_favorites_debug_btn"):
                # FavoriteManager 내부의 _favorites는 _load_favorites() 호출 시 갱신됨
                # 또는 간단히 st.rerun()을 통해 UI를 다시 그리면서 데이터를 다시 로드하게 할 수 있음
                self.favorite_manager._favorites = self.favorite_manager._load_favorites() # 내부 캐시 직접 갱신
                st.rerun()

            all_favorites = self.favorite_manager.list_all_favorites(sort_by_date=True, ascending=False)
            
            st.metric("총 즐겨찾기 개수", len(all_favorites))

            if not all_favorites:
                st.info("저장된 즐겨찾기가 없습니다.")
                return

            st.write("최근 즐겨찾기 목록 (최대 10개):")
            for i, fav in enumerate(all_favorites[:10]):
                exp_title = f"ID: {fav.id} | 내용: {fav.content[:40]}"
                exp_title += "..." if len(fav.content) > 40 else ""
                
                with st.expander(exp_title, expanded=False):
                    # FavoriteMessage 객체의 내용을 좀 더 상세히 보여주기
                    st.json(fav.to_dict(), expanded=False) # 객체를 dict로 변환하여 JSON 형태로 표시
                    
                    # 간단한 삭제 기능 (디버그용)
                    if st.button("이 즐겨찾기 삭제", key=f"delete_fav_debug_{fav.id}_{i}", type="secondary"):
                        if self.favorite_manager.remove_favorite(fav.id):
                            st.success(f"즐겨찾기 '{fav.id}'가 삭제되었습니다.")
                            # 목록을 즉시 갱신하기 위해 rerun 필요
                            st.rerun()
                        else:
                            st.error(f"즐겨찾기 '{fav.id}' 삭제에 실패했습니다.")
        except Exception as e:
            logger.error(f"즐겨찾기 정보 로드/표시 중 오류: {e}", exc_info=True)
            st.error(f"즐겨찾기 정보를 가져오는 중 오류가 발생했습니다: {str(e)}")

    def render_performance_section(self):
        """성능 섹션"""
        st.subheader("성능 정보")

        # 사용량 통계
        usage_stats = {
            "오늘": self.usage_tracker.get_today_usage_from_summary(),
            "주간": self.usage_tracker.get_weekly_usage(),
            "월간": self.usage_tracker.get_monthly_usage(),
        }

        # 메트릭 표시
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("오늘")
            today = usage_stats["오늘"]
            st.metric("요청", f"{today['total_requests']:,}")
            st.metric("토큰", f"{today['total_tokens']:,}")
            st.metric("비용", f"${today['total_cost']:.4f}")

        with col2:
            st.subheader("이번 주")
            weekly = usage_stats["주간"]
            st.metric("요청", f"{weekly['total_requests']:,}")
            st.metric("토큰", f"{weekly['total_tokens']:,}")
            st.metric("비용", f"${weekly['total_cost']:.4f}")

        with col3:
            st.subheader("이번 달")
            monthly = usage_stats["월간"]
            st.metric("요청", f"{monthly['total_requests']:,}")
            st.metric("토큰", f"{monthly['total_tokens']:,}")
            st.metric("비용", f"${monthly['total_cost']:.4f}")

        # 모델별 사용량
        st.subheader("모델별 사용량 (최근 30일)")

        model_usage = self.usage_tracker.get_usage_by_model(30)
        if model_usage:
            model_data = []
            for model, stats in model_usage.items():
                model_data.append(
                    {
                        "모델": model,
                        "요청": stats["requests"],
                        "토큰": f"{stats['tokens']:,}",
                        "비용": f"${stats['cost']:.4f}",
                    }
                )

            import pandas as pd

            df = pd.DataFrame(model_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("모델 사용량 데이터가 없습니다.")

        # 메모리 사용량 (참고용)
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            st.subheader("메모리 사용량")
            st.text(f"RSS: {memory_info.rss / 1024 / 1024:.1f} MB")
            st.text(f"VMS: {memory_info.vms / 1024 / 1024:.1f} MB")

        except ImportError:
            st.info("메모리 정보를 보려면 psutil 패키지를 설치하세요.")