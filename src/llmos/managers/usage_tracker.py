# src/llmos/managers/usage_tracker.py
"""
LLM OS - 사용량 추적 관리자
"""

import json
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..models.data_models import TokenUsage

logger = logging.getLogger(__name__)


class UsageTracker:
    """토큰 사용량 추적 관리자"""

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.usage_file = self.storage_path / "usage_history.jsonl"
        self.daily_summary_file = self.storage_path / "daily_summary.json"

        # 🔧 세션별 사용량 추적 - Streamlit session_state 활용
        import streamlit as st

        # session_state에 세션 사용량이 없으면 초기화
        if "usage_session_start_time" not in st.session_state:
            st.session_state.usage_session_start_time = datetime.now()

        if "usage_session_data" not in st.session_state:
            st.session_state.usage_session_data = {
                "total_tokens": 0,
                "total_cost": 0.0,
                "requests": 0,
                "by_model": {},
            }

        # 기존 속성들을 session_state 참조로 변경
        self.session_start_time = st.session_state.usage_session_start_time
        self.session_usage = st.session_state.usage_session_data

    def _load_usage_history(self) -> List[TokenUsage]:
        """사용량 히스토리 로드 (안전장치 포함)"""
        history = []
        if not self.usage_file.exists():
            return history

        try:
            with open(self.usage_file, "r", encoding="utf-8") as f:
                line_number = 0
                for line in f:
                    line_number += 1
                    line = line.strip()
                    if not line:  # 빈 줄 건너뛰기
                        continue

                    try:
                        # JSON 파싱 시도
                        usage_data = json.loads(line)

                        # 필수 필드 검증
                        required_fields = [
                            "input_tokens",
                            "output_tokens",
                            "total_tokens",
                            "model_name",
                            "provider",
                            "timestamp",
                            "cost_usd",
                        ]

                        if all(field in usage_data for field in required_fields):
                            history.append(TokenUsage.from_dict(usage_data))
                        else:
                            logger.warning(
                                f"Line {line_number}: Missing required fields, skipping"
                            )

                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"Line {line_number}: Invalid JSON format, skipping - {e}"
                        )
                        continue
                    except Exception as e:
                        logger.warning(
                            f"Line {line_number}: Error parsing usage data, skipping - {e}"
                        )
                        continue

        except Exception as e:
            logger.error(f"Error loading usage history file: {e}")

            # 파일이 심각하게 손상된 경우 백업 생성
            if self.usage_file.exists():
                try:
                    backup_file = self.usage_file.with_suffix(".backup")
                    self.usage_file.rename(backup_file)
                    logger.info(f"Corrupted usage file backed up to: {backup_file}")

                    # 새로운 빈 파일 생성
                    self.usage_file.touch()
                    logger.info("Created new empty usage history file")

                except Exception as backup_error:
                    logger.error(f"Failed to backup corrupted file: {backup_error}")

        logger.info(f"Loaded {len(history)} usage records from history")
        return history

    def add_usage(self, usage: TokenUsage):
        """사용량 기록 추가"""
        try:
            # JSONL 파일에 추가
            with open(self.usage_file, "a", encoding="utf-8") as f:
                json.dump(usage.to_dict(), f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            logger.error(f"Error saving usage entry: {e}")

        # 세션 사용량 업데이트
        self._update_session_usage(usage)

        # 일간 요약 업데이트
        self._update_daily_summary(usage)

    def _update_daily_summary(self, usage: TokenUsage):
        """일간 요약 업데이트"""
        today = datetime.now().date().isoformat()
        summary = {}

        if self.daily_summary_file.exists():
            try:
                with open(self.daily_summary_file, "r", encoding="utf-8") as f:
                    summary = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                summary = {}

        # 오늘 데이터 업데이트
        day_data = summary.setdefault(
            today, {"total_tokens": 0, "total_cost": 0.0, "requests": 0, "by_model": {}}
        )

        day_data["total_tokens"] += usage.total_tokens
        day_data["total_cost"] = round(day_data["total_cost"] + usage.cost_usd, 6)
        day_data["requests"] += 1

        # 모델별 통계
        model_key = f"{usage.provider}_{usage.model_name}"
        model_stats = day_data["by_model"].setdefault(
            model_key, {"tokens": 0, "cost": 0.0, "requests": 0}
        )

        model_stats["tokens"] += usage.total_tokens
        model_stats["cost"] = round(model_stats["cost"] + usage.cost_usd, 6)
        model_stats["requests"] += 1

        # 파일 저장
        try:
            with open(self.daily_summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving daily summary: {e}")

    def get_total_usage_from_history(self) -> dict:
        """전체 사용량 (히스토리 기반)"""
        all_history = self._load_usage_history()
        return {
            "total_tokens": sum(u.total_tokens for u in all_history),
            "total_cost": round(sum(u.cost_usd for u in all_history), 6),
            "total_requests": len(all_history),
        }

    def get_today_usage_from_summary(self) -> dict:
        """오늘 사용량 (요약 기반)"""
        today = datetime.now().date().isoformat()
        summary = {}

        if self.daily_summary_file.exists():
            try:
                with open(self.daily_summary_file, "r", encoding="utf-8") as f:
                    summary = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        today_data = summary.get(
            today, {"total_tokens": 0, "total_cost": 0.0, "requests": 0}
        )

        return {
            "total_tokens": today_data["total_tokens"],
            "total_cost": round(today_data["total_cost"], 6),
            "total_requests": today_data["requests"],
        }

    def get_usage_by_date_range(
        self, start_date: date, end_date: date
    ) -> Dict[str, Dict[str, Any]]:
        """날짜 범위별 사용량"""
        summary = {}

        if self.daily_summary_file.exists():
            try:
                with open(self.daily_summary_file, "r", encoding="utf-8") as f:
                    all_summary = json.load(f)

                current_date = start_date
                while current_date <= end_date:
                    date_str = current_date.isoformat()
                    if date_str in all_summary:
                        summary[date_str] = all_summary[date_str]
                    current_date += timedelta(days=1)

            except (json.JSONDecodeError, FileNotFoundError):
                pass

        return summary

    def get_weekly_usage(self) -> Dict[str, Any]:
        """지난 7일 사용량"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)

        weekly_data = self.get_usage_by_date_range(start_date, end_date)

        total_tokens = sum(
            day_data.get("total_tokens", 0) for day_data in weekly_data.values()
        )
        total_cost = sum(
            day_data.get("total_cost", 0.0) for day_data in weekly_data.values()
        )
        total_requests = sum(
            day_data.get("requests", 0) for day_data in weekly_data.values()
        )

        return {
            "period": f"{start_date.isoformat()} ~ {end_date.isoformat()}",
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 6),
            "total_requests": total_requests,
            "daily_breakdown": weekly_data,
        }

    def get_monthly_usage(self) -> Dict[str, Any]:
        """이번 달 사용량"""
        today = datetime.now().date()
        start_date = today.replace(day=1)

        monthly_data = self.get_usage_by_date_range(start_date, today)

        total_tokens = sum(
            day_data.get("total_tokens", 0) for day_data in monthly_data.values()
        )
        total_cost = sum(
            day_data.get("total_cost", 0.0) for day_data in monthly_data.values()
        )
        total_requests = sum(
            day_data.get("requests", 0) for day_data in monthly_data.values()
        )

        return {
            "period": f"{start_date.isoformat()} ~ {today.isoformat()}",
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 6),
            "total_requests": total_requests,
            "daily_breakdown": monthly_data,
        }

    def get_usage_by_model(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """모델별 사용량 통계"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        period_data = self.get_usage_by_date_range(start_date, end_date)

        model_stats = {}
        for day_data in period_data.values():
            by_model = day_data.get("by_model", {})
            for model_key, model_data in by_model.items():
                if model_key not in model_stats:
                    model_stats[model_key] = {"tokens": 0, "cost": 0.0, "requests": 0}

                model_stats[model_key]["tokens"] += model_data.get("tokens", 0)
                model_stats[model_key]["cost"] += model_data.get("cost", 0.0)
                model_stats[model_key]["requests"] += model_data.get("requests", 0)

        # 비용 반올림
        for model_key in model_stats:
            model_stats[model_key]["cost"] = round(model_stats[model_key]["cost"], 6)

        return model_stats

    def get_usage_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """사용량 트렌드 (일별)"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        daily_data = self.get_usage_by_date_range(start_date, end_date)

        trends = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            day_stats = daily_data.get(
                date_str, {"total_tokens": 0, "total_cost": 0.0, "requests": 0}
            )

            trends.append(
                {
                    "date": date_str,
                    "tokens": day_stats["total_tokens"],
                    "cost": round(day_stats["total_cost"], 6),
                    "requests": day_stats["requests"],
                }
            )

            current_date += timedelta(days=1)

        return trends

    def estimate_monthly_cost(self) -> float:
        """월 예상 비용 (현재까지 평균 기준)"""
        today = datetime.now().date()
        start_of_month = today.replace(day=1)
        days_elapsed = (today - start_of_month).days + 1

        monthly_usage = self.get_monthly_usage()
        current_cost = monthly_usage["total_cost"]

        if days_elapsed > 0:
            # 일평균 * 한달 일수
            days_in_month = 30  # 평균
            estimated_cost = (current_cost / days_elapsed) * days_in_month
            return round(estimated_cost, 6)

        return 0.0

    def cleanup_old_data(self, keep_days: int = 90) -> int:
        """오래된 데이터 정리"""
        cutoff_date = datetime.now().date() - timedelta(days=keep_days)

        # 일간 요약에서 오래된 데이터 제거
        removed_days = 0
        if self.daily_summary_file.exists():
            try:
                with open(self.daily_summary_file, "r", encoding="utf-8") as f:
                    summary = json.load(f)

                keys_to_remove = []
                for date_str in summary.keys():
                    try:
                        file_date = datetime.fromisoformat(date_str).date()
                        if file_date < cutoff_date:
                            keys_to_remove.append(date_str)
                    except ValueError:
                        continue

                for key in keys_to_remove:
                    del summary[key]
                    removed_days += 1

                with open(self.daily_summary_file, "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)

            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

        logger.info(f"Cleaned up {removed_days} days of old usage data")
        return removed_days

    def export_usage_data(self, days: Optional[int] = None) -> Dict[str, Any]:
        """사용량 데이터 내보내기"""
        if days:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days - 1)
            data = self.get_usage_by_date_range(start_date, end_date)
        else:
            # 전체 데이터
            if self.daily_summary_file.exists():
                try:
                    with open(self.daily_summary_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {}
            else:
                data = {}

        return {
            "exported_at": datetime.now().isoformat(),
            "data": data,
            "summary": {
                "total_days": len(data),
                "total_tokens": sum(
                    day.get("total_tokens", 0) for day in data.values()
                ),
                "total_cost": round(
                    sum(day.get("total_cost", 0.0) for day in data.values()), 6
                ),
                "total_requests": sum(day.get("requests", 0) for day in data.values()),
            },
        }

    def _update_session_usage(self, usage: TokenUsage):
        """세션 사용량 업데이트 (session_state 사용)"""
        import streamlit as st

        # session_state에서 직접 업데이트
        st.session_state.usage_session_data["total_tokens"] += usage.total_tokens
        st.session_state.usage_session_data["total_cost"] = round(
            st.session_state.usage_session_data["total_cost"] + usage.cost_usd, 6
        )
        st.session_state.usage_session_data["requests"] += 1

        # 모델별 통계
        model_key = f"{usage.provider}_{usage.model_name}"
        model_stats = st.session_state.usage_session_data["by_model"].setdefault(
            model_key, {"tokens": 0, "cost": 0.0, "requests": 0}
        )

        model_stats["tokens"] += usage.total_tokens
        model_stats["cost"] = round(model_stats["cost"] + usage.cost_usd, 6)
        model_stats["requests"] += 1

        # 로컬 참조도 업데이트
        self.session_usage = st.session_state.usage_session_data

    def get_session_usage(self) -> Dict[str, Any]:
        """현재 세션 사용량 반환 (session_state 사용)"""
        import streamlit as st

        # session_state에서 최신 데이터 가져오기
        session_start = st.session_state.usage_session_start_time
        session_data = st.session_state.usage_session_data

        session_duration = datetime.now() - session_start

        return {
            "session_start": session_start.isoformat(),
            "session_duration_minutes": round(session_duration.total_seconds() / 60, 2),
            "total_tokens": session_data["total_tokens"],
            "total_cost": round(session_data["total_cost"], 6),
            "total_requests": session_data["requests"],
            "by_model": session_data["by_model"],
        }

    def reset_session_usage(self):
        """세션 사용량 리셋 (새 세션 시작시 사용) - session_state 사용"""
        import streamlit as st

        # session_state 초기화
        st.session_state.usage_session_start_time = datetime.now()
        st.session_state.usage_session_data = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "requests": 0,
            "by_model": {},
        }

        # 로컬 참조도 업데이트
        self.session_start_time = st.session_state.usage_session_start_time
        self.session_usage = st.session_state.usage_session_data
