import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from src.tedos.models.data_models import FavoriteMessage
from src.tedos.models.enums import ModelProvider

from ..dependencies import AppContext, get_app_context
from ..models.favorite_models import FavoriteCreateRequest, FavoriteUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/favorites")


@router.get("", response_model=List[FavoriteMessage])
def get_favorites(
    query: Optional[str] = None,
    tags: Optional[str] = None,
    context: AppContext = Depends(get_app_context),
):
    try:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
        if query or tag_list:
            return context.favorite_manager.find_favorites(query=query, tags=tag_list)
        return context.favorite_manager.list_all_favorites()
    except Exception as e:
        logger.error(f"Error retrieving favorites: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve favorites")


@router.post("", response_model=FavoriteMessage)
def create_favorite(
    request: FavoriteCreateRequest,
    context: AppContext = Depends(get_app_context),
):
    try:
        created_at = datetime.fromisoformat(request.created_at.replace('Z', '+00:00'))
        model_provider = None
        if request.model_provider:
            try:
                model_provider = ModelProvider(request.model_provider)
            except ValueError:
                logger.warning(f"Invalid model provider: {request.model_provider}")
        return context.favorite_manager.add_favorite(
            session_id=request.session_id,
            message_id=request.message_id,
            role=request.role,
            content=request.content,
            created_at=created_at,
            model_provider=model_provider,
            model_name=request.model_name,
            context_messages=request.context_messages,
            tags=request.tags or [],
            notes=request.notes,
        )
    except ValueError as e:
        logger.error(f"Invalid request data: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating favorite: {e}")
        raise HTTPException(status_code=500, detail="Failed to create favorite")


@router.get("/{favorite_id}", response_model=FavoriteMessage)
def get_favorite(
    favorite_id: str,
    context: AppContext = Depends(get_app_context),
):
    favorite = context.favorite_manager.get_favorite_by_id(favorite_id)
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return favorite


@router.put("/{favorite_id}", response_model=FavoriteMessage)
def update_favorite(
    favorite_id: str,
    request: FavoriteUpdateRequest,
    context: AppContext = Depends(get_app_context),
):
    if request.tags is None and request.notes is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (tags or notes) must be provided for update",
        )
    updated = context.favorite_manager.update_favorite_details(
        favorite_id=favorite_id,
        tags=request.tags,
        notes=request.notes,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return updated


@router.delete("/{favorite_id}")
def delete_favorite(
    favorite_id: str,
    context: AppContext = Depends(get_app_context),
):
    success = context.favorite_manager.remove_favorite(favorite_id)
    if not success:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": f"Favorite {favorite_id} deleted successfully"}
