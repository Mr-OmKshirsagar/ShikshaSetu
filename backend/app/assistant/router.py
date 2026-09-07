"""FastAPI router for the AI Virtual Capability Assistant."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pymongo.database import Database
from pydantic import BaseModel, Field
from typing import Optional

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
    """
    user_id = str(current_user["_id"])
    return service.process_chat(user_id=user_id, request=payload)


# ─── Dataset 18: Feedback Log ────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="The chat session/message identifier")
    query: str = Field(..., description="The original user query")
    retrieved_chunk_ids: list[str] = Field(default_factory=list)
    final_answer: str = Field(default="")
    user_rating: Optional[int] = Field(default=None, ge=1, le=5, description="1-5 rating")
    thumbs_up: Optional[bool] = Field(default=None, description="True=helpful, False=not helpful")
    flagged_hallucination: bool = Field(default=False)
    flagged_reason: Optional[str] = Field(default=None)


@router.post("/feedback", status_code=201)
def submit_feedback(
    payload: FeedbackRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Dataset 18 — Append feedback record to the retrieval feedback log.
    Used for future retrieval improvement and hallucination tracking.
    The feedback is user-scoped: no cross-user data is stored.
    """
    db = getattr(request.app.state, "database", None)
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    user_id = str(current_user["_id"])
    doc = {
        "user_id": user_id,           # scoped to requesting user
        "session_id": payload.session_id,
        "query": payload.query,
        "retrieved_chunk_ids": payload.retrieved_chunk_ids,
        "final_answer": payload.final_answer[:500] if payload.final_answer else "",
        "user_rating": payload.user_rating,
        "thumbs_up": payload.thumbs_up,
        "flagged_hallucination": payload.flagged_hallucination,
        "flagged_reason": payload.flagged_reason,
        "timestamp": datetime.now(UTC),
        "resolved": False,
        "resolution_notes": None,
    }
    try:
        result = db.rag_feedback.insert_one(doc)
        return {"status": "recorded", "feedback_id": str(result.inserted_id)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {exc}")
