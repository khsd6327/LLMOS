import logging
from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import AppContext, get_app_context
from ..models.status_models import UsageStatsResponse, ProviderStatusResponse
from src.tedos.models.model_registry import ModelRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/status")


@router.get("/usage", response_model=UsageStatsResponse)
def get_usage_statistics(context: AppContext = Depends(get_app_context)):
    try:
        total_usage = context.usage_tracker.get_total_usage_from_history()
        today_usage = context.usage_tracker.get_today_usage_from_summary()
        weekly_usage = context.usage_tracker.get_weekly_usage()
        monthly_usage = context.usage_tracker.get_monthly_usage()
        usage_by_model = context.usage_tracker.get_usage_by_model(days=30)
        usage_trends = context.usage_tracker.get_usage_trends(days=7)
        estimated_monthly_cost = context.usage_tracker.estimate_monthly_cost()
        return UsageStatsResponse(
            total_usage=total_usage,
            today_usage=today_usage,
            weekly_usage=weekly_usage,
            monthly_usage=monthly_usage,
            usage_by_model=usage_by_model,
            usage_trends=usage_trends,
            estimated_monthly_cost=estimated_monthly_cost,
        )
    except Exception as e:
        logger.error(f"Error retrieving usage statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage statistics")


@router.get("/providers", response_model=ProviderStatusResponse)
def get_provider_status(context: AppContext = Depends(get_app_context)):
    try:
        provider_names = ModelRegistry.get_all_provider_display_names()
        providers_status = {}
        total_providers = len(provider_names)
        configured_count = 0
        total_models = 0

        for provider_name in provider_names:
            provider_enum = ModelRegistry.get_provider_enum_by_display_name(provider_name)
            has_api_key = False
            if provider_enum:
                has_api_key = context.settings.has_api_key(provider_enum)
                if has_api_key:
                    configured_count += 1
            models = ModelRegistry.get_models_for_provider(provider_name)
            model_count = len(models)
            total_models += model_count
            model_summaries = []
            for model_id, model_config in models.items():
                model_summaries.append({
                    "id": model_id,
                    "display_name": model_config.display_name,
                    "max_tokens": model_config.max_tokens,
                    "supports_streaming": model_config.supports_streaming,
                    "supports_vision": model_config.supports_vision,
                    "supports_functions": model_config.supports_functions,
                    "input_cost_per_1k": model_config.input_cost_per_1k,
                    "output_cost_per_1k": model_config.output_cost_per_1k,
                })
            providers_status[provider_name] = {
                "provider_enum": provider_enum.value if provider_enum else None,
                "api_key_configured": has_api_key,
                "status": "configured" if has_api_key else "not_configured",
                "model_count": model_count,
                "models": model_summaries,
            }
        summary = {
            "total_providers": total_providers,
            "configured_providers": configured_count,
            "unconfigured_providers": total_providers - configured_count,
            "total_models": total_models,
            "configuration_rate": round(configured_count / total_providers * 100, 1) if total_providers > 0 else 0,
        }
        return ProviderStatusResponse(providers=providers_status, summary=summary)
    except Exception as e:
        logger.error(f"Error retrieving provider status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve provider status")
