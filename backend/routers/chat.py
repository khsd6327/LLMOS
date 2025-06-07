import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List

from ..dependencies import AppContext, get_app_context
from ..models.chat_models import (
    ChatMessageRequest,
    SessionCreateRequest,
    SessionUpdateRequest,
    SessionResponse,
)
from src.tedos.models.data_models import ChatSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
def health_check():
    return {"message": "Ted OS Backend is running"}


@router.get("/api/sessions", response_model=List[ChatSession])
def get_chat_sessions(context: AppContext = Depends(get_app_context)):
    return context.chat_manager.get_all_sessions()


@router.post("/api/sessions/{session_id}/chat")
async def handle_chat_message(
    session_id: str,
    request: ChatMessageRequest,
    context: AppContext = Depends(get_app_context),
):
    session = context.chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    new_message = {"role": "user", "content": request.prompt}
    session.messages.append(new_message)
    context.chat_manager.update_session(session)

    provider_name = request.model_provider or context.settings.get("ui.selected_provider")
    model_id = request.model_name or context.settings.get("defaults.model")
    if not provider_name or not model_id:
        raise HTTPException(status_code=400, detail="Model provider or name not configured")

    async def stream_wrapper():
        try:
            current_session = context.chat_manager.get_session(session_id)
            messages = current_session.messages
            ai_message = {"role": "assistant", "content": ""}
            current_session.messages.append(ai_message)
            ai_index = len(current_session.messages) - 1

            stream_gen = context.model_manager.stream_generate(
                messages=messages[:-1],
                provider_display_name=provider_name,
                model_id_key=model_id,
            )
            full_response = ""
            for chunk, _ in stream_gen:
                full_response += chunk
                current_session.messages[ai_index]["content"] = full_response
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.01)
            context.chat_manager.update_session(current_session)
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            yield f"data: 오류가 발생했습니다: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_wrapper(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/api/sessions", response_model=SessionResponse)
def create_session(
    request: SessionCreateRequest,
    context: AppContext = Depends(get_app_context),
):
    session = context.chat_manager.create_session(title=request.title)
    return SessionResponse(session=session, message="Session created successfully")


@router.delete("/api/sessions/{session_id}")
def delete_session(session_id: str, context: AppContext = Depends(get_app_context)):
    success = context.chat_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": f"Session {session_id} deleted successfully"}


@router.put("/api/sessions/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: str,
    request: SessionUpdateRequest,
    context: AppContext = Depends(get_app_context),
):
    session = context.chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if request.title is None and request.is_pinned is None:
        raise HTTPException(
            status_code=400,
            detail="At least one field (title or is_pinned) must be provided for update",
        )

    if request.title is not None:
        context.chat_manager.update_session_title(session_id, request.title)

    if request.is_pinned is not None:
        if request.is_pinned:
            if not context.chat_manager.pin_session(session_id):
                raise HTTPException(
                    status_code=400,
                    detail="Failed to pin session (maximum 7 pinned sessions allowed)",
                )
        else:
            context.chat_manager.unpin_session(session_id)

    updated = context.chat_manager.get_session(session_id)
    return SessionResponse(session=updated, message="Session updated successfully")
