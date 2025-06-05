# ted-os-project/src/llmos/core/config.py
# src/llmos/core/config.py
"""
LLM OS - 전역 설정 및 상수 정의
"""

# 애플리케이션 정보
APP_VERSION = "0.1.4.5"
APP_NAME = "LLM OS"
APP_DESCRIPTION = "개인 맞춤형 AI 비서 시스템"

# 기본 설정값
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096
MAX_HISTORY_LENGTH = 10
LOG_HANDLER_MAX_LEN = 200

# UI 관련 설정
UI_CHAT_INPUT_PLACEHOLDER = "메시지를 입력하거나 이미지를 첨부하세요..."
SUPPORTED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "webp", "gif", "bmp"]

# 페이지 설정 관련
PAGE_ICON = "😽"
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# 사이드바 관련 설정
SIDEBAR_MAX_SESSIONS = 10
SESSION_TITLE_MAX_LENGTH = 30

# 파일 및 디렉토리 설정
DEFAULT_CONFIG_DIR = ".llm_os_config"
CHAT_SESSIONS_DIR = "chat_sessions"
ARTIFACTS_DIR = "artifacts"
USAGE_DATA_DIR = "usage_data"
FAVORITES_DIR = "favorites"

# 데이터 관리 설정
DATA_CLEANUP_KEEP_DAYS = 90

# API 관련 설정
API_RETRY_ATTEMPTS = 3
API_TIMEOUT_SECONDS = 30
STREAMING_CHUNK_SIZE = 1024

# 토큰 및 비용 계산 설정
TOKEN_ESTIMATION_BUFFER = 1.1  # 10% 여유분
MAX_CONTEXT_TOKENS = 128000

# 로깅 설정
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# UI 스타일 관련
SIDEBAR_WIDTH = 300
CHAT_CONTAINER_HEIGHT = 600
CODE_BLOCK_MAX_HEIGHT = 200

# Spotify 관련 설정
SPOTIFY_DEFAULT_REDIRECT_URI = "http://127.0.0.1:8888/callback"
SPOTIFY_DEFAULT_PORT_TYPE = "fixed"
SPOTIFY_TOKEN_CACHE_FILENAME = ".spotify_token_cache"
SPOTIFY_CACHE_DIR_NAME = "spotify_cache"
SPOTIFY_CONFIG_DIR_NAME = ".llmos"
SPOTIFY_CACHE_EXPIRY_HOURS = 24

# Spotify 캐시 키
SPOTIFY_CACHE_KEY_USER_PLAYLISTS = "user_playlists"
SPOTIFY_CACHE_KEY_SAVED_TRACKS = "saved_tracks"
SPOTIFY_CACHE_KEY_TOP_TRACKS_PREFIX = "top_tracks"
SPOTIFY_CACHE_KEY_RECENT_FREQUENT_PREFIX = "recent_frequent"
SPOTIFY_CACHE_KEY_PLAYLIST_TRACKS_PREFIX = "playlist_tracks"

# 기본 AI 모델 설정
DEFAULT_MODELS = {
    "OpenAI": "gpt-4.1-mini",
    "Google": "gemini-2.5-flash-preview-05-20", 
    "Anthropic": "claude-sonnet-4-20250514",
}
DEFAULT_PROVIDER = "Anthropic"

# Spotify 설정 키
SPOTIFY_SETTING_CLIENT_ID = "spotify_client_id"
SPOTIFY_SETTING_CLIENT_SECRET = "spotify_client_secret"
SPOTIFY_SETTING_REDIRECT_URI = "spotify_redirect_uri"
SPOTIFY_SETTING_PORT_TYPE = "spotify_port_type"