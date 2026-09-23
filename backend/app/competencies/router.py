from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import get_current_user
from app.competencies import service
from app.competencies.schemas import CompetencyResponse, UserApplicableCompetencyResponse
from app.core.analytics_cache import (
    get_user_competencies_cache,
    set_user_competencies_cache,
)
from app.core.database import get_or_reconnect_database

router = APIRouter(prefix="/competencies", tags=["competencies"])


@router.get("", response_model=list[CompetencyResponse])
def get_competencies(request: Request) -> list[dict]:
    db = get_or_reconnect_database(request.app)
    return service.list_competencies(db)


@router.get("/me", response_model=list[UserApplicableCompetencyResponse])
def get_my_competencies(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> list[dict]:
    user_id = str(current_user["_id"])
    cached = get_user_competencies_cache(user_id)
    if cached is not None:
        return cached
    db = get_or_reconnect_database(request.app)
    data = service.list_user_competencies(
        db,
        user_id,
    )
    set_user_competencies_cache(user_id, data)
    return data


@router.get("/{competency_id}", response_model=CompetencyResponse)
def get_competency(request: Request, competency_id: str) -> dict:
    db = get_or_reconnect_database(request.app)
    return service.get_competency(db, competency_id)
