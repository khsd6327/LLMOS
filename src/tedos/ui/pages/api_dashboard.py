# ted-os-project/src/tedos/ui/pages/api_dashboard.py
"""
Ted OS - API 대시보드 페이지
"""

import logging

import streamlit as st

from ...managers.settings import SettingsManager
from ...managers.model_manager import EnhancedModelManager
from ...managers.usage_tracker import UsageTracker

logger = logging.getLogger(__name__)


class APIDashboardPage:
    """API 대시보드 페이지 클래스"""

    def __init__(
        self,
        settings_manager: SettingsManager,
        model_manager: EnhancedModelManager,
        usage_tracker: UsageTracker,
    ):
        self.settings = settings_manager
        self.model_manager = model_manager
        self.usage_tracker = usage_tracker

    def render(self):
        """API 대시보드 페이지 렌더링"""
        st.header("🔗 API 대시보드")

        # 뒤로가기 버튼
        if st.button("⬅️ 채팅으로 돌아가기", key="back_from_api_dashboard_btn"):
            st.session_state.show_api_dashboard_page = False
            st.rerun()

        st.markdown("---")

        # 탭으로 섹션 분리
        tabs = st.tabs(["🔌 제공업체 상태", "🔗 플랫폼 링크", "📊 사용량 요약", "⚙️ 빠른 설정"])

        with tabs[0]:
            self._render_provider_status_section()

        with tabs[1]:
            self._render_platform_links_section()

        with tabs[2]:
            self._render_usage_summary_section()

        with tabs[3]:
            self._render_quick_settings_section()

    def _render_provider_status_section(self):
        """제공업체 상태 섹션"""
        st.subheader("🔌 AI 제공업체 연결 상태")
        st.caption("각 AI 제공업체의 API 키 설정 및 연결 상태를 확인하세요.")

        # 기존에 만든 공통 컴포넌트 활용
        provider_status = self.ui.render_provider_status(
            model_manager=self.model_manager,
            settings_manager=self.settings,
            show_test_buttons=True,
            show_details=True,
            key_suffix="api_dashboard"
        )

        # 전체 상태 요약
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if provider_status["active_providers"] > 0:
                st.success(f"✅ {provider_status['active_providers']}개 제공업체 활성")
            else:
                st.error("❌ 활성 제공업체 없음")
        
        with col2:
            if provider_status["errors"] == 0:
                st.success("✅ 오류 없음")
            else:
                st.error(f"❌ {provider_status['errors']}개 오류")
        
        with col3:
            if provider_status["warnings"] == 0:
                st.success("✅ 경고 없음")
            else:
                st.warning(f"⚠️ {provider_status['warnings']}개 경고")

    def _render_platform_links_section(self):
        """플랫폼 링크 섹션"""
        st.subheader("🔗 AI 플랫폼 바로가기")
        st.caption("각 AI 제공업체의 공식 플랫폼으로 바로 이동하세요.")

        # 플랫폼 정보 정의
        platforms = [
            {
                "name": "OpenAI Platform",
                "description": "API 키 관리, 사용량 확인, 모델 문서",
                "url": "https://platform.openai.com/",
                "icon": "🤖",
                "color": "#00A67E",
                "api_key_setting": "api_keys.openai"
            },
            {
                "name": "Anthropic Console",
                "description": "Claude 모델 관리, API 설정, 사용량 모니터링",
                "url": "https://console.anthropic.com/",
                "icon": "🧠",
                "color": "#D4A853",
                "api_key_setting": "api_keys.anthropic"
            },
            {
                "name": "Google AI Studio",
                "description": "Gemini 모델 테스트, API 키 발급, 프로젝트 관리",
                "url": "https://aistudio.google.com/",
                "icon": "🌟",
                "color": "#4285F4",
                "api_key_setting": "api_keys.google"
            }
        ]

        # 플랫폼별 카드 생성
        for platform in platforms:
            has_api_key = bool(self.settings.get(platform["api_key_setting"]))
            status_icon = "🟢" if has_api_key else "🔴"
            status_text = "연결됨" if has_api_key else "미연결"

            with st.container():
                col1, col2, col3 = st.columns([1, 4, 2])
                
                with col1:
                    st.markdown(f"## {platform['icon']}")
                
                with col2:
                    st.markdown(f"**{platform['name']}** {status_icon} {status_text}")
                    st.caption(platform['description'])
                
                with col3:
                    if st.button(
                        f"🔗 {platform['name']} 열기",
                        key=f"open_{platform['name'].lower().replace(' ', '_')}_btn",
                        help=f"{platform['name']} 웹사이트로 이동합니다."
                    ):
                        st.markdown(f"[{platform['name']} 바로가기]({platform['url']})")
                        st.info(f"새 탭에서 {platform['url']} 를 열어주세요.")

                st.divider()

        # 추가 유용한 링크들
        st.subheader("📚 추가 리소스")
        
        additional_links = [
            ("📖 OpenAI API 문서", "https://platform.openai.com/docs/"),
            ("📖 Anthropic API 문서", "https://docs.anthropic.com/"),
            ("📖 Google AI API 문서", "https://ai.google.dev/docs"),
            ("💰 OpenAI 가격 정보", "https://openai.com/pricing"),
            ("💰 Anthropic 가격 정보", "https://www.anthropic.com/pricing"),
            ("💰 Google AI 가격 정보", "https://ai.google.dev/pricing"),
        ]

        cols = st.columns(2)
        for i, (title, url) in enumerate(additional_links):
            with cols[i % 2]:
                if st.button(title, key=f"resource_link_{i}", use_container_width=True):
                    st.markdown(f"[{title} 바로가기]({url})")
                    st.info(f"새 탭에서 {url} 를 열어주세요.")

    def _render_usage_summary_section(self):
        """사용량 요약 섹션"""
        st.subheader("📊 API 사용량 요약")
        st.caption("최근 API 사용량과 비용을 확인하세요.")

        try:
            # 기존 사용량 통계 컴포넌트 재사용
            self.ui.render_usage_stats(self.usage_tracker)

            # 추가 상세 정보
            st.markdown("---")
            st.subheader("📈 상세 사용량 분석")

            # 최근 7일 사용량 트렌드
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🗓️ 주간 사용량")
                weekly_usage = self.usage_tracker.get_weekly_usage()
                
                # 주간 사용량 메트릭
                st.metric("주간 요청", f"{weekly_usage['total_requests']:,}")
                st.metric("주간 토큰", f"{weekly_usage['total_tokens']:,}")
                weekly_cost_str = (
                    f"${weekly_usage['total_cost']:.4f}"
                    if weekly_usage["total_cost"] > 0.00001
                    else "$0.00"
                )
                st.metric("주간 비용", weekly_cost_str)

            with col2:
                st.markdown("#### 📅 월간 사용량")
                monthly_usage = self.usage_tracker.get_monthly_usage()
                
                # 월간 사용량 메트릭
                st.metric("월간 요청", f"{monthly_usage['total_requests']:,}")
                st.metric("월간 토큰", f"{monthly_usage['total_tokens']:,}")
                monthly_cost_str = (
                    f"${monthly_usage['total_cost']:.4f}"
                    if monthly_usage["total_cost"] > 0.00001
                    else "$0.00"
                )
                st.metric("월간 비용", monthly_cost_str)

            # 모델별 사용량 (최근 30일)
            st.markdown("#### 🤖 모델별 사용량 (최근 30일)")
            model_usage = self.usage_tracker.get_usage_by_model(30)
            
            if model_usage:
                import pandas as pd
                
                model_data = []
                for model, stats in model_usage.items():
                    model_data.append({
                        "모델": model,
                        "요청 수": stats["requests"],
                        "토큰 수": f"{stats['tokens']:,}",
                        "비용 (USD)": f"${stats['cost']:.4f}",
                    })
                
                df = pd.DataFrame(model_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("모델별 사용량 데이터가 없습니다.")

        except Exception as e:
            logger.error(f"Error rendering usage summary: {e}")
            st.error(f"사용량 정보를 불러오는 중 오류가 발생했습니다: {e}")

    def _render_quick_settings_section(self):
        """빠른 설정 섹션"""
        st.subheader("⚙️ 빠른 API 설정")
        st.caption("API 키 설정과 기본 매개변수를 빠르게 조정하세요.")

        # API 키 빠른 설정
        st.markdown("#### 🔑 API 키 빠른 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔧 API 키 설정 페이지로 이동", key="goto_api_keys_btn", use_container_width=True):
                st.session_state.show_api_dashboard_page = False
                st.session_state.show_settings_page = True
                st.rerun()
        
        with col2:
            if st.button("🐛 디버그 페이지로 이동", key="goto_debug_btn", use_container_width=True):
                st.session_state.show_api_dashboard_page = False
                st.session_state.show_debug_page = True
                st.rerun()

        st.markdown("---")

        # 빠른 모델 선택
        st.markdown("#### 🤖 빠른 모델 선택")
        
        # 현재 선택된 모델 정보 표시
        current_provider = self.settings.get("ui.selected_provider")
        if current_provider:
            current_model = self.settings.get_default_model_for_provider(current_provider)
            if current_model:
                st.info(f"현재 선택: **{current_provider}** - **{current_model}**")
            else:
                st.warning(f"현재 제공업체: **{current_provider}** (모델 미선택)")
        else:
            st.warning("제공업체가 선택되지 않았습니다.")

        # 모델 선택 컴포넌트
        provider_name, model_key = self.ui.render_model_selector(self.settings)
        
        if provider_name and model_key:
            st.success(f"✅ {provider_name}/{model_key} 선택됨")

        st.markdown("---")

        # 빠른 생성 매개변수 조정
        st.markdown("#### ⚙️ 빠른 매개변수 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature 빠른 조정
            current_temp = self.settings.get("defaults.temperature", 0.7)
            new_temp = st.select_slider(
                "🌡️ Temperature (창의성)",
                options=[0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0],
                value=current_temp,
                key="quick_temp_slider",
                help="낮을수록 일관적, 높을수록 창의적"
            )
            
            if new_temp != current_temp:
                self.settings.set("defaults.temperature", new_temp)
                st.success(f"Temperature을 {new_temp}로 설정했습니다.")

        with col2:
            # Max Tokens 빠른 조정
            current_max_tokens = self.settings.get("defaults.max_tokens", 4096)
            token_options = [512, 1024, 2048, 4096, 8192, 16384, 32768]
            
            # 현재 값이 옵션에 없으면 추가
            if current_max_tokens not in token_options:
                token_options.append(current_max_tokens)
                token_options.sort()
            
            new_max_tokens = st.selectbox(
                "📏 최대 토큰 (응답 길이)",
                options=token_options,
                index=token_options.index(current_max_tokens),
                key="quick_max_tokens_select",
                help="AI 응답의 최대 길이"
            )
            
            if new_max_tokens != current_max_tokens:
                self.settings.set("defaults.max_tokens", new_max_tokens)
                st.success(f"최대 토큰을 {new_max_tokens:,}로 설정했습니다.")

        # 사용량 추적 설정
        st.markdown("---")
        st.markdown("#### 📊 사용량 추적 설정")
        
        usage_tracking = st.checkbox(
            "사용량 추적 활성화",
            value=self.settings.get("features.usage_tracking", True),
            key="quick_usage_tracking_toggle",
            help="토큰 사용량과 비용을 자동으로 추적합니다."
        )
        
        if usage_tracking != self.settings.get("features.usage_tracking", True):
            self.settings.set("features.usage_tracking", usage_tracking)
            if usage_tracking:
                st.success("✅ 사용량 추적이 활성화되었습니다.")
            else:
                st.info("ℹ️ 사용량 추적이 비활성화되었습니다.")
