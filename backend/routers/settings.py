import logging
from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import AppContext, get_app_context
from ..models.status_models import SettingsUpdateRequest, SettingsResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/settings", response_model=SettingsResponse)
def get_settings(context: AppContext = Depends(get_app_context)):
    try:
        safe_settings = context.settings.export_settings()
        return SettingsResponse(settings=safe_settings)
    except Exception as e:
        logger.error(f"Error retrieving settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve settings")


@router.put("/settings", response_model=SettingsResponse)
def update_settings(
    request: SettingsUpdateRequest,
    context: AppContext = Depends(get_app_context),
):
    try:
        updated_count = 0
        for key_path, value in request.updates.items():
            if key_path.startswith("api_keys."):
                logger.warning(f"Attempted to update API key via settings API: {key_path}")
                continue
            context.settings.set(key_path, value)
            updated_count += 1
        safe_settings = context.settings.export_settings()
        return SettingsResponse(settings=safe_settings, message=f"Successfully updated {updated_count} settings")
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")
