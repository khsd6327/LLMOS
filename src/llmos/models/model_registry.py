# src/llmos/models/model_registry.py
"""
LLM OS - 모델 레지스트리
"""

from typing import Dict, List, Optional

from .data_models import ModelConfig
from .enums import ModelProvider


class ModelRegistry:
    """AI 모델 설정 레지스트리"""
    
    MODELS_BY_PROVIDER: Dict[str, Dict[str, any]] = {
            "Google": {
                "provider": ModelProvider.GOOGLE,
                "models": {
                    "gemini-2.5-flash-preview-05-20": ModelConfig(
                        provider=ModelProvider.GOOGLE,
                        model_name="models/gemini-2.5-flash-preview-05-20",
                        display_name="Gemini 2.5 Flash Preview 05-20",
                        max_tokens=65536,
                        supports_streaming=True,
                        supports_functions=True,
                        supports_vision=True,
                        description="Our best model in terms of price-performance, offering well-rounded capabilities. Supports thinking, code execution, and function calling.",
                        input_cost_per_1k=0.00015,    # $0.15 per 1M tokens
                        output_cost_per_1k=0.0006     # $0.60 per 1M tokens (non-thinking)
                    ),
                    "gemini-2.5-pro-preview-05-06": ModelConfig(
                        provider=ModelProvider.GOOGLE,
                        model_name="gemini-2.5-pro-preview-05-06",
                        display_name="Gemini 2.5 Pro Preview",
                        max_tokens=65536,
                        supports_streaming=True,
                        supports_functions=True,
                        supports_vision=True,
                        description="Our state-of-the-art thinking model, capable of reasoning over complex problems in code, math, and STEM. Supports large document analysis.",
                        input_cost_per_1k=0.00125,    # $1.25 per 1M tokens (<=200k)
                        output_cost_per_1k=0.01       # $10.00 per 1M tokens (<=200k)
                    )
                }
            },
            "OpenAI": {
                "provider": ModelProvider.OPENAI,
                "models": {
                    "gpt-4.1": ModelConfig(
                        provider=ModelProvider.OPENAI,
                        model_name="gpt-4.1-2025-04-14",
                        display_name="GPT-4.1",
                        max_tokens=32768,
                        supports_streaming=True,
                        supports_functions=True,
                        supports_vision=True,
                        description="Flagship GPT model for complex tasks. Well suited for problem solving across domains with 1M+ context window.",
                        input_cost_per_1k=0.002,      # $2.00 per 1M tokens
                        output_cost_per_1k=0.008      # $8.00 per 1M tokens
                    ),
                    "o4-mini": ModelConfig(
                        provider=ModelProvider.OPENAI,
                        model_name="o4-mini-2025-04-16",
                        display_name="o4-mini",
                        max_tokens=100000,
                        supports_streaming=True,
                        supports_functions=True,
                        supports_vision=True,
                        description="Faster, more affordable reasoning model. Optimized for fast, effective reasoning with efficient performance in coding and visual tasks.",
                        input_cost_per_1k=0.0011,     # $1.10 per 1M tokens
                        output_cost_per_1k=0.0044     # $4.40 per 1M tokens
                    ),
                    "chatgpt-4o-latest": ModelConfig(
                        provider=ModelProvider.OPENAI,
                        model_name="chatgpt-4o-latest",
                        display_name="ChatGPT-4o",
                        max_tokens=16384,
                        supports_streaming=True,
                        supports_functions=False,
                        supports_vision=True,
                        description="GPT-4o model used in ChatGPT. Versatile, high-intelligence flagship model with text and image inputs.",
                        input_cost_per_1k=0.005,      # $5.00 per 1M tokens
                        output_cost_per_1k=0.015      # $15.00 per 1M tokens
                    ),
                    "gpt-4.1-mini": ModelConfig(
                        provider=ModelProvider.OPENAI,
                        model_name="gpt-4.1-mini-2025-04-14",
                        display_name="GPT-4.1 mini",
                        max_tokens=32768,
                        supports_streaming=True,
                        supports_functions=True,
                        supports_vision=True,
                        description="Balanced for intelligence, speed, and cost. Attractive model for many use cases with 1M+ context window.",
                        input_cost_per_1k=0.0004,     # $0.40 per 1M tokens
                        output_cost_per_1k=0.0016     # $1.60 per 1M tokens
                    ),
                    "gpt-4.1-nano": ModelConfig(
                        provider=ModelProvider.OPENAI,
                        model_name="gpt-4.1-nano-2025-04-14",
                        display_name="GPT-4.1 nano",
                        max_tokens=32768,
                        supports_streaming=True,
                        supports_functions=True,
                        supports_vision=True,
                        description="Fastest, most cost-effective GPT-4.1 model with 1M+ context window. Optimized for speed and efficiency.",
                        input_cost_per_1k=0.0001,     # $0.10 per 1M tokens
                        output_cost_per_1k=0.0004     # $0.40 per 1M tokens
                    )
                }
            },
            "Anthropic": {
                "provider": ModelProvider.ANTHROPIC,
                "models": {
                    "claude-opus-4-20250514": ModelConfig(
                        provider=ModelProvider.ANTHROPIC,
                        model_name="claude-opus-4-20250514",
                        display_name="Claude Opus 4",
                        max_tokens=65536,
                        supports_streaming=True,
                        supports_functions=True,
                        supports_vision=True,
                        description="Anthropic's most powerful model with superior performance on highly complex tasks, including research and advanced analysis.",
                        input_cost_per_1k=0.015,      # $15.00 per 1M tokens
                        output_cost_per_1k=0.075      # $75.00 per 1M tokens
                    ),
                    "claude-sonnet-4-20250514": ModelConfig(
                        provider=ModelProvider.ANTHROPIC,
                        model_name="claude-sonnet-4-20250514",
                        display_name="Claude Sonnet 4",
                        max_tokens=65536,
                        supports_streaming=True,
                        supports_functions=True,
                        supports_vision=True,
                        description="Smart, efficient model for everyday use. Balanced performance for a wide range of tasks with excellent cost-effectiveness.",
                        input_cost_per_1k=0.003,      # $3.00 per 1M tokens
                        output_cost_per_1k=0.015      # $15.00 per 1M tokens
                    )
                }
            }
        }
    
    @classmethod
    def get_all_provider_display_names(cls) -> List[str]:
        """모든 제공업체 표시명 반환"""
        return list(cls.MODELS_BY_PROVIDER.keys())

    @classmethod
    def get_models_for_provider(cls, provider_display_name: str) -> Dict[str, ModelConfig]:
        """특정 제공업체의 모든 모델 반환"""
        return cls.MODELS_BY_PROVIDER.get(provider_display_name, {}).get("models", {})

    @classmethod
    def get_model_config(cls, provider_display_name: str, model_id_key: str) -> Optional[ModelConfig]:
        """특정 모델 설정 반환"""
        return cls.get_models_for_provider(provider_display_name).get(model_id_key)

    @classmethod
    def get_provider_enum_by_display_name(cls, provider_display_name: str) -> Optional[ModelProvider]:
        """표시명으로 제공업체 Enum 반환"""
        provider_data = cls.MODELS_BY_PROVIDER.get(provider_display_name)
        return provider_data["provider"] if provider_data else None

    @classmethod
    def add_model(cls, provider_display_name: str, model_id: str, config: ModelConfig):
        """새 모델 추가"""
        if provider_display_name not in cls.MODELS_BY_PROVIDER:
            cls.MODELS_BY_PROVIDER[provider_display_name] = {
                "provider": config.provider,
                "models": {}
            }
        cls.MODELS_BY_PROVIDER[provider_display_name]["models"][model_id] = config

    @classmethod
    def remove_model(cls, provider_display_name: str, model_id: str) -> bool:
        """모델 제거"""
        if provider_display_name in cls.MODELS_BY_PROVIDER:
            models = cls.MODELS_BY_PROVIDER[provider_display_name].get("models", {})
            if model_id in models:
                del models[model_id]
                return True
        return False

    @classmethod
    def get_all_models(cls) -> Dict[str, Dict[str, ModelConfig]]:
        """모든 모델 반환"""
        result = {}
        for provider_name, provider_data in cls.MODELS_BY_PROVIDER.items():
            result[provider_name] = provider_data.get("models", {})
        return result