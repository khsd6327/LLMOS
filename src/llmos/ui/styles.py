# src/llmos/ui/styles.py
"""
LLM OS - UI 스타일 정의
"""

import streamlit as st


def load_custom_css():
    """커스텀 CSS 로드"""
    st.markdown("""
    <style>
        /* 메인 앱 레이아웃 */
        .stApp { 
            margin-top: -70px !important; 
        }
        
        /* 헤더 및 메뉴 숨기기 */
        #MainMenu, footer, header[data-testid="stHeader"] { 
            visibility: hidden !important; 
        }
        
        /* 사이드바 버튼 스타일 */
        div[data-testid="stSidebarUserContent"] .stButton > button {
            width: 100%; 
            border-radius: 0.3rem; 
            border: 1px solid #ddd;
            margin-bottom: 0.3rem; 
            text-align: left; 
            padding: 0.4rem 0.6rem;
            transition: all 0.2s ease;
        }
        
        div[data-testid="stSidebarUserContent"] .stButton > button:hover {
            border-color: #007bff; 
            background-color: #f0f8ff;
            transform: translateX(2px);
        }
        
        /* 채팅 메시지 버튼 스타일 */
        .stChatMessage .stButton > button { 
            padding: 0.1rem 0.3rem; 
            font-size: 0.75rem; 
            margin: 0.1rem;
            border: none; 
            background: #f0f2f6; 
            border-radius: 0.2rem;
            transition: background 0.2s ease;
        }
        
        .stChatMessage .stButton > button:hover { 
            background: #e0e0e0; 
        }
        
        /* 코드 블록 스타일 */
        .stCodeBlock { 
            max-height: 200px; 
            overflow-y: auto; 
            font-size: 0.85em;
            border-radius: 0.5rem;
        }
        
        /* 채팅 입력창 스타일 */
        .stChatInput > div > div > div > div {
            border-radius: 1rem;
        }
        
        /* 메트릭 카드 스타일 */
        [data-testid="metric-container"] {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 0.5rem;
            border-radius: 0.5rem;
            margin: 0.1rem;
        }
        
        /* 확장기 스타일 */
        .streamlit-expanderHeader {
            font-weight: 600;
            border-radius: 0.3rem;
        }
        
        /* 파일 업로더 스타일 */
        .stFileUploader > div > div > div {
            border-radius: 0.5rem;
            border-style: dashed;
        }
        
        /* 알림 스타일 */
        .stAlert {
            border-radius: 0.5rem;
            border-left: 4px solid;
        }
        
        /* 사용자 정의 클래스들 */
        .llmos-header {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(90deg, #007bff, #28a745);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .llmos-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 0.75rem;
            padding: 1rem;
            margin: 0.5rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .llmos-status-success {
            color: #28a745;
            font-weight: 600;
        }
        
        .llmos-status-error {
            color: #dc3545;
            font-weight: 600;
        }
        
        .llmos-status-warning {
            color: #ffc107;
            font-weight: 600;
        }
        
        .llmos-status-info {
            color: #17a2b8;
            font-weight: 600;
        }
        
        .llmos-model-info {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.7);
            margin-top: 0.25rem;
        }
        
        .llmos-usage-metric {
            text-align: center;
            padding: 0.5rem;
            background: rgba(0, 123, 255, 0.1);
            border-radius: 0.5rem;
            margin: 0.2rem;
        }
        
        .llmos-session-item {
            padding: 0.5rem;
            margin: 0.2rem 0;
            border-radius: 0.3rem;
            border-left: 3px solid #007bff;
            background: rgba(255, 255, 255, 0.02);
        }
        
        .llmos-session-item:hover {
            background: rgba(255, 255, 255, 0.05);
            transform: translateX(2px);
            transition: all 0.2s ease;
        }
        
        /* 다크 테마 지원 */
        @media (prefers-color-scheme: dark) {
            .llmos-card {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            
            .llmos-session-item {
                background: rgba(255, 255, 255, 0.01);
            }
            
            .llmos-session-item:hover {
                background: rgba(255, 255, 255, 0.03);
            }
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .stApp {
                margin-top: -50px !important;
            }
            
            .llmos-header {
                font-size: 1.5rem;
            }
            
            .stChatMessage .stButton > button {
                font-size: 0.7rem;
                padding: 0.05rem 0.2rem;
            }
        }
        
        /* 스크롤바 스타일 */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.5);
        }
        
        /* 애니메이션 */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slideIn {
            from { transform: translateX(-10px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .llmos-fade-in {
            animation: fadeIn 0.3s ease-out;
        }
        
        .llmos-slide-in {
            animation: slideIn 0.3s ease-out;
        }
        
        /* 로딩 애니메이션 */
        .llmos-loading {
            display: inline-block;
            width: 1rem;
            height: 1rem;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #007bff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* 호버 효과 */
        .llmos-hover-lift:hover {
            transform: translateY(-2px);
            transition: transform 0.2s ease;
        }
        
        .llmos-hover-glow:hover {
            box-shadow: 0 0 10px rgba(0, 123, 255, 0.3);
            transition: box-shadow 0.2s ease;
        }
    </style>
    """, unsafe_allow_html=True)


def apply_theme(theme: str = "auto"):
    """테마 적용"""
    if theme == "dark":
        st.markdown("""
        <style>
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
        </style>
        """, unsafe_allow_html=True)
    elif theme == "light":
        st.markdown("""
        <style>
            .stApp {
                background-color: #ffffff;
                color: #262730;
            }
        </style>
        """, unsafe_allow_html=True)


def render_custom_header(title: str, subtitle: str = ""):
    """커스텀 헤더 렌더링"""
    st.markdown(f"""
    <div class="llmos-header llmos-fade-in">
        {title}
    </div>
    """, unsafe_allow_html=True)
    
    if subtitle:
        st.markdown(f"""
        <div style="font-size: 1.1rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 2rem;">
            {subtitle}
        </div>
        """, unsafe_allow_html=True)


def render_status_badge(status: str, text: str):
    """상태 배지 렌더링"""
    status_class = f"llmos-status-{status}"
    st.markdown(f"""
    <span class="{status_class}">
        {text}
    </span>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, delta: str = "", color: str = "blue"):
    """메트릭 카드 렌더링"""
    st.markdown(f"""
    <div class="llmos-usage-metric llmos-hover-lift">
        <div style="font-size: 0.8rem; opacity: 0.8;">{title}</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: {color};">{value}</div>
        {f'<div style="font-size: 0.7rem; opacity: 0.6;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)


def render_session_item(title: str, subtitle: str = "", is_active: bool = False):
    """세션 아이템 렌더링"""
    active_class = "llmos-session-active" if is_active else ""
    st.markdown(f"""
    <div class="llmos-session-item {active_class} llmos-slide-in">
        <div style="font-weight: 600; font-size: 0.9rem;">{title}</div>
        {f'<div style="font-size: 0.7rem; opacity: 0.7;">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def show_loading(text: str = "로딩 중..."):
    """로딩 표시"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div class="llmos-loading"></div>
        <div style="margin-top: 1rem; opacity: 0.7;">{text}</div>
    </div>
    """, unsafe_allow_html=True)