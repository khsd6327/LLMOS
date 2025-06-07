from typing import Any, Dict, List
from pydantic import BaseModel


class SettingsUpdateRequest(BaseModel):
    updates: Dict[str, Any]


class SettingsResponse(BaseModel):
    settings: Dict[str, Any]
    message: str = "Settings retrieved successfully"


class UsageStatsResponse(BaseModel):
    total_usage: Dict[str, Any]
    today_usage: Dict[str, Any]
    weekly_usage: Dict[str, Any]
    monthly_usage: Dict[str, Any]
    usage_by_model: Dict[str, Any]
    usage_trends: List[Dict[str, Any]]
    estimated_monthly_cost: float
    message: str = "Usage statistics retrieved successfully"


class ProviderStatusResponse(BaseModel):
    providers: Dict[str, Dict[str, Any]]
    summary: Dict[str, Any]
    message: str = "Provider status retrieved successfully"
