# src/llmos/interfaces/base.py
"""
LLM OS - 기본 인터페이스 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Generator

from ..models.data_models import TokenUsage


class LLMInterface(ABC):
    """AI 모델 인터페이스 기본 클래스"""

    @abstractmethod
    def generate(
        self, messages: List[Dict[str, Any]], model: str, **kwargs: Any
    ) -> Tuple[str, Optional[TokenUsage]]:
        """
        AI 응답 생성 (동기식)

        Args:
            messages: 대화 메시지 목록
            model: 사용할 모델명
            **kwargs: 추가 생성 매개변수

        Returns:
            생성된 텍스트와 토큰 사용량 정보
        """
        pass

    @abstractmethod
    def stream(
        self, messages: List[Dict[str, Any]], model: str, **kwargs: Any
    ) -> Generator[Any, None, None]:
        """
        AI 응답 스트리밍 생성

        Args:
            messages: 대화 메시지 목록
            model: 사용할 모델명
            **kwargs: 추가 생성 매개변수

        Yields:
            스트리밍 청크 데이터
        """
        pass

    def validate_api_key(self, api_key: str) -> bool:
        """
        API 키 유효성 검증

        Args:
            api_key: 검증할 API 키

        Returns:
            유효성 여부
        """
        return bool(api_key and api_key.strip())

    def estimate_tokens(self, text: str) -> int:
        """
        텍스트의 토큰 수 추정 (매우 단순한 추정치)

        ⚠️ 중요: 이 구현은 매우 단순한 추정치입니다!
        - 각 AI 제공업체는 서로 다른 토크나이저를 사용합니다
        - 정확한 토큰 계산이 필요한 경우 각 클라이언트에서 이 메서드를 재정의하세요
        - 현재 구현은 대략적인 비용 추정 및 제한 확인용으로만 사용하세요

        Args:
            text: 추정할 텍스트

        Returns:
            추정 토큰 수 (실제 토큰 수와 상당한 차이가 있을 수 있음)

        Note:
            각 제공업체별 정확한 토큰 계산을 위해서는:
            - OpenAI: tiktoken 라이브러리 사용
            - Anthropic: 공식 토크나이저 사용
            - Google: 해당 모델의 토크나이저 사용
        """
        # 간단한 추정 (단어 수 * 1.3) - 실제와 차이가 클 수 있음
        words = text.split()
        return int(len(words) * 1.3)

    def prepare_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        메시지를 해당 제공업체 형식으로 변환

        Args:
            messages: 원본 메시지 목록

        Returns:
            변환된 메시지 목록
        """
        # 기본 구현 - 하위 클래스에서 오버라이드
        return messages

    def get_supported_features(self) -> Dict[str, bool]:
        """
        지원 기능 정보 반환

        Returns:
            기능별 지원 여부
        """
        return {
            "streaming": True,
            "vision": False,
            "functions": False,
            "system_messages": True,
        }