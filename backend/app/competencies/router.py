from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import get_current_user
from app.competencies import service
from app.competencies.schemas import CompetencyResponse, UserApplicableCompetencyResponse
from app.core.analytics_cache import (
    get_user_competencies_cache,
    set_user_competencies_cache,
)

router = APIRouter(prefix="/competencies", tags=["competencies"])


@router.get("", response_model=list[CompetencyResponse])
def get_competencies(request: Request) -> list[dict]:
    return service.list_competencies(getattr(request.app.state, "database", None))


@router.get("/me", response_model=list[UserApplicableCompetencyResponse])
def get_my_competencies(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> list[dict]:
    user_id = str(current_user["_id"])
    cached = get_user_competencies_cache(user_id)
    if cached is not None:
        return cached
    data = service.list_user_competencies(
        getattr(request.app.state, "database", None),
        user_id,
    )
    set_user_competencies_cache(user_id, data)
    return data


@router.get("/{competency_id}", response_model=CompetencyResponse)
def get_competency(request: Request, competency_id: str) -> dict:
    return service.get_competency(getattr(request.app.state, "database", None), competency_id)

