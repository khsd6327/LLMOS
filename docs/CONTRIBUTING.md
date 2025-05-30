# 🤝 LLM OS 기여 가이드

LLM OS 프로젝트에 기여해주셔서 감사합니다! 이 문서는 프로젝트에 효과적으로 기여하는 방법을 안내합니다.

## 📋 목차

- [시작하기 전에](#시작하기-전에)
- [개발 환경 설정](#개발-환경-설정)
- [기여 방법](#기여-방법)
- [코딩 스타일](#코딩-스타일)
- [테스트](#테스트)
- [Pull Request 프로세스](#pull-request-프로세스)
- [이슈 리포팅](#이슈-리포팅)
- [커뮤니티 가이드라인](#커뮤니티-가이드라인)

## 시작하기 전에

### 🎯 프로젝트 목표 이해하기

LLM OS는 다음을 목표로 합니다:

- **사용자 친화적**: 누구나 쉽게 AI를 활용할 수 있도록
- **모듈화**: 확장 가능하고 유지보수하기 쉬운 구조
- **성능**: 효율적이고 빠른 응답
- **보안**: 사용자 데이터와 프라이버시 보호
- **오픈소스**: 투명하고 협력적인 개발

### 📚 필수 지식

기여하기 전에 다음 기술들에 대한 기본 지식이 있으면 도움이 됩니다:

- **Python 3.8+**: 주 개발 언어
- **Streamlit**: 웹 UI 프레임워크
- **Git**: 버전 관리
- **API 통합**: REST API 사용 경험
- **AI/ML 기초**: LLM 모델에 대한 이해

## 개발 환경 설정

### 1. 저장소 포크 및 클론

```bash
# GitHub에서 저장소를 Fork한 후
git clone https://github.com/YOUR_USERNAME/llmos.git
cd llmos

# 원본 저장소를 upstream으로 추가
git remote add upstream https://github.com/llmos/llmos.git
```

### 2. 개발 환경 구성

```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 개발용 의존성 설치
pip install -e .[dev]

# pre-commit 훅 설치 (선택사항)
pre-commit install
```

### 3. 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp .env.example .env

# .env 파일에 테스트용 API 키 입력
# (실제 API 키 또는 테스트용 더미 키)
```

### 4. 애플리케이션 실행 확인

```bash
# 애플리케이션 실행
streamlit run main.py

# 또는 테스트 실행
pytest tests/
```

## 기여 방법

### 🐛 버그 수정

1. **이슈 확인**: GitHub Issues에서 관련 버그 확인
2. **재현**: 버그를 로컬에서 재현
3. **수정**: 최소한의 변경으로 문제 해결
4. **테스트**: 수정사항이 다른 부분에 영향을 주지 않는지 확인

### ✨ 새 기능 추가

1. **논의**: GitHub Discussions에서 기능에 대해 먼저 논의
2. **설계**: 기능의 구조와 인터페이스 설계
3. **구현**: 모듈화된 방식으로 구현
4. **문서화**: API 문서와 사용법 추가

### 📖 문서 개선

1. **README.md**: 사용법, 설치 가이드 개선
2. **API.md**: API 문서 업데이트
3. **코드 주석**: 독스트링과 인라인 주석 추가
4. **예제**: 사용 예제 코드 추가

### 🧪 테스트 추가

1. **단위 테스트**: 개별 함수/클래스 테스트
2. **통합 테스트**: 컴포넌트 간 상호작용 테스트
3. **E2E 테스트**: 전체 워크플로우 테스트

## 코딩 스타일

### Python 스타일 가이드

프로젝트는 [PEP 8](https://pep8.org/)을 따르되 다음 규칙을 추가합니다:

```python
# 1. Import 순서
import os                    # 표준 라이브러리
import json

import streamlit as st       # 서드파티 라이브러리
import pandas as pd

from .models import *        # 로컬 임포트
from .utils import helpers

# 2. 함수 및 클래스 문서화
def calculate_cost(tokens: int, model: str) -> float:
    """
    토큰 수와 모델에 따른 비용 계산
    
    Args:
        tokens: 토큰 수
        model: 모델명
        
    Returns:
        계산된 비용 (USD)
        
    Raises:
        ValueError: 지원하지 않는 모델인 경우
    """
    pass

class DataManager:
    """데이터 관리 클래스"""
    
    def __init__(self, storage_path: str):
        """
        Args:
            storage_path: 데이터 저장 경로
        """
        self.storage_path = storage_path

# 3. 타입 힌팅 사용
from typing import Dict, List, Optional, Any, Union

def process_messages(
    messages: List[Dict[str, Any]], 
    max_tokens: Optional[int] = None
) -> Tuple[str, TokenUsage]:
    pass

# 4. 상수는 대문자로
MAX_RETRIES = 3
DEFAULT_TEMPERATURE = 0.7
API_BASE_URL = "https://api.openai.com"

# 5. 에러 처리
try:
    result = risky_operation()
except SpecificException as e:
    logging.error(f"Specific error occurred: {e}")
    raise
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    # 적절한 폴백 또는 재발생
```

### 코드 포맷팅

```bash
# Black으로 자동 포맷팅
black src/ tests/

# flake8으로 린팅
flake8 src/ tests/

# mypy로 타입 검사
mypy src/
```

### 디렉토리 구조 규칙

```
src/llmos/
├── core/           # 핵심 앱 로직
├── models/         # 데이터 모델과 Enum
├── interfaces/     # 외부 API 인터페이스
├── managers/       # 비즈니스 로직 관리자
├── ui/            # 사용자 인터페이스
│   ├── components.py  # 재사용 가능한 UI 컴포넌트
│   ├── pages/         # 페이지별 UI
│   └── styles.py      # CSS 스타일
└── utils/         # 유틸리티 함수들
```

## 테스트

### 테스트 작성 가이드

```python
# tests/test_example.py
import unittest
from unittest.mock import Mock, patch
from src.llmos.managers.example import ExampleManager

class TestExampleManager(unittest.TestCase):
    
    def setUp(self):
        """각 테스트 전에 실행"""
        self.manager = ExampleManager()
    
    def tearDown(self):
        """각 테스트 후에 정리"""
        # 필요한 정리 작업
        pass
    
    def test_basic_functionality(self):
        """기본 기능 테스트"""
        result = self.manager.basic_function("input")
        self.assertEqual(result, "expected_output")
    
    @patch('src.llmos.managers.example.external_api_call')
    def test_with_mock(self, mock_api):
        """외부 의존성을 Mock으로 테스트"""
        mock_api.return_value = "mocked_response"
        
        result = self.manager.function_with_api_call()
        
        mock_api.assert_called_once()
        self.assertEqual(result, "expected_result")
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        with self.assertRaises(ValueError):
            self.manager.function_that_raises("invalid_input")
```

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 파일 테스트
pytest tests/test_managers/test_settings.py

# 커버리지 포함
pytest --cov=src/llmos tests/

# 상세 출력
pytest -v

# 특정 테스트만
pytest tests/test_managers/test_settings.py::TestSettingsManager::test_basic_functionality
```

### 테스트 커버리지

- **목표**: 80% 이상의 코드 커버리지
- **핵심 로직**: 100% 커버리지 권장
- **UI 코드**: 주요 기능만 테스트

## Pull Request 프로세스

### 1. 브랜치 생성

```bash
# 최신 코드로 동기화
git fetch upstream
git checkout main
git merge upstream/main

# 새 브랜치 생성
git checkout -b feature/your-feature-name
# 또는
git checkout -b fix/bug-description
```

### 2. 개발 및 커밋

```bash
# 작은 단위로 자주 커밋
git add .
git commit -m "feat: add new AI model support"

# 커밋 메시지 형식
# type(scope): description
#
# Types: feat, fix, docs, style, refactor, test, chore
# Scope: component name (optional)
# Description: what you did
```

#### 커밋 메시지 예시

```
feat(models): add Claude 3.5 Sonnet support
fix(ui): resolve chat input focus issue
docs(api): update ModelManager documentation
test(managers): add tests for ArtifactManager
refactor(utils): simplify image processing logic
style(ui): fix code formatting in components
chore(deps): update streamlit to 1.28.0
```

### 3. 테스트 및 검증

```bash
# 로컬 테스트 실행
pytest tests/

# 코드 스타일 검사
black --check src/ tests/
flake8 src/ tests/

# 타입 검사
mypy src/

# 애플리케이션 실행 테스트
streamlit run main.py
```

### 4. Pull Request 생성

**PR 제목**: 간결하고 명확하게
```
feat: Add support for Claude 3.5 Sonnet model
fix: Resolve memory leak in chat sessions
docs: Update installation guide for Windows
```

**PR 설명 템플릿**:
```markdown
## 📝 변경 사항 요약
- 추가/수정/삭제된 내용 간략 설명

## 🔧 변경 이유
- 왜 이 변경이 필요한지 설명
- 관련 이슈 번호: #123

## 🧪 테스트
- [ ] 단위 테스트 추가/업데이트
- [ ] 수동 테스트 완료
- [ ] 기존 테스트 통과 확인

## 📸 스크린샷 (UI 변경 시)
<!-- 변경 전후 이미지 -->

## ✅ 체크리스트
- [ ] 코드 스타일 가이드 준수
- [ ] 문서 업데이트 (필요시)
- [ ] 테스트 추가/업데이트
- [ ] 변경사항이 기존 기능에 영향 없음 확인
```

### 5. 코드 리뷰 대응

- **피드백 수용**: 건설적인 피드백에 열린 마음으로 대응
- **명확한 답변**: 질문에 명확하게 답변
- **추가 커밋**: 필요한 수정사항을 추가 커밋으로 반영

## 이슈 리포팅

### 버그 리포트

```markdown
**🐛 버그 설명**
간단명료한 버그 설명

**📋 재현 단계**
1. '...' 로 이동
2. '...' 클릭
3. '...' 입력
4. 오류 발생

**💭 예상 동작**
어떻게 동작해야 하는지 설명

**🖼️ 스크린샷**
가능하면 스크린샷 첨부

**🔧 환경 정보**
- OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
- Python: [e.g. 3.9.0]
- LLM OS: [e.g. 0.0.9]
- Browser: [e.g. Chrome 91.0]

**📋 추가 정보**
기타 관련 정보나 로그
```

### 기능 요청

```markdown
**✨ 기능 설명**
원하는 기능에 대한 명확한 설명

**💡 동기**
왜 이 기능이 필요한지 설명

**📝 상세 설명**
기능이 어떻게 동작해야 하는지 자세히 설명

**🎯 대안 고려사항**
고려했던 다른 방법들

**📊 우선순위**
- [ ] 낮음
- [ ] 보통  
- [ ] 높음
- [ ] 긴급
```

## 커뮤니티 가이드라인

### 🤝 행동 강령

- **존중**: 모든 기여자를 존중하며 협력적으로 소통
- **건설적**: 건설적인 피드백과 비판 제공
- **포용적**: 다양한 배경과 경험을 가진 사람들 환영
- **학습**: 실수를 통해 배우는 문화 조성

### 💬 커뮤니케이션

- **GitHub Issues**: 버그 리포트, 기능 요청
- **GitHub Discussions**: 일반적인 질문, 아이디어 논의
- **Pull Request**: 코드 리뷰, 구현 논의

### 🏷️ 라벨 시스템

**타입**:
- `bug`: 버그 수정
- `feature`: 새 기능
- `enhancement`: 기존 기능 개선
- `documentation`: 문서 관련
- `refactor`: 코드 리팩토링

**우선순위**:
- `priority:low`: 낮은 우선순위
- `priority:medium`: 보통 우선순위  
- `priority:high`: 높은 우선순위
- `priority:critical`: 긴급

**상태**:
- `help-wanted`: 도움이 필요한 이슈
- `good-first-issue`: 첫 기여자에게 좋은 이슈
- `in-progress`: 작업 중
- `blocked`: 차단된 이슈

## 🎉 인정받기

기여해주신 모든 분들은 다음과 같이 인정받습니다:

1. **README.md 기여자 섹션**에 이름 추가
2. **Release Notes**에 기여 내용 언급
3. **GitHub Contributors** 페이지에 자동 표시

### 첫 기여 환영 🎊

첫 기여를 환영합니다! `good-first-issue` 라벨이 붙은 이슈들을 확인해보세요. 작고 간단한 기여부터 시작하여 프로젝트에 익숙해지시기 바랍니다.

질문이 있으시면 언제든지 GitHub Discussions에서 물어보세요. 기꺼이 도와드리겠습니다!

---

**함께 만들어가는 LLM OS** 🚀