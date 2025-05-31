# src/llmos/core/config.py
"""
LLM OS - 전역 설정 및 상수 정의
"""

# 애플리케이션 정보
APP_VERSION = "0.1.0"
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
PAGE_ICON = "🧠"
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