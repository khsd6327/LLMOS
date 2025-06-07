# ted-os-project/src/tedos/utils/helpers.py
"""
Ted OS - 공통 유틸리티 함수들
"""

import base64
import hashlib
import io
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple

from PIL import Image
import math
import re


logger = logging.getLogger(__name__)


def generate_id() -> str:
    """고유 ID 생성"""
    return str(uuid.uuid4())


def generate_short_id() -> str:
    """짧은 ID 생성 (8자리)"""
    return str(uuid.uuid4())[:8]


def get_current_timestamp() -> datetime:
    """현재 타임스탬프 반환"""
    return datetime.now()


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """타임스탬프 포맷팅"""
    return dt.strftime(format_str)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """텍스트 자르기"""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """파일명 정리"""
    # 위험한 문자 제거
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # 연속된 점과 공백 정리
    sanitized = re.sub(r"\.{2,}", ".", sanitized)
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized


def calculate_file_hash(file_path: Union[str, Path]) -> str:
    """파일 해시 계산"""
    hash_obj = hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash: {e}")
        return ""


def calculate_text_hash(text: str) -> str:
    """텍스트 해시 계산"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """파일 크기 포맷팅"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def format_number(number: Union[int, float], precision: int = 2) -> str:
    """숫자 포맷팅 (천 단위 구분자)"""
    if isinstance(number, float):
        return f"{number:,.{precision}f}"
    return f"{number:,}"

def ensure_directory_exists(dir_path: str):
    """지정된 디렉토리가 존재하지 않으면 생성합니다."""
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            logger.info(f"Created directory: {dir_path}")
        except OSError as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
            raise # 에러를 다시 발생시켜 호출한 쪽에서 알 수 있도록 함
    else:
        logger.debug(f"Directory already exists: {dir_path}")

def parse_data_uri(data_uri: str) -> Tuple[str, bytes]:
    """Data URI 파싱"""
    try:
        header, encoded = data_uri.split(",", 1)
        mime_type = header.split(":", 1)[1].split(";", 1)[0]
        data = base64.b64decode(encoded)
        return mime_type, data
    except Exception as e:
        logger.error(f"Error parsing data URI: {e}")
        raise ValueError("Invalid data URI format")


def create_data_uri(data: bytes, mime_type: str) -> str:
    """Data URI 생성"""
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def detect_image_mime_type(image_bytes: bytes, filename: Optional[str] = None) -> str:
    """이미지 MIME 타입 감지"""
    if filename:
        ext = Path(filename).suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
        }
        if ext in mime_map:
            return mime_map[ext]

    # 바이트 시그니처로 감지
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    elif image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    elif image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    elif image_bytes.startswith(b"GIF87a") or image_bytes.startswith(b"GIF89a"):
        return "image/gif"
    elif image_bytes.startswith(b"BM"):
        return "image/bmp"

    logger.warning(
        f"Could not determine MIME type for image. Defaulting to application/octet-stream."
    )
    return "application/octet-stream"


def resize_image(
    image_bytes: bytes, max_width: int = 1024, max_height: int = 1024, quality: int = 85
) -> bytes:
    """이미지 리사이즈"""
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            # 원본 크기
            orig_width, orig_height = img.size

            # 리사이즈 필요 여부 확인
            if orig_width <= max_width and orig_height <= max_height:
                return image_bytes

            # 비율 유지하며 리사이즈
            ratio = min(max_width / orig_width, max_height / orig_height)
            new_width = int(orig_width * ratio)
            new_height = int(orig_height * ratio)

            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 바이트로 변환
            output = io.BytesIO()
            format_name = img.format or "JPEG"

            if format_name == "JPEG":
                resized.save(output, format=format_name, quality=quality, optimize=True)
            else:
                resized.save(output, format=format_name, optimize=True)

            return output.getvalue()

    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return image_bytes


def validate_image(image_bytes: bytes, max_size_mb: int = 10) -> bool:
    """이미지 유효성 검사"""
    try:
        # 크기 확인
        if len(image_bytes) > max_size_mb * 1024 * 1024:
            return False

        # PIL로 열기 시도
        with Image.open(io.BytesIO(image_bytes)) as img:
            # 기본 검증
            img.verify()
            return True

    except Exception as e:
        logger.warning(f"Image validation failed: {e}")
        return False


def clean_dict(
    data: Dict[str, Any], remove_none: bool = True, remove_empty: bool = False
) -> Dict[str, Any]:
    """딕셔너리 정리"""
    cleaned = {}

    for key, value in data.items():
        # None 값 제거
        if remove_none and value is None:
            continue

        # 빈 값 제거
        if remove_empty and not value:
            continue

        # 중첩 딕셔너리 처리
        if isinstance(value, dict):
            cleaned[key] = clean_dict(value, remove_none, remove_empty)
        else:
            cleaned[key] = value

    return cleaned


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """딕셔너리 병합 (깊은 복사)"""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def safe_get(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """안전한 딕셔너리 값 가져오기 (점 표기법)"""
    try:
        keys = key_path.split(".")
        value = data

        for key in keys:
            value = value[key]

        return value
    except (KeyError, TypeError, AttributeError):
        return default


def flatten_dict(
    data: Dict[str, Any], prefix: str = "", separator: str = "."
) -> Dict[str, Any]:
    """딕셔너리 평면화"""
    flattened = {}

    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key

        if isinstance(value, dict):
            flattened.update(flatten_dict(value, new_key, separator))
        else:
            flattened[new_key] = value

    return flattened


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """리스트를 청크로 분할"""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List[Any], key_func=None) -> List[Any]:
    """중복 제거"""
    if key_func is None:
        return list(set(lst))

    seen = set()
    result = []

    for item in lst:
        key = key_func(item)
        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """읽기 시간 추정 (분)"""
    word_count = len(text.split())
    reading_time = max(1, round(word_count / wpm))
    return reading_time


def extract_urls(text: str) -> List[str]:
    """텍스트에서 URL 추출"""
    url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+'

    return re.findall(url_pattern, text)

def mask_sensitive_data(text: str, patterns: Optional[List[str]] = None) -> str:
    """민감한 데이터 마스킹"""
    if patterns is None:
        patterns = [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # 이메일
            r"\b\d{3}-\d{3,4}-\d{4}\b",  # 전화번호
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # 카드번호
        ]

    masked_text = text
    for pattern in patterns:
        masked_text = re.sub(pattern, "[MASKED]", masked_text)

    return masked_text

def trigger_autoscroll():
    """
    채팅 메시지 컨테이너를 맨 아래로 한 번 스크롤하는 JavaScript를 주입합니다.
    """
    import streamlit as st

    js = f"""
    <script>
        function scroll_to_bottom() {{
            var chat_messages = window.parent.document.querySelectorAll('[data-testid="stChatMessage"]');
            if (chat_messages.length > 0) {{
                // 마지막 메시지를 부드럽게 보이도록 스크롤
                chat_messages[chat_messages.length - 1].scrollIntoView({{ behavior: 'smooth', block: 'end' }});
            }}
        }}
        // 페이지가 로드된 후 100ms 뒤에 한 번만 실행
        setTimeout(scroll_to_bottom, 100);
    </script>
    """
    st.components.v1.html(js, height=0)
