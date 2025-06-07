# ted-os-project/src/tedos/managers/settings.py
"""
Ted OS - 설정 관리자
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

from ..models.enums import ModelProvider
from ..core.config import (
    DEFAULT_CONFIG_DIR,
    CHAT_SESSIONS_DIR,
    ARTIFACTS_DIR,
    USAGE_DATA_DIR,
    FAVORITES_DIR,
    DEFAULT_MODELS,
    DEFAULT_PROVIDER,
)

logger = logging.getLogger(__name__)


class SettingsManager:
    """애플리케이션 설정 관리자"""

    def __init__(self, config_path_name: str = DEFAULT_CONFIG_DIR):
        self.config_path = Path.home() / config_path_name
        self.config_file = self.config_path / "settings.json"
        self.env_file = self.config_path / ".env"
        self.settings: Dict[str, Any] = {}

        self._ensure_config_directory()
        self.load_settings()

    def _ensure_config_directory(self):
        """설정 디렉토리 생성"""
        self.config_path.mkdir(parents=True, exist_ok=True)

    def load_settings(self):
        """설정 파일 로드"""
        # 환경 변수 파일 로드
        if self.env_file.exists():
            load_dotenv(self.env_file, override=True)

        # 기본 설정
        defaults = self._get_default_settings()

        # 설정 파일에서 로드
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)

                self.settings = defaults.copy()
                for k, v in loaded_settings.items():
                    if isinstance(v, dict) and isinstance(self.settings.get(k), dict):
                        self.settings[k].update(v)
                    else:
                        self.settings[k] = v
            except json.JSONDecodeError as e:
                logger.error(f"Error loading settings file: {e}")
                self.settings = defaults
        else:
            self.settings = defaults

        # 설정 저장
        self.save_settings()

    def _get_default_settings(self) -> dict:
        """기본 설정 반환"""
        return {
            "api_keys": {
                p.value: os.getenv(f"{p.name}_API_KEY", "") for p in ModelProvider
            },
            "paths": {
                "chat_sessions": str(self.config_path / CHAT_SESSIONS_DIR),
                "artifacts": str(self.config_path / ARTIFACTS_DIR),
                "usage_tracking": str(self.config_path / USAGE_DATA_DIR),
                "favorites": str(self.config_path / FAVORITES_DIR),
            },
            "defaults": {
                "models_by_provider": DEFAULT_MODELS.copy(),
                "temperature": 0.7,
                "max_tokens": 4000,
            },
            "ui": {
                "selected_provider": DEFAULT_PROVIDER,  # ← 기본 제공업체 설정
                "theme": "auto",
                "language": "ko",
            },
        }

    def save_settings(self):
        """설정 파일 저장"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving settings: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """설정 값 가져오기 (점 표기법 지원)"""
        val = self.settings
        try:
            for k in key_path.split("."):
                val = val[k]
            return val
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any):
        """설정 값 설정 (점 표기법 지원)"""
        lvl = self.settings
        keys = key_path.split(".")

        # 중간 딕셔너리들 생성
        for k in keys[:-1]:
            lvl = lvl.setdefault(k, {})

        # 최종 값 설정
        lvl[keys[-1]] = value
        self.save_settings()

    def set_api_key(self, provider_val: str, api_key: str):
        """API 키 설정"""
        env_key = f"{provider_val.upper()}_API_KEY"
        lines = []
        found = False

        # 기존 .env 파일 읽기
        if self.env_file.exists():
            with open(self.env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith(f"{env_key}="):
                        lines.append(f"{env_key}={api_key}\n")
                        found = True
                    else:
                        lines.append(line)

        # 새 키 추가
        if not found:
            lines.append(f"{env_key}={api_key}\n")

        # .env 파일 쓰기
        try:
            with open(self.env_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception as e:
            logger.error(f"Error writing to .env: {e}")

        # 환경 변수와 설정에 저장
        os.environ[env_key] = api_key
        self.set(f"api_keys.{provider_val}", api_key)

    def ensure_paths_exist(self):
        """필요한 디렉토리들 생성"""
        for _, p_val in self.get("paths", {}).items():
            try:
                Path(p_val).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creating directory {p_val}: {e}")

    def get_api_key(self, provider: ModelProvider) -> str:
        """특정 제공업체의 API 키 반환"""
        return self.get(f"api_keys.{provider.value}", "")

    def has_api_key(self, provider: ModelProvider) -> bool:
        """API 키 존재 여부 확인"""
        api_key = self.get_api_key(provider)
        return bool(api_key and api_key.strip())

    def get_all_api_keys(self) -> Dict[str, str]:
        """모든 API 키 반환"""
        return self.get("api_keys", {})

    def reset_to_defaults(self):
        """설정을 기본값으로 리셋"""
        self.settings = self._get_default_settings()
        self.save_settings()
        logger.info("Settings reset to defaults")

    def export_settings(self) -> Dict[str, Any]:
        """설정 내보내기 (API 키 제외)"""
        export_data = self.settings.copy()
        # API 키는 보안상 제외
        if "api_keys" in export_data:
            export_data["api_keys"] = {
                k: "***" if v else "" for k, v in export_data["api_keys"].items()
            }
        return export_data

    def import_settings(
        self, settings_data: Dict[str, Any], include_api_keys: bool = False
    ):
        """설정 가져오기"""
        for key, value in settings_data.items():
            if key == "api_keys" and not include_api_keys:
                continue
            self.set(key, value)

    def get_default_model_for_provider(self, provider_name: str) -> str:
        """특정 제공업체의 기본 모델 반환"""
        default_models = self.get("defaults.models_by_provider", {})
        return default_models.get(provider_name, "")

    def set_default_model_for_provider(self, provider_name: str, model_id: str):
        """특정 제공업체의 기본 모델 설정"""
        self.set(f"defaults.models_by_provider.{provider_name}", model_id)

    def get_all_default_models(self) -> Dict[str, str]:
        """모든 제공업체의 기본 모델 반환"""
        return self.get("defaults.models_by_provider", {})
