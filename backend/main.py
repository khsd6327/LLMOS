# ted-os-project/backend/main.py
"""
Ted OS - Backend API Server (FastAPI)
"""

import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# --- 프로젝트 루트 경로 설정 ---
# 이 파일의 위치(backend/)의 부모 폴더(프로젝트 루트)를 시스템 경로에 추가합니다.
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# ------------------------------

# --- 기존 Ted OS 매니저들 임포트 ---
from backend.managers.settings import SettingsManager
from backend.managers.chat_sessions import ChatSessionManager
from backend.managers.model_manager import EnhancedModelManager
from backend.managers.usage_tracker import UsageTracker
from backend.models.data_models import ChatSession, FavoriteMessage
from backend.models.enums import ModelProvider
from backend.managers.favorite_manager import FavoriteManager
from backend.managers.spotify_manager import SpotifyManager
from backend.models.model_registry import ModelRegistry
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import logging
import uuid

# --- 로거 설정 ---
logger = logging.getLogger(__name__)


# --- 작업 상태 추적 시스템 ---
class JobManager:
    def __init__(self):
        self.jobs = {}  # job_id -> job_status
        self.executor = ThreadPoolExecutor(max_workers=3)  # 동시 실행 제한

    def create_job(self, job_type: str) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "id": job_id,
            "type": job_type,
            "status": "started",
            "progress": 0,
            "current_step": "초기화 중...",
            "total_items": None,
            "processed_items": 0,
            "error_message": None,
            "started_at": datetime.now().isoformat(),
            "completed_at": None
        }
        return job_id

    def update_job(self, job_id: str, **updates):
        if job_id in self.jobs:
            self.jobs[job_id].update(updates)

    def get_job(self, job_id: str) -> dict:
        return self.jobs.get(job_id)

    def complete_job(self, job_id: str, success: bool = True, error: str = None):
        if job_id in self.jobs:
            self.jobs[job_id].update({
                "status": "completed" if success else "failed",
                "progress": 100 if success else self.jobs[job_id]["progress"],
                "error_message": error,
                "completed_at": datetime.now().isoformat(),
                "current_step": "완료" if success else "오류 발생"
            })


job_manager = JobManager()

# ------------------------------------

# --- FastAPI 애플리케이션 생성 ---
app = FastAPI(
    title="Ted OS Backend API",
    description="Ted OS의 비즈니스 로직을 제공하는 API 서버",
    version="0.1.0",
)
# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용 - 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)
# ---------------------------------

# --- 애플리케이션 컨텍스트 (싱글톤) ---
# 서버가 실행되는 동안 단 한 번만 매니저들을 초기화하고,
# API 요청이 있을 때마다 재사용하기 위한 구조입니다.
class AppContext:
    def __init__(self):
        self.settings = SettingsManager()
        self.settings.ensure_paths_exist()
        self.usage_tracker = UsageTracker(self.settings.get("paths.usage_tracking"))
        self.model_manager = EnhancedModelManager(self.settings, self.usage_tracker)
        self.chat_manager = ChatSessionManager(self.settings.get("paths.chat_sessions"))
        self.favorite_manager = FavoriteManager(self.settings.get("paths.favorites"))
        self.spotify_manager = SpotifyManager(self.settings)

app_context = AppContext()
# ------------------------------------

# --- FastAPI 의존성 주입 ---
# 각 API 엔드포인트에서 매니저 객체들을 쉽게 가져다 쓸 수 있도록 합니다.
def get_app_context() -> AppContext:
    return app_context
# --------------------------

# --- API 엔드포인트 정의 ---

class ChatMessageRequest(BaseModel):
    """채팅 요청 모델"""
    prompt: str
    model_provider: str | None = None
    model_name: str | None = None

class SettingsUpdateRequest(BaseModel):
    """설정 업데이트 요청 모델"""
    updates: Dict[str, Any]  # 키-값 쌍으로 설정 업데이트

class SettingsResponse(BaseModel):
    """설정 조회 응답 모델"""
    settings: Dict[str, Any]
    message: str = "Settings retrieved successfully"

class FavoriteCreateRequest(BaseModel):
    """즐겨찾기 생성 요청 모델"""
    session_id: str
    message_id: str
    role: str
    content: str
    created_at: str  # ISO format datetime string
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    context_messages: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class FavoriteUpdateRequest(BaseModel):
    """즐겨찾기 업데이트 요청 모델"""
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class FavoriteSearchRequest(BaseModel):
    """즐겨찾기 검색 요청 모델"""
    query: Optional[str] = None
    tags: Optional[List[str]] = None

class UsageStatsResponse(BaseModel):
    """사용량 통계 응답 모델"""
    total_usage: Dict[str, Any]
    today_usage: Dict[str, Any]
    weekly_usage: Dict[str, Any]
    monthly_usage: Dict[str, Any]
    usage_by_model: Dict[str, Any]
    usage_trends: List[Dict[str, Any]]
    estimated_monthly_cost: float
    message: str = "Usage statistics retrieved successfully"

class ProviderStatusResponse(BaseModel):
    """AI 제공업체 상태 응답 모델"""
    providers: Dict[str, Dict[str, Any]]
    summary: Dict[str, Any]
    message: str = "Provider status retrieved successfully"

class SessionCreateRequest(BaseModel):
    """세션 생성 요청 모델"""
    title: Optional[str] = None

class SessionUpdateRequest(BaseModel):
    """세션 업데이트 요청 모델"""
    title: Optional[str] = None
    is_pinned: Optional[bool] = None

class SessionResponse(BaseModel):
    """세션 응답 모델"""
    session: ChatSession
    message: str = "Session operation completed successfully"

class SpotifyStatusResponse(BaseModel):
    """Spotify 상태 응답 모델"""
    is_configured: bool
    is_authenticated: bool
    user_id: Optional[str] = None
    message: str = "Spotify status retrieved successfully"

class SpotifyPlaylistsResponse(BaseModel):
    """Spotify 플레이리스트 목록 응답 모델"""
    playlists: List[Dict[str, Any]]
    count: int
    message: str = "Playlists retrieved successfully"

class SpotifyTracksResponse(BaseModel):
    """Spotify 트랙 목록 응답 모델"""
    tracks: List[Dict[str, Any]]
    count: int
    message: str = "Tracks retrieved successfully"

class SyncJobResponse(BaseModel):
    """동기화 작업 응답 모델"""
    job_id: str
    status: str  # "started", "running", "completed", "failed"
    message: str

class SyncStatusResponse(BaseModel):
    """동기화 상태 응답 모델"""
    job_id: str
    status: str
    progress: int  # 0-100
    current_step: str
    total_items: Optional[int] = None
    processed_items: Optional[int] = None
    error_message: Optional[str] = None
    started_at: str
    completed_at: Optional[str] = None
    
@app.get("/")
def read_root():
    """헬스 체크 엔드포인트"""
    return {"message": "Ted OS Backend is running"}

@app.get("/api/sessions", response_model=list[ChatSession])
def get_chat_sessions(context: AppContext = Depends(get_app_context)):
    """모든 채팅 세션 목록을 가져옵니다."""
    sessions = context.chat_manager.get_all_sessions()
    return sessions

from fastapi.responses import StreamingResponse
import asyncio


@app.post("/api/sessions/{session_id}/chat")
async def handle_chat_message(
        session_id: str,
        request: ChatMessageRequest,
        context: AppContext = Depends(get_app_context)
):
    """지정된 세션에 채팅 메시지를 보내고 AI의 응답을 스트리밍으로 받습니다."""
    logger.info(
        ">>>>>>>>>>>>> CHAT HANDLER EXECUTING! FILE IS SAVED. <<<<<<<<<<<<<"
    )

    session = context.chat_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # 1. 새로운 메시지 딕셔너리를 만듭니다.
    new_message = {"role": "user", "content": request.prompt}

    # 2. 현재 세션의 messages 리스트에 직접 추가합니다.
    session.messages.append(new_message)

    # 3. 변경된 세션 객체를 저장하여 업데이트합니다.
    context.chat_manager.update_session(session)

    provider_name = request.model_provider or context.settings.get("ui.selected_provider")
    model_id = request.model_name or context.settings.get_default_model_for_provider(provider_name)

    if not provider_name or not model_id:
        raise HTTPException(status_code=400, detail="Model provider or name not configured")

    async def stream_wrapper():
        try:
            current_session = context.chat_manager.get_session(session_id)
            messages = current_session.messages
            
            # AI 응답 메시지를 세션에 미리 추가
            ai_message = {"role": "assistant", "content": ""}
            current_session.messages.append(ai_message)
            ai_message_index = len(current_session.messages) - 1

            stream_generator = context.model_manager.stream_generate(
                messages=messages[:-1],  # AI 응답 메시지는 제외
                provider_display_name=provider_name,
                model_id_key=model_id
            )

            full_response = ""
            for chunk, _ in stream_generator:
                full_response += chunk
                
                # 세션에 누적된 응답 저장
                current_session.messages[ai_message_index]["content"] = full_response
                
                # 클라이언트에 청크 전송
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.01)  # 작은 지연으로 안정성 확보

            # 최종 세션 저장
            context.chat_manager.update_session(current_session)
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            yield f"data: 오류가 발생했습니다: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_wrapper(), 
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/api/settings", response_model=SettingsResponse)
def get_settings(context: AppContext = Depends(get_app_context)):
    """현재 애플리케이션 설정을 조회합니다. (API 키 등 민감 정보 제외)"""
    try:
        # SettingsManager의 export_settings 메서드 사용 (API 키 자동 제외)
        safe_settings = context.settings.export_settings()
        return SettingsResponse(settings=safe_settings)
    except Exception as e:
        logger.error(f"Error retrieving settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve settings")


# --- 즐겨찾기 API 엔드포인트들 ---

# --- 즐겨찾기 API 엔드포인트들 ---

@app.get("/api/favorites", response_model=List[FavoriteMessage])
def get_favorites(
        query: Optional[str] = None,
        tags: Optional[str] = None,  # 쉼표로 구분된 태그 문자열
        context: AppContext = Depends(get_app_context)
):
    """즐겨찾기 목록을 조회합니다. 검색 기능 포함."""
    try:
        # 태그 문자열을 리스트로 변환
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        # 검색어나 태그가 있으면 검색, 없으면 전체 조회
        if query or tag_list:
            favorites = context.favorite_manager.find_favorites(query=query, tags=tag_list)
        else:
            favorites = context.favorite_manager.list_all_favorites()

        return favorites

    except Exception as e:
        logger.error(f"Error retrieving favorites: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve favorites")


@app.post("/api/favorites", response_model=FavoriteMessage)
def create_favorite(
        request: FavoriteCreateRequest,
        context: AppContext = Depends(get_app_context)
):
    """새로운 즐겨찾기를 생성합니다."""
    try:
        # 문자열을 datetime으로 변환
        created_at = datetime.fromisoformat(request.created_at.replace('Z', '+00:00'))

        # ModelProvider 변환
        model_provider = None
        if request.model_provider:
            try:
                model_provider = ModelProvider(request.model_provider)
            except ValueError:
                logger.warning(f"Invalid model provider: {request.model_provider}")

        # 즐겨찾기 추가
        favorite = context.favorite_manager.add_favorite(
            session_id=request.session_id,
            message_id=request.message_id,
            role=request.role,
            content=request.content,
            created_at=created_at,
            model_provider=model_provider,
            model_name=request.model_name,
            context_messages=request.context_messages,
            tags=request.tags or [],
            notes=request.notes
        )

        return favorite

    except ValueError as e:
        logger.error(f"Invalid request data: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating favorite: {e}")
        raise HTTPException(status_code=500, detail="Failed to create favorite")


@app.get("/api/favorites/{favorite_id}", response_model=FavoriteMessage)
def get_favorite(
        favorite_id: str,
        context: AppContext = Depends(get_app_context)
):
    """특정 즐겨찾기를 조회합니다."""
    try:
        favorite = context.favorite_manager.get_favorite_by_id(favorite_id)
        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")

        return favorite

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving favorite {favorite_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve favorite")


@app.put("/api/favorites/{favorite_id}", response_model=FavoriteMessage)
def update_favorite(
        favorite_id: str,
        request: FavoriteUpdateRequest,
        context: AppContext = Depends(get_app_context)
):
    """즐겨찾기의 태그나 노트를 업데이트합니다."""
    try:
        # 최소 하나의 필드는 업데이트되어야 함
        if request.tags is None and request.notes is None:
            raise HTTPException(
                status_code=400,
                detail="At least one field (tags or notes) must be provided for update"
            )

        updated_favorite = context.favorite_manager.update_favorite_details(
            favorite_id=favorite_id,
            tags=request.tags,
            notes=request.notes
        )

        if not updated_favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")

        return updated_favorite

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating favorite {favorite_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update favorite")


@app.delete("/api/favorites/{favorite_id}")
def delete_favorite(
        favorite_id: str,
        context: AppContext = Depends(get_app_context)
):
    """즐겨찾기를 삭제합니다."""
    try:
        success = context.favorite_manager.remove_favorite(favorite_id)

        if not success:
            raise HTTPException(status_code=404, detail="Favorite not found")

        return {"message": f"Favorite {favorite_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting favorite {favorite_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete favorite")

@app.get("/api/status/usage", response_model=UsageStatsResponse)
def get_usage_statistics(context: AppContext = Depends(get_app_context)):
    """토큰 사용량 통계를 조회합니다."""
    try:
        # 다양한 사용량 통계 수집 (세션 기능 제외)
        total_usage = context.usage_tracker.get_total_usage_from_history()
        today_usage = context.usage_tracker.get_today_usage_from_summary()
        weekly_usage = context.usage_tracker.get_weekly_usage()
        monthly_usage = context.usage_tracker.get_monthly_usage()
        usage_by_model = context.usage_tracker.get_usage_by_model(days=30)  # 최근 30일
        usage_trends = context.usage_tracker.get_usage_trends(days=7)  # 최근 7일
        estimated_monthly_cost = context.usage_tracker.estimate_monthly_cost()

        return UsageStatsResponse(
            total_usage=total_usage,
            today_usage=today_usage,
            weekly_usage=weekly_usage,
            monthly_usage=monthly_usage,
            usage_by_model=usage_by_model,
            usage_trends=usage_trends,
            estimated_monthly_cost=estimated_monthly_cost
        )

    except Exception as e:
        logger.error(f"Error retrieving usage statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage statistics")


@app.get("/api/status/providers", response_model=ProviderStatusResponse)
def get_provider_status(context: AppContext = Depends(get_app_context)):
    """AI 제공업체별 상태 정보를 조회합니다."""
    try:
        # 모든 제공업체 목록 가져오기
        provider_names = ModelRegistry.get_all_provider_display_names()

        providers_status = {}
        total_providers = len(provider_names)
        configured_count = 0
        total_models = 0

        for provider_name in provider_names:
            # 제공업체 enum 가져오기
            provider_enum = ModelRegistry.get_provider_enum_by_display_name(provider_name)

            # API 키 설정 여부 확인
            has_api_key = False
            if provider_enum:
                has_api_key = context.settings.has_api_key(provider_enum)
                if has_api_key:
                    configured_count += 1

            # 사용 가능한 모델 목록
            models = ModelRegistry.get_models_for_provider(provider_name)
            model_count = len(models)
            total_models += model_count

            # 모델 정보 요약
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
                    "output_cost_per_1k": model_config.output_cost_per_1k
                })

            # 제공업체 상태 정보
            providers_status[provider_name] = {
                "provider_enum": provider_enum.value if provider_enum else None,
                "api_key_configured": has_api_key,
                "status": "configured" if has_api_key else "not_configured",
                "model_count": model_count,
                "models": model_summaries
            }

        # 전체 요약 정보
        summary = {
            "total_providers": total_providers,
            "configured_providers": configured_count,
            "unconfigured_providers": total_providers - configured_count,
            "total_models": total_models,
            "configuration_rate": round(configured_count / total_providers * 100, 1) if total_providers > 0 else 0
        }

        return ProviderStatusResponse(
            providers=providers_status,
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error retrieving provider status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve provider status")


@app.post("/api/sessions", response_model=SessionResponse)
def create_session(
        request: SessionCreateRequest,
        context: AppContext = Depends(get_app_context)
):
    """새로운 채팅 세션을 생성합니다."""
    try:
        session = context.chat_manager.create_session(title=request.title)
        return SessionResponse(session=session, message="Session created successfully")

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@app.delete("/api/sessions/{session_id}")
def delete_session(
        session_id: str,
        context: AppContext = Depends(get_app_context)
):
    """채팅 세션을 삭제합니다."""
    try:
        success = context.chat_manager.delete_session(session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"message": f"Session {session_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


@app.put("/api/sessions/{session_id}", response_model=SessionResponse)
def update_session(
        session_id: str,
        request: SessionUpdateRequest,
        context: AppContext = Depends(get_app_context)
):
    """채팅 세션의 제목이나 고정 상태를 업데이트합니다."""
    try:
        # 세션 존재 여부 확인
        session = context.chat_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # 최소 하나의 필드는 업데이트되어야 함
        if request.title is None and request.is_pinned is None:
            raise HTTPException(
                status_code=400,
                detail="At least one field (title or is_pinned) must be provided for update"
            )

        # 제목 업데이트
        if request.title is not None:
            context.chat_manager.update_session_title(session_id, request.title)

        # 고정 상태 업데이트
        if request.is_pinned is not None:
            if request.is_pinned:
                pin_success = context.chat_manager.pin_session(session_id)
                if not pin_success:
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to pin session (maximum 7 pinned sessions allowed)"
                    )
            else:
                context.chat_manager.unpin_session(session_id)

        # 업데이트된 세션 반환
        updated_session = context.chat_manager.get_session(session_id)
        return SessionResponse(session=updated_session, message="Session updated successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update session")


@app.get("/api/spotify/status", response_model=SpotifyStatusResponse)
def get_spotify_status(context: AppContext = Depends(get_app_context)):
    """Spotify 연결 상태를 조회합니다."""
    try:
        is_configured = context.spotify_manager.is_configured()
        is_authenticated = False
        user_id = None

        if is_configured:
            is_authenticated = context.spotify_manager.is_authenticated()
            if is_authenticated and context.spotify_manager.client:
                user_id = context.spotify_manager.client.user_id

        return SpotifyStatusResponse(
            is_configured=is_configured,
            is_authenticated=is_authenticated,
            user_id=user_id
        )

    except Exception as e:
        logger.error(f"Error getting Spotify status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Spotify status")


@app.post("/api/spotify/authenticate")
def authenticate_spotify(context: AppContext = Depends(get_app_context)):
    """Spotify 인증을 시작합니다."""
    try:
        if not context.spotify_manager.is_configured():
            raise HTTPException(status_code=400, detail="Spotify is not configured")

        success = context.spotify_manager.authenticate()

        if success:
            return {"message": "Spotify authentication successful", "authenticated": True}
        else:
            return {"message": "Spotify authentication failed", "authenticated": False}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error authenticating Spotify: {e}")
        raise HTTPException(status_code=500, detail="Failed to authenticate Spotify")


@app.get("/api/spotify/playlists", response_model=SpotifyPlaylistsResponse)
def get_spotify_playlists(context: AppContext = Depends(get_app_context)):
    """사용자의 Spotify 플레이리스트 목록을 조회합니다."""
    try:
        if not context.spotify_manager.is_authenticated():
            raise HTTPException(status_code=401, detail="Spotify authentication required")

        playlists = context.spotify_manager.get_user_playlists()
        playlist_dicts = [playlist.to_dict() for playlist in playlists]

        return SpotifyPlaylistsResponse(
            playlists=playlist_dicts,
            count=len(playlist_dicts)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Spotify playlists: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Spotify playlists")


@app.get("/api/spotify/tracks/liked", response_model=SpotifyTracksResponse)
def get_spotify_liked_tracks(context: AppContext = Depends(get_app_context)):
    """캐시된 Spotify 좋아요 트랙 목록을 조회합니다."""
    try:
        if not context.spotify_manager.is_authenticated():
            raise HTTPException(status_code=401, detail="Spotify authentication required")

        # 캐시에서 데이터 조회 (빠른 응답)
        tracks = context.spotify_manager.get_saved_tracks(use_cache=True)
        track_dicts = [track.to_dict() for track in tracks]

        return SpotifyTracksResponse(
            tracks=track_dicts,
            count=len(track_dicts),
            message=f"Retrieved {len(track_dicts)} cached liked tracks"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cached Spotify liked tracks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cached liked tracks")
        """사용자의 Spotify 좋아요 트랙 목록을 조회합니다."""
    try:
        if not context.spotify_manager.is_authenticated():
            raise HTTPException(status_code=401, detail="Spotify authentication required")

        tracks = context.spotify_manager.get_saved_tracks()
        track_dicts = [track.to_dict() for track in tracks]

        return SpotifyTracksResponse(
            tracks=track_dicts,
            count=len(track_dicts)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Spotify liked tracks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Spotify liked tracks")


@app.get("/api/spotify/playlists/{playlist_id}/tracks", response_model=SpotifyTracksResponse)
def get_spotify_playlist_tracks(
        playlist_id: str,
        context: AppContext = Depends(get_app_context)
):
    """특정 플레이리스트의 트랙 목록을 조회합니다."""
    try:
        if not context.spotify_manager.is_authenticated():
            raise HTTPException(status_code=401, detail="Spotify authentication required")

        tracks = context.spotify_manager.get_playlist_tracks(playlist_id)
        track_dicts = [track.to_dict() for track in tracks]

        return SpotifyTracksResponse(
            tracks=track_dicts,
            count=len(track_dicts)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting playlist tracks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get playlist tracks")


@app.delete("/api/spotify/cache")
def clear_spotify_cache(context: AppContext = Depends(get_app_context)):
    """Spotify 캐시를 삭제합니다."""
    try:
        context.spotify_manager.clear_cache()
        return {"message": "Spotify cache cleared successfully"}

    except Exception as e:
        logger.error(f"Error clearing Spotify cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear Spotify cache")


@app.post("/api/spotify/sync/start", response_model=SyncJobResponse)
def start_spotify_sync(
        background_tasks: BackgroundTasks,
        context: AppContext = Depends(get_app_context)
):
    """Spotify 데이터 동기화를 비동기로 시작합니다."""
    try:
        if not context.spotify_manager.is_authenticated():
            raise HTTPException(status_code=401, detail="Spotify authentication required")

        # 새 작업 생성
        job_id = job_manager.create_job("spotify_sync")

        # 백그라운드 작업 시작
        background_tasks.add_task(sync_spotify_data, job_id, context.spotify_manager)

        return SyncJobResponse(
            job_id=job_id,
            status="started",
            message=f"Spotify 동기화 작업이 시작되었습니다. Job ID: {job_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting Spotify sync: {e}")
        raise HTTPException(status_code=500, detail="Failed to start Spotify sync")


@app.get("/api/spotify/sync/status/{job_id}", response_model=SyncStatusResponse)
def get_sync_status(job_id: str):
    """동기화 작업의 진행 상태를 조회합니다."""
    try:
        job = job_manager.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return SyncStatusResponse(
            job_id=job["id"],
            status=job["status"],
            progress=job["progress"],
            current_step=job["current_step"],
            total_items=job["total_items"],
            processed_items=job["processed_items"],
            error_message=job["error_message"],
            started_at=job["started_at"],
            completed_at=job["completed_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sync status")

@app.put("/api/settings", response_model=SettingsResponse)
def update_settings(
        request: SettingsUpdateRequest,
        context: AppContext = Depends(get_app_context)
):
    """애플리케이션 설정을 업데이트합니다."""
    try:
        updated_count = 0

        # 각 설정값을 개별적으로 업데이트
        for key_path, value in request.updates.items():
            # API 키는 보안상 직접 업데이트 불가
            if key_path.startswith("api_keys."):
                logger.warning(f"Attempted to update API key via settings API: {key_path}")
                continue

            context.settings.set(key_path, value)
            updated_count += 1
            logger.info(f"Updated setting: {key_path}")

        # 업데이트된 설정 반환
        safe_settings = context.settings.export_settings()
        return SettingsResponse(
            settings=safe_settings,
            message=f"Successfully updated {updated_count} settings"
        )

    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")


# --- 백그라운드 작업 함수들 ---
def sync_spotify_data(job_id: str, spotify_manager):
    """Spotify 데이터 동기화 백그라운드 작업"""
    try:
        logger.info(f"Starting Spotify sync job: {job_id}")

        # 1단계: 기본 상태 업데이트
        job_manager.update_job(job_id,
                               status="running",
                               current_step="Spotify 연결 확인 중...",
                               progress=5
                               )

        if not spotify_manager.is_authenticated():
            job_manager.complete_job(job_id, success=False, error="Spotify 인증이 필요합니다")
            return

        # 2단계: 좋아요 트랙 수 확인
        job_manager.update_job(job_id,
                               current_step="좋아요 트랙 개수 확인 중...",
                               progress=10
                               )

        # 간단히 첫 페이지만 가져와서 전체 개수 확인
        if spotify_manager.client and spotify_manager.client.sp:
            try:
                initial_result = spotify_manager.client.sp.current_user_saved_tracks(limit=1)
                total_tracks = initial_result['total']

                job_manager.update_job(job_id,
                                       current_step=f"총 {total_tracks}개 좋아요 트랙 발견",
                                       progress=15,
                                       total_items=total_tracks
                                       )

                # 너무 많으면 제한 (프로토타입용)
                if total_tracks > 1000:
                    job_manager.update_job(job_id,
                                           current_step="안전을 위해 최신 1000개만 동기화합니다...",
                                           progress=20,
                                           total_items=1000
                                           )


            except (AttributeError, KeyError, ValueError) as e:
                logger.error(f"Error checking track count: {e}")
                job_manager.complete_job(job_id, success=False, error=f"트랙 개수 확인 실패: {str(e)}")
                return

            except Exception as e:
                logger.error(f"Unexpected error checking track count: {e}")
                job_manager.complete_job(job_id, success=False, error=f"예기치 않은 오류: {str(e)}")
                return

        # 3단계: 실제 데이터 동기화 (진행률 콜백 포함)
        def progress_callback(message: str):
            # 메시지에서 진행률 추출 시도
            current_progress = job_manager.get_job(job_id)["progress"]
            if "로드" in message and "/" in message:
                try:
                    # "1500/3000" 같은 패턴에서 진행률 계산
                    parts = message.split()
                    for part in parts:
                        if "/" in part:
                            current, total = part.split("/")
                            progress = int(20 + (int(current) / int(total)) * 70)  # 20-90% 범위
                            job_manager.update_job(job_id,
                                                   current_step=message,
                                                   progress=min(progress, 90),
                                                   processed_items=int(current)
                                                   )
                            break
                except (ValueError, IndexError, AttributeError):
                            # 진행률 파싱 실패는 무시
                    pass
            else:
                # 일반 메시지
                job_manager.update_job(job_id,
                                       current_step=message,
                                       progress=min(current_progress + 5, 85)
                                       )

        job_manager.update_job(job_id,
                               current_step="좋아요 트랙 데이터 동기화 중...",
                               progress=25
                               )

        # 실제 동기화 실행 (캐시 강제 갱신)
        tracks = spotify_manager.get_saved_tracks(
            progress_callback=progress_callback,
            use_cache=False  # 강제로 새 데이터 가져오기
        )

        # 4단계: 완료
        job_manager.update_job(job_id,
                               current_step="동기화 완료!",
                               progress=100,
                               processed_items=len(tracks)
                               )

        job_manager.complete_job(job_id, success=True)
        logger.info(f"Spotify sync job completed: {job_id}, {len(tracks)} tracks")

    except Exception as e:
        logger.error(f"Error in Spotify sync job {job_id}: {e}")
        job_manager.complete_job(job_id, success=False, error=str(e))


# -----------------------------

# --- 서버 실행 (로컬 개발용) ---
if __name__ == "__main__":
    # 터미널에서 `python backend/main.py` 를 실행하면 서버가 시작됩니다.
    uvicorn.run(app, host="0.0.0.0", port=8000)
# -----------------------------
