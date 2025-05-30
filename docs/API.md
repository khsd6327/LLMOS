# 🔌 LLM OS API 문서

이 문서는 LLM OS의 주요 클래스와 메서드들에 대한 API 참조를 제공합니다.

## 📚 목차

- [핵심 클래스](#핵심-클래스)
- [관리자 클래스](#관리자-클래스)
- [데이터 모델](#데이터-모델)
- [인터페이스](#인터페이스)
- [유틸리티](#유틸리티)

## 핵심 클래스

### EnhancedLLMOSApp

메인 애플리케이션 클래스입니다.

```python
from src.llmos.core.app import EnhancedLLMOSApp

app = EnhancedLLMOSApp()
app.run()
```

#### 메서드

- `run()`: 애플리케이션 실행
- `cleanup()`: 리소스 정리
- `get_app_info()`: 애플리케이션 정보 반환

## 관리자 클래스

### SettingsManager

애플리케이션 설정을 관리합니다.

```python
from src.llmos.managers.settings import SettingsManager

settings = SettingsManager()
```

#### 주요 메서드

```python
# 설정 값 가져오기
value = settings.get("key.path", default_value)

# 설정 값 설정하기
settings.set("key.path", value)

# API 키 설정
settings.set_api_key("openai", "your-api-key")

# API 키 존재 확인
has_key = settings.has_api_key(ModelProvider.OPENAI)

# 설정 초기화
settings.reset_to_defaults()

# 설정 내보내기/가져오기
exported = settings.export_settings()
settings.import_settings(data)
```

### ChatSessionManager

채팅 세션을 관리합니다.

```python
from src.llmos.managers.chat_sessions import ChatSessionManager

chat_manager = ChatSessionManager("/path/to/sessions")
```

#### 주요 메서드

```python
# 새 세션 생성
session = chat_manager.create_session("세션 제목")

# 세션 조회
session = chat_manager.get_session(session_id)

# 세션 업데이트
chat_manager.update_session(session)

# 세션 삭제
chat_manager.delete_session(session_id)

# 모든 세션 조회
sessions = chat_manager.get_all_sessions()

# 세션 검색
results = chat_manager.search_sessions("검색어")

# 세션 통계
stats = chat_manager.get_session_statistics()

# 빈 세션 정리
deleted_count = chat_manager.cleanup_empty_sessions()
```

### ArtifactManager

아티팩트를 관리합니다.

```python
from src.llmos.managers.artifacts import ArtifactManager
from src.llmos.models.enums import ArtifactType

artifact_manager = ArtifactManager("/path/to/artifacts")
```

#### 주요 메서드

```python
# 아티팩트 생성
artifact = artifact_manager.create(
    type_val=ArtifactType.TEXT,
    title="제목",
    content="내용",
    tags=["태그1", "태그2"],
    metadata={"key": "value"}
)

# 아티팩트 조회
artifact = artifact_manager.get(artifact_id)

# 아티팩트 업데이트
artifact_manager.update(artifact_id, title="새 제목")

# 아티팩트 삭제
artifact_manager.delete(artifact_id)

# 아티팩트 검색
results = artifact_manager.search(
    query="검색어",
    type_val=ArtifactType.CODE,
    tags=["태그1"],
    limit=50
)

# 아티팩트 통계
stats = artifact_manager.get_statistics()
```

### UsageTracker

토큰 사용량을 추적합니다.

```python
from src.llmos.managers.usage_tracker import UsageTracker

usage_tracker = UsageTracker("/path/to/usage_data")
```

#### 주요 메서드

```python
# 사용량 기록 추가
usage_tracker.add_usage(token_usage)

# 오늘 사용량
today_usage = usage_tracker.get_today_usage_from_summary()

# 전체 사용량
total_usage = usage_tracker.get_total_usage_from_history()

# 주간 사용량
weekly_usage = usage_tracker.get_weekly_usage()

# 월간 사용량
monthly_usage = usage_tracker.get_monthly_usage()

# 모델별 사용량
model_usage = usage_tracker.get_usage_by_model(days=30)

# 사용량 트렌드
trends = usage_tracker.get_usage_trends(days=7)

# 월 예상 비용
estimated_cost = usage_tracker.estimate_monthly_cost()

# 오래된 데이터 정리
cleaned = usage_tracker.cleanup_old_data(keep_days=90)
```

### EnhancedModelManager

AI 모델을 관리하고 호출합니다.

```python
from src.llmos.managers.model_manager import EnhancedModelManager

model_manager = EnhancedModelManager(settings_manager, usage_tracker)
```

#### 주요 메서드

```python
# AI 응답 생성
response, usage = model_manager.generate(
    messages=[{"role": "user", "content": "안녕하세요"}],
    provider_display_name="OpenAI",
    model_id_key="chatgpt-4o-latest",
    temperature=0.7,
    max_tokens=1000
)

# 스트리밍 응답 생성
for chunk, usage in model_manager.stream_generate(messages):
    print(chunk)

# 사용 가능한 제공업체
providers = model_manager.get_available_providers()

# 제공업체 사용 가능 확인
is_available = model_manager.is_provider_available(ModelProvider.OPENAI)

# 모델 정보 조회
model_info = model_manager.get_model_info("OpenAI", "chatgpt-4o-latest")

# 설정 검증
validation = model_manager.validate_configuration()
```

## 데이터 모델

### ChatSession

채팅 세션 데이터 모델입니다.

```python
from src.llmos.models.data_models import ChatSession
from datetime import datetime

session = ChatSession(
    id="session-id",
    title="채팅 제목",
    messages=[
        {"role": "user", "content": "안녕하세요"},
        {"role": "assistant", "content": "안녕하세요!"}
    ],
    created_at=datetime.now(),
    updated_at=datetime.now(),
    metadata={}
)

# 딕셔너리 변환
session_dict = session.to_dict()

# 딕셔너리에서 생성
session = ChatSession.from_dict(session_dict)
```

### Artifact

아티팩트 데이터 모델입니다.

```python
from src.llmos.models.data_models import Artifact
from src.llmos.models.enums import ArtifactType
from datetime import datetime

artifact = Artifact(
    id="artifact-id",
    type=ArtifactType.TEXT,
    title="아티팩트 제목",
    content="내용",
    tags=["태그1", "태그2"],
    created_at=datetime.now(),
    updated_at=datetime.now(),
    metadata={"key": "value"}
)
```

### TokenUsage

토큰 사용량 데이터 모델입니다.

```python
from src.llmos.models.data_models import TokenUsage
from datetime import datetime

usage = TokenUsage(
    input_tokens=100,
    output_tokens=50,
    total_tokens=150,
    model_name="gpt-4o",
    provider="openai",
    timestamp=datetime.now(),
    cost_usd=0.002
)
```

### ModelConfig

모델 설정 데이터 모델입니다.

```python
from src.llmos.models.data_models import ModelConfig
from src.llmos.models.enums import ModelProvider

config = ModelConfig(
    provider=ModelProvider.OPENAI,
    model_name="gpt-4o",
    display_name="GPT-4o",
    max_tokens=128000,
    supports_streaming=True,
    supports_functions=True,
    supports_vision=True,
    description="OpenAI의 최신 모델",
    input_cost_per_1k=0.005,
    output_cost_per_1k=0.015
)
```

## 인터페이스

### LLMInterface

AI 모델 인터페이스의 기본 클래스입니다.

```python
from src.llmos.interfaces.base import LLMInterface

class CustomInterface(LLMInterface):
    def generate(self, messages, model, **kwargs):
        # 구현
        pass
    
    def stream(self, messages, model, **kwargs):
        # 구현
        pass
```

### OpenAIInterface

OpenAI API 인터페이스입니다.

```python
from src.llmos.interfaces.openai_client import OpenAIInterface

interface = OpenAIInterface("your-api-key")

# 응답 생성
response, usage = interface.generate(
    messages=[{"role": "user", "content": "Hello"}],
    model="gpt-4o",
    temperature=0.7,
    max_tokens=100
)

# 스트리밍
for chunk in interface.stream(messages, model="gpt-4o"):
    print(chunk)
```

### AnthropicInterface

Anthropic Claude API 인터페이스입니다.

```python
from src.llmos.interfaces.anthropic_client import AnthropicInterface

interface = AnthropicInterface("your-api-key")

# 사용법은 OpenAIInterface와 동일
```

### GoogleInterface

Google Gemini API 인터페이스입니다.

```python
from src.llmos.interfaces.google_client import GoogleInterface

interface = GoogleInterface("your-api-key")

# 사용법은 다른 인터페이스와 동일
```

## 유틸리티

### 로깅

```python
from src.llmos.utils.logging_handler import setup_logging, get_app_logger

# 로깅 설정
setup_logging()

# 로거 가져오기
logger = get_app_logger("module_name")

# 사용
logger.info("정보 메시지")
logger.error("오류 메시지")
```

### 출력 렌더링

```python
from src.llmos.utils.output_renderer import OutputRenderer

renderer = OutputRenderer()

# 텍스트 후처리
processed_text = renderer.process_output(raw_text)

# 메타데이터와 함께 렌더링
result = renderer.render_with_metadata(text, {"key": "value"})
```

### 헬퍼 함수들

```python
from src.llmos.utils.helpers import *

# ID 생성
id = generate_id()
short_id = generate_short_id()

# 텍스트 처리
truncated = truncate_text("긴 텍스트", max_length=50)
safe_filename = sanitize_filename("파일이름.txt")

# 파일 처리
file_hash = calculate_file_hash("file.txt")
file_size = format_file_size(1024)

# 이미지 처리
mime_type = detect_image_mime_type(image_bytes)
resized_image = resize_image(image_bytes, max_width=800)
is_valid = validate_image(image_bytes)

# 데이터 URI
data_uri = create_data_uri(image_bytes, "image/png")
mime_type, data = parse_data_uri(data_uri)

# 딕셔너리 처리
cleaned = clean_dict({"a": None, "b": "value"}, remove_none=True)
merged = merge_dicts(dict1, dict2)
value = safe_get(data, "nested.key.path", default="default")

# 기타
reading_time = estimate_reading_time(text)
urls = extract_urls(text)
masked = mask_sensitive_data(text)
```

## 🔧 설정

### 환경 변수

| 변수명 | 타입 | 기본값 | 설명 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | string | - | OpenAI API 키 |
| `ANTHROPIC_API_KEY` | string | - | Anthropic API 키 |
| `GOOGLE_API_KEY` | string | - | Google AI API 키 |
| `LLMOS_CONFIG_DIR` | string | `~/.llm_os_config` | 설정 디렉토리 |
| `LLMOS_LOG_LEVEL` | string | `INFO` | 로그 레벨 |
| `LLMOS_DEBUG` | boolean | `false` | 디버그 모드 |

### 설정 구조

```json
{
  "api_keys": {
    "openai": "your-openai-key",
    "anthropic": "your-anthropic-key",
    "google": "your-google-key"
  },
  "paths": {
    "chat_sessions": "~/.llm_os_config/chat_sessions",
    "artifacts": "~/.llm_os_config/artifacts",
    "usage_tracking": "~/.llm_os_config/usage_data"
  },
  "defaults": {
    "model": null,
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "ui": {
    "selected_provider": null,
    "theme": "auto",
    "language": "ko"
  },
  "features": {
    "auto_title_generation": true,
    "usage_tracking": true,
    "debug_mode": false
  }
}
```

## 📈 확장하기

### 새 AI 제공업체 추가

1. `LLMInterface`를 상속하는 새 클래스 생성
2. `ModelRegistry`에 모델 설정 추가
3. `ModelManager`에서 초기화 코드 추가

```python
from src.llmos.interfaces.base import LLMInterface

class NewProviderInterface(LLMInterface):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate(self, messages, model, **kwargs):
        # 구현
        pass
    
    def stream(self, messages, model, **kwargs):
        # 구현  
        pass
```

### 새 아티팩트 타입 추가

```python
from src.llmos.models.enums import ArtifactType

# 새 타입을 enum에 추가
class ArtifactType(Enum):
    # 기존 타입들...
    NEW_TYPE = "new_type"
```

### 커스텀 UI 컴포넌트

```python
from src.llmos.ui.components import EnhancedUI

class CustomUI(EnhancedUI):
    @staticmethod
    def render_custom_component():
        # 구현
        pass
```

이 API 문서는 LLM OS의 주요 기능들을 다루고 있습니다. 더 자세한 정보는 소스 코드의 독스트링을 참조하세요.