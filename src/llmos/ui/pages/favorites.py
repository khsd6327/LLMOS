# src/llmos/ui/pages/favorites.py
"""
LLM OS - 즐겨찾기 모음 페이지
"""
import streamlit as st
import logging
from datetime import datetime

# 즐겨찾기 데이터를 가져오기 위해 FavoriteManager가 필요합니다.
from ...managers.favorite_manager import FavoriteManager
# 일관된 UI 컴포넌트를 위해 EnhancedUI를 사용할 수 있습니다.
from ...ui.components import EnhancedUI

logger = logging.getLogger(__name__)

class FavoritesPage:
    """즐겨찾기 메시지를 보여주고 관리하는 페이지 클래스"""

    def __init__(self, favorite_manager: FavoriteManager, ui: EnhancedUI):
        """
        FavoritesPage를 초기화합니다.

        :param favorite_manager: FavoriteManager 인스턴스
        :param ui: EnhancedUI 인스턴스
        """
        self.favorite_manager = favorite_manager
        self.ui = ui
        self._initialize_state()

    def _initialize_state(self):
        """페이지에 필요한 세션 상태를 초기화합니다."""
        # 검색어, 정렬 순서 등 페이지의 상태를 st.session_state에 저장합니다.
        if "favorites_search_query" not in st.session_state:
            st.session_state.favorites_search_query = ""
        if "favorites_sort_order" not in st.session_state:
            st.session_state.favorites_sort_order = "최신순"  # 기본 정렬

    def render(self):
        """페이지 전체 UI를 렌더링합니다."""
        st.header("⭐ 즐겨찾기 모음")
        st.write("즐겨찾기한 메시지들을 여기서 확인하고 관리할 수 있습니다.")

        # --- 검색 및 정렬 툴바 ---
        self._render_toolbar()
        st.divider()
        # --- 즐겨찾기 목록 ---
        self._render_favorites_list()

    def _render_toolbar(self):
        """검색 및 정렬을 위한 툴바를 렌더링합니다."""
        cols = st.columns([3, 1])
        with cols[0]:
            # 검색창
            st.session_state.favorites_search_query = st.text_input(
                "검색",
                value=st.session_state.favorites_search_query,
                placeholder="내용, 태그, 노트에서 검색..."
            )
        with cols[1]:
            # 정렬 순서 선택
            st.session_state.favorites_sort_order = st.selectbox(
                "정렬",
                ["최신순", "오래된순"],
                index=["최신순", "오래된순"].index(st.session_state.favorites_sort_order)
            )

    def _render_favorites_list(self):
        """필터링 및 정렬된 즐겨찾기 목록을 렌더링합니다."""
        query = st.session_state.favorites_search_query
        sort_descending = (st.session_state.favorites_sort_order == "최신순")

        try:
            # 검색어가 있으면 find_favorites 사용, 없으면 list_all_favorites 사용
            if query:
                # find_favorites는 기본적으로 최신순 정렬이므로, 오래된순일 경우 재정렬 필요
                favorites_list = self.favorite_manager.find_favorites(query=query)
                if not sort_descending:
                    favorites_list.sort(key=lambda fav: fav.favorited_at, reverse=False)
            else:
                favorites_list = self.favorite_manager.list_all_favorites(sort_by_date=True, ascending=not sort_descending)

            if not favorites_list:
                st.info("표시할 즐겨찾기가 없습니다. 채팅 페이지에서 ⭐ 버튼을 눌러 메시지를 추가해보세요.")
                return

            st.write(f"총 **{len(favorites_list)}**개의 즐겨찾기")

            # 각 즐겨찾기 항목을 UI에 표시
            for fav in favorites_list:
                with st.container(border=True):
                    # 메시지 역할과 즐겨찾기된 시간 표시
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.caption(f"작성자: `{fav.role}`")
                    with col2:
                        st.caption(f"즐겨찾기 시각: {fav.favorited_at.strftime('%Y-%m-%d %H:%M')}")

                    # 메시지 본문
                    st.markdown(fav.content, unsafe_allow_html=True)

                    # 상세 정보 및 삭제 버튼
                    with st.expander("상세 정보 및 컨텍스트 보기"):
                        # FavoriteMessage 객체를 딕셔너리로 변환하여 JSON 형태로 표시
                        st.json(fav.to_dict(), expanded=False)

                    if st.button("삭제", key=f"fav_page_delete_{fav.id}", type="secondary", use_container_width=True):
                        self.favorite_manager.remove_favorite(fav.id)
                        st.toast(f"즐겨찾기를 삭제했습니다.", icon="🗑️")
                        st.rerun() # 삭제 후 즉시 목록 갱신

        except Exception as e:
            logger.error(f"즐겨찾기 목록을 렌더링하는 중 오류 발생: {e}", exc_info=True)
            st.error(f"즐겨찾기 목록을 불러오는 중 오류가 발생했습니다.")