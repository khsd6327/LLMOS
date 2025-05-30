# src/llmos/utils/logging_handler.py
"""
LLM OS - 로깅 핸들러
"""

import logging
from collections import deque
from typing import Deque, List, Optional

from ..core.config import LOG_HANDLER_MAX_LEN


class AppLogHandler(logging.Handler):
    """애플리케이션 전용 로그 핸들러"""

    def __init__(self, maxlen: int = LOG_HANDLER_MAX_LEN):
        super().__init__()
        self.records: Deque[str] = deque(maxlen=maxlen)
        self.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s (%(name)s)'
            )
        )

    def emit(self, record: logging.LogRecord):
        """로그 레코드 처리"""
        try:
            self.records.append(self.format(record))
        except Exception:
            self.handleError(record)

    def get_logs(self, count: Optional[int] = None) -> List[str]:
        """로그 목록 반환"""
        logs = list(self.records)
        if count:
            return logs[-count:]
        return logs

    def get_recent_logs(self, count: int = 50) -> List[str]:
        """최근 로그 반환"""
        return self.get_logs(count)

    def clear_logs(self):
        """로그 기록 삭제"""
        self.records.clear()

    def get_log_count(self) -> int:
        """저장된 로그 수 반환"""
        return len(self.records)

    def get_logs_by_level(self, level: str) -> List[str]:
        """특정 레벨의 로그만 반환"""
        filtered_logs = []
        for log_entry in self.records:
            if f" - {level.upper()} - " in log_entry:
                filtered_logs.append(log_entry)
        return filtered_logs

    def search_logs(self, query: str) -> List[str]:
        """로그 검색"""
        matching_logs = []
        query_lower = query.lower()
        
        for log_entry in self.records:
            if query_lower in log_entry.lower():
                matching_logs.append(log_entry)
        
        return matching_logs


# 전역 로그 핸들러 인스턴스
app_log_handler = AppLogHandler()


def setup_logging(level: int = logging.INFO):
    """로깅 설정"""
    # 루트 로거 설정
    root_logger = logging.getLogger()
    
    # 기본 설정
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 앱 로그 핸들러 추가
    if app_log_handler not in root_logger.handlers:
        root_logger.addHandler(app_log_handler)

def get_log_handler() -> AppLogHandler:
    """앱 로그 핸들러 반환"""
    return app_log_handler