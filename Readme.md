# 🧠 LLM OS - 개인 맞춤형 AI 비서 시스템

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-orange.svg)](https://github.com/llmos/llmos/releases)

> **목표**: Python으로 만드는 나만의 AI 비서 시스템  
> **현재 단계**: Phase 1 완료, Phase 2 진입  
> **주요 특징**: 멀티모달 지원, 실시간 스트리밍, 사용량 추적

## 📋 프로젝트 개요

LLM OS는 개인 사용자를 위한 통합 AI 비서 시스템입니다. 여러 AI 제공업체(OpenAI, Anthropic, Google)의 최신 모델들을 하나의 인터페이스에서 사용할 수 있으며, 채팅 기록 관리, 아티팩트 저장, 사용량 추적 등의 기능을 제공합니다.

### ✨ 주요 특징

- 🤖 **멀티 AI 제공업체 지원**: OpenAI, Anthropic, Google의 최신 모델들
- 💬 **ChatGPT 스타일 UI**: 직관적이고 사용하기 쉬운 채팅 인터페이스
- 🖼️ **멀티모달 지원**: 텍스트와 이미지를 함께 처리
- ⚡ **실시간 스트리밍**: AI 응답을 실시간으로 확인
- 📊 **사용량 추적**: 토큰 사용량과 비용 자동 계산
- 💾 **데이터 관리**: 채팅 기록과 아티팩트 영구 저장
- 🔧 **개발자 친화적**: 모듈화된 구조와 확장 가능한 아키텍처

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/llmos/llmos.git
cd llmos

# 의존성 설치
pip install -r requirements.txt

# 또는 pip로 직접 설치
pip install llmos
```

### 2. API 키 설정

```bash
# 환경 변수 파일 생성
cp .env.example .env

# .env 파일을 편집하여 API 키 입력
# 최소한 하나의 AI 제공업체 API 키가 필요합니다
```

**API 키 발급 방법:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google AI**: https://ai.google.dev/

### 3. 실행

```bash
# 애플리케이션 실행
streamlit run main.py

# 또는 패키지로 설치한 경우
llmos
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 📖 사용 가이드

### 기본 사용법

1. **새 채팅 시작**: 사이드바에서 "➕ 새 채팅 시작" 클릭
2. **모델 선택**: 사이드바에서 AI 제공업체와 모델 선택
3. **대화**: 하단 입력창에 메시지 입력
4. **이미지 첨부**: 드래그&드롭 또는 파일 업로더로 이미지 첨부

### 고급 기능

#### 🎛️ 생성 매개변수 조정
- **Temperature**: 창의성 조절 (0.0 = 일관적, 2.0 = 창의적)
- **Max Tokens**: 응답 길이 제한
- **실시간 조정**: 사이드바에서 바로 변경 가능

#### 📚 아티팩트 관리
- AI가 생성한 콘텐츠를 아티팩트로 저장
- 태그 기반 분류 및 검색
- 다양한 타입 지원: 텍스트, 코드, 이미지, JSON 등

#### 📊 사용량 추적
- 토큰 사용량 실시간 모니터링
- 일별/월별 비용 계산
- 모델별 사용 통계

## 🛠️ 아키텍처

### 프로젝트 구조

```
LLMOS/
├── src/llmos/
│   ├── core/           # 핵심 앱 로직
│   ├── models/         # 데이터 모델
│   ├── interfaces/     # AI 제공업체 인터페이스
│   ├── managers/       # 비즈니스 로직 관리자들
│   ├── ui/            # 사용자 인터페이스
│   └── utils/         # 유틸리티 함수들
├── tests/             # 테스트 코드
├── docs/              # 문서
└── main.py           # 실행 진입점
```

### 핵심 컴포넌트

- **EnhancedLLMOSApp**: 메인 애플리케이션 클래스
- **ModelManager**: AI 모델 관리 및 호출
- **ChatSessionManager**: 채팅 세션 관리
- **ArtifactManager**: 아티팩트 저장 및 검색
- **UsageTracker**: 사용량 추적 및 비용 계산
- **SettingsManager**: 설정 관리

## 🔧 설정

### 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|---------|
| `OPENAI_API_KEY` | OpenAI API 키 | - |
| `ANTHROPIC_API_KEY` | Anthropic API 키 | - |
| `GOOGLE_API_KEY` | Google AI API 키 | - |
| `LLMOS_CONFIG_DIR` | 설정 디렉토리 | `~/.llm_os_config` |
| `LLMOS_LOG_LEVEL` | 로그 레벨 | `INFO` |

### 설정 파일

설정은 `~/.llm_os_config/settings.json`에 저장됩니다:

```json
{
  "api_keys": {
    "openai": "your-openai-key",
    "anthropic": "your-anthropic-key", 
    "google": "your-google-key"
  },
  "defaults": {
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "features": {
    "auto_title_generation": true,
    "usage_tracking": true
  }
}
```

## 🤖 지원 모델

### OpenAI
- **o4-mini**: GPT-4o Mini (비용 효율적)
- **chatgpt-4o-latest**: 최신 GPT-4o 모델
- **gpt-4.1**: GPT-4 Turbo

### Anthropic
- **claude-opus-4**: Claude 3 Opus (최고 성능)
- **claude-sonnet-4**: Claude 3.5 Sonnet (균형)

### Google
- **gemini-2.5-flash-preview**: Gemini 1.5 Flash (빠른 처리)
- **gemini-2.5-pro-preview**: Gemini 1.5 Pro (고성능)

## 📈 개발 로드맵

### ✅ Phase 1: 기초 구축 (완료)
- [x] 핵심 모듈 개발
- [x] 기본 UI 구현
- [x] 멀티모달 지원
- [x] 사용량 추적 시스템
- [x] 스트리밍 응답

### 🚧 Phase 2: 고도화 (진행 중)
- [ ] 프롬프트 템플릿 시스템
- [ ] 고급 검색 및 필터링
- [ ] 데이터 백업 시스템
- [ ] 성능 최적화

### 🔮 Phase 3: 고급 기능 (계획)
- [ ] RAG (문서 기반 답변) 시스템
- [ ] 자동화 워크플로우
- [ ] 플러그인 아키텍처

### 🚀 Phase 4: AI 에이전트 (미래)
- [ ] 자율 리서치 시스템
- [ ] 웹 검색 통합
- [ ] 자동 보고서 생성

## 🧪 개발 및 기여

### 개발 환경 설정

```bash
# 개발용 의존성 설치
pip install -e .[dev]

# 코드 포맷팅
black src/

# 린팅
flake8 src/

# 타입 검사
mypy src/

# 테스트 실행
pytest tests/
```

### 기여 가이드

1. Fork 및 Clone
2. 새 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📊 성능 및 제한사항

### 권장 시스템 요구사항
- **Python**: 3.8 이상
- **RAM**: 2GB 이상
- **디스크**: 1GB 여유 공간
- **네트워크**: 안정적인 인터넷 연결

### 알려진 제한사항
- 대용량 파일 처리 시 메모리 사용량 증가
- 일부 모델에서 한글 토큰 카운팅 부정확성
- 오프라인 모드 미지원

## 🔒 보안 및 프라이버시

- **로컬 저장**: 모든 데이터는 로컬 시스템에 저장
- **API 키 보안**: 환경 변수 또는 암호화된 설정 파일 사용
- **데이터 암호화**: 민감한 정보 자동 암호화
- **감사 로그**: 모든 API 호출 기록

## ❓ FAQ

### Q: 어떤 AI 제공업체를 사용해야 하나요?
**A**: 용도에 따라 다릅니다:
- **일반적인 대화**: OpenAI GPT-4o Mini (비용 효율적)
- **복잡한 추론**: Anthropic Claude Opus (최고 성능)  
- **빠른 처리**: Google Gemini Flash (속도 우선)

### Q: API 비용이 얼마나 드나요?
**A**: 모델마다 다르지만, 일반적인 사용 시 월 $5-20 정도입니다. 앱에서 실시간 비용을 추적할 수 있습니다.

### Q: 데이터는 어디에 저장되나요?
**A**: 모든 데이터는 로컬 시스템(`~/.llm_os_config/`)에 저장됩니다. 클라우드로 전송되지 않습니다.

### Q: 오프라인에서 사용할 수 있나요?
**A**: 현재는 AI API 호출을 위해 인터넷 연결이 필요합니다. 로컬 모델 지원은 향후 계획에 있습니다.

## 📄 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들의 도움을 받았습니다:

- [Streamlit](https://streamlit.io/) - 웹 인터페이스
- [OpenAI Python SDK](https://github.com/openai/openai-python) - OpenAI API
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) - Anthropic API
- [Google Generative AI](https://ai.google.dev/) - Google AI API

## 📞 지원 및 문의

- **GitHub Issues**: [버그 리포트 및 기능 요청](https://github.com/llmos/llmos/issues)
- **Discussions**: [질문 및 아이디어 공유](https://github.com/llmos/llmos/discussions)
- **Email**: dev@llmos.com

---

**LLM OS**로 당신만의 AI 비서를 만들어보세요! 🚀