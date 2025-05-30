# tests/__init__.py
"""
LLM OS 테스트 모듈
"""

import os
import sys
from pathlib import Path

# 테스트를 위한 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 테스트 환경 변수 설정
os.environ["LLMOS_TEST_MODE"] = "true"
os.environ["LLMOS_CONFIG_DIR"] = str(project_root / "test_config")

# 테스트용 더미 API 키 설정
os.environ["OPENAI_API_KEY"] = "test-openai-key"
os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
os.environ["GOOGLE_API_KEY"] = "test-google-key"