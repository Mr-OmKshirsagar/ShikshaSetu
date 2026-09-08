"""FastAPI router for the AI Virtual Capability Assistant."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pymongo.database import Database

from app.auth.dependencies import get_current_user
from app.core.config import get_settings
from .service import AssistantService
from .schemas import AssistantChatRequest, AssistantChatResponse

router = APIRouter(prefix="/assistant", tags=["Virtual Capability Assistant"])


def _get_db(request: Request) -> Database:
    db = getattr(request.app.state, "database", None)
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        )
    return db


def get_assistant_service(request: Request) -> AssistantService:
    database = _get_db(request)
    settings = getattr(request.app.state, "settings", None) or get_settings()
    return AssistantService(database, settings)


@router.post("/chat", response_model=AssistantChatResponse)
def chat_with_copilot(
    payload: AssistantChatRequest,
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service),
) -> AssistantChatResponse:
    """
    Conversational capability advisor grounded in user's real competency state,
    skill gaps, recommended courses, and curriculum RAG chunks.
    Deterministic queries (gaps, recommendations) use fast backend data.
    """
    user_id = str(current_user["_id"])
    return service.process_chat(user_id=user_id, request=payload)


@router.post("/chat/stream")
def stream_chat_with_copilot(
    payload: AssistantChatRequest,
    current_user: dict = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service),
) -> StreamingResponse:
    """
    Server-Sent Events (SSE) streaming endpoint for the Karmayogi AI Co-Pilot.
    Yields progressive status events, text chunk deltas, and the final response.
    """
    user_id = str(current_user["_id"])
    return StreamingResponse(
        service.stream_chat(user_id=user_id, request=payload),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
