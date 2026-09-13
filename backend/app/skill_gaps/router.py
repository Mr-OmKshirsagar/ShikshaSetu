"""
API router for skill gaps.

Endpoints:
  GET /api/v1/skill-gaps/me
"""

from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import get_current_user
from app.core.analytics_cache import (
    get_user_skill_gaps_cache,
    set_user_skill_gaps_cache,
)
from app.skill_gaps import service
from app.skill_gaps.schemas import SkillGapResponse

router = APIRouter(prefix="/skill-gaps", tags=["skill-gaps"])


@router.get("/me", response_model=SkillGapResponse)
def get_my_skill_gaps(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> SkillGapResponse:
    """
    Get skill gaps for authenticated employee.
    
    Returns:
        SkillGapResponse with role, summary, and sorted gaps
    
    Raises:
        422: User does not have a professional role
        404: Role has no competency requirements
        503: Database unavailable
    """
    user_id = str(current_user["_id"])
    cached = get_user_skill_gaps_cache(user_id)
    if cached is not None:
        return cached
    database = getattr(request.app.state, "database", None)
    data = service.calculate_skill_gaps(database, user_id)
    set_user_skill_gaps_cache(user_id, data)
    return data
