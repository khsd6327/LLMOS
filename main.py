# main.py
"""
LLM OS - 메인 실행 파일
개인 맞춤형 AI 비서 시스템

사용법:
    streamlit run main.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 메인 애플리케이션 임포트
from src.llmos.core.app import run_app

if __name__ == "__main__":
    print("🧠 LLM OS - 개인 맞춤형 AI 비서 시스템")
    print("=" * 50)
    print("시작 중...")
    
    try:
        run_app()
    except KeyboardInterrupt:
        print("\n애플리케이션이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n오류가 발생했습니다: {e}")
        sys.exit(1)