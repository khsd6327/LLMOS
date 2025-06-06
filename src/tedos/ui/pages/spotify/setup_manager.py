# ted-os-project/src/tedos/ui/pages/spotify/setup_manager.py
"""
Ted OS - Spotify 설정 및 인증 관리자
"""

import logging

import streamlit as st

from ....managers.spotify_manager import SpotifyManager

logger = logging.getLogger(__name__)


class SetupManager:
    """Spotify 설정 및 인증 전담 클래스"""

    def __init__(self, spotify_manager: SpotifyManager):
        self.spotify_manager = spotify_manager

    def render_spotify_setup(self):
        """Spotify 설정 UI"""
        st.warning("⚠️ Spotify API 설정이 필요합니다.")
        
        st.markdown(
            """
            ### 🎵 Spotify API 설정
            
            TedOS에서 Spotify 기능을 사용하려면, Spotify 개발자 대시보드에서 애플리케이션을 생성하고 다음 정보를 얻어야 합니다:
            
            1. **Client ID**
            2. **Client Secret**  
            3. **Redirect URI 설정:** `http://127.0.0.1:8888/callback` (또는 아래 입력한 URI)을 Spotify 앱 설정에 추가해야 합니다.
            
            [📱 Spotify Developer Dashboard 바로가기](https://developer.spotify.com/dashboard/)
            """
        )
        
        # 현재 저장된 설정 불러오기
        settings_manager = self.spotify_manager.settings_manager
        saved_client_id = settings_manager.get("spotify_client_id", "")
        saved_client_secret = settings_manager.get("spotify_client_secret", "")
        saved_redirect_uri = settings_manager.get("spotify_redirect_uri", "http://127.0.0.1:8888/callback")
        saved_port_type = settings_manager.get("spotify_port_type", "fixed")
        
        # 설정 입력 폼
        with st.form("spotify_api_setup_form"):
            st.markdown("#### 📝 API 정보 입력")
            
            client_id = st.text_input(
                "Spotify Client ID",
                value=saved_client_id,
                key="spotify_setup_client_id",
                help="Spotify 개발자 대시보드에서 발급받은 Client ID입니다."
            )
            
            client_secret = st.text_input(
                "Spotify Client Secret",
                value=saved_client_secret,
                type="password",
                key="spotify_setup_client_secret", 
                help="Spotify 개발자 대시보드에서 발급받은 Client Secret입니다."
            )
            
            redirect_uri = st.text_input(
                "Spotify Redirect URI",
                value=saved_redirect_uri,
                key="spotify_setup_redirect_uri",
                help="Spotify 앱 설정에 등록한 Redirect URI와 정확히 일치해야 합니다."
            )
            
            port_options = ["fixed", "dynamic"]
            try:
                default_port_index = port_options.index(saved_port_type)
            except ValueError:
                default_port_index = 0
                
            port_type = st.radio(
                "인증 시 사용할 로컬 포트 타입",
                options=port_options,
                index=default_port_index,
                format_func=lambda x: "고정 포트 (예: 8888)" if x == "fixed" else "동적 포트 (자동 할당)",
                key="spotify_setup_port_type",
                help="대부분의 경우 기본값을 유지해도 괜찮습니다."
            )
            
            # 저장 버튼
            submitted = st.form_submit_button("💾 설정 저장 및 연결", use_container_width=True)
            
            if submitted:
                if client_id and client_secret and redirect_uri:
                    try:
                        # SpotifyManager를 통해 설정 저장
                        success = self.spotify_manager.save_spotify_settings(
                            client_id=client_id,
                            client_secret=client_secret, 
                            redirect_uri=redirect_uri,
                            port_type=port_type
                        )
                        
                        if success:
                            # session_state에 성공 상태 저장
                            st.session_state['spotify_setup_success'] = True
                        else:
                            st.error("❌ 설정 저장 중 오류가 발생했습니다. 다시 시도해주세요.")
                            
                    except Exception as e:
                        st.error(f"❌ 설정 저장 중 오류가 발생했습니다: {str(e)}")
                        logger.error(f"Error saving Spotify settings in setup: {e}")
                else:
                    st.error("⚠️ Client ID, Client Secret, Redirect URI는 반드시 입력해야 합니다.")
        
        # 성공 메시지 표시 (session_state 기반)
        if st.session_state.get('spotify_setup_success', False):
            st.success("✅ Spotify API 설정이 성공적으로 저장되었습니다!")
            st.info("🔄 페이지를 새로고침하여 인증을 진행하세요.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 인증 단계로 이동", use_container_width=True):
                    st.session_state['spotify_setup_success'] = False  # 상태 초기화
                    st.rerun()
            with col2:
                if st.button("❌ 메시지 닫기", use_container_width=True):
                    st.session_state['spotify_setup_success'] = False  # 상태 초기화
                    st.rerun()
        
        # 추가 도움말
        with st.expander("🤔 설정 방법이 궁금하다면", expanded=False):
            st.markdown(
                """
                ### Spotify 개발자 앱 설정 가이드
                
                1. **[Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)** 접속
                2. **"Create app"** 클릭
                3. 앱 정보 입력:
                   - **App name**: 원하는 이름 (예: "My TedOS App")
                   - **App description**: 간단한 설명
                   - **Redirect URI**: `http://127.0.0.1:8888/callback` 입력
                   - **API/SDKs**: Web API 선택
                4. 생성된 앱에서 **Client ID**와 **Client Secret** 복사
                5. 위 폼에 입력하고 저장
                
                💡 **주의사항**: Redirect URI는 정확히 일치해야 합니다!
                """
            )

    def render_authentication(self):
        """Spotify 인증 UI"""
        st.info("🔐 Spotify 인증이 필요합니다.")
        
        if st.button("🎵 Spotify 로그인", use_container_width=True):
            with st.spinner("인증 중..."):
                if self.spotify_manager.authenticate():
                    st.success("✅ 인증 성공!")
                    st.rerun()
                else:
                    st.error("❌ 인증 실패. 설정을 확인해주세요.")