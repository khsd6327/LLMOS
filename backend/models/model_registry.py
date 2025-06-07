# ted-os-project/src/tedos/models/model_registry.py
"""
Ted OS - 모델 레지스트리
"""

import json
import logging
import os
from typing import Dict, List, Optional

from .data_models import ModelConfig
from .enums import ModelProvider

logger = logging.getLogger(__name__)


class ModelRegistry:
    """AI 모델 설정 레지스트리"""

    _models_data: Optional[Dict] = None
    _models_by_provider: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_models_data(cls) -> Dict:
        """models.json 파일에서 모델 데이터 로드"""
        if cls._models_data is not None:
            return cls._models_data

        try:
            # models.json 파일 경로 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            models_json_path = os.path.join(current_dir, "models.json")

            if not os.path.exists(models_json_path):
                logger.error(f"models.json file not found at {models_json_path}")
                raise FileNotFoundError(
                    f"models.json file not found at {models_json_path}"
                )

            # JSON 파일 로드
            with open(models_json_path, "r", encoding="utf-8") as f:
                cls._models_data = json.load(f)

            logger.info(f"Successfully loaded models data from {models_json_path}")
            return cls._models_data

        except Exception as e:
            logger.error(f"Error loading models.json: {e}")
            # 에러 시 빈 딕셔너리 반환
            cls._models_data = {}
            return cls._models_data

    @classmethod
    def _get_models_by_provider(cls) -> Dict[str, Dict]:
        """ModelConfig 객체로 변환된 모델 데이터 반환"""
        if cls._models_by_provider is not None:
            return cls._models_by_provider

        raw_data = cls._load_models_data()
        cls._models_by_provider = {}

        try:
            for provider_name, provider_data in raw_data.items():
                # 제공업체 enum 변환
                provider_enum_str = provider_data.get("provider", "")
                try:
                    provider_enum = ModelProvider[provider_enum_str]
                except KeyError:
                    logger.warning(
                        f"Unknown provider enum: {provider_enum_str} for {provider_name}"
                    )
                    continue

                # 모델들을 ModelConfig 객체로 변환
                models = {}
                for model_key, model_data in provider_data.get("models", {}).items():
                    try:
                        # provider enum 문자열을 실제 enum으로 변환
                        model_provider_str = model_data.get("provider", "")
                        model_provider_enum = ModelProvider[model_provider_str]

                        # ModelConfig 객체 생성
                        model_config = ModelConfig(
                            provider=model_provider_enum,
                            model_name=model_data.get("model_name", ""),
                            display_name=model_data.get("display_name", ""),
                            max_tokens=model_data.get("max_tokens", 4096),
                            supports_streaming=model_data.get(
                                "supports_streaming", False
                            ),
                            supports_functions=model_data.get(
                                "supports_functions", False
                            ),
                            supports_vision=model_data.get("supports_vision", False),
                            description=model_data.get("description", ""),
                            input_cost_per_1k=model_data.get("input_cost_per_1k", 0.0),
                            output_cost_per_1k=model_data.get(
                                "output_cost_per_1k", 0.0
                            ),
                        )
                        models[model_key] = model_config

                    except Exception as e:
                        logger.error(
                            f"Error converting model {model_key} for {provider_name}: {e}"
                        )
                        continue

                # 제공업체 데이터 저장
                cls._models_by_provider[provider_name] = {
                    "provider": provider_enum,
                    "models": models,
                }

            logger.info(
                f"Successfully converted {len(cls._models_by_provider)} providers to ModelConfig objects"
            )

        except Exception as e:
            logger.error(f"Error converting models data: {e}")
            cls._models_by_provider = {}

        return cls._models_by_provider

    @classmethod
    def get_all_provider_display_names(cls) -> List[str]:
        """모든 제공업체 표시명 반환"""
        models_data = cls._get_models_by_provider()
        return list(models_data.keys())

    @classmethod
    def get_models_for_provider(
        cls, provider_display_name: str
    ) -> Dict[str, ModelConfig]:
        """특정 제공업체의 모든 모델 반환"""
        models_data = cls._get_models_by_provider()
        return models_data.get(provider_display_name, {}).get("models", {})

    @classmethod
    def get_model_config(
        cls, provider_display_name: str, model_id_key: str
    ) -> Optional[ModelConfig]:
        """특정 모델 설정 반환"""
        return cls.get_models_for_provider(provider_display_name).get(model_id_key)

    @classmethod
    def get_provider_enum_by_display_name(
        cls, provider_display_name: str
    ) -> Optional[ModelProvider]:
        """표시명으로 제공업체 Enum 반환"""
        models_data = cls._get_models_by_provider()
        provider_data = models_data.get(provider_display_name)
        return provider_data["provider"] if provider_data else None

    @classmethod
    def add_model(cls, provider_display_name: str, model_id: str, config: ModelConfig):
        """새 모델 추가 (런타임에만 적용, JSON 파일은 수정하지 않음)"""
        models_data = cls._get_models_by_provider()
        if provider_display_name not in models_data:
            models_data[provider_display_name] = {
                "provider": config.provider,
                "models": {},
            }
        models_data[provider_display_name]["models"][model_id] = config
        logger.info(
            f"Added model {model_id} to provider {provider_display_name} (runtime only)"
        )

    @classmethod
    def remove_model(cls, provider_display_name: str, model_id: str) -> bool:
        """모델 제거 (런타임에만 적용, JSON 파일은 수정하지 않음)"""
        models_data = cls._get_models_by_provider()
        if provider_display_name in models_data:
            models = models_data[provider_display_name].get("models", {})
            if model_id in models:
                del models[model_id]
                logger.info(
                    f"Removed model {model_id} from provider {provider_display_name} (runtime only)"
                )
                return True
        return False

    @classmethod
    def get_all_models(cls) -> Dict[str, Dict[str, ModelConfig]]:
        """모든 모델 반환"""
        models_data = cls._get_models_by_provider()
        result = {}
        for provider_name, provider_data in models_data.items():
            result[provider_name] = provider_data.get("models", {})
        return result

    @classmethod
    def reload_models(cls):
        """모델 데이터 다시 로드 (캐시 초기화)"""
        cls._models_data = None
        cls._models_by_provider = None
        logger.info("Model data cache cleared, will reload on next access")

    @classmethod
    def get_models_json_path(cls) -> str:
        """models.json 파일 경로 반환"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "models.json")

    @classmethod
    def validate_models_data(cls) -> Dict[str, any]:
        """모델 데이터 유효성 검사"""
        try:
            models_data = cls._get_models_by_provider()
            total_providers = len(models_data)
            total_models = sum(
                len(provider_data.get("models", {}))
                for provider_data in models_data.values()
            )

            return {
                "valid": True,
                "total_providers": total_providers,
                "total_models": total_models,
                "providers": list(models_data.keys()),
                "message": f"Successfully loaded {total_providers} providers with {total_models} models",
            }
        except Exception as e:
            return {
                "valid": False,
                "total_providers": 0,
                "total_models": 0,
                "providers": [],
                "error": str(e),
                "message": f"Failed to load models data: {e}",
            }
