# setup.py
"""
LLM OS 설치 스크립트
"""

from setuptools import setup, find_packages
from pathlib import Path

# 프로젝트 루트 디렉토리
here = Path(__file__).parent.resolve()

# README 파일 읽기
long_description = (here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else ""

# requirements.txt에서 의존성 읽기
def read_requirements():
    requirements_file = here / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, encoding="utf-8") as f:
            return [
                line.strip() 
                for line in f 
                if line.strip() and not line.startswith("#")
            ]
    return []

# 버전 정보 가져오기
def get_version():
    try:
        from src.llmos.core.config import APP_VERSION
        return APP_VERSION
    except ImportError:
        return "0.0.9"  # 기본값

setup(
    name="llmos",
    version=get_version(),
    author="LLM OS Team",  
    author_email="dev@llmos.com",
    description="개인 맞춤형 AI 비서 시스템",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llmos/llmos",
    project_urls={
        "Bug Reports": "https://github.com/llmos/llmos/issues",
        "Source": "https://github.com/llmos/llmos",
        "Documentation": "https://llmos.readthedocs.io/",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="ai, llm, chatbot, assistant, openai, anthropic, google, streamlit",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0", 
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pytest-cov>=4.0.0",
        ],
        "performance": [
            "psutil>=5.9.0",
            "ujson>=5.7.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0", 
            "mypy>=1.0.0",
            "pytest-cov>=4.0.0",
            "psutil>=5.9.0",
            "ujson>=5.7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "llmos=src.llmos.core.app:run_app",
        ],
    },
    include_package_data=True,
    package_data={
        "llmos": [
            "ui/styles/*.css",
            "*.json",
            "*.yaml",
            "*.yml"
        ],
    },
    zip_safe=False,
    platforms=["any"],
)

# 설치 후 메시지
print("""
🧠 LLM OS 설치가 완료되었습니다!

사용법:
1. API 키 설정:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   - Google: https://ai.google.dev/

2. 애플리케이션 실행:
   streamlit run main.py

3. 문서:
   https://github.com/llmos/llmos/blob/main/README.md

문제가 있으시면 GitHub Issues를 통해 신고해 주세요.
https://github.com/llmos/llmos/issues
""")